# Weather Data Streaming with Kafka

## Project Overview

This project implements a real-time weather data streaming system using Apache Kafka and MySQL. The system fetches current weather data from the Open-Meteo API, publishes it to a Kafka topic, and then consumes and stores the data in a MySQL database.

## Architecture

The system consists of four main components:

- **Producer**: Fetches weather data from Open-Meteo API and publishes it to a Kafka topic
- **Kafka Broker**: Message broker that handles the data stream
- **Consumer**: Subscribes to Kafka topic and persists the data to MySQL
- **MySQL Database**: Stores the weather data for further analysis

## Features

- Real-time weather data collection for Kraków, Poland
- Fault-tolerant messaging with Apache Kafka
- Persistent storage in MySQL database
- Configurable data collection intervals
- Comprehensive logging for monitoring and debugging

## Technologies Used

- **Python 3.11**: Core programming language
- **Apache Kafka**: Distributed event streaming platform
- **MySQL**: Relational database management system
- **Docker/Docker Compose**: Containerization and orchestration
- **Open-Meteo API**: Free weather data service

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/weather-kafka.git
cd weather-kafka
```

2. Create a .env file with your configuration:
```bash
mysql_pass=your_password_here
```

3. Start the containers:
```bash
docker-compose up -d
```

## Usage

The system automatically starts collecting weather data when the containers are running. By default, weather data is collected every 60 seconds.

Check the data
Connect to the MySQL database and query the weather data:
```bash
mysql -h mysql -u user -p weather
```
```bash
SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 10;
```

## Monitoring

View the logs of the producer and consumer:
```bash
docker-compose logs -f producer
docker-compose logs -f consumer
```

# Project Structure
```bash
weather-kafka/
├── producer/
│   ├── producer.py       # Weather data producer
│   └── requirements.txt  # Producer dependencies
├── consumer/
│   ├── consumer.py       # Weather data consumer
│   └── requirements.txt  # Consumer dependencies
├── mysql/
│   └── init/            # MySQL initialization scripts
├── docker-compose.yml    # Docker Compose configuration
├── .env                  # Environment variables
└── README.md            # Project documentation
```

# Configuration

 - **Data Collection Interval**: Modify the interval parameter in producer.py (default: 60 seconds)
 - **Location**: Change latitude and longitude in the params dictionary in producer.py
 - **Database Schema**: Modify the table creation query in consumer.py

## Future Improvements

 - Add a web-based dashboard for real-time data visualization
 - Implement data analytics and weather pattern detection
 - Add alert system for extreme weather conditions
 - Support multiple locations for weather data collection
 - Improve error handling and retry mechanisms

## License

Mit License

## Acknowledgments
 - Open-Meteo for providing free weather data