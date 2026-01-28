#!/usr/bin/env python3
"""
CodeMentor Analysis Demo

This script demonstrates the capabilities of the CodeMentor analysis engine
by analyzing sample code with various patterns and issues.

Run with: python demo_analysis.py
"""

import tempfile
import os
from code_analyzer import CodeAnalyzer, format_analysis_report


def create_sample_files():
    """Create sample Python files with various patterns and issues for analysis"""

    # Sample 1: Singleton pattern with issues
    singleton_code = '''
class DatabaseConnection:
    """A singleton database connection class"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        if self.connection is None:
            self.connection = "fake_connection"
        return self.connection

    def execute_query(self, query, param1, param2, param3, param4, param5):
        # This is a very long method that does too many things
        # First we validate the query
        if not query:
            raise ValueError("Query cannot be empty")

        # Then we check if connection is alive
        if self.connection is None:
            self.connect()

        # Then we prepare the query
        prepared_query = query.replace("?", "%s")

        # Then we execute it
        result = self.connection.execute(prepared_query)

        # Then we log it
        print(f"Executed query: {query}")

        # Then we format the result
        if result:
            formatted_result = []
            for row in result:
                formatted_row = {}
                for i, value in enumerate(row):
                    formatted_row[f"col_{i}"] = value
                formatted_result.append(formatted_row)
            return formatted_result

        # Then we handle empty results
        return []

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
'''

    # Sample 2: Factory pattern with magic numbers
    factory_code = '''
def create_user_account(account_type, balance=1000):
    """Factory method for creating different types of user accounts"""

    if account_type == "premium":
        return PremiumAccount(balance, 0.05, 50000)  # Magic numbers!
    elif account_type == "standard":
        return StandardAccount(balance, 0.02, 10000)  # More magic numbers!
    elif account_type == "basic":
        return BasicAccount(balance, 0.01, 5000)     # Even more magic numbers!
    else:
        raise ValueError("Unknown account type")

class PremiumAccount:
    def __init__(self, balance, interest_rate, credit_limit):
        self.balance = balance
        self.interest_rate = interest_rate
        self.credit_limit = credit_limit

class StandardAccount:
    def __init__(self, balance, interest_rate, credit_limit):
        self.balance = balance
        self.interest_rate = interest_rate
        self.credit_limit = credit_limit

class BasicAccount:
    def __init__(self, balance, interest_rate, credit_limit):
        self.balance = balance
        self.interest_rate = interest_rate
        self.credit_limit = credit_limit
'''

    # Sample 3: Observer pattern with God object
    observer_code = '''
import requests
import sqlite3
import json
import os

class NotificationManager:
    """A class that handles way too many responsibilities"""

    def __init__(self):
        self.observers = []
        self.database_connection = sqlite3.connect("notifications.db")
        self.api_key = "secret_key_12345"
        self.ui_elements = {}

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, event):
        for observer in self.observers:
            observer.update(event)

    # Database operations
    def save_notification(self, notification):
        cursor = self.database_connection.cursor()
        cursor.execute("INSERT INTO notifications VALUES (?, ?)",
                      (notification.id, notification.message))
        self.database_connection.commit()

    def load_notifications(self):
        cursor = self.database_connection.cursor()
        cursor.execute("SELECT * FROM notifications")
        return cursor.fetchall()

    # Network operations
    def send_email_notification(self, email, message):
        response = requests.post("https://api.email.com/send", {
            "api_key": self.api_key,
            "to": email,
            "message": message
        })
        return response.status_code == 200

    def send_sms_notification(self, phone, message):
        response = requests.post("https://api.sms.com/send", {
            "api_key": self.api_key,
            "to": phone,
            "message": message
        })
        return response.status_code == 200

    # File operations
    def save_to_file(self, notifications, filename):
        with open(filename, 'w') as f:
            json.dump([n.__dict__ for n in notifications], f)

    def load_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return []

    # UI operations
    def render_notification_list(self, notifications):
        html = "<ul>"
        for notification in notifications:
            html += f"<li>{notification.message}</li>"
        html += "</ul>"
        return html

    def display_notification_popup(self, message):
        popup = f"<div class='popup'>{message}</div>"
        self.ui_elements['popup'] = popup
        return popup

    # Business logic with feature envy
    def process_user_notification(self, user, notification):
        # This method is more interested in the user object than itself
        if user.is_premium():
            priority = user.get_priority_level()
            preferences = user.get_notification_preferences()
            contact_info = user.get_contact_information()

            if preferences.email_enabled:
                self.send_email_notification(contact_info.email, notification.message)
            if preferences.sms_enabled:
                self.send_sms_notification(contact_info.phone, notification.message)

            user.update_last_notification_time()
            user.increment_notification_count()

        return user.get_notification_history()
'''

    # Sample 4: Code with duplicates and long method
    duplicate_code = '''
def calculate_shipping_cost_domestic(weight, distance):
    """Calculate shipping cost for domestic orders"""
    base_cost = 5.00
    weight_multiplier = 0.50
    distance_multiplier = 0.10

    if weight > 50:
        weight_multiplier = 0.75

    if distance > 1000:
        distance_multiplier = 0.15

    total_cost = base_cost + (weight * weight_multiplier) + (distance * distance_multiplier)

    # Apply domestic discount
    if total_cost > 25.00:
        total_cost = total_cost * 0.95

    return round(total_cost, 2)


def calculate_shipping_cost_international(weight, distance):
    """Calculate shipping cost for international orders"""
    base_cost = 15.00  # Different base cost
    weight_multiplier = 0.50
    distance_multiplier = 0.10

    if weight > 50:
        weight_multiplier = 0.75

    if distance > 1000:
        distance_multiplier = 0.15

    total_cost = base_cost + (weight * weight_multiplier) + (distance * distance_multiplier)

    # Apply international surcharge instead of discount
    if total_cost > 25.00:
        total_cost = total_cost * 1.15

    return round(total_cost, 2)


def process_large_order(items, customer, shipping_address, billing_address,
                       payment_method, discount_code, special_instructions,
                       delivery_date, is_gift, gift_message, insurance_needed):
    """This method is way too long and does too many things"""

    # Validate customer information
    if not customer.is_valid():
        raise ValueError("Invalid customer information")

    if not customer.email:
        raise ValueError("Customer email is required")

    if not customer.phone:
        raise ValueError("Customer phone is required")

    # Validate addresses
    if not shipping_address.is_complete():
        raise ValueError("Incomplete shipping address")

    if not billing_address.is_complete():
        raise ValueError("Incomplete billing address")

    # Validate payment method
    if not payment_method.is_valid():
        raise ValueError("Invalid payment method")

    # Process items
    total_weight = 0
    total_cost = 0
    processed_items = []

    for item in items:
        if not item.in_stock():
            raise ValueError(f"Item {item.name} is out of stock")

        processed_item = {
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'weight': item.weight,
            'quantity': item.quantity
        }

        total_weight += item.weight * item.quantity
        total_cost += item.price * item.quantity
        processed_items.append(processed_item)

    # Apply discount
    if discount_code:
        discount = get_discount_by_code(discount_code)
        if discount:
            total_cost = total_cost * (1 - discount.percentage)

    # Calculate shipping
    distance = calculate_distance(customer.address, shipping_address)
    if shipping_address.country == "USA":
        shipping_cost = calculate_shipping_cost_domestic(total_weight, distance)
    else:
        shipping_cost = calculate_shipping_cost_international(total_weight, distance)

    # Process payment
    payment_result = payment_method.charge(total_cost + shipping_cost)
    if not payment_result.success:
        raise ValueError("Payment processing failed")

    # Create order record
    order = {
        'customer': customer,
        'items': processed_items,
        'total_cost': total_cost,
        'shipping_cost': shipping_cost,
        'payment_id': payment_result.transaction_id,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'special_instructions': special_instructions,
        'delivery_date': delivery_date,
        'is_gift': is_gift,
        'gift_message': gift_message if is_gift else None
    }

    # Save to database
    save_order_to_database(order)

    # Send confirmation emails
    send_order_confirmation_email(customer.email, order)

    if is_gift:
        send_gift_notification_email(shipping_address.recipient_email, gift_message)

    # Schedule delivery
    schedule_delivery(order, delivery_date)

    # Update inventory
    for item in items:
        update_inventory(item.id, item.quantity)

    return order
'''

    return [
        ("singleton_issues.py", singleton_code),
        ("factory_magic.py", factory_code),
        ("god_object.py", observer_code),
        ("duplicate_long.py", duplicate_code)
    ]


def run_demo():
    """Run the CodeMentor analysis demo"""
    print("🚀 CodeMentor Analysis Engine Demo")
    print("=" * 50)
    print()

    # Create temporary directory for sample files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Creating sample files in: {temp_dir}")

        # Create sample files
        sample_files = create_sample_files()
        file_paths = []

        for filename, content in sample_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            file_paths.append(file_path)
            print(f"   ✅ Created {filename}")

        print()

        # Analyze each file
        analyzer = CodeAnalyzer()

        for file_path in file_paths:
            filename = os.path.basename(file_path)
            print(f"🔍 Analyzing {filename}...")
            print("-" * 30)

            results = analyzer.analyze_file(file_path)
            report = format_analysis_report(results)
            print(report)
            print("\n" + "=" * 50 + "\n")

        # Analyze entire directory
        print("🌍 Analyzing entire directory...")
        print("-" * 30)

        all_results = analyzer.analyze_directory(temp_dir)
        directory_report = format_analysis_report(all_results)
        print(directory_report)

        print("\n" + "🎉 Demo completed!")
        print(f"📊 Total findings across all files: {len(all_results)}")


if __name__ == "__main__":
    run_demo()