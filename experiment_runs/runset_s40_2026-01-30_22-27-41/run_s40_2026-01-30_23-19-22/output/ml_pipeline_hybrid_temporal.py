#!/usr/bin/env python3
"""
Hybrid Temporal ML Pipeline Experiment

Testing how different temporal characteristics naturally lead to different
paradigms, and how paradigm transitions feel at the boundaries.

Three Temporal Zones:
1. TIMELESS: Data preprocessing (functional)
2. TEMPORAL: Real-time streaming (event-driven)
3. ENTITY: Model management (object-oriented)
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import statistics
import random

# =============================================================================
# ZONE 1: TIMELESS DATA PREPROCESSING (Functional Paradigm)
# =============================================================================

def normalize_features(raw_data: List[float]) -> List[float]:
    """Pure function: normalize data to 0-1 range"""
    if not raw_data:
        return []
    min_val, max_val = min(raw_data), max(raw_data)
    if min_val == max_val:
        return [0.5] * len(raw_data)
    return [(x - min_val) / (max_val - min_val) for x in raw_data]

def extract_statistical_features(data: List[float]) -> Dict[str, float]:
    """Pure function: extract statistical features from raw data"""
    if not data:
        return {"mean": 0, "std": 0, "median": 0}
    return {
        "mean": statistics.mean(data),
        "std": statistics.stdev(data) if len(data) > 1 else 0,
        "median": statistics.median(data)
    }

def validate_data_quality(features: Dict[str, float]) -> Dict[str, Any]:
    """Pure function: validate data quality and add quality metrics"""
    quality_score = 1.0
    issues = []

    if any(abs(v) > 10 for v in features.values()):
        quality_score -= 0.3
        issues.append("extreme_values")

    if features["std"] < 0.01:
        quality_score -= 0.2
        issues.append("low_variance")

    return {
        **features,
        "quality_score": max(0, quality_score),
        "quality_issues": issues
    }

def preprocess_pipeline(raw_data: List[float]) -> Dict[str, Any]:
    """Compose pure transformations into preprocessing pipeline"""
    normalized = normalize_features(raw_data)
    features = extract_statistical_features(normalized)
    validated = validate_data_quality(features)
    return validated

# =============================================================================
# ZONE 2: TEMPORAL STREAMING (Event-Driven Paradigm)
# =============================================================================

class StreamEvent(Enum):
    DATA_RECEIVED = "data_received"
    FEATURES_PROCESSED = "features_processed"
    PREDICTION_MADE = "prediction_made"
    ANOMALY_DETECTED = "anomaly_detected"

@dataclass
class Event:
    type: StreamEvent
    timestamp: float
    data: Any
    source_id: str

class StreamProcessor:
    """Event-driven streaming processor"""

    def __init__(self):
        self.handlers: Dict[StreamEvent, List[Callable]] = {event: [] for event in StreamEvent}
        self.recent_predictions: List[float] = []

    def subscribe(self, event_type: StreamEvent, handler: Callable):
        """Subscribe to specific event types"""
        self.handlers[event_type].append(handler)

    async def publish_event(self, event: Event):
        """Publish event to all subscribed handlers"""
        for handler in self.handlers[event.type]:
            await handler(event)

    async def handle_data_received(self, event: Event):
        """Handle incoming raw data streams"""
        processed_features = preprocess_pipeline(event.data)

        # Emit features processed event
        await self.publish_event(Event(
            type=StreamEvent.FEATURES_PROCESSED,
            timestamp=time.time(),
            data=processed_features,
            source_id=event.source_id
        ))

    async def handle_features_processed(self, event: Event):
        """Handle processed features and make predictions"""
        # Simple mock prediction based on mean
        prediction = event.data["mean"] * 100  # Mock model
        self.recent_predictions.append(prediction)

        # Keep only last 10 predictions for anomaly detection
        self.recent_predictions = self.recent_predictions[-10:]

        await self.publish_event(Event(
            type=StreamEvent.PREDICTION_MADE,
            timestamp=time.time(),
            data={"prediction": prediction, "features": event.data},
            source_id=event.source_id
        ))

    async def handle_prediction_made(self, event: Event):
        """Detect anomalies in prediction stream"""
        if len(self.recent_predictions) < 5:
            return

        recent_mean = statistics.mean(self.recent_predictions[-5:])
        current_pred = event.data["prediction"]

        if abs(current_pred - recent_mean) > 50:  # Anomaly threshold
            await self.publish_event(Event(
                type=StreamEvent.ANOMALY_DETECTED,
                timestamp=time.time(),
                data={
                    "anomaly_score": abs(current_pred - recent_mean),
                    "prediction": current_pred,
                    "baseline": recent_mean
                },
                source_id=event.source_id
            ))

# =============================================================================
# ZONE 3: ENTITY-BASED MODEL MANAGEMENT (Object-Oriented Paradigm)
# =============================================================================

class ModelVersion:
    """Encapsulates a specific model version with its metadata"""

    def __init__(self, version_id: str, accuracy: float, deployment_time: float):
        self.version_id = version_id
        self.accuracy = accuracy
        self.deployment_time = deployment_time
        self.prediction_count = 0
        self.total_inference_time = 0

    def record_prediction(self, inference_time: float):
        """Update performance metrics"""
        self.prediction_count += 1
        self.total_inference_time += inference_time

    def get_avg_inference_time(self) -> float:
        """Calculate average inference time"""
        if self.prediction_count == 0:
            return 0
        return self.total_inference_time / self.prediction_count

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get complete performance summary"""
        return {
            "version_id": self.version_id,
            "accuracy": self.accuracy,
            "predictions_made": self.prediction_count,
            "avg_inference_time": self.get_avg_inference_time(),
            "deployment_time": self.deployment_time
        }

class ABTestManager:
    """Manages A/B testing between different model versions"""

    def __init__(self):
        self.active_models: Dict[str, ModelVersion] = {}
        self.traffic_split: Dict[str, float] = {}

    def deploy_model(self, model: ModelVersion, traffic_percentage: float):
        """Deploy a new model version with specified traffic split"""
        self.active_models[model.version_id] = model
        self.traffic_split[model.version_id] = traffic_percentage
        self._normalize_traffic_split()

    def _normalize_traffic_split(self):
        """Ensure traffic splits sum to 1.0"""
        total = sum(self.traffic_split.values())
        if total > 0:
            for version_id in self.traffic_split:
                self.traffic_split[version_id] /= total

    def select_model_for_request(self, request_id: str) -> Optional[ModelVersion]:
        """Select model based on traffic split and request hash"""
        if not self.active_models:
            return None

        # Use request_id hash for consistent routing
        hash_val = hash(request_id) % 100 / 100
        cumulative_prob = 0

        for version_id, probability in self.traffic_split.items():
            cumulative_prob += probability
            if hash_val <= cumulative_prob:
                return self.active_models[version_id]

        # Fallback to first model
        return list(self.active_models.values())[0]

    def get_comparative_performance(self) -> Dict[str, Any]:
        """Compare performance across all active models"""
        return {
            version_id: model.get_performance_summary()
            for version_id, model in self.active_models.items()
        }

# =============================================================================
# BOUNDARY INTEGRATION: Where Paradigms Meet
# =============================================================================

class HybridMLPipeline:
    """Integration layer that bridges all three paradigm zones"""

    def __init__(self):
        # Temporal zone (event-driven)
        self.stream_processor = StreamProcessor()
        self._setup_stream_handlers()

        # Entity zone (object-oriented)
        self.ab_test_manager = ABTestManager()
        self._deploy_initial_models()

        # Metrics collection
        self.performance_metrics = []

    def _setup_stream_handlers(self):
        """Wire up event handlers - boundary between paradigms"""
        self.stream_processor.subscribe(StreamEvent.DATA_RECEIVED, self.stream_processor.handle_data_received)
        self.stream_processor.subscribe(StreamEvent.FEATURES_PROCESSED, self.stream_processor.handle_features_processed)
        self.stream_processor.subscribe(StreamEvent.PREDICTION_MADE, self.stream_processor.handle_prediction_made)
        self.stream_processor.subscribe(StreamEvent.ANOMALY_DETECTED, self._handle_anomaly)

    def _deploy_initial_models(self):
        """Set up A/B test with two model versions"""
        model_a = ModelVersion("v1.0", accuracy=0.85, deployment_time=time.time())
        model_b = ModelVersion("v1.1", accuracy=0.87, deployment_time=time.time())

        self.ab_test_manager.deploy_model(model_a, 0.8)
        self.ab_test_manager.deploy_model(model_b, 0.2)

    async def _handle_anomaly(self, event: Event):
        """Handle anomalies detected in stream - paradigm boundary point"""
        # This is where event-driven meets object-oriented
        print(f"🚨 ANOMALY DETECTED: {event.data['anomaly_score']:.2f}")

        # Could trigger model retraining, alerting, etc.
        # This is where temporal events influence entity behavior

    async def process_data_stream(self, raw_data: List[float], source_id: str):
        """Main entry point - orchestrates all paradigm zones"""
        # Create initial event to start the pipeline
        event = Event(
            type=StreamEvent.DATA_RECEIVED,
            timestamp=time.time(),
            data=raw_data,
            source_id=source_id
        )

        await self.stream_processor.publish_event(event)

    def get_system_health(self) -> Dict[str, Any]:
        """System-wide health check spanning all paradigms"""
        return {
            "model_performance": self.ab_test_manager.get_comparative_performance(),
            "recent_predictions": len(self.stream_processor.recent_predictions),
            "active_models": len(self.ab_test_manager.active_models)
        }

# =============================================================================
# DEMO AND TESTING
# =============================================================================

async def run_pipeline_demo():
    """Demonstrate the hybrid pipeline in action"""
    pipeline = HybridMLPipeline()

    print("🧪 Starting Hybrid Temporal ML Pipeline Demo")
    print("=" * 60)

    # Simulate data streams from multiple sources
    for i in range(5):
        # Generate mock sensor data
        raw_data = [random.gauss(50, 10) for _ in range(20)]
        source_id = f"sensor_{i}"

        print(f"\n📊 Processing data stream from {source_id}")
        await pipeline.process_data_stream(raw_data, source_id)

        # Small delay to see temporal behavior
        await asyncio.sleep(0.1)

    print("\n📈 Final System Health:")
    health = pipeline.get_system_health()
    print(json.dumps(health, indent=2))

if __name__ == "__main__":
    asyncio.run(run_pipeline_demo())