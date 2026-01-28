"""
Example code with various patterns for CodeMentor to detect.
This file demonstrates several design patterns and potential code smells.
"""

class DatabaseConnection:
    """Singleton pattern example - only one database connection should exist."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.connection = None
            self.host = "localhost"
            self.port = 5432
            self._initialized = True

    def connect(self):
        if not self.connection:
            # Simulate connection logic
            self.connection = f"Connected to {self.host}:{self.port}"
        return self.connection


class UserController:
    """Controller class that might get too large over time."""

    def __init__(self):
        self.db = DatabaseConnection()

    def create_user(self, username, email, password, first_name, last_name,
                   phone, address, city, state, zip_code, country,
                   date_of_birth, preferences, notifications, avatar):
        """This method is getting very long and has too many parameters."""

        # Validate username
        if not username:
            raise ValueError("Username is required")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(username) > 20:
            raise ValueError("Username must be less than 20 characters")

        # Validate email
        if not email:
            raise ValueError("Email is required")
        if "@" not in email:
            raise ValueError("Invalid email format")
        if not email.endswith((".com", ".org", ".net", ".edu")):
            raise ValueError("Email must end with common domain")

        # Validate password
        if not password:
            raise ValueError("Password is required")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain digit")

        # Validate names
        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")
        if len(first_name) > 50:
            raise ValueError("First name too long")
        if len(last_name) > 50:
            raise ValueError("Last name too long")

        # Validate phone
        if phone and len(phone) < 10:
            raise ValueError("Phone number must be at least 10 digits")

        # Validate address components
        if address and len(address) > 200:
            raise ValueError("Address too long")
        if city and len(city) > 100:
            raise ValueError("City name too long")
        if state and len(state) > 50:
            raise ValueError("State name too long")
        if zip_code and len(zip_code) > 20:
            raise ValueError("Zip code too long")
        if country and len(country) > 100:
            raise ValueError("Country name too long")

        # Create user object
        user = {
            'username': username,
            'email': email,
            'password': self._hash_password(password),
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'country': country,
            'date_of_birth': date_of_birth,
            'preferences': preferences or {},
            'notifications': notifications or True,
            'avatar': avatar,
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp(),
            'is_active': True,
            'email_verified': False,
            'login_attempts': 0
        }

        # Save to database
        self.db.connect()
        # Simulate database save
        print(f"Saving user: {username}")

        # Send welcome email
        self._send_welcome_email(user)

        # Log user creation
        self._log_user_creation(user)

        # Update statistics
        self._update_user_statistics()

        return user

    def _hash_password(self, password):
        """Hash the password - simplified for demo."""
        return f"hashed_{password}"

    def _get_current_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now()

    def _send_welcome_email(self, user):
        """Send welcome email to user."""
        print(f"Sending welcome email to {user['email']}")

    def _log_user_creation(self, user):
        """Log user creation event."""
        print(f"Logged user creation: {user['username']}")

    def _update_user_statistics(self):
        """Update system user statistics."""
        print("Updated user statistics")

    def get_user(self, user_id):
        """Get user by ID."""
        self.db.connect()
        return {"id": user_id, "username": f"user_{user_id}"}

    def update_user(self, user_id, data):
        """Update user data."""
        self.db.connect()
        print(f"Updated user {user_id}")

    def delete_user(self, user_id):
        """Delete user."""
        self.db.connect()
        print(f"Deleted user {user_id}")

    def list_users(self, page=1, per_page=10, filters=None):
        """List users with pagination."""
        self.db.connect()
        return [{"id": i, "username": f"user_{i}"} for i in range(1, 11)]

    def search_users(self, query):
        """Search users by query."""
        self.db.connect()
        return [{"id": 1, "username": "matching_user"}]

    def activate_user(self, user_id):
        """Activate user account."""
        self.db.connect()
        print(f"Activated user {user_id}")

    def deactivate_user(self, user_id):
        """Deactivate user account."""
        self.db.connect()
        print(f"Deactivated user {user_id}")

    def reset_password(self, user_id):
        """Reset user password."""
        self.db.connect()
        print(f"Reset password for user {user_id}")

    def change_password(self, user_id, old_password, new_password):
        """Change user password."""
        self.db.connect()
        print(f"Changed password for user {user_id}")

    def verify_email(self, user_id, token):
        """Verify user email."""
        self.db.connect()
        print(f"Verified email for user {user_id}")

    def send_verification_email(self, user_id):
        """Send email verification."""
        self.db.connect()
        print(f"Sent verification email to user {user_id}")

    def get_user_profile(self, user_id):
        """Get complete user profile."""
        self.db.connect()
        return {"id": user_id, "profile": "complete"}

    def update_user_preferences(self, user_id, preferences):
        """Update user preferences."""
        self.db.connect()
        print(f"Updated preferences for user {user_id}")

    def get_user_activity(self, user_id, days=30):
        """Get user activity history."""
        self.db.connect()
        return {"activities": []}

    def export_user_data(self, user_id):
        """Export user data for GDPR compliance."""
        self.db.connect()
        return {"user_data": "exported"}

    def anonymize_user(self, user_id):
        """Anonymize user data."""
        self.db.connect()
        print(f"Anonymized user {user_id}")


def create_user_factory(user_type):
    """Factory function to create different types of users."""
    user_types = {
        'admin': {'role': 'administrator', 'permissions': ['all']},
        'regular': {'role': 'user', 'permissions': ['read', 'write']},
        'guest': {'role': 'guest', 'permissions': ['read']}
    }

    return user_types.get(user_type, user_types['guest'])


class EventListener:
    """Observer pattern example - listens for user events."""

    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        """Subscribe to user events."""
        self.subscribers.append(callback)

    def notify(self, event, data):
        """Notify all subscribers of an event."""
        for callback in self.subscribers:
            callback(event, data)