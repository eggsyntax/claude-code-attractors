"""
Alice's Data Processing Pipeline Implementation
Functional Programming Approach with Immutable Data Transformations
"""

from typing import List, Dict, Callable, Tuple, Optional
from dataclasses import dataclass
from functools import reduce
import json
from datetime import datetime


@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    timestamp: str
    value: float
    metadata: Dict[str, str]


@dataclass(frozen=True)
class ProcessedData:
    sensor_id: str
    average_value: float
    reading_count: int
    anomalies: List[SensorReading]
    processing_timestamp: str


@dataclass(frozen=True)
class Alert:
    sensor_id: str
    anomaly_value: float
    severity: str
    message: str
    timestamp: str


# Pure transformation functions
def parse_raw_data(raw_line: str) -> Optional[SensorReading]:
    """Parse a single line of sensor data"""
    try:
        data = json.loads(raw_line)
        return SensorReading(
            sensor_id=data["sensor_id"],
            timestamp=data["timestamp"],
            value=float(data["value"]),
            metadata=data.get("metadata", {})
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def filter_valid_readings(readings: List[Optional[SensorReading]]) -> List[SensorReading]:
    """Remove invalid readings and apply basic filters"""
    return [
        reading for reading in readings
        if reading is not None and 0 <= reading.value <= 1000
    ]


def group_by_sensor(readings: List[SensorReading]) -> Dict[str, List[SensorReading]]:
    """Group readings by sensor ID"""
    groups = {}
    for reading in readings:
        if reading.sensor_id not in groups:
            groups[reading.sensor_id] = []
        groups[reading.sensor_id].append(reading)
    return groups


def calculate_statistics(readings: List[SensorReading]) -> Tuple[float, int]:
    """Calculate average and count for a group of readings"""
    if not readings:
        return 0.0, 0

    total = sum(reading.value for reading in readings)
    return total / len(readings), len(readings)


def detect_anomalies(readings: List[SensorReading], average: float, threshold: float = 2.0) -> List[SensorReading]:
    """Detect readings that deviate significantly from average"""
    return [
        reading for reading in readings
        if abs(reading.value - average) > threshold * average
    ]


def process_sensor_group(sensor_id: str, readings: List[SensorReading]) -> ProcessedData:
    """Process a single sensor's readings"""
    average, count = calculate_statistics(readings)
    anomalies = detect_anomalies(readings, average)

    return ProcessedData(
        sensor_id=sensor_id,
        average_value=average,
        reading_count=count,
        anomalies=anomalies,
        processing_timestamp=datetime.now().isoformat()
    )


def generate_alerts(processed_data: ProcessedData) -> List[Alert]:
    """Generate alerts based on processed data"""
    alerts = []

    for anomaly in processed_data.anomalies:
        severity = "HIGH" if abs(anomaly.value - processed_data.average_value) > 5 * processed_data.average_value else "MEDIUM"

        alert = Alert(
            sensor_id=processed_data.sensor_id,
            anomaly_value=anomaly.value,
            severity=severity,
            message=f"Sensor {processed_data.sensor_id} anomaly: {anomaly.value:.2f} (avg: {processed_data.average_value:.2f})",
            timestamp=datetime.now().isoformat()
        )
        alerts.append(alert)

    return alerts


# Pipeline composition function
def create_pipeline() -> Callable[[List[str]], Tuple[List[ProcessedData], List[Alert]]]:
    """Create a composable data processing pipeline"""

    def pipeline(raw_data_lines: List[str]) -> Tuple[List[ProcessedData], List[Alert]]:
        # Transform raw data through pure function composition
        parsed_readings = [parse_raw_data(line) for line in raw_data_lines]
        valid_readings = filter_valid_readings(parsed_readings)
        grouped_readings = group_by_sensor(valid_readings)

        # Process each sensor group
        processed_results = [
            process_sensor_group(sensor_id, readings)
            for sensor_id, readings in grouped_readings.items()
        ]

        # Generate all alerts
        all_alerts = []
        for processed in processed_results:
            all_alerts.extend(generate_alerts(processed))

        return processed_results, all_alerts

    return pipeline


# Usage example
def run_pipeline_example():
    """Demonstrate the functional pipeline"""
    sample_data = [
        '{"sensor_id": "temp_01", "timestamp": "2026-01-30T10:00:00", "value": 23.5, "metadata": {"location": "room_a"}}',
        '{"sensor_id": "temp_01", "timestamp": "2026-01-30T10:01:00", "value": 24.1, "metadata": {"location": "room_a"}}',
        '{"sensor_id": "temp_01", "timestamp": "2026-01-30T10:02:00", "value": 35.7, "metadata": {"location": "room_a"}}',  # Anomaly
        '{"sensor_id": "humid_02", "timestamp": "2026-01-30T10:00:00", "value": 45.2, "metadata": {"location": "room_b"}}',
        'invalid_json_line',  # Will be filtered out
        '{"sensor_id": "humid_02", "timestamp": "2026-01-30T10:01:00", "value": 46.8, "metadata": {"location": "room_b"}}'
    ]

    # Create and run pipeline
    pipeline = create_pipeline()
    processed_data, alerts = pipeline(sample_data)

    print("=== Functional Pipeline Results ===")
    print(f"Processed {len(processed_data)} sensor groups:")
    for data in processed_data:
        print(f"  {data.sensor_id}: avg={data.average_value:.2f}, count={data.reading_count}, anomalies={len(data.anomalies)}")

    print(f"\nGenerated {len(alerts)} alerts:")
    for alert in alerts:
        print(f"  {alert.severity}: {alert.message}")


if __name__ == "__main__":
    run_pipeline_example()