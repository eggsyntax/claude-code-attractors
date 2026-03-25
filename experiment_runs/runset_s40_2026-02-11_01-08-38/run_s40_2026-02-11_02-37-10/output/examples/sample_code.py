# Sample Python code for analysis
import os
import sys
from typing import List, Dict, Optional

class UserManager:
    def __init__(self):
        self.users = {}
        self.active_sessions = []

    def add_user(self, username, password):
        # TODO: Add password validation
        if username in self.users:
            return False
        self.users[username] = password
        return True

    def authenticate(self, username, password):
        if username not in self.users:
            return None
        if self.users[username] == password:
            session_id = len(self.active_sessions) + 1
            self.active_sessions.append({"user": username, "id": session_id})
            return session_id
        return None

    def get_user_data(self, username):
        # Direct database query - potential security issue
        query = f"SELECT * FROM users WHERE username = '{username}'"
        # This is just a placeholder - no actual database
        return {"username": username, "data": "some_data"}

    def cleanup_sessions(self):
        for i in range(len(self.active_sessions)):
            # Inefficient iteration
            if self.active_sessions[i]["id"] < 100:
                del self.active_sessions[i]
                break

def process_file(filename):
    # No error handling
    with open(filename, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    result = []

    for line in lines:
        if len(line) > 0:
            result.append(line.strip())

    return result

# Global variable
GLOBAL_CONFIG = {"debug": True, "max_users": 1000}