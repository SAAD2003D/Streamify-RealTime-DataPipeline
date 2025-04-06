# In Spark-streaming/consumer.py (or consumer_simple.py)

import os
from pyspark.sql import SparkSession
# ... other imports ...
import time # Import time for delay
import traceback

# --- Configuration ---
KAFKA_BROKER = 'broker:9092'
KAFKA_TOPIC = 'streamify_topic'
APP_NAME = "KafkaSparkConsumer" # Or SimpleKafkaSparkConsumer
SPARK_KAFKA_VERSION = "3.4.0" 
SPARK_KAFKA_PACKAGE = f"org.apache.spark:spark-sql-kafka-0-10_2.12:{SPARK_KAFKA_VERSION}"
# --- End Configuration ---

# Define correct schema matching producer output
# KAFKA_SCHEMA = ... 

def main():
    wait_seconds = 15 # Delay for network stabilization
    print(f"--- Waiting {wait_seconds} seconds for network/DNS ---")
    time.sleep(wait_seconds)

    print("--- Spark Streaming Consumer ---") 
    print(f"Reading from Kafka topic '{KAFKA_TOPIC}' at broker '{KAFKA_BROKER}'")
    print(f"Using Spark Kafka package: {SPARK_KAFKA_PACKAGE}")

    spark = None
    try:
        driver_host_name = os.uname()[1]
        print(f"--- DEBUG: Setting spark.driver.host to {driver_host_name} ---")
        
        # --- ADD JAVA DNS OPTIONS and verify bindAddress ---
        spark = SparkSession.builder \
            .appName(APP_NAME) \
            .config("spark.jars.packages", SPARK_KAFKA_PACKAGE) \
            .config("spark.sql.streaming.failOnDataLoss", "false") \
            .config("spark.driver.host", driver_host_name) \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .config("spark.driver.extraJavaOptions", "-Djava.net.preferIPv4Stack=true -Dnetworkaddress.cache.ttl=1 -Dnetworkaddress.cache.negative.ttl=1") \
            .config("spark.executor.extraJavaOptions", "-Djava.net.preferIPv4Stack=true -Dnetworkaddress.cache.ttl=1 -Dnetworkaddress.cache.negative.ttl=1") \
            .getOrCreate()
        # --- END JAVA DNS OPTIONS ---

        spark.sparkContext.setLogLevel("WARN")
        print("SparkSession created successfully.")

        print("--- DEBUG: Preparing Kafka DataFrame readStream ---")
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .option("kafka.session.timeout.ms", "60000") .option("kafka.request.timeout.ms", "75000") \
            .load()
        print("--- DEBUG: Kafka DataFrame readStream initialized ---")
        
        # ... rest of consumer script ...

    except Exception as e:
        print(f"\nERROR: An unexpected error occurred in the Spark job:")
        traceback.print_exc()
    finally:
        print("\nStopping Spark session...")
        if spark:
             spark.stop()
        print("--- Spark Streaming Consumer Finished ---")

if __name__ == "__main__":
    main()