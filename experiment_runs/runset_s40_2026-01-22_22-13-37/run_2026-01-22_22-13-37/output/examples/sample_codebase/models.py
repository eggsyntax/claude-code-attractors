"""
Sample models file to demonstrate pattern detection.
This file intentionally contains various patterns and anti-patterns.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

# Singleton pattern example
class DatabaseConnection:
    """Database connection singleton - classic singleton anti-pattern."""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.connection = None
            self.config = {}
            DatabaseConnection._initialized = True

    def connect(self):
        pass

    def execute_query(self, query: str):
        pass

# God Object - violating Single Responsibility Principle
class UserManager:
    """
    A god object that handles too many responsibilities.
    This violates SRP and demonstrates an anti-pattern.
    """

    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.permissions = {}
        self.audit_logs = []
        self.email_service = EmailService()
        self.notification_service = NotificationService()
        self.payment_processor = PaymentProcessor()
        self.analytics = AnalyticsTracker()

    # User management
    def create_user(self, user_data: Dict):
        # Complex user creation logic
        user_id = self._generate_user_id()
        self.users[user_id] = user_data
        self._log_user_creation(user_id)
        self._send_welcome_email(user_id)
        self._track_user_signup(user_id)
        return user_id

    def update_user(self, user_id: str, data: Dict):
        if user_id in self.users:
            self.users[user_id].update(data)
            self._log_user_update(user_id)
            self._notify_user_update(user_id)

    def delete_user(self, user_id: str):
        if user_id in self.users:
            del self.users[user_id]
            self._cleanup_user_sessions(user_id)
            self._cleanup_user_permissions(user_id)
            self._log_user_deletion(user_id)

    # Session management
    def create_session(self, user_id: str):
        session_id = self._generate_session_id()
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id

    def validate_session(self, session_id: str):
        return session_id in self.sessions

    def destroy_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    # Permission management
    def grant_permission(self, user_id: str, permission: str):
        if user_id not in self.permissions:
            self.permissions[user_id] = []
        self.permissions[user_id].append(permission)

    def revoke_permission(self, user_id: str, permission: str):
        if user_id in self.permissions:
            if permission in self.permissions[user_id]:
                self.permissions[user_id].remove(permission)

    def check_permission(self, user_id: str, permission: str) -> bool:
        return user_id in self.permissions and permission in self.permissions[user_id]

    # Email functionality
    def send_notification_email(self, user_id: str, message: str):
        user = self.users.get(user_id)
        if user and 'email' in user:
            self.email_service.send(user['email'], message)

    def send_bulk_email(self, user_ids: List[str], subject: str, body: str):
        for user_id in user_ids:
            user = self.users.get(user_id)
            if user and 'email' in user:
                self.email_service.send(user['email'], body, subject)

    # Analytics and logging
    def track_user_action(self, user_id: str, action: str):
        self.analytics.track_event(user_id, action)
        self._log_action(user_id, action)

    def generate_user_report(self, user_id: str):
        user = self.users.get(user_id)
        sessions = [s for s in self.sessions.values() if s['user_id'] == user_id]
        permissions = self.permissions.get(user_id, [])
        return {
            'user': user,
            'active_sessions': len(sessions),
            'permissions': permissions,
            'last_activity': max([s['last_activity'] for s in sessions]) if sessions else None
        }

    # Payment processing
    def process_payment(self, user_id: str, amount: float, currency: str):
        user = self.users.get(user_id)
        if user:
            result = self.payment_processor.charge(user['payment_method'], amount, currency)
            self._log_payment(user_id, amount, currency, result['status'])
            return result

    # Private helper methods (too many for one class)
    def _generate_user_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

    def _generate_session_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

    def _log_user_creation(self, user_id: str):
        self.audit_logs.append({'action': 'user_created', 'user_id': user_id, 'timestamp': datetime.now()})

    def _log_user_update(self, user_id: str):
        self.audit_logs.append({'action': 'user_updated', 'user_id': user_id, 'timestamp': datetime.now()})

    def _log_user_deletion(self, user_id: str):
        self.audit_logs.append({'action': 'user_deleted', 'user_id': user_id, 'timestamp': datetime.now()})

    def _log_action(self, user_id: str, action: str):
        self.audit_logs.append({'action': action, 'user_id': user_id, 'timestamp': datetime.now()})

    def _log_payment(self, user_id: str, amount: float, currency: str, status: str):
        self.audit_logs.append({
            'action': 'payment_processed',
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'status': status,
            'timestamp': datetime.now()
        })

    def _send_welcome_email(self, user_id: str):
        self.email_service.send_welcome(user_id)

    def _notify_user_update(self, user_id: str):
        self.notification_service.notify(user_id, 'Your profile has been updated')

    def _track_user_signup(self, user_id: str):
        self.analytics.track_event(user_id, 'user_signup')

    def _cleanup_user_sessions(self, user_id: str):
        sessions_to_remove = [sid for sid, session in self.sessions.items() if session['user_id'] == user_id]
        for sid in sessions_to_remove:
            del self.sessions[sid]

    def _cleanup_user_permissions(self, user_id: str):
        if user_id in self.permissions:
            del self.permissions[user_id]

# Placeholder classes to make the code complete
class EmailService:
    def send(self, email: str, message: str, subject: str = None):
        pass

    def send_welcome(self, user_id: str):
        pass

class NotificationService:
    def notify(self, user_id: str, message: str):
        pass

class PaymentProcessor:
    def charge(self, payment_method: Dict, amount: float, currency: str):
        return {'status': 'success', 'transaction_id': '12345'}

class AnalyticsTracker:
    def track_event(self, user_id: str, event: str):
        pass