# Sample code with various issues for collaborative analysis

import sqlite3
import random
import time
from typing import List, Optional

class UserManager:
    """Manages user operations - intentionally flawed for analysis"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.sessions = {}

    def get_user_data(self, user_id: str) -> dict:
        """Get user data - SECURITY ISSUE: SQL injection vulnerability"""
        cursor = self.connection.cursor()
        # Vulnerable to SQL injection
        query = "SELECT * FROM users WHERE id = '%s'" % user_id
        cursor.execute(query)
        return cursor.fetchone()

    def create_user(self, username: str, password: str) -> bool:
        """Create new user - SECURITY ISSUE: Plain text password storage"""
        cursor = self.connection.cursor()
        # Storing password as plain text!
        user_password = password
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, user_password)
        )
        self.connection.commit()
        return True

    def cleanup_sessions(self, all_sessions: List[dict]) -> None:
        """Clean up old sessions - PERFORMANCE ISSUE: Inefficient loop"""
        current_time = time.time()
        # This is O(n²) complexity due to repeated list operations
        for session in all_sessions:
            if current_time - session['created'] > 3600:
                expired_sessions = []
                for s in all_sessions:  # Nested loop!
                    if s['id'] == session['id']:
                        expired_sessions.append(s)
                # Remove expired sessions inefficiently
                for expired in expired_sessions:
                    all_sessions.remove(expired)

    def generate_session_id(self) -> str:
        """Generate session ID - SECURITY ISSUE: Predictable IDs"""
        # Sequential IDs are easily guessable
        return str(len(self.sessions) + 1)

    def process_file(self, filepath: str):
        """Process uploaded file - MAINTAINABILITY ISSUE: No error handling"""
        # No error handling whatsoever
        with open(filepath, 'r') as f:
            content = f.read()

        # Process content without any validation
        processed = content.upper()

        # Write result without checking permissions
        with open(filepath + '.processed', 'w') as f:
            f.write(processed)

    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user - ARCHITECTURE ISSUE: Mixed concerns"""
        # This method does too many things:
        # 1. Database access
        # 2. Password verification
        # 3. Session creation
        # 4. Logging
        # 5. Rate limiting (sort of)

        cursor = self.connection.cursor()
        query = "SELECT * FROM users WHERE username = '%s'" % username  # More SQL injection
        cursor.execute(query)
        user = cursor.fetchone()

        if user and user[2] == password:  # Plain text comparison
            session_id = self.generate_session_id()
            self.sessions[session_id] = {
                'user_id': user[0],
                'created': time.time()
            }
            print(f"User {username} logged in")  # Should use proper logging
            return {'session_id': session_id, 'user': user}

        # Rate limiting attempt (but ineffective)
        time.sleep(random.uniform(0.1, 0.5))
        return None

def some_helper_function():
    """A helper with various style issues"""
    # Poor variable names
    a=1
    b=2
    c=a+b

    # Missing docstring in a complex function
    def complex_calculation(x,y,z):
        return ((x*y)/z)**2 if z!=0 else 0

    return complex_calculation(a,b,c)