#!/usr/bin/env python3
"""
Streaming Data Processing Pipeline - Temporal/Event-Driven Approach
"""
import asyncio
import time
from typing import AsyncIterator, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SensorReading:
    timestamp: datetime
    sensor_id: str
    value: float

@dataclass
class ProcessedData:
    timestamp: datetime
    sensor_id: str
    raw_value: float
    smoothed_value: float
    is_anomaly: bool
    context_window: List[float]

class StreamingProcessor:
    def __init__(self, window_size: int = 5, threshold: float = 2.0):
        self.window_size = window_size
        self.threshold = threshold
        self.windows = {}  # sensor_id -> rolling window

    async def process_stream(self, data_stream: AsyncIterator[SensorReading]) -> AsyncIterator[ProcessedData]:
        """Process sensor readings in real-time as they arrive"""
        async for reading in data_stream:
            # Maintain rolling window per sensor
            if reading.sensor_id not in self.windows:
                self.windows[reading.sensor_id] = []

            window = self.windows[reading.sensor_id]
            window.append(reading.value)

            # Keep only recent values
            if len(window) > self.window_size:
                window.pop(0)

            # Calculate smoothed value and detect anomalies
            if len(window) >= 3:  # Need minimum data for processing
                smoothed = sum(window) / len(window)
                recent_avg = sum(window[-3:]) / 3
                is_anomaly = abs(reading.value - smoothed) > self.threshold * smoothed

                yield ProcessedData(
                    timestamp=reading.timestamp,
                    sensor_id=reading.sensor_id,
                    raw_value=reading.value,
                    smoothed_value=smoothed,
                    is_anomaly=is_anomaly,
                    context_window=window.copy()
                )

async def sensor_simulator() -> AsyncIterator[SensorReading]:
    """Simulate real-time sensor data arriving"""
    import random

    sensors = ['temp_01', 'pressure_02', 'flow_03']

    while True:
        # Simulate varying arrival times
        await asyncio.sleep(random.uniform(0.1, 0.5))

        sensor_id = random.choice(sensors)
        base_value = {'temp_01': 20.0, 'pressure_02': 100.0, 'flow_03': 50.0}[sensor_id]

        # Add some noise and occasional anomalies
        if random.random() < 0.1:  # 10% chance of anomaly
            value = base_value * random.uniform(1.5, 3.0)
        else:
            value = base_value + random.uniform(-5, 5)

        yield SensorReading(
            timestamp=datetime.now(),
            sensor_id=sensor_id,
            value=value
        )

async def main():
    """Run the streaming pipeline"""
    processor = StreamingProcessor(window_size=5, threshold=1.5)

    print("🌊 Starting streaming data processor...")
    print("Press Ctrl+C to stop\n")

    try:
        data_stream = sensor_simulator()
        async for result in processor.process_stream(data_stream):
            status = "🚨 ANOMALY" if result.is_anomaly else "✓ Normal"
            print(f"{result.timestamp.strftime('%H:%M:%S')} | "
                  f"{result.sensor_id:12} | "
                  f"Raw: {result.raw_value:6.1f} | "
                  f"Avg: {result.smoothed_value:6.1f} | "
                  f"{status}")

            if result.is_anomaly:
                print(f"  └─ Context: {[f'{v:.1f}' for v in result.context_window]}")

    except KeyboardInterrupt:
        print("\n🛑 Stream processing stopped")

if __name__ == "__main__":
    asyncio.run(main())