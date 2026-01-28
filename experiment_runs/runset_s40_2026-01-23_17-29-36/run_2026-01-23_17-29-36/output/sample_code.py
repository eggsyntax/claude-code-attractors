"""
Sample code for testing our collaborative analyzer.
This file intentionally contains various issues for demonstration.
"""

import sqlite3
import time


class DataProcessor:
    """A class that processes data in various problematic ways."""

    def __init__(self):
        self.data = []
        self.results = []
        self.cache = {}
        self.db_connection = None
        self.user_sessions = {}
        self.config = {}

    def process_user_data(self, user_input, query_type):
        """Process user data with security vulnerabilities."""
        # SQL injection vulnerability - directly interpolating user input
        sql = f"SELECT * FROM users WHERE name = '{user_input}'"

        cursor = self.db_connection.cursor()
        cursor.execute(sql)  # Vulnerable!
        return cursor.fetchall()

    def inefficient_search(self, target_list, search_items):
        """Demonstrate O(n²) complexity."""
        results = []
        for search_item in search_items:  # O(n)
            for item in target_list:      # O(n) nested -> O(n²)
                if item == search_item:
                    results.append(item)
        return results

    def string_building_antipattern(self, items):
        """Inefficient string concatenation in loop."""
        result = ""
        for item in items:  # String concatenation in loop is O(n²)
            result += str(item) + ", "
        return result

    def god_method(self, data, user_id, session_id, config_updates):
        """
        This method does too many things (violates SRP).
        Also has performance and security issues.
        """
        # Validate user (should be separate method)
        if not user_id:
            raise ValueError("User ID required")

        # Update configuration (should be separate)
        for key, value in config_updates.items():
            self.config[key] = value

        # Process data inefficiently
        processed = []
        for i in range(len(data)):  # Should use enumerate
            for j in range(len(data)):  # Nested loops without clear purpose
                if i != j:
                    processed.append(data[i] + data[j])

        # Database operations (should be separate)
        query = f"UPDATE sessions SET data = '{str(processed)}' WHERE id = {session_id}"
        cursor = self.db_connection.cursor()
        cursor.execute(query)  # Another SQL injection risk

        # Session management (should be separate)
        self.user_sessions[user_id] = {
            'last_activity': time.time(),
            'session_id': session_id,
            'data': processed
        }

        # Return processing results
        return processed

    def unused_complex_method(self):
        """This method has high complexity but might be dead code."""
        for i in range(100):
            for j in range(100):
                for k in range(100):
                    if i == j == k:
                        return i
        return None


def standalone_function_with_issues(user_input):
    """Function that doesn't validate input properly."""
    # No input validation
    return eval(user_input)  # Dangerous! Code injection vulnerability


# Missing main guard
if True:  # This should be `if __name__ == "__main__":`
    processor = DataProcessor()
    # This code runs on import, which is bad practice
    print("Processor initialized")