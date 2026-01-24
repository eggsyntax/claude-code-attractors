"""
Sample services file demonstrating various architectural patterns.
This includes both good patterns and potential issues.
"""

from typing import List, Dict, Any, Protocol
from abc import ABC, abstractmethod
from models import UserManager, DatabaseConnection

# Factory Pattern - Good design pattern
class NotificationFactory:
    """Factory for creating different types of notifications."""

    @staticmethod
    def create_notification(notification_type: str, message: str, recipient: str):
        if notification_type == "email":
            return EmailNotification(message, recipient)
        elif notification_type == "sms":
            return SMSNotification(message, recipient)
        elif notification_type == "push":
            return PushNotification(message, recipient)
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")

# Abstract base for notifications
class Notification(ABC):
    def __init__(self, message: str, recipient: str):
        self.message = message
        self.recipient = recipient

    @abstractmethod
    def send(self):
        pass

class EmailNotification(Notification):
    def send(self):
        print(f"Sending email to {self.recipient}: {self.message}")

class SMSNotification(Notification):
    def send(self):
        print(f"Sending SMS to {self.recipient}: {self.message}")

class PushNotification(Notification):
    def send(self):
        print(f"Sending push notification to {self.recipient}: {self.message}")

# Observer Pattern - Event-driven architecture
class EventObserver(Protocol):
    def notify(self, event: str, data: Dict[str, Any]):
        pass

class EventDispatcher:
    """Manages event observers and dispatches events."""

    def __init__(self):
        self._observers: Dict[str, List[EventObserver]] = {}

    def subscribe(self, event_type: str, observer: EventObserver):
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(observer)

    def unsubscribe(self, event_type: str, observer: EventObserver):
        if event_type in self._observers:
            self._observers[event_type].remove(observer)

    def dispatch(self, event_type: str, data: Dict[str, Any]):
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                observer.notify(event_type, data)

class AuditLogger:
    """Observer that logs all events."""

    def notify(self, event: str, data: Dict[str, Any]):
        print(f"AUDIT: {event} - {data}")

class MetricsCollector:
    """Observer that collects metrics from events."""

    def __init__(self):
        self.metrics = {}

    def notify(self, event: str, data: Dict[str, Any]):
        if event not in self.metrics:
            self.metrics[event] = 0
        self.metrics[event] += 1

# Feature Envy Anti-pattern - This class is too interested in UserManager
class UserService:
    """
    Service that exhibits Feature Envy - it's overly dependent on UserManager
    and could be better integrated or refactored.
    """

    def __init__(self):
        self.user_manager = UserManager()
        self.db = DatabaseConnection()
        self.event_dispatcher = EventDispatcher()

    def advanced_user_analytics(self, user_id: str):
        # This method is too interested in UserManager's internals
        user = self.user_manager.users.get(user_id)  # Direct access to internal data
        sessions = [s for s in self.user_manager.sessions.values() if s['user_id'] == user_id]  # Direct access
        permissions = self.user_manager.permissions.get(user_id, [])  # Direct access

        # Complex analytics logic that should probably be in UserManager or a separate service
        session_duration = 0
        for session in sessions:
            duration = (session.get('last_activity', session['created_at']) - session['created_at']).seconds
            session_duration += duration

        return {
            'user': user,
            'total_sessions': len(sessions),
            'avg_session_duration': session_duration / max(len(sessions), 1),
            'permissions_count': len(permissions),
            'is_power_user': len(permissions) > 5
        }

    def bulk_user_operation(self, operation: str, user_ids: List[str]):
        # Another method that's too dependent on UserManager internals
        results = []
        for user_id in user_ids:
            user = self.user_manager.users.get(user_id)  # Direct access again
            if user:
                if operation == 'deactivate':
                    user['active'] = False
                    self.user_manager._log_action(user_id, 'deactivated')  # Accessing private method
                elif operation == 'premium_upgrade':
                    self.user_manager.grant_permission(user_id, 'premium')
                    self.user_manager._send_notification_email(user_id, 'Welcome to Premium!')
                results.append({'user_id': user_id, 'status': 'success'})
            else:
                results.append({'user_id': user_id, 'status': 'not_found'})

        return results

# Circular dependency potential - imports could create cycles
from analytics import AdvancedAnalyticsEngine  # This might create circular imports

class ReportingService:
    """Service for generating complex reports."""

    def __init__(self):
        self.user_manager = UserManager()
        self.analytics_engine = AdvancedAnalyticsEngine()  # Potential circular dependency

    def generate_user_report(self, user_id: str):
        # Uses both UserManager and AdvancedAnalyticsEngine
        user_data = self.user_manager.generate_user_report(user_id)
        analytics_data = self.analytics_engine.get_user_insights(user_id)

        return {
            **user_data,
            'analytics': analytics_data,
            'generated_at': '2024-01-01T00:00:00Z'
        }

# Shotgun Surgery candidate - changes here might require many changes elsewhere
class ConfigurationManager:
    """
    Configuration manager that's used throughout the application.
    Changes to this class might require updates in many places.
    """

    def __init__(self):
        self.config = {
            'database_url': 'localhost:5432',
            'redis_url': 'localhost:6379',
            'email_provider': 'sendgrid',
            'notification_settings': {
                'email_enabled': True,
                'sms_enabled': False,
                'push_enabled': True
            },
            'feature_flags': {
                'advanced_analytics': True,
                'premium_features': False,
                'beta_ui': False
            }
        }

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value

    def is_feature_enabled(self, feature: str) -> bool:
        return self.config.get('feature_flags', {}).get(feature, False)

    def get_notification_setting(self, setting: str) -> bool:
        return self.config.get('notification_settings', {}).get(setting, False)