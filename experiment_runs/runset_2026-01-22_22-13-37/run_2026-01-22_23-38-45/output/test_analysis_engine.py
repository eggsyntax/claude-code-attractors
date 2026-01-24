"""
Test cases for the CodeMentor Analysis Engine

Demonstrates the capabilities and validates the functionality
of the pattern detection and code quality analysis features.
"""

import unittest
from analysis_engine import (
    CodeAnalysisEngine,
    CollaborationInterface,
    PatternType,
    SeverityLevel
)


class TestCodeAnalysisEngine(unittest.TestCase):
    """Test suite for the CodeAnalysisEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = CodeAnalysisEngine()

    def test_singleton_pattern_detection(self):
        """Test detection of Singleton pattern."""
        singleton_code = '''
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        return "Connected to database"
'''
        result = self.engine.analyze_file("test_singleton.py", singleton_code)

        singleton_patterns = [
            p for p in result["patterns"]
            if p.pattern_type == PatternType.SINGLETON
        ]

        self.assertEqual(len(singleton_patterns), 1)
        self.assertGreater(singleton_patterns[0].confidence, 0.7)
        self.assertIn("DatabaseConnection", singleton_patterns[0].description)

    def test_factory_pattern_detection(self):
        """Test detection of Factory pattern."""
        factory_code = '''
def create_user(user_type, name):
    if user_type == "admin":
        return AdminUser(name)
    elif user_type == "regular":
        return RegularUser(name)
    else:
        return GuestUser(name)

def create_notification(notification_type):
    if notification_type == "email":
        return EmailNotification()
    elif notification_type == "sms":
        return SMSNotification()
    return DefaultNotification()
'''
        result = self.engine.analyze_file("test_factory.py", factory_code)

        factory_patterns = [
            p for p in result["patterns"]
            if p.pattern_type == PatternType.FACTORY
        ]

        self.assertGreaterEqual(len(factory_patterns), 1)
        factory_pattern = factory_patterns[0]
        self.assertGreater(factory_pattern.confidence, 0.5)

    def test_observer_pattern_detection(self):
        """Test detection of Observer pattern."""
        observer_code = '''
class EventManager:
    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)

    def unsubscribe(self, observer):
        self.observers.remove(observer)

    def notify_all(self, event):
        for observer in self.observers:
            observer.update(event)

class NewsletterSubscriber:
    def update(self, news):
        print(f"Received news: {news}")
'''
        result = self.engine.analyze_file("test_observer.py", observer_code)

        observer_patterns = [
            p for p in result["patterns"]
            if p.pattern_type == PatternType.OBSERVER
        ]

        self.assertGreaterEqual(len(observer_patterns), 1)
        observer_pattern = observer_patterns[0]
        self.assertGreater(observer_pattern.confidence, 0.5)

    def test_dependency_injection_detection(self):
        """Test detection of Dependency Injection pattern."""
        di_code = '''
class OrderService:
    def __init__(self, payment_processor, email_service, logger):
        self.payment_processor = payment_processor
        self.email_service = email_service
        self.logger = logger

    def process_order(self, order):
        self.logger.info(f"Processing order {order.id}")
        payment_result = self.payment_processor.charge(order.amount)
        if payment_result.success:
            self.email_service.send_confirmation(order.customer)
            return True
        return False
'''
        result = self.engine.analyze_file("test_di.py", di_code)

        di_patterns = [
            p for p in result["patterns"]
            if p.pattern_type == PatternType.DEPENDENCY_INJECTION
        ]

        self.assertGreaterEqual(len(di_patterns), 1)

    def test_function_length_analysis(self):
        """Test function length quality analysis."""
        # Create a long function with many lines
        lines = [f"    line_{i} = {i}" for i in range(60)]
        long_function_code = f'''
def very_long_function():
{chr(10).join(lines)}
    return "completed"
'''
        result = self.engine.analyze_file("test_long_function.py", long_function_code)

        length_issues = [
            issue for issue in result["quality_issues"]
            if issue.category == "Function Length"
        ]

        self.assertGreater(len(length_issues), 0)

    def test_naming_convention_analysis(self):
        """Test naming convention quality analysis."""
        naming_code = '''
class badClassName:
    def BadMethodName(self):
        pass

def AnotherBadFunctionName():
    pass

class GoodClassName:
    def good_method_name(self):
        pass

def good_function_name():
    pass
'''
        result = self.engine.analyze_file("test_naming.py", naming_code)

        naming_issues = [
            issue for issue in result["quality_issues"]
            if issue.category == "Naming Convention"
        ]

        self.assertGreaterEqual(len(naming_issues), 2)

    def test_code_metrics_calculation(self):
        """Test code metrics calculation."""
        metrics_code = '''
class TestClass:
    def method_one(self):
        if True:
            for i in range(10):
                while i > 0:
                    try:
                        i -= 1
                    except:
                        break

    def method_two(self):
        pass

def function_one():
    if True:
        return "yes"
    else:
        return "no"
'''
        result = self.engine.analyze_file("test_metrics.py", metrics_code)

        metrics = result["metrics"]
        self.assertGreater(metrics["functions"], 0)
        self.assertGreater(metrics["classes"], 0)
        self.assertGreater(metrics["cyclomatic_complexity"], 0)
        self.assertGreater(metrics["lines_of_code"], 10)

    def test_educational_insights_generation(self):
        """Test educational insights generation."""
        pattern_rich_code = '''
class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

def create_logger(log_type):
    if log_type == "file":
        return FileLogger()
    elif log_type == "console":
        return ConsoleLogger()
    return NullLogger()

class EventBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def notify_subscribers(self, event):
        for subscriber in self.subscribers:
            subscriber.handle(event)
'''
        result = self.engine.analyze_file("test_insights.py", pattern_rich_code)

        self.assertGreater(len(result["educational_insights"]), 0)
        self.assertGreater(len(result["patterns"]), 1)

    def test_collaboration_opportunities(self):
        """Test collaboration opportunity identification."""
        # Create a complex function with many nested conditions
        conditions = []
        for i in range(15):
            condition_block = f"    if condition_{i}:\n"
            for j in range(5):
                condition_block += f"        nested_call_{j}()\n"
            conditions.append(condition_block)

        complex_code = f'''
def extremely_complex_function():
{chr(10).join(conditions)}
    return result
'''
        result = self.engine.analyze_file("test_collaboration.py", complex_code)

        self.assertGreater(len(result["collaboration_opportunities"]), 0)


class TestCollaborationInterface(unittest.TestCase):
    """Test suite for the CollaborationInterface."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = CodeAnalysisEngine()
        self.interface = CollaborationInterface(self.engine)

    def test_review_data_preparation(self):
        """Test preparation of data for collaborative review."""
        # Create sample code with patterns and issues
        operations = [f"        operation_{i}()" for i in range(30)]
        sample_code = f'''
class UserManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def VeryLongMethodNameThatViolatesConventions(self):
{chr(10).join(operations)}
        return "done"
'''

        review_data = self.interface.prepare_review_data("test_review.py", sample_code)

        self.assertIn("summary", review_data)
        self.assertIn("review_points", review_data)
        self.assertIn("learning_opportunities", review_data)
        self.assertIn("collaboration_suggestions", review_data)
        self.assertIn("raw_analysis", review_data)

        # Verify review points are prioritized
        review_points = review_data["review_points"]
        if review_points:
            priorities = [point["priority"] for point in review_points]
            self.assertIn(priorities[0], ["high", "medium", "low"])

    def test_summary_generation(self):
        """Test summary generation for collaborative review."""
        simple_code = '''
def simple_function():
    return "hello"

class SimpleClass:
    pass
'''

        review_data = self.interface.prepare_review_data("test_simple.py", simple_code)
        summary = review_data["summary"]

        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 10)

    def test_review_points_structure(self):
        """Test structure of generated review points."""
        # Create code with multiple issues
        processing_lines = [f"        line_{i} = process_data_{i}()" for i in range(25)]
        code_with_issues = f'''
class badNaming:
    def __init__(self, dependency_one, dependency_two, dependency_three):
        self.dep1 = dependency_one
        self.dep2 = dependency_two
        self.dep3 = dependency_three

    def VeryLongMethodName(self):
{chr(10).join(processing_lines)}
        return result
'''

        review_data = self.interface.prepare_review_data("test_structure.py", code_with_issues)
        review_points = review_data["review_points"]

        if review_points:
            point = review_points[0]
            required_keys = ["type", "priority", "title", "description", "location"]
            for key in required_keys:
                self.assertIn(key, point)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for real-world scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = CodeAnalysisEngine()
        self.interface = CollaborationInterface(self.engine)

    def test_mvc_architecture_analysis(self):
        """Test analysis of MVC-style architecture."""
        mvc_code = '''
class UserController:
    def __init__(self, user_service, view_renderer):
        self.user_service = user_service
        self.view_renderer = view_renderer

    def create_user(self, user_data):
        user = self.user_service.create(user_data)
        return self.view_renderer.render("user_created", user)

class UserService:
    def __init__(self, user_repository, email_service):
        self.repository = user_repository
        self.email_service = email_service

    def create(self, user_data):
        user = User(user_data)
        self.repository.save(user)
        self.email_service.send_welcome(user)
        return user

class UserRepository:
    def save(self, user):
        # Database save logic
        pass

class User:
    def __init__(self, data):
        self.name = data["name"]
        self.email = data["email"]
'''

        result = self.engine.analyze_file("mvc_example.py", mvc_code)

        # Should detect dependency injection patterns
        di_patterns = [
            p for p in result["patterns"]
            if p.pattern_type == PatternType.DEPENDENCY_INJECTION
        ]
        self.assertGreater(len(di_patterns), 0)

        # Should have good metrics (multiple classes, reasonable complexity)
        self.assertGreater(result["metrics"]["classes"], 2)
        self.assertLess(result["metrics"]["cyclomatic_complexity"], 10)

    def test_refactoring_candidate_identification(self):
        """Test identification of code that needs refactoring."""
        legacy_code = '''
class LegacyProcessor:
    def process_everything(self, data):
        # This function does too much
        results = []

        # Data validation
        if not data:
            raise ValueError("No data")
        if not isinstance(data, list):
            raise ValueError("Data must be list")
        if len(data) == 0:
            return []

        # Data transformation
        for item in data:
            if item["type"] == "A":
                transformed = item["value"] * 2
            elif item["type"] == "B":
                transformed = item["value"] + 10
            elif item["type"] == "C":
                transformed = item["value"] / 2
            else:
                transformed = item["value"]

            # Business logic
            if transformed > 100:
                category = "high"
                priority = 1
                needs_approval = True
            elif transformed > 50:
                category = "medium"
                priority = 2
                needs_approval = False
            else:
                category = "low"
                priority = 3
                needs_approval = False

            # Data formatting
            result = {
                "original": item,
                "transformed": transformed,
                "category": category,
                "priority": priority,
                "needs_approval": needs_approval,
                "processed_at": "now"
            }

            # Storage preparation
            if needs_approval:
                result["status"] = "pending"
            else:
                result["status"] = "processed"

            results.append(result)

        # Final sorting
        results.sort(key=lambda x: x["priority"])

        return results
'''

        result = self.engine.analyze_file("legacy_refactor.py", legacy_code)

        # Should identify function length issues
        length_issues = [
            issue for issue in result["quality_issues"]
            if issue.category == "Function Length"
        ]
        self.assertGreater(len(length_issues), 0)

        # Should suggest collaboration due to complexity
        self.assertGreater(len(result["collaboration_opportunities"]), 0)


def create_example_files():
    """Create example files to demonstrate the analysis engine."""

    examples = {
        "singleton_example.py": '''
"""
Example: Singleton Pattern Implementation
A thread-safe singleton for managing application configuration.
"""

import threading

class AppConfig:
    """Thread-safe singleton for application configuration."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.settings = {}
            self._initialized = True

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
''',

        "factory_example.py": '''
"""
Example: Factory Pattern Implementation
Creates different types of data processors based on input format.
"""

from abc import ABC, abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def process(self, data):
        pass

class JSONProcessor(DataProcessor):
    def process(self, data):
        import json
        return json.loads(data)

class XMLProcessor(DataProcessor):
    def process(self, data):
        # Simplified XML processing
        return {"xml_data": data}

class CSVProcessor(DataProcessor):
    def process(self, data):
        lines = data.strip().split('\\n')
        return [line.split(',') for line in lines]

def create_processor(data_format):
    """Factory method to create appropriate data processor."""
    if data_format.lower() == "json":
        return JSONProcessor()
    elif data_format.lower() == "xml":
        return XMLProcessor()
    elif data_format.lower() == "csv":
        return CSVProcessor()
    else:
        raise ValueError(f"Unsupported data format: {data_format}")

def create_processor_by_content(content):
    """Factory method that determines format from content."""
    content = content.strip()
    if content.startswith('{') and content.endswith('}'):
        return JSONProcessor()
    elif content.startswith('<') and content.endswith('>'):
        return XMLProcessor()
    elif ',' in content:
        return CSVProcessor()
    else:
        raise ValueError("Cannot determine data format from content")
''',

        "observer_example.py": '''
"""
Example: Observer Pattern Implementation
Event-driven notification system for user actions.
"""

from abc import ABC, abstractmethod
from typing import List, Any

class Observer(ABC):
    @abstractmethod
    def update(self, event_data: Any):
        pass

class EventPublisher:
    def __init__(self):
        self.observers: List[Observer] = []

    def subscribe(self, observer: Observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def unsubscribe(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, event_data: Any):
        for observer in self.observers:
            observer.update(event_data)

class EmailNotificationObserver(Observer):
    def update(self, event_data: Any):
        print(f"Sending email notification: {event_data}")

class LoggingObserver(Observer):
    def update(self, event_data: Any):
        print(f"Logging event: {event_data}")

class MetricsObserver(Observer):
    def update(self, event_data: Any):
        print(f"Recording metrics for: {event_data}")

class UserActionTracker(EventPublisher):
    def user_registered(self, user_id: str):
        event_data = {"event": "user_registered", "user_id": user_id}
        self.notify_observers(event_data)

    def user_login(self, user_id: str):
        event_data = {"event": "user_login", "user_id": user_id}
        self.notify_observers(event_data)
'''
    }

    return examples


if __name__ == "__main__":
    # Run the tests
    unittest.main(argv=[''], exit=False, verbosity=2)

    print("\n" + "="*50)
    print("Creating example files for demonstration...")

    examples = create_example_files()
    engine = CodeAnalysisEngine()

    for filename, code in examples.items():
        print(f"\nAnalyzing {filename}...")
        result = engine.analyze_file(filename, code)

        print(f"Patterns found: {len(result['patterns'])}")
        for pattern in result['patterns']:
            print(f"  - {pattern.pattern_type.value}: {pattern.description}")

        print(f"Quality issues: {len(result['quality_issues'])}")
        for issue in result['quality_issues'][:3]:  # Show first 3
            print(f"  - {issue.severity.value}: {issue.description}")

        if result['educational_insights']:
            print("Educational insight:")
            print(f"  - {result['educational_insights'][0]}")