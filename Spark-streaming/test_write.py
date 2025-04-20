from pyspark.sql import SparkSession
import time

# Define the output path INSIDE the container
output_path = "/tmp/spark_output/test_batch_write"

print("--- Starting Simple Spark Batch Write Test ---")
print(f"Attempting to write to: {output_path}")

spark = None
try:
    spark = SparkSession.builder \
        .appName("BatchWriteTest") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    print("SparkSession created.")

    # Create a simple DataFrame
    data = [("test1", 1), ("test2", 2)]
    columns = ["label", "value"]
    df = spark.createDataFrame(data, columns)

    print("DataFrame created:")
    df.show()

    # Write the DataFrame using BATCH writer (overwrite)
    print(f"Writing DataFrame to {output_path}...")
    df.write.mode("overwrite").parquet(output_path)
    print(f"Write command completed.")

    # Add a small sleep to allow filesystem events to potentially propagate
    print("Sleeping for 10 seconds...")
    time.sleep(10)
    print("Test finished.")


except Exception as e:
    print(f"\nERROR: An error occurred in the batch write test:")
    import traceback
    traceback.print_exc()

finally:
    if spark:
        print("Stopping Spark session.")
        spark.stop()