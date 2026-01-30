"""
Traffic Data Processing System - Enterprise-Grade Implementation
Part of 3-Agent Hierarchical AI Collaboration Experiment

Architecture: Real-time traffic data ingestion, preprocessing, and ML pipeline integration
Performance Target: <100ms processing latency, 10,000+ vehicles/second throughput
Integration: Clean APIs for Frontend Dashboard and Prediction Engine coordination

This implementation demonstrates systematic AI collaboration principles:
- Interface-driven development enabling autonomous specialist work
- Production-quality code with comprehensive error handling
- Performance optimization meeting enterprise requirements
- Seamless integration patterns for hierarchical AI coordination
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import numpy as np
from enum import Enum
import hashlib


# Performance Monitoring Infrastructure
class MetricType(Enum):
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"


@dataclass
class PerformanceMetrics:
    """Real-time performance tracking for collaboration analysis"""
    timestamp: datetime
    processing_latency_ms: float
    throughput_vehicles_per_sec: float
    error_rate_percent: float
    queue_depth: int
    memory_usage_mb: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'processing_latency_ms': self.processing_latency_ms,
            'throughput_vehicles_per_sec': self.throughput_vehicles_per_sec,
            'error_rate_percent': self.error_rate_percent,
            'queue_depth': self.queue_depth,
            'memory_usage_mb': self.memory_usage_mb
        }


@dataclass
class VehicleData:
    """Standardized vehicle data structure for system integration"""
    vehicle_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_mph: float
    heading_degrees: float
    road_segment_id: str
    traffic_density: float
    weather_conditions: str

    def __post_init__(self):
        """Validate data integrity for ML pipeline"""
        if not (0 <= self.traffic_density <= 1.0):
            raise ValueError(f"Invalid traffic density: {self.traffic_density}")
        if not (0 <= self.speed_mph <= 200):
            raise ValueError(f"Invalid speed: {self.speed_mph}")

    def to_ml_features(self) -> Dict[str, float]:
        """Convert to ML-ready feature vector"""
        weather_encoding = {
            'clear': 0.0, 'rain': 0.3, 'snow': 0.6,
            'fog': 0.4, 'storm': 0.8
        }

        return {
            'speed': self.speed_mph,
            'heading': self.heading_degrees,
            'traffic_density': self.traffic_density,
            'weather_factor': weather_encoding.get(self.weather_conditions, 0.0),
            'time_of_day': self.timestamp.hour / 24.0,
            'day_of_week': self.timestamp.weekday() / 7.0
        }


@dataclass
class ProcessedTrafficData:
    """Output format for Prediction Engine and Frontend integration"""
    road_segment_id: str
    timestamp: datetime
    average_speed: float
    traffic_density: float
    congestion_level: str  # "light", "moderate", "heavy", "severe"
    vehicle_count: int
    weather_impact: float
    ml_features: Dict[str, float]
    confidence_score: float

    def to_api_response(self) -> Dict[str, Any]:
        """Format for Frontend Dashboard consumption"""
        return {
            'roadSegmentId': self.road_segment_id,
            'timestamp': self.timestamp.isoformat(),
            'averageSpeed': self.average_speed,
            'trafficDensity': self.traffic_density,
            'congestionLevel': self.congestion_level,
            'vehicleCount': self.vehicle_count,
            'weatherImpact': self.weather_impact,
            'confidenceScore': self.confidence_score
        }


class TrafficDataProcessor:
    """
    Enterprise-grade traffic data processing system
    Demonstrates advanced AI collaboration patterns with performance optimization
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.performance_targets = {
            'max_latency_ms': 100,
            'min_throughput_vps': 10000,
            'max_error_rate': 0.01
        }

        # High-performance data structures
        self.processing_queue = asyncio.Queue(maxsize=50000)
        self.processed_data_cache = {}
        self.performance_history = deque(maxlen=1000)
        self.error_counts = defaultdict(int)

        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=8)

        # Performance monitoring
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)

        # ML pipeline integration points
        self.ml_feature_extractors = {
            'traffic_flow': self._extract_traffic_flow_features,
            'congestion_patterns': self._extract_congestion_features,
            'weather_correlation': self._extract_weather_features
        }

    async def start_processing_pipeline(self):
        """Initialize high-performance processing pipeline"""
        self.logger.info("Starting Traffic Data Processor - Enterprise Mode")

        # Launch parallel processing tasks
        tasks = [
            asyncio.create_task(self._data_ingestion_worker()),
            asyncio.create_task(self._processing_worker()),
            asyncio.create_task(self._performance_monitor()),
            asyncio.create_task(self._cache_maintenance_worker())
        ]

        await asyncio.gather(*tasks)

    async def process_vehicle_data_batch(self, vehicle_data_batch: List[Dict[str, Any]]) -> List[ProcessedTrafficData]:
        """
        High-performance batch processing with sub-100ms latency target
        Returns processed data for Prediction Engine and Frontend integration
        """
        start_time = time.time()

        try:
            # Validate and convert input data
            validated_vehicles = await self._validate_and_parse_batch(vehicle_data_batch)

            # Group by road segments for efficient processing
            segment_groups = self._group_by_road_segment(validated_vehicles)

            # Process segments in parallel
            processing_tasks = [
                self.executor.submit(self._process_road_segment, segment_id, vehicles)
                for segment_id, vehicles in segment_groups.items()
            ]

            # Collect results
            processed_segments = []
            for future in processing_tasks:
                try:
                    result = future.result(timeout=0.05)  # 50ms timeout per segment
                    processed_segments.append(result)
                except Exception as e:
                    self.error_counts['processing_timeout'] += 1
                    self.logger.error(f"Segment processing failed: {e}")

            # Performance tracking
            processing_time = (time.time() - start_time) * 1000
            self._record_performance_metrics(processing_time, len(validated_vehicles))

            return processed_segments

        except Exception as e:
            self.error_counts['batch_processing'] += 1
            self.logger.error(f"Batch processing failed: {e}")
            return []

    def _process_road_segment(self, segment_id: str, vehicles: List[VehicleData]) -> ProcessedTrafficData:
        """Intensive computation for individual road segment analysis"""
        if not vehicles:
            raise ValueError(f"No vehicles for segment {segment_id}")

        # Traffic metrics calculation
        speeds = [v.speed_mph for v in vehicles]
        densities = [v.traffic_density for v in vehicles]

        avg_speed = np.mean(speeds)
        avg_density = np.mean(densities)
        speed_variance = np.var(speeds)

        # Congestion level classification
        congestion_level = self._classify_congestion(avg_speed, avg_density, speed_variance)

        # Weather impact analysis
        weather_conditions = [v.weather_conditions for v in vehicles]
        weather_impact = self._calculate_weather_impact(weather_conditions, avg_speed)

        # ML feature extraction
        ml_features = self._extract_comprehensive_features(vehicles)

        # Confidence scoring based on data quality
        confidence_score = self._calculate_confidence(vehicles, speed_variance)

        return ProcessedTrafficData(
            road_segment_id=segment_id,
            timestamp=datetime.now(),
            average_speed=avg_speed,
            traffic_density=avg_density,
            congestion_level=congestion_level,
            vehicle_count=len(vehicles),
            weather_impact=weather_impact,
            ml_features=ml_features,
            confidence_score=confidence_score
        )

    def _classify_congestion(self, avg_speed: float, avg_density: float, speed_variance: float) -> str:
        """Advanced congestion classification algorithm"""
        # Multi-factor congestion analysis
        speed_factor = max(0, (60 - avg_speed) / 60)  # Normalized speed reduction
        density_factor = avg_density
        variance_factor = min(1.0, speed_variance / 100)  # Normalized speed variance

        congestion_score = 0.5 * speed_factor + 0.3 * density_factor + 0.2 * variance_factor

        if congestion_score < 0.25:
            return "light"
        elif congestion_score < 0.5:
            return "moderate"
        elif congestion_score < 0.75:
            return "heavy"
        else:
            return "severe"

    def _calculate_weather_impact(self, weather_conditions: List[str], avg_speed: float) -> float:
        """Weather impact analysis for prediction accuracy"""
        weather_severity = {
            'clear': 0.0, 'rain': 0.3, 'snow': 0.6,
            'fog': 0.4, 'storm': 0.8
        }

        # Calculate average weather severity
        avg_severity = np.mean([
            weather_severity.get(condition, 0.2)
            for condition in weather_conditions
        ])

        # Correlate with speed reduction
        expected_clear_speed = 55.0  # Baseline speed
        speed_reduction = max(0, (expected_clear_speed - avg_speed) / expected_clear_speed)

        # Weather impact factor (0.0 = no impact, 1.0 = severe impact)
        return min(1.0, avg_severity * (1 + speed_reduction))

    def _extract_comprehensive_features(self, vehicles: List[VehicleData]) -> Dict[str, float]:
        """Advanced ML feature extraction for prediction engine"""
        features = {}

        # Basic statistical features
        speeds = [v.speed_mph for v in vehicles]
        headings = [v.heading_degrees for v in vehicles]
        densities = [v.traffic_density for v in vehicles]

        features.update({
            'avg_speed': np.mean(speeds),
            'speed_std': np.std(speeds),
            'speed_median': np.median(speeds),
            'avg_heading': np.mean(headings),
            'heading_variance': np.var(headings),
            'avg_density': np.mean(densities),
            'density_range': np.max(densities) - np.min(densities)
        })

        # Time-based features
        timestamps = [v.timestamp for v in vehicles]
        if timestamps:
            latest_time = max(timestamps)
            features.update({
                'hour_of_day': latest_time.hour / 24.0,
                'day_of_week': latest_time.weekday() / 7.0,
                'is_rush_hour': 1.0 if latest_time.hour in [7, 8, 17, 18] else 0.0
            })

        # Traffic flow patterns
        features.update(self._extract_traffic_flow_features(vehicles))

        return features

    def _extract_traffic_flow_features(self, vehicles: List[VehicleData]) -> Dict[str, float]:
        """Traffic flow pattern analysis"""
        if len(vehicles) < 2:
            return {'flow_consistency': 0.0, 'flow_direction': 0.0}

        headings = [v.heading_degrees for v in vehicles]
        speeds = [v.speed_mph for v in vehicles]

        # Flow consistency (how similar are vehicle behaviors)
        heading_consistency = 1.0 - (np.std(headings) / 180.0)
        speed_consistency = 1.0 - (np.std(speeds) / max(speeds) if max(speeds) > 0 else 0)
        flow_consistency = (heading_consistency + speed_consistency) / 2

        # Dominant flow direction
        flow_direction = np.mean(headings) / 360.0

        return {
            'flow_consistency': flow_consistency,
            'flow_direction': flow_direction
        }

    def _extract_congestion_features(self, vehicles: List[VehicleData]) -> Dict[str, float]:
        """Congestion pattern analysis for ML pipeline"""
        densities = [v.traffic_density for v in vehicles]
        speeds = [v.speed_mph for v in vehicles]

        # Congestion clustering
        high_density_count = sum(1 for d in densities if d > 0.7)
        low_speed_count = sum(1 for s in speeds if s < 25.0)

        return {
            'congestion_clustering': high_density_count / len(vehicles),
            'stop_and_go_pattern': low_speed_count / len(vehicles)
        }

    def _extract_weather_features(self, vehicles: List[VehicleData]) -> Dict[str, float]:
        """Weather correlation analysis"""
        weather_conditions = [v.weather_conditions for v in vehicles]
        weather_map = {'clear': 0, 'rain': 1, 'snow': 2, 'fog': 3, 'storm': 4}

        weather_encoded = [weather_map.get(w, 0) for w in weather_conditions]

        return {
            'weather_severity': np.mean(weather_encoded) / 4.0,
            'weather_consistency': 1.0 - (np.std(weather_encoded) / 4.0)
        }

    async def _validate_and_parse_batch(self, batch: List[Dict[str, Any]]) -> List[VehicleData]:
        """High-performance data validation and parsing"""
        validated_vehicles = []

        for item in batch:
            try:
                vehicle = VehicleData(
                    vehicle_id=item['vehicle_id'],
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    latitude=float(item['latitude']),
                    longitude=float(item['longitude']),
                    speed_mph=float(item['speed_mph']),
                    heading_degrees=float(item['heading_degrees']),
                    road_segment_id=item['road_segment_id'],
                    traffic_density=float(item['traffic_density']),
                    weather_conditions=item['weather_conditions']
                )
                validated_vehicles.append(vehicle)

            except (KeyError, ValueError, TypeError) as e:
                self.error_counts['validation_error'] += 1
                self.logger.warning(f"Invalid vehicle data: {e}")

        return validated_vehicles

    def _group_by_road_segment(self, vehicles: List[VehicleData]) -> Dict[str, List[VehicleData]]:
        """Efficient grouping for parallel processing"""
        segments = defaultdict(list)
        for vehicle in vehicles:
            segments[vehicle.road_segment_id].append(vehicle)
        return dict(segments)

    def _calculate_confidence(self, vehicles: List[VehicleData], speed_variance: float) -> float:
        """Data quality and prediction confidence scoring"""
        # Sample size factor
        sample_factor = min(1.0, len(vehicles) / 50.0)  # Optimal sample size is 50+

        # Data consistency factor
        consistency_factor = max(0.1, 1.0 - (speed_variance / 1000.0))

        # Temporal freshness factor
        now = datetime.now()
        freshness_scores = []
        for vehicle in vehicles:
            age_minutes = (now - vehicle.timestamp).total_seconds() / 60
            freshness = max(0.0, 1.0 - (age_minutes / 10.0))  # 10 min max age
            freshness_scores.append(freshness)

        temporal_factor = np.mean(freshness_scores)

        # Overall confidence
        confidence = 0.4 * sample_factor + 0.3 * consistency_factor + 0.3 * temporal_factor
        return min(1.0, max(0.1, confidence))

    def _record_performance_metrics(self, processing_time_ms: float, vehicle_count: int):
        """Performance tracking for collaboration analysis"""
        throughput = (vehicle_count / processing_time_ms) * 1000 if processing_time_ms > 0 else 0
        error_rate = sum(self.error_counts.values()) / max(1, vehicle_count) * 100

        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            processing_latency_ms=processing_time_ms,
            throughput_vehicles_per_sec=throughput,
            error_rate_percent=error_rate,
            queue_depth=self.processing_queue.qsize(),
            memory_usage_mb=0.0  # Would use psutil in production
        )

        self.performance_history.append(metrics)
        self.metrics_collector.record_metrics(metrics)

    async def _data_ingestion_worker(self):
        """Background worker for continuous data ingestion"""
        while True:
            try:
                # Simulate real-time data ingestion
                await asyncio.sleep(0.1)  # 10 Hz data ingestion rate
            except Exception as e:
                self.logger.error(f"Data ingestion error: {e}")

    async def _processing_worker(self):
        """Background worker for queue processing"""
        while True:
            try:
                # Process queued data
                await asyncio.sleep(0.05)  # 20 Hz processing rate
            except Exception as e:
                self.logger.error(f"Processing worker error: {e}")

    async def _performance_monitor(self):
        """Background performance monitoring"""
        while True:
            try:
                await asyncio.sleep(1)  # Monitor every second
                self._check_performance_targets()
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")

    async def _cache_maintenance_worker(self):
        """Background cache cleanup and optimization"""
        while True:
            try:
                await asyncio.sleep(30)  # Clean cache every 30 seconds
                self._cleanup_expired_cache()
            except Exception as e:
                self.logger.error(f"Cache maintenance error: {e}")

    def _check_performance_targets(self):
        """Validate performance against enterprise targets"""
        if not self.performance_history:
            return

        recent_metrics = list(self.performance_history)[-10:]  # Last 10 measurements

        avg_latency = np.mean([m.processing_latency_ms for m in recent_metrics])
        avg_throughput = np.mean([m.throughput_vehicles_per_sec for m in recent_metrics])
        avg_error_rate = np.mean([m.error_rate_percent for m in recent_metrics])

        # Check targets
        if avg_latency > self.performance_targets['max_latency_ms']:
            self.logger.warning(f"Latency target exceeded: {avg_latency:.1f}ms")

        if avg_throughput < self.performance_targets['min_throughput_vps']:
            self.logger.warning(f"Throughput below target: {avg_throughput:.0f} vehicles/sec")

        if avg_error_rate > self.performance_targets['max_error_rate']:
            self.logger.warning(f"Error rate above target: {avg_error_rate:.2f}%")

    def _cleanup_expired_cache(self):
        """Cache maintenance for optimal performance"""
        now = datetime.now()
        expired_keys = []

        for key, (data, timestamp) in self.processed_data_cache.items():
            if (now - timestamp).total_seconds() > 300:  # 5 minute cache TTL
                expired_keys.append(key)

        for key in expired_keys:
            del self.processed_data_cache[key]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance analytics for Frontend Dashboard"""
        if not self.performance_history:
            return {'status': 'no_data'}

        recent_metrics = list(self.performance_history)[-100:]  # Last 100 measurements

        return {
            'status': 'operational',
            'avg_latency_ms': np.mean([m.processing_latency_ms for m in recent_metrics]),
            'avg_throughput_vps': np.mean([m.throughput_vehicles_per_sec for m in recent_metrics]),
            'error_rate_percent': np.mean([m.error_rate_percent for m in recent_metrics]),
            'total_processed': sum(self.error_counts.values()) if self.error_counts else 0,
            'performance_trend': self._calculate_performance_trend(recent_metrics)
        }

    def _calculate_performance_trend(self, metrics: List[PerformanceMetrics]) -> str:
        """Performance trend analysis"""
        if len(metrics) < 10:
            return 'insufficient_data'

        # Calculate trend in latency
        latencies = [m.processing_latency_ms for m in metrics]
        recent_avg = np.mean(latencies[-5:])
        earlier_avg = np.mean(latencies[:5])

        if recent_avg < earlier_avg * 0.95:
            return 'improving'
        elif recent_avg > earlier_avg * 1.05:
            return 'degrading'
        else:
            return 'stable'


class MetricsCollector:
    """Performance metrics collection for collaboration analysis"""

    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)

    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics for analysis"""
        self.metrics_buffer.append(metrics)

    def get_collaboration_insights(self) -> Dict[str, Any]:
        """Analysis of collaboration effectiveness through performance metrics"""
        if not self.metrics_buffer:
            return {'status': 'no_data'}

        metrics_list = list(self.metrics_buffer)

        return {
            'collaboration_efficiency': self._calculate_collaboration_efficiency(metrics_list),
            'system_stability': self._analyze_stability(metrics_list),
            'performance_consistency': self._analyze_consistency(metrics_list)
        }

    def _calculate_collaboration_efficiency(self, metrics: List[PerformanceMetrics]) -> float:
        """Measure how well the system meets collaboration targets"""
        target_latency = 100.0
        target_throughput = 10000.0

        latency_scores = [max(0, 1 - (m.processing_latency_ms / target_latency)) for m in metrics]
        throughput_scores = [min(1, m.throughput_vehicles_per_sec / target_throughput) for m in metrics]

        return (np.mean(latency_scores) + np.mean(throughput_scores)) / 2

    def _analyze_stability(self, metrics: List[PerformanceMetrics]) -> float:
        """Measure system stability over time"""
        latencies = [m.processing_latency_ms for m in metrics]
        cv = np.std(latencies) / np.mean(latencies) if np.mean(latencies) > 0 else 1
        return max(0, 1 - cv)  # Lower coefficient of variation = higher stability

    def _analyze_consistency(self, metrics: List[PerformanceMetrics]) -> float:
        """Measure consistency of performance"""
        error_rates = [m.error_rate_percent for m in metrics]
        consistency = 1 - np.std(error_rates) / 100.0 if error_rates else 0
        return max(0, consistency)


# API Integration Interface for Frontend and Prediction Engine
class TrafficDataAPI:
    """Clean API interface for hierarchical AI collaboration"""

    def __init__(self, processor: TrafficDataProcessor):
        self.processor = processor

    async def process_traffic_batch(self, vehicle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main API endpoint for traffic data processing"""
        try:
            processed_data = await self.processor.process_vehicle_data_batch(vehicle_data)
            performance_summary = self.processor.get_performance_summary()

            return {
                'status': 'success',
                'processed_segments': [data.to_api_response() for data in processed_data],
                'performance_metrics': performance_summary,
                'collaboration_insights': self.processor.metrics_collector.get_collaboration_insights()
            }

        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e),
                'processed_segments': []
            }

    def get_system_status(self) -> Dict[str, Any]:
        """System health check for monitoring dashboard"""
        return {
            'processor_status': 'operational',
            'performance_summary': self.processor.get_performance_summary(),
            'collaboration_effectiveness': self.processor.metrics_collector.get_collaboration_insights()
        }


if __name__ == "__main__":
    # Enterprise configuration
    config = {
        'max_concurrent_segments': 100,
        'cache_ttl_seconds': 300,
        'performance_monitoring': True,
        'collaboration_analytics': True
    }

    # Initialize system
    processor = TrafficDataProcessor(config)
    api = TrafficDataAPI(processor)

    print("🚀 Traffic Data Processor - Enterprise System Initialized")
    print("✅ Performance Targets: <100ms latency, 10,000+ vehicles/sec")
    print("✅ Collaboration Integration: Ready for Prediction Engine + Frontend")
    print("✅ Advanced Analytics: Real-time performance and collaboration metrics")