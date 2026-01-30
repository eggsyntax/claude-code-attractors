#!/usr/bin/env python3
"""
Real-Time Traffic Data Ingestion Pipeline
Smart City Traffic Optimization Platform - Backend Component

This module handles the ingestion, processing, and storage of real-time traffic data
from multiple sources including sensors, GPS devices, weather services, and events.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

import asyncpg
import aioredis
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrafficDataPoint:
    """Structure for standardized traffic data points"""
    sensor_id: str
    timestamp: datetime
    location: Dict[str, float]  # {"lat": float, "lng": float}
    vehicle_count: int
    average_speed: float
    occupancy_rate: float
    data_type: str = "traffic_sensor"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class WeatherData:
    """Structure for weather information affecting traffic"""
    timestamp: datetime
    location: Dict[str, float]
    temperature: float
    precipitation: float
    visibility: float
    wind_speed: float
    conditions: str
    data_type: str = "weather"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class IncidentData:
    """Structure for traffic incidents and events"""
    incident_id: str
    timestamp: datetime
    location: Dict[str, float]
    incident_type: str  # accident, construction, event, emergency
    severity: int  # 1-5 scale
    estimated_duration: int  # minutes
    affected_roads: List[str]
    data_type: str = "incident"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class DataSource(ABC):
    """Abstract base class for data sources"""

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def disconnect(self):
        pass


class TrafficSensorSource(DataSource):
    """Data source for traffic sensor information"""

    def __init__(self, sensor_endpoints: List[str]):
        self.sensor_endpoints = sensor_endpoints
        self.active_sensors = []

    async def connect(self):
        """Initialize connections to traffic sensors"""
        logger.info(f"Connecting to {len(self.sensor_endpoints)} traffic sensors")
        # Simulate sensor connections
        self.active_sensors = self.sensor_endpoints

    async def fetch_data(self) -> List[TrafficDataPoint]:
        """Fetch current traffic data from all sensors"""
        data_points = []

        for sensor_id in self.active_sensors:
            # Simulate fetching sensor data
            data_point = TrafficDataPoint(
                sensor_id=sensor_id,
                timestamp=datetime.now(),
                location={"lat": 37.7749 + hash(sensor_id) % 100 * 0.001,
                         "lng": -122.4194 + hash(sensor_id) % 100 * 0.001},
                vehicle_count=max(0, 50 + (hash(sensor_id) % 100) - 50),
                average_speed=max(5, 35 + (hash(sensor_id) % 30) - 15),
                occupancy_rate=min(1.0, max(0.0, 0.3 + (hash(sensor_id) % 70) * 0.01))
            )
            data_points.append(data_point)

        return data_points

    async def disconnect(self):
        """Clean up sensor connections"""
        logger.info("Disconnecting from traffic sensors")
        self.active_sensors = []


class WeatherSource(DataSource):
    """Data source for weather information"""

    def __init__(self, weather_api_key: str):
        self.api_key = weather_api_key
        self.connected = False

    async def connect(self):
        """Initialize weather API connection"""
        logger.info("Connecting to weather service")
        self.connected = True

    async def fetch_data(self) -> List[WeatherData]:
        """Fetch current weather conditions"""
        if not self.connected:
            return []

        # Simulate weather data for city center
        weather = WeatherData(
            timestamp=datetime.now(),
            location={"lat": 37.7749, "lng": -122.4194},
            temperature=18.5,
            precipitation=0.2,
            visibility=10.0,
            wind_speed=12.0,
            conditions="partly_cloudy"
        )

        return [weather]

    async def disconnect(self):
        """Clean up weather API connection"""
        logger.info("Disconnecting from weather service")
        self.connected = False


class DataProcessor:
    """Processes and validates incoming data streams"""

    def __init__(self):
        self.validation_rules = {
            'traffic_sensor': self._validate_traffic_data,
            'weather': self._validate_weather_data,
            'incident': self._validate_incident_data
        }

    def _validate_traffic_data(self, data: Dict[str, Any]) -> bool:
        """Validate traffic sensor data"""
        required_fields = ['sensor_id', 'timestamp', 'location', 'vehicle_count', 'average_speed']
        return all(field in data for field in required_fields)

    def _validate_weather_data(self, data: Dict[str, Any]) -> bool:
        """Validate weather data"""
        required_fields = ['timestamp', 'location', 'temperature', 'conditions']
        return all(field in data for field in required_fields)

    def _validate_incident_data(self, data: Dict[str, Any]) -> bool:
        """Validate incident data"""
        required_fields = ['incident_id', 'timestamp', 'location', 'incident_type']
        return all(field in data for field in required_fields)

    async def process_data_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate a batch of data points"""
        processed_data = []

        for data_point in data_batch:
            data_type = data_point.get('data_type', 'unknown')

            if data_type in self.validation_rules:
                if self.validation_rules[data_type](data_point):
                    # Add processing metadata
                    data_point['processed_at'] = datetime.now().isoformat()
                    data_point['processor_version'] = '1.0.0'
                    processed_data.append(data_point)
                else:
                    logger.warning(f"Invalid {data_type} data point: {data_point}")
            else:
                logger.warning(f"Unknown data type: {data_type}")

        return processed_data


class DataStorage:
    """Handles data persistence to multiple storage systems"""

    def __init__(self, postgres_url: str, redis_url: str):
        self.postgres_url = postgres_url
        self.redis_url = redis_url
        self.db_pool = None
        self.redis_client = None

    async def connect(self):
        """Initialize database connections"""
        try:
            self.db_pool = await asyncpg.create_pool(self.postgres_url)
            self.redis_client = aioredis.from_url(self.redis_url)
            logger.info("Database connections established")
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            raise

    async def store_traffic_data(self, data_points: List[Dict[str, Any]]):
        """Store traffic data in time-series database"""
        if not self.db_pool:
            logger.error("Database not connected")
            return

        async with self.db_pool.acquire() as connection:
            for data_point in data_points:
                await connection.execute("""
                    INSERT INTO traffic_data
                    (sensor_id, timestamp, location, vehicle_count, average_speed, occupancy_rate)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                data_point['sensor_id'],
                data_point['timestamp'],
                json.dumps(data_point['location']),
                data_point['vehicle_count'],
                data_point['average_speed'],
                data_point['occupancy_rate'])

        # Also cache recent data in Redis for real-time access
        for data_point in data_points:
            cache_key = f"sensor:{data_point['sensor_id']}:latest"
            await self.redis_client.setex(
                cache_key,
                300,  # 5-minute TTL
                json.dumps(data_point)
            )

    async def store_weather_data(self, weather_data: List[Dict[str, Any]]):
        """Store weather data"""
        if not self.db_pool:
            return

        async with self.db_pool.acquire() as connection:
            for weather in weather_data:
                await connection.execute("""
                    INSERT INTO weather_data
                    (timestamp, location, temperature, precipitation, visibility, wind_speed, conditions)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                weather['timestamp'],
                json.dumps(weather['location']),
                weather['temperature'],
                weather['precipitation'],
                weather['visibility'],
                weather['wind_speed'],
                weather['conditions'])

    async def disconnect(self):
        """Clean up database connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()


class TrafficDataPipeline:
    """Main pipeline orchestrator for traffic data ingestion"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources = []
        self.processor = DataProcessor()
        self.storage = DataStorage(
            config['postgres_url'],
            config['redis_url']
        )
        self.kafka_producer = None
        self.running = False

    async def initialize(self):
        """Initialize all pipeline components"""
        logger.info("Initializing traffic data pipeline")

        # Initialize data sources
        traffic_sensors = TrafficSensorSource(self.config['sensor_endpoints'])
        weather_source = WeatherSource(self.config['weather_api_key'])

        self.data_sources = [traffic_sensors, weather_source]

        # Connect to all data sources
        for source in self.data_sources:
            await source.connect()

        # Initialize storage
        await self.storage.connect()

        # Initialize Kafka producer for real-time streaming
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=self.config['kafka_servers'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        logger.info("Pipeline initialization complete")

    async def run_data_collection_cycle(self):
        """Execute one cycle of data collection from all sources"""
        all_data = []

        # Collect data from all sources
        for source in self.data_sources:
            try:
                data = await source.fetch_data()
                # Convert data objects to dictionaries
                if data:
                    if hasattr(data[0], 'to_dict'):
                        data = [item.to_dict() for item in data]
                    all_data.extend(data)
            except Exception as e:
                logger.error(f"Error fetching data from {source.__class__.__name__}: {e}")

        if not all_data:
            return

        # Process and validate data
        processed_data = await self.processor.process_data_batch(all_data)

        if not processed_data:
            logger.warning("No valid data points after processing")
            return

        # Store data
        traffic_data = [d for d in processed_data if d.get('data_type') == 'traffic_sensor']
        weather_data = [d for d in processed_data if d.get('data_type') == 'weather']

        try:
            if traffic_data:
                await self.storage.store_traffic_data(traffic_data)
            if weather_data:
                await self.storage.store_weather_data(weather_data)
        except Exception as e:
            logger.error(f"Error storing data: {e}")

        # Stream to Kafka for real-time processing
        for data_point in processed_data:
            try:
                self.kafka_producer.send('traffic_data', data_point)
            except KafkaError as e:
                logger.error(f"Error sending to Kafka: {e}")

        logger.info(f"Processed {len(processed_data)} data points")

    async def start(self):
        """Start the continuous data pipeline"""
        logger.info("Starting traffic data pipeline")
        self.running = True

        while self.running:
            try:
                await self.run_data_collection_cycle()
                await asyncio.sleep(self.config.get('collection_interval', 30))
            except Exception as e:
                logger.error(f"Error in pipeline cycle: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def stop(self):
        """Stop the data pipeline gracefully"""
        logger.info("Stopping traffic data pipeline")
        self.running = False

        # Disconnect from all sources
        for source in self.data_sources:
            await source.disconnect()

        # Close storage connections
        await self.storage.disconnect()

        # Close Kafka producer
        if self.kafka_producer:
            self.kafka_producer.close()


# Example configuration
PIPELINE_CONFIG = {
    'postgres_url': 'postgresql://traffic_user:password@localhost:5432/traffic_db',
    'redis_url': 'redis://localhost:6379',
    'kafka_servers': ['localhost:9092'],
    'sensor_endpoints': [f'sensor_{i:03d}' for i in range(1, 101)],  # 100 sensors
    'weather_api_key': 'your_weather_api_key',
    'collection_interval': 30  # seconds
}


async def main():
    """Main entry point for the data pipeline"""
    pipeline = TrafficDataPipeline(PIPELINE_CONFIG)

    try:
        await pipeline.initialize()
        await pipeline.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await pipeline.stop()


if __name__ == "__main__":
    asyncio.run(main())