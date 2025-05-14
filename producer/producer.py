import openmeteo_requests
import requests_cache
import pandas as pd
import json
import time
import logging
from retry_requests import retry
from datetime import datetime
from kafka import KafkaProducer

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('weather_producer')

# Set up the requests cache and retry session
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
url = 'https://api.open-meteo.com/v1/forecast'
params = {
    'latitude': 50.049683,
    'longitude': 19.944544,
    'current': ["temperature_2m", "relative_humidity_2m", "precipitation", "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
    'timezone': 'Europe/Berlin',
    "forecast_days": 1
}

# Create a Kafka producer


def create_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
        logger.info("Kafka producer created successfully.")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise


# Fetch weather data from Open-Meteo API
def fetch_data():
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    current_data = {
        "temperature": current.Variables(0).Value(),
        "relative_humidity": current.Variables(1).Value(),
        "precipitation": current.Variables(2).Value(),
        "surface_pressure": current.Variables(3).Value(),
        "wind_speed": current.Variables(4).Value(),
        "wind_direction": current.Variables(5).Value(),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return current_data


# Send the data to Kafka
def send_to_kafka(producer: KafkaProducer, topic_name, data):
    try:
        future = producer.send(topic_name, value=data)
        future.get(timeout=10)
        logger.info(f"Data sent to Kafka topic {topic_name}: {data}")
    except Exception as e:
        logger.error(f"Failed to send data to Kafka: {e}")
        raise


def run_weather_stream(interval=600, topic_name='weather_data'):
    producer = create_kafka_producer()

    try:
        while True:
            # Fetch the data
            weather_data = fetch_data()

            # Send the data to Kafka
            send_to_kafka(producer, topic_name, weather_data)

            # Wait for the specified interval
            logger.info(
                f"Waiting for {interval} seconds before fetching new data...")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Weather data streaming stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if producer:
            producer.flush()
            producer.close()
            logger.info("Kafka producer closed.")


if __name__ == "__main__":
    # Run the weather data streaming
    run_weather_stream(interval=600, topic_name='weather_data')
