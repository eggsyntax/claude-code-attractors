#!/usr/bin/env python3
"""
Real-world code analysis using our conversational framework.
Let's test this on some common patterns from actual codebases.
"""

# Sample: Typical Flask API endpoint (based on common patterns I've seen)
from flask import Flask, request, jsonify
import sqlite3
import jwt
import hashlib
import time

app = Flask(__name__)

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    # Get token from header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401

    try:
        # Decode JWT
        payload = jwt.decode(token.replace('Bearer ', ''), 'secret_key', algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

    # Database query
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT username, email, created_at FROM users WHERE id = {user_id}")
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    # Log access
    with open('access.log', 'a') as f:
        f.write(f"{time.time()},{user_id},{request.remote_addr}\n")

    return jsonify({
        'username': user_data[0],
        'email': user_data[1],
        'created_at': user_data[2]
    })

@app.route('/api/user/update', methods=['POST'])
def update_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401

    try:
        payload = jwt.decode(token.replace('Bearer ', ''), 'secret_key', algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

    # Get update data
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    # Update database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    if username:
        cursor.execute(f"UPDATE users SET username = '{username}' WHERE id = {user_id}")
    if email:
        cursor.execute(f"UPDATE users SET email = '{email}' WHERE id = {user_id}")

    conn.commit()
    conn.close()

    return jsonify({'message': 'User updated successfully'})

# Sample: Background task processor
import threading
import queue
import json

class TaskProcessor:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_tasks)
        self.worker_thread.start()
        self.results = {}

    def submit_task(self, task_id, task_data):
        self.task_queue.put((task_id, task_data))
        return task_id

    def _process_tasks(self):
        while True:
            task_id, task_data = self.task_queue.get()

            # Process task (simulate heavy computation)
            if task_data.get('type') == 'image_processing':
                # Simulate processing
                time.sleep(2)
                result = {'status': 'processed', 'data': f'processed_{task_data.get("filename")}'}
            elif task_data.get('type') == 'data_analysis':
                # Load data from file
                filename = task_data.get('filename')
                with open(f'/tmp/{filename}', 'r') as f:
                    data = json.load(f)

                # Simulate analysis
                result = {'status': 'analyzed', 'count': len(data.get('items', []))}
            else:
                result = {'status': 'error', 'message': 'Unknown task type'}

            self.results[task_id] = result
            self.task_queue.task_done()

    def get_result(self, task_id):
        return self.results.get(task_id)

if __name__ == "__main__":
    # Demo usage
    processor = TaskProcessor()

    # Submit some tasks
    task1 = processor.submit_task('img_001', {'type': 'image_processing', 'filename': 'photo.jpg'})
    task2 = processor.submit_task('data_001', {'type': 'data_analysis', 'filename': 'dataset.json'})

    # Check results
    time.sleep(3)
    print("Results:", processor.get_result('img_001'))

    app.run(debug=True)