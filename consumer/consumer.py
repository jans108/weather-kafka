import json
import logging
import time
import os
from datetime import datetime
from kafka import KafkaConsumer
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('weather_consumer')


# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DATABASE', 'weather'),
    'user': os.getenv('MYSQL_USER', 'user'),
    'password': os.getenv('MYSQL_PASSWORD', os.getenv('mysql_pass'))
}

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'weather_data')
CONSUMER_GROUP = 'weather_consumers'


def create_kafka_consumer():
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=CONSUMER_GROUP,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        logger.info("Kafka consumer created successfully.")
        return consumer
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        raise


def create_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Connected to MySQL Server version {db_info}")
            return connection
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        raise


def ensure_table_exists(connection: mysql.connector.connection.MySQLConnection):
    try:
        cursor = connection.cursor()

        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            temperature FLOAT,
            relative_humidity FLOAT,
            precipitation FLOAT,
            surface_pressure FLOAT,
            wind_speed FLOAT,
            wind_direction FLOAT,
            timestamp DATETIME
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        logger.info("Weather data table is ready")
    except Error as e:
        logger.error(f"Error while creating table: {e}")
        raise
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()


def store_weather_data(connection: mysql.connector.connection.MySQLConnection, data: dict):
    try:
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO weather_data (temperature, relative_humidity, precipitation,
                                  surface_pressure, wind_speed, wind_direction, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Prepare the data for insertion
        values = (
            data.get('temperature'),
            data.get('relative_humidity'),
            data.get('precipitation'),
            data.get('surface_pressure'),
            data.get('wind_speed'),
            data.get('wind_direction'),
            data.get('timestamp')
        )

        cursor.execute(insert_query, values)
        connection.commit()
        logger.info(f"Weather data stored in MySQL: {data}")
    except Error as e:
        logger.error(f"Error while inserting data into MySQL: {e}")
        raise
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()


def run_weather_consumer():
    # Create Kafka consumer
    consumer = create_kafka_consumer()

    # Initial database connection
    connection = None

    try:
        connection = create_db_connection()

        ensure_table_exists(connection)

        logger.info(
            "Starting to consume messages from Kafka. Topic {KAFKA_TOPIC}")

        for message in consumer:
            weather_data = message.value
            logger.info(f"Received message: {weather_data}")

            # Store the data in MySQL
            store_weather_data(connection, weather_data)

            if not connection.is_connected():
                logger.info(
                    "Database connection lost. Reconnecting to MySQL...")
                connection = create_db_connection()

    except KeyboardInterrupt:
        logger.info("Weather data consumption stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if consumer:
            consumer.close()
            logger.info("Kafka consumer closed.")
        if connection and connection.is_connected():
            connection.close()
            logger.info("MySQL connection closed.")


if __name__ == "__main__":
    run_weather_consumer()
