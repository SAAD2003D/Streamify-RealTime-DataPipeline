# Located at: kafka-producer/producer_simple.py

import json
from kafka import KafkaProducer
import pandas as pd
from kafka.errors import NoBrokersAvailable
import time

# --- Configuration ---
KAFKA_BROKER = 'broker:9092'      # Docker service name and internal port
KAFKA_TOPIC = 'streamify_topic'   # Topic to send messages to
#MESSAGE_COUNT = 5                 # How many messages to send
DELAY_SECONDS = 1                 # Delay between messages
# --- End Configuration ---

print(f"--- Simple Kafka Producer ---")
print(f"Attempting to connect to Kafka broker at {KAFKA_BROKER}...")

producer = None # Initialize producer variable
df= pd.read_csv('./datasets/dataset.csv') # Read the CSV file
MESSAGE_COUNT =df.shape[0] # Get the number of rows in the CSV file
try:
    # Create the producer instance
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        # Serialize message value as JSON bytes
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        # Wait only for leader acknowledgment (faster for testing)
        acks=1,
        # Increase request timeout slightly, helps if broker is slow initially
        request_timeout_ms=15000 , # 15 seconds
        metadata_max_age_ms=90000
    )
    print(f"Successfully connected to Kafka broker at {KAFKA_BROKER}.")

    # Send messages
    print(f"Sending {MESSAGE_COUNT} messages to topic '{KAFKA_TOPIC}'...")
    for _,row in df.iterrows()  :
        
        message_data=row.to_dict() 

        # Send the message (asynchronously by default)
        future = producer.send(KAFKA_TOPIC, value=message_data)
        print(f"Sent message: {message_data}")
        # Optional: Check if send failed immediately (basic check)
        try:
            # Quick check if metadata available, otherwise moves on
            future.get(timeout=0.1) 
        except Exception:
            # Errors will likely surface during flush if persistent
            pass 
            
        time.sleep(DELAY_SECONDS)

    print(f"Finished sending loop.")

except NoBrokersAvailable:
    print(f"ERROR: Could not connect to Kafka broker at {KAFKA_BROKER}. Ensure it's running and accessible on the network.")
except Exception as e:
    print(f"ERROR: An unexpected error occurred during connection or sending: {e}")

finally:
    # Ensure all buffered messages are sent before exiting
    if producer:
        print("Flushing remaining messages...")
        try:
            producer.flush(timeout=30) # Wait up to 30 seconds for flush
            print("Messages flushed.")
        except Exception as e:
            print(f"ERROR: Failed to flush messages: {e}")
        finally:
             print("Closing producer.")
             producer.close()
    print("--- Simple Kafka Producer Finished ---")