#!/usr/bin/env python3
"""
Paradigm Experiment: Testing Cognitive Alignment Theory

Problem: Build a data processing pipeline that:
1. Reads temperature data from multiple sensors
2. Applies noise filtering
3. Calculates moving averages
4. Detects anomalies
5. Generates alerts for extreme values

We'll implement this using OOP, Functional, and Event-Driven approaches
to test which paradigm feels most "cognitively aligned" with data processing.
"""

import json
import statistics
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

# Sample temperature data generator
def generate_sample_data():
    """Generate sample temperature readings from multiple sensors"""
    sensors = ['sensor_001', 'sensor_002', 'sensor_003']
    base_time = datetime.now() - timedelta(hours=24)

    data = []
    for i in range(100):
        timestamp = base_time + timedelta(minutes=i * 10)
        for sensor in sensors:
            # Normal temp around 20°C with some noise and occasional spikes
            base_temp = 20.0 + random.normalvariate(0, 2)
            if random.random() < 0.05:  # 5% chance of anomaly
                base_temp += random.choice([-15, 15])  # Extreme reading

            reading = {
                'sensor_id': sensor,
                'timestamp': timestamp.isoformat(),
                'temperature': round(base_temp, 2),
                'raw_voltage': base_temp * 0.1 + random.normalvariate(0, 0.01)
            }
            data.append(reading)

    return data

if __name__ == "__main__":
    # Generate test data
    sample_data = generate_sample_data()

    with open('/tmp/cc-exp/run_s40_2026-01-30_23-19-22/output/temperature_data.json', 'w') as f:
        json.dump(sample_data, f, indent=2)

    print(f"Generated {len(sample_data)} temperature readings")
    print("Ready for paradigm comparison implementations!")