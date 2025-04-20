import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import time
from faker import Faker
import random
import pandas as pd

# --- Configuration ---
KAFKA_BROKER = 'broker:9092'      # Kafka broker address
KAFKA_TOPIC = 'user_events_topic' # Kafka topic for user events
EVENT_COUNT = 1000                 # Number of events to generate
DELAY_SECONDS = 1                 # Delay between events
CSV_FILE_PATH = './datasets/cleaned_dataset.csv'  # Path to the CSV file
# --- End Configuration ---

# Initialize Faker instance
faker = Faker()

# Define possible event types, devices, and locations
EVENT_TYPES = ['play', 'pause', 'skip', 'auth', 'navigate']
DEVICES = ['mobile', 'desktop', 'tablet']
LOCATIONS = ['USA', 'India', 'Germany', 'UK', 'Canada']

print(f"--- Kafka User Events Producer ---")
print(f"Attempting to connect to Kafka broker at {KAFKA_BROKER}...")

producer = None  # Initialize producer variable

try:
    # Load the CSV file into a DataFrame
    print(f"Loading song data from '{CSV_FILE_PATH}'...")
    songs_df = pd.read_csv(CSV_FILE_PATH)
    print(f"Loaded {len(songs_df)} songs from the CSV file.")

    # Create the Kafka producer instance
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=1,
        request_timeout_ms=15000,
        metadata_max_age_ms=90000
    )
    print(f"Successfully connected to Kafka broker at {KAFKA_BROKER}.")

    # Generate and send random user events
    print(f"Generating and sending {EVENT_COUNT} user events to topic '{KAFKA_TOPIC}'...")
    for _ in range(EVENT_COUNT):
        # Randomly select a song from the DataFrame
        song = songs_df.sample(n=1).iloc[0]
        song_id = song['song_id']
        song_title = song['title']
        artist_name = song['artist_name']

        # Generate a random user event
        event = {
            "user_id": faker.uuid4(),
            "event_type": random.choice(EVENT_TYPES),
            "timestamp": faker.iso8601(),
            "song_id": song_id,
            "song_title": song_title,
            "artist_name": artist_name,
            "device": random.choice(DEVICES),
            "location": random.choice(LOCATIONS)
        }

        # Send the event to Kafka
        future = producer.send(KAFKA_TOPIC, value=event)
        print(f"Sent event: {event}")

        # Optional: Check if send failed immediately (basic check)
        try:
            future.get(timeout=0.1)
        except Exception:
            pass

        # Delay between events
        time.sleep(DELAY_SECONDS)

    print(f"Finished sending {EVENT_COUNT} user events.")

except FileNotFoundError:
    print(f"ERROR: CSV file '{CSV_FILE_PATH}' not found. Ensure the file exists and the path is correct.")
except NoBrokersAvailable:
    print(f"ERROR: Could not connect to Kafka broker at {KAFKA_BROKER}. Ensure it's running and accessible on the network.")
except Exception as e:
    print(f"ERROR: An unexpected error occurred during connection or sending: {e}")

finally:
    # Ensure all buffered messages are sent before exiting
    if producer:
        print("Flushing remaining messages...")
        try:
            producer.flush(timeout=30)
            print("Messages flushed.")
        except Exception as e:
            print(f"ERROR: Failed to flush messages: {e}")
        finally:
            print("Closing producer.")
            producer.close()
    print("--- Kafka User Events Producer Finished ---")