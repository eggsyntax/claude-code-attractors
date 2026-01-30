"""
Smart Traffic Optimization System - Real-Time Data Ingestion Engine
Backend Implementation by Bob (Backend Specialist)
Part of 3-Agent Hierarchical Collaboration Experiment

This module implements enterprise-grade real-time traffic data processing
with multi-source integration, intelligent buffering, and ML-ready output.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import aiohttp
import asyncpg
from kafka import KafkaProducer, KafkaConsumer
from redis.asyncio import Redis


class DataSourceType(Enum):
    """Traffic data source types with reliability indicators"""
    TRAFFIC_CAMERAS = "cameras"
    SENSOR_NETWORKS = "sensors"
    GPS_AGGREGATES = "gps"
    WEATHER_API = "weather"
    INCIDENT_FEEDS = "incidents"


@dataclass
class TrafficDataPoint:
    """Standardized traffic measurement with metadata"""
    source_type: DataSourceType
    location_id: str
    timestamp: datetime
    vehicle_count: Optional[int] = None
    average_speed: Optional[float] = None  # km/h
    congestion_level: Optional[float] = None  # 0-1 scale
    weather_conditions: Optional[Dict[str, Any]] = None
    incidents: Optional[List[Dict[str, Any]]] = None
    confidence_score: float = 1.0  # Data reliability
    raw_data: Optional[Dict[str, Any]] = None

    def to_ml_features(self) -> Dict[str, float]:
        """Convert to ML-ready feature vector"""
        return {
            'vehicle_count': self.vehicle_count or 0,
            'average_speed': self.average_speed or 0,
            'congestion_level': self.congestion_level or 0,
            'hour_of_day': self.timestamp.hour,
            'day_of_week': self.timestamp.weekday(),
            'confidence_score': self.confidence_score,
            'has_weather': 1.0 if self.weather_conditions else 0.0,
            'has_incidents': 1.0 if self.incidents else 0.0,
        }


class StreamProcessor:
    """
    Enterprise-grade real-time traffic data processor

    Handles multi-source ingestion, intelligent buffering, data quality
    validation, and ML pipeline preparation with enterprise reliability.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Connection pools
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis: Optional[Redis] = None
        self.kafka_producer: Optional[KafkaProducer] = None

        # Processing state
        self.processing_buffer: List[TrafficDataPoint] = []
        self.buffer_max_size = config.get('buffer_max_size', 1000)
        self.buffer_flush_interval = config.get('buffer_flush_interval', 30)  # seconds

        # Data quality thresholds
        self.min_confidence_score = config.get('min_confidence_score', 0.7)
        self.max_processing_delay = config.get('max_processing_delay', 300)  # seconds

        # Performance metrics
        self.processed_count = 0
        self.error_count = 0
        self.last_flush_time = datetime.now()

    async def initialize(self) -> None:
        """Initialize all connections and processing infrastructure"""
        try:
            # Database connection pool
            self.db_pool = await asyncpg.create_pool(
                host=self.config['db_host'],
                port=self.config['db_port'],
                user=self.config['db_user'],
                password=self.config['db_password'],
                database=self.config['db_name'],
                min_size=5,
                max_size=20
            )

            # Redis for caching and coordination
            self.redis = Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                decode_responses=True
            )

            # Kafka for ML pipeline integration
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.config['kafka_servers'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                acks='all',  # Ensure reliability
                retries=3
            )

            self.logger.info("StreamProcessor initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize StreamProcessor: {e}")
            raise

    async def process_data_stream(self, source_type: DataSourceType) -> AsyncGenerator[TrafficDataPoint, None]:
        """
        Process real-time data stream from specified source

        Implements intelligent buffering, quality validation, and
        error recovery for enterprise reliability.
        """
        try:
            while True:
                # Fetch raw data from source
                raw_data = await self._fetch_from_source(source_type)

                if raw_data:
                    # Convert to standardized format
                    data_point = await self._normalize_data(raw_data, source_type)

                    # Quality validation
                    if self._validate_data_quality(data_point):
                        # Add to processing buffer
                        self.processing_buffer.append(data_point)
                        self.processed_count += 1

                        # Yield for immediate processing
                        yield data_point

                        # Flush buffer if needed
                        await self._maybe_flush_buffer()
                    else:
                        self.logger.warning(f"Data quality validation failed for {source_type}")
                        self.error_count += 1

                # Adaptive polling based on data velocity
                await asyncio.sleep(await self._calculate_polling_interval(source_type))

        except Exception as e:
            self.logger.error(f"Error processing {source_type} stream: {e}")
            self.error_count += 1
            raise

    async def _fetch_from_source(self, source_type: DataSourceType) -> Optional[Dict[str, Any]]:
        """Fetch raw data from external traffic data sources"""
        try:
            if source_type == DataSourceType.TRAFFIC_CAMERAS:
                # Simulate camera API integration
                return await self._fetch_camera_data()
            elif source_type == DataSourceType.SENSOR_NETWORKS:
                # Simulate sensor network integration
                return await self._fetch_sensor_data()
            elif source_type == DataSourceType.GPS_AGGREGATES:
                # Simulate GPS aggregation service
                return await self._fetch_gps_data()
            elif source_type == DataSourceType.WEATHER_API:
                # Simulate weather service integration
                return await self._fetch_weather_data()
            elif source_type == DataSourceType.INCIDENT_FEEDS:
                # Simulate incident reporting integration
                return await self._fetch_incident_data()

        except Exception as e:
            self.logger.error(f"Failed to fetch from {source_type}: {e}")
            return None

    async def _fetch_camera_data(self) -> Dict[str, Any]:
        """Simulate traffic camera data fetching"""
        # In production: integrate with traffic camera APIs
        import random
        return {
            'location_id': f'cam_{random.randint(1, 100)}',
            'timestamp': datetime.now().isoformat(),
            'vehicle_count': random.randint(0, 50),
            'average_speed': random.uniform(20, 80),
            'image_analysis_confidence': random.uniform(0.7, 1.0)
        }

    async def _fetch_sensor_data(self) -> Dict[str, Any]:
        """Simulate traffic sensor data fetching"""
        import random
        return {
            'location_id': f'sensor_{random.randint(1, 200)}',
            'timestamp': datetime.now().isoformat(),
            'vehicle_count': random.randint(0, 100),
            'average_speed': random.uniform(10, 90),
            'sensor_accuracy': random.uniform(0.8, 1.0)
        }

    async def _normalize_data(self, raw_data: Dict[str, Any], source_type: DataSourceType) -> TrafficDataPoint:
        """Convert raw source data to standardized TrafficDataPoint"""

        # Parse timestamp
        timestamp = datetime.fromisoformat(raw_data['timestamp'].replace('Z', '+00:00'))

        # Calculate confidence score based on source reliability
        confidence_score = 1.0
        if source_type == DataSourceType.TRAFFIC_CAMERAS:
            confidence_score = raw_data.get('image_analysis_confidence', 0.8)
        elif source_type == DataSourceType.SENSOR_NETWORKS:
            confidence_score = raw_data.get('sensor_accuracy', 0.9)

        # Calculate congestion level from speed and count
        congestion_level = None
        if raw_data.get('vehicle_count') and raw_data.get('average_speed'):
            # Simple heuristic: higher count + lower speed = higher congestion
            normalized_count = min(raw_data['vehicle_count'] / 100, 1.0)
            normalized_speed = max(0, min(raw_data['average_speed'] / 80, 1.0))
            congestion_level = (normalized_count + (1 - normalized_speed)) / 2

        return TrafficDataPoint(
            source_type=source_type,
            location_id=raw_data['location_id'],
            timestamp=timestamp,
            vehicle_count=raw_data.get('vehicle_count'),
            average_speed=raw_data.get('average_speed'),
            congestion_level=congestion_level,
            confidence_score=confidence_score,
            raw_data=raw_data
        )

    def _validate_data_quality(self, data_point: TrafficDataPoint) -> bool:
        """Validate data quality and reliability"""

        # Confidence score threshold
        if data_point.confidence_score < self.min_confidence_score:
            return False

        # Timestamp freshness check
        age = (datetime.now() - data_point.timestamp).total_seconds()
        if age > self.max_processing_delay:
            return False

        # Basic data sanity checks
        if data_point.vehicle_count is not None and data_point.vehicle_count < 0:
            return False

        if data_point.average_speed is not None and (data_point.average_speed < 0 or data_point.average_speed > 200):
            return False

        return True

    async def _maybe_flush_buffer(self) -> None:
        """Flush processing buffer based on size or time thresholds"""
        should_flush = (
            len(self.processing_buffer) >= self.buffer_max_size or
            (datetime.now() - self.last_flush_time).total_seconds() >= self.buffer_flush_interval
        )

        if should_flush:
            await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Flush buffered data to persistent storage and ML pipeline"""
        if not self.processing_buffer:
            return

        try:
            # Batch insert to database
            await self._batch_insert_to_db(self.processing_buffer)

            # Send to ML pipeline via Kafka
            await self._send_to_ml_pipeline(self.processing_buffer)

            # Update caches
            await self._update_redis_cache(self.processing_buffer)

            self.logger.info(f"Flushed {len(self.processing_buffer)} data points")

            # Clear buffer
            self.processing_buffer.clear()
            self.last_flush_time = datetime.now()

        except Exception as e:
            self.logger.error(f"Error flushing buffer: {e}")
            raise

    async def _batch_insert_to_db(self, data_points: List[TrafficDataPoint]) -> None:
        """Batch insert data points to PostgreSQL"""
        if not self.db_pool:
            return

        async with self.db_pool.acquire() as conn:
            records = []
            for dp in data_points:
                records.append((
                    dp.source_type.value,
                    dp.location_id,
                    dp.timestamp,
                    dp.vehicle_count,
                    dp.average_speed,
                    dp.congestion_level,
                    dp.confidence_score,
                    json.dumps(dp.raw_data) if dp.raw_data else None
                ))

            await conn.executemany("""
                INSERT INTO traffic_data
                (source_type, location_id, timestamp, vehicle_count, average_speed,
                 congestion_level, confidence_score, raw_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, records)

    async def _send_to_ml_pipeline(self, data_points: List[TrafficDataPoint]) -> None:
        """Send data points to ML training pipeline via Kafka"""
        if not self.kafka_producer:
            return

        for dp in data_points:
            ml_features = dp.to_ml_features()
            message = {
                'features': ml_features,
                'timestamp': dp.timestamp.isoformat(),
                'location_id': dp.location_id
            }

            self.kafka_producer.send('traffic_ml_features', value=message)

        self.kafka_producer.flush()  # Ensure delivery

    async def _update_redis_cache(self, data_points: List[TrafficDataPoint]) -> None:
        """Update Redis cache with latest traffic conditions"""
        if not self.redis:
            return

        # Group by location for efficient caching
        location_data = {}
        for dp in data_points:
            if dp.location_id not in location_data:
                location_data[dp.location_id] = []
            location_data[dp.location_id].append(dp)

        # Update each location's cached state
        for location_id, points in location_data.items():
            # Use most recent data point for this location
            latest_point = max(points, key=lambda x: x.timestamp)

            cache_data = {
                'vehicle_count': latest_point.vehicle_count,
                'average_speed': latest_point.average_speed,
                'congestion_level': latest_point.congestion_level,
                'last_update': latest_point.timestamp.isoformat(),
                'confidence': latest_point.confidence_score
            }

            await self.redis.hset(f'traffic:{location_id}', mapping=cache_data)
            await self.redis.expire(f'traffic:{location_id}', 3600)  # 1 hour TTL

    async def _calculate_polling_interval(self, source_type: DataSourceType) -> float:
        """Calculate adaptive polling interval based on data source characteristics"""
        base_intervals = {
            DataSourceType.TRAFFIC_CAMERAS: 5.0,  # seconds
            DataSourceType.SENSOR_NETWORKS: 2.0,
            DataSourceType.GPS_AGGREGATES: 10.0,
            DataSourceType.WEATHER_API: 300.0,  # 5 minutes
            DataSourceType.INCIDENT_FEEDS: 30.0
        }

        base_interval = base_intervals.get(source_type, 10.0)

        # Adjust based on current processing load
        if len(self.processing_buffer) > self.buffer_max_size * 0.8:
            return base_interval * 1.5  # Slow down when buffer is full
        elif len(self.processing_buffer) < self.buffer_max_size * 0.2:
            return base_interval * 0.8  # Speed up when buffer is light

        return base_interval

    async def get_processing_metrics(self) -> Dict[str, Any]:
        """Get real-time processing performance metrics"""
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'buffer_size': len(self.processing_buffer),
            'error_rate': self.error_count / max(self.processed_count, 1),
            'buffer_utilization': len(self.processing_buffer) / self.buffer_max_size,
            'last_flush_age': (datetime.now() - self.last_flush_time).total_seconds()
        }

    async def shutdown(self) -> None:
        """Graceful shutdown with final buffer flush"""
        try:
            # Final buffer flush
            await self._flush_buffer()

            # Close connections
            if self.db_pool:
                await self.db_pool.close()

            if self.redis:
                await self.redis.close()

            if self.kafka_producer:
                self.kafka_producer.close()

            self.logger.info("StreamProcessor shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Example usage and integration point
async def main():
    """Example usage of the StreamProcessor"""
    config = {
        'db_host': 'localhost',
        'db_port': 5432,
        'db_user': 'traffic_user',
        'db_password': 'secure_password',
        'db_name': 'smart_traffic',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'kafka_servers': ['localhost:9092'],
        'buffer_max_size': 1000,
        'buffer_flush_interval': 30,
        'min_confidence_score': 0.7
    }

    processor = StreamProcessor(config)
    await processor.initialize()

    # Start processing multiple data streams concurrently
    tasks = []
    for source_type in DataSourceType:
        task = asyncio.create_task(
            process_source_stream(processor, source_type)
        )
        tasks.append(task)

    # Wait for all streams
    await asyncio.gather(*tasks)

async def process_source_stream(processor: StreamProcessor, source_type: DataSourceType):
    """Process a single data source stream"""
    async for data_point in processor.process_data_stream(source_type):
        # Data point is automatically processed and buffered
        logging.info(f"Processed {source_type}: {data_point.location_id}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())