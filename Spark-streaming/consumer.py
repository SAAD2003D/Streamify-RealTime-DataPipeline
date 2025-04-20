import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, count
from pyspark.sql.types import StructType, StructField, StringType
import time
import traceback

# --- Dependencies for GCS Upload from Driver ---
from google.cloud import storage
import pandas as pd
import io
# --- End GCS Upload Dependencies ---

# --- Configuration ---
KAFKA_BROKER = 'broker:9092'
KAFKA_TOPIC = 'user_events_topic'
APP_NAME = "KafkaSparkGCSUploadDriver" # New name
# Kafka package needed for readStream, provided via spark-submit CMD
# SPARK_KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0"

# --- GCS Configuration ---
GCS_BUCKET_NAME = "user-event-bucket"  # <--- *** REPLACE WITH YOUR ACTUAL BUCKET NAME ***
GCP_PROJECT_ID = "manifest-glyph-456012-i8"    # <--- *** REPLACE WITH YOUR ACTUAL GCP PROJECT ID ***
# Path INSIDE container where the key file is MOUNTED via docker-compose.yml
GCS_KEYFILE_PATH = "/etc/gcp-keys/gcs-keyfile.json"

# --- GCS Output & Checkpoint Paths ---
# Checkpoints still need to be reliable - GCS is best practice
CHECKPOINT_BASE_DIR = "/tmp/spark_checkpoints_local"
OUTPUT_BASE_DIR = f"gs://{GCS_BUCKET_NAME}/output/{APP_NAME}" # Base path for blobs

# Define specific paths/prefixes using the GCS base paths
SONG_COUNTS_CHECKPOINT = f"{CHECKPOINT_BASE_DIR}/song_counts"
SONG_COUNTS_OUTPUT_GCS_PREFIX = f"{OUTPUT_BASE_DIR}/song_counts" # Used as prefix for blob name

EVENT_COUNTS_CHECKPOINT = f"{CHECKPOINT_BASE_DIR}/event_counts"
EVENT_COUNTS_OUTPUT_GCS_PREFIX = f"{OUTPUT_BASE_DIR}/event_counts"

LOCATION_COUNTS_CHECKPOINT = f"{CHECKPOINT_BASE_DIR}/location_counts"
LOCATION_COUNTS_OUTPUT_GCS_PREFIX = f"{OUTPUT_BASE_DIR}/location_counts"
# --- End Configuration ---

# --- Define Kafka Message Schema ---
schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("song_id", StringType(), True),
    StructField("song_title", StringType(), True),
    StructField("artist_name", StringType(), True),
    StructField("device", StringType(), True),
    StructField("location", StringType(), True)
])
# --- End Schema ---

# --- Function for forEachBatch (Collect to Driver & Upload) ---
def upload_aggregation_to_gcs(df, epoch_id, gcs_path_prefix, bucket_name, key_file_path, output_format="parquet"):
    """
    Collects aggregated data to the driver and uploads to GCS as a single file per batch.
    WARNING: This can cause Driver OutOfMemory errors if aggregated data per batch is large.
    """
    # Trigger action to get count (and potentially cache if df is reused)
    # Persisting can help if the df plan is complex and recomputed during count/toPandas
    # df.persist()
    count = df.count()
    print(f"--- Processing batch {epoch_id} for GCS Upload to {gcs_path_prefix} (Count: {count}) ---")

    if count > 0:
        print(f"--- Collecting data for batch {epoch_id} to driver... ---")
        try:
            # ** WARNING: Potential Driver OOM if data is large **
            pandas_df = df.toPandas()
            print(f"--- Collected {len(pandas_df)} rows. Preparing upload buffer... ---")

            # Use an in-memory buffer
            buffer = None
            content_type = None
            blob_suffix = ""

            if output_format == "parquet":
                buffer = io.BytesIO()
                pandas_df.to_parquet(buffer, index=False, engine='pyarrow')
                content_type = 'application/octet-stream' # Standard for binary parquet
                blob_suffix = "parquet"
            elif output_format == "csv":
                buffer = io.StringIO()
                pandas_df.to_csv(buffer, index=False, header=True)
                content_type = 'text/csv'
                # Convert StringIO to BytesIO for upload_from_file
                buffer_bytes = io.BytesIO(buffer.getvalue().encode('utf-8'))
                buffer_bytes.seek(0)
                buffer = buffer_bytes # Use the BytesIO version
                blob_suffix = "csv"
            else:
                 print(f"ERROR: Unsupported output format '{output_format}' for batch {epoch_id}")
                 # df.unpersist() # Unpersist if you persisted
                 return # Don't proceed

            buffer.seek(0) # Rewind buffer to the beginning before upload

            # Construct the target blob name - overwrites the same blob each time
            blob_relative_path = f"{gcs_path_prefix.replace(f'gs://{bucket_name}/', '')}/aggregated_output.{blob_suffix}"

            # --- Upload using google-cloud-storage ---
            print(f"--- Authenticating GCS client using: {key_file_path} ---")
            storage_client = storage.Client.from_service_account_json(key_file_path)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_relative_path)

            print(f"--- Uploading {buffer.getbuffer().nbytes} bytes to gs://{bucket_name}/{blob_relative_path} ---")
            blob.upload_from_file(buffer, content_type=content_type)
            print(f"--- Finished uploading batch {epoch_id} to gs://{bucket_name}/{blob_relative_path} ---")

        except Exception as e:
             # This error happens on the DRIVER
             print(f"--- ERROR during GCS upload for batch {epoch_id} to {gcs_path_prefix}: {e} ---")
             traceback.print_exc() # Print full stack trace for the error
        finally:
            # Ensure buffer is closed if it exists
            if buffer and hasattr(buffer, 'close'):
                 buffer.close()
            # df.unpersist() # Unpersist if you persisted

    else:
        print(f"--- Skipping GCS upload for empty batch {epoch_id} to {gcs_path_prefix} ---")
        # Optionally, you could delete the target blob here if you want empty batches
        # to clear the previous output, but skipping is usually fine.
# --- End forEachBatch function ---


def main():
    wait_seconds = 15
    print(f"--- Waiting {wait_seconds} seconds for network/DNS ---")
    time.sleep(wait_seconds)

    print(f"--- Spark Streaming Consumer - Uploading to GCS from Driver ---")
    print(f"Reading from Kafka topic '{KAFKA_TOPIC}' at broker '{KAFKA_BROKER}'")

    spark = None
    try:
        driver_host_name = os.uname()[1]
        print(f"--- DEBUG: Setting spark.driver.host to {driver_host_name} ---")

        # Build SparkSession - Kafka package from CMD, NO GCS packages/jars needed here
        spark_builder = SparkSession.builder \
            .appName(APP_NAME) \
            .config("spark.sql.streaming.failOnDataLoss", "false") \
            .config("spark.driver.host", driver_host_name) \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .config("spark.executor.memory", "4g") \
            .config("spark.driver.memory", "3g") \
            .config("spark.executor.cores", "2") \
            .config("spark.driver.extraJavaOptions", "-Djava.net.preferIPv4Stack=true -Dnetworkaddress.cache.ttl=1 -Dnetworkaddress.cache.negative.ttl=1") \
            .config("spark.executor.extraJavaOptions", "-Djava.net.preferIPv4Stack=true -Dnetworkaddress.cache.ttl=1 -Dnetworkaddress.cache.negative.ttl=1") \
            # Crucially, ensure the GCS Connector JAR (downloaded via --packages in CMD) IS on the classpath for checkpointing!
            # If checkpointing to GCS fails, you might need to revert to adding GCS package here too
            # OR ensure spark-submit propagates the classpath correctly.

        spark = spark_builder.getOrCreate()

        spark.sparkContext.setLogLevel("WARN")
        print("SparkSession created (GCS config for checkpoints).")

        # 1. Read from Kafka
        kafka_df_raw = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "earliest") \
            .load() # This needs the Kafka package from CMD

        # 2. Parse JSON
        parsed_df = kafka_df_raw \
            .selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")

        # 3. Aggregations
        song_counts_df = parsed_df \
            .groupBy("song_id", "song_title", "artist_name") \
            .agg(count("*").alias("play_count"))

        event_counts_df = parsed_df \
            .groupBy("event_type") \
            .agg(count("*").alias("event_count"))

        location_counts_df = parsed_df \
            .groupBy("location") \
            .agg(count("*").alias("location_count"))

        # 4. Write Outputs using forEachBatch (Upload from Driver)

        print("--- Starting Output Streams ---")
        # Choose output format for upload function ("parquet" or "csv")
        upload_format = "parquet"

        # --- Song Counts Sinks ---
        print(f"Setting up Song Counts stream (Console & Upload to GCS as {upload_format})")
        song_counts_console = song_counts_df.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", "false") \
            .option("numRows", 20) \
            .option("checkpointLocation", CHECKPOINT_BASE_DIR + "/console_checkpoints/song_counts") \
            .trigger(processingTime='60 seconds') \
            .start()

        song_counts_gcs = song_counts_df.writeStream \
            .outputMode("complete") \
            .foreachBatch(lambda df, epoch_id: upload_aggregation_to_gcs(df, epoch_id, SONG_COUNTS_OUTPUT_GCS_PREFIX, GCS_BUCKET_NAME, GCS_KEYFILE_PATH, upload_format)) \
            .option("checkpointLocation", SONG_COUNTS_CHECKPOINT) \
            .trigger(processingTime='60 seconds') \
            .start()

        # --- Event Type Counts Sinks ---
        print(f"Setting up Event Type Counts stream (Console & Upload to GCS as {upload_format})")
        event_counts_console = event_counts_df.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", "false") \
            .option("checkpointLocation", CHECKPOINT_BASE_DIR + "/console_checkpoints/event_counts") \
            .trigger(processingTime='60 seconds') \
            .start()

        event_counts_gcs = event_counts_df.writeStream \
            .outputMode("complete") \
            .foreachBatch(lambda df, epoch_id: upload_aggregation_to_gcs(df, epoch_id, EVENT_COUNTS_OUTPUT_GCS_PREFIX, GCS_BUCKET_NAME, GCS_KEYFILE_PATH, upload_format)) \
            .option("checkpointLocation", EVENT_COUNTS_CHECKPOINT) \
            .trigger(processingTime='60 seconds') \
            .start()

        # --- Location Counts Sinks ---
        print(f"Setting up Location Counts stream (Console & Upload to GCS as {upload_format})")
        location_counts_console = location_counts_df.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", "false") \
            .option("checkpointLocation", LOCATION_COUNTS_CHECKPOINT + "/console_checkpoints/location_counts") \
            .trigger(processingTime='60 seconds') \
            .start()

        location_counts_gcs = location_counts_df.writeStream \
            .outputMode("complete") \
            .foreachBatch(lambda df, epoch_id: upload_aggregation_to_gcs(df, epoch_id, LOCATION_COUNTS_OUTPUT_GCS_PREFIX, GCS_BUCKET_NAME, GCS_KEYFILE_PATH, upload_format)) \
            .option("checkpointLocation", LOCATION_COUNTS_CHECKPOINT) \
            .trigger(processingTime='60 seconds') \
            .start()

        print("--- All streams started. Awaiting termination... (Press Ctrl+C to stop) ---")
        spark.streams.awaitAnyTermination()

    except Exception as e:
        print(f"\nERROR: An unexpected error occurred in the Spark job:")
        traceback.print_exc()

    finally:
        # --- Graceful Shutdown (same as before) ---
        print("\nStopping Spark session...")
        # ... (rest of finally block) ...

if __name__ == "__main__":
    main()