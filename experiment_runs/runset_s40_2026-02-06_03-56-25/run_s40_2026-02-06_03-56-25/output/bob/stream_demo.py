#!/usr/bin/env python3
"""
Demo script showing the streaming capabilities of StreamLogix
This demonstrates how the tool handles large files with minimal memory usage
"""

from log_analyzer import StreamLogAnalyzer, AnalysisPipeline
import time
import random
from datetime import datetime, timedelta


def generate_large_log_file(filename: str, num_entries: int = 10000):
    """Generate a large log file for testing streaming performance"""

    sources = ['webapp.auth', 'webapp.database', 'webapp.api', 'webapp.payment',
               'webapp.cache', 'webapp.scheduler', 'webapp.monitoring', 'webapp.security']
    levels = ['DEBUG', 'INFO', 'INFO', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']  # Weighted toward INFO

    messages = {
        'webapp.auth': [
            'User login successful for user{id}',
            'Token validation passed for user{id}',
            'User logout for user{id}',
            'Invalid credentials for user{id}',
            'Session expired for user{id}'
        ],
        'webapp.database': [
            'Database connection established',
            'Query executed successfully in {time}ms',
            'Connection timeout to primary database',
            'Failover to secondary database successful',
            'Database health check passed'
        ],
        'webapp.api': [
            'GET /api/users/{id} returned 200',
            'POST /api/orders created new order',
            'Rate limit exceeded for client {id}',
            'API endpoint /api/{resource} processing request',
            'Invalid API key provided'
        ],
        'webapp.payment': [
            'Payment processing completed for order {id}',
            'Payment processing failed for order {id}',
            'Refund issued for transaction {id}',
            'Credit card validation failed',
            'Payment gateway timeout'
        ]
    }

    base_time = datetime(2024, 1, 15, 10, 0, 0)

    print(f"Generating {num_entries} log entries...")

    with open(filename, 'w') as f:
        for i in range(num_entries):
            # Generate timestamp with some realistic progression
            timestamp = base_time + timedelta(seconds=i // 10)  # ~10 entries per second

            # Choose source and level
            source = random.choice(sources)
            level = random.choice(levels)

            # Generate message based on source
            if source in messages:
                message_template = random.choice(messages[source])
                message = message_template.format(
                    id=random.randint(100, 999),
                    time=random.randint(50, 2000),
                    resource=random.choice(['users', 'orders', 'products', 'inventory'])
                )
            else:
                message = f"Generic message for {source}"

            # Introduce some realistic error patterns
            if random.random() < 0.02:  # 2% chance of error bursts
                level = 'ERROR'
                if source == 'webapp.database':
                    message = 'Connection timeout to primary database'
                elif source == 'webapp.payment':
                    message = 'Payment processing failed for order {}'.format(random.randint(100, 999))

            log_line = f"{timestamp.isoformat()} {level} {source} {message}"
            f.write(log_line + '\n')

    print(f"Generated {filename} with {num_entries} entries")


def benchmark_streaming_vs_loading():
    """Compare streaming vs loading entire file into memory"""

    filename = "large_sample.log"
    generate_large_log_file(filename, 50000)

    analyzer = StreamLogAnalyzer()

    print("Benchmarking analysis approaches...")

    # Time the analysis
    start_time = time.time()
    result = analyzer.analyze_file(filename)
    end_time = time.time()

    print(f"\nAnalysis completed in {end_time - start_time:.2f} seconds")
    print(f"Memory-efficient streaming approach processed {result.total_entries} entries")
    print("\nSummary results:")
    print(f"- Time range: {result.time_range[0]} to {result.time_range[1]}")
    print(f"- Error rate: {result.level_distribution.get('ERROR', 0) / result.total_entries:.2%}")
    print(f"- Top 3 sources: {result.top_sources[:3]}")

    # Clean up
    import os
    os.remove(filename)


if __name__ == "__main__":
    print("StreamLogix Streaming Demonstration")
    print("===================================")
    benchmark_streaming_vs_loading()