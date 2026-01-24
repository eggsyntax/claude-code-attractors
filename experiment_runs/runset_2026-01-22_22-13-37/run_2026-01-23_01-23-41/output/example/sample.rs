// Sample Rust code to demonstrate analysis capabilities

use std::collections::HashMap;

/// A simple function with low complexity
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

/// A more complex function with multiple decision points
pub fn calculate_tax(income: f64, deductions: Vec<f64>) -> f64 {
    let total_deductions: f64 = deductions.iter().sum();
    let taxable_income = income - total_deductions;

    if taxable_income <= 0.0 {
        return 0.0;
    }

    let tax_rate = if taxable_income <= 10000.0 {
        0.10
    } else if taxable_income <= 40000.0 {
        0.15
    } else if taxable_income <= 85000.0 {
        0.25
    } else {
        0.35
    };

    let mut tax = taxable_income * tax_rate;

    // Apply additional rules
    if taxable_income > 100000.0 {
        tax += (taxable_income - 100000.0) * 0.05;
    }

    // Round to nearest cent
    (tax * 100.0).round() / 100.0
}

/// A function with high cyclomatic complexity (intentionally complex for demo)
pub fn process_orders(orders: Vec<Order>) -> Result<OrderSummary, ProcessingError> {
    let mut summary = OrderSummary::new();

    for order in orders {
        match order.status {
            OrderStatus::Pending => {
                if order.amount > 1000.0 {
                    if order.customer.is_premium() {
                        summary.add_premium_order(order.amount);

                        for item in &order.items {
                            if item.category == "electronics" {
                                if item.price > 500.0 {
                                    summary.add_high_value_item();
                                } else if item.price > 100.0 {
                                    summary.add_medium_value_item();
                                } else {
                                    summary.add_low_value_item();
                                }
                            } else if item.category == "books" {
                                summary.add_book_order();
                            } else {
                                summary.add_other_order();
                            }
                        }
                    } else {
                        summary.add_regular_order(order.amount);
                    }
                } else {
                    summary.add_small_order(order.amount);
                }
            }
            OrderStatus::Processing => {
                summary.add_processing_order();
            }
            OrderStatus::Shipped => {
                summary.add_shipped_order();

                if order.shipping_method == "express" {
                    summary.add_express_shipment();
                }
            }
            OrderStatus::Delivered => {
                summary.add_delivered_order();

                match order.customer.satisfaction_rating() {
                    Some(rating) if rating >= 4 => summary.add_satisfied_customer(),
                    Some(rating) if rating >= 3 => summary.add_neutral_customer(),
                    Some(_) => summary.add_unsatisfied_customer(),
                    None => summary.add_unrated_customer(),
                }
            }
            OrderStatus::Cancelled => {
                summary.add_cancelled_order();
            }
            OrderStatus::Refunded => {
                summary.add_refunded_order();

                if order.refund_reason.contains("defective") {
                    summary.add_quality_issue();
                } else if order.refund_reason.contains("delivery") {
                    summary.add_delivery_issue();
                } else {
                    summary.add_other_issue();
                }
            }
        }

        // Additional validation
        if order.amount < 0.0 {
            return Err(ProcessingError::InvalidAmount);
        }

        if order.customer.email.is_empty() {
            return Err(ProcessingError::MissingEmail);
        }
    }

    Ok(summary)
}

// Supporting types for the example
#[derive(Debug)]
pub struct Order {
    pub amount: f64,
    pub status: OrderStatus,
    pub customer: Customer,
    pub items: Vec<OrderItem>,
    pub shipping_method: String,
    pub refund_reason: String,
}

#[derive(Debug, PartialEq)]
pub enum OrderStatus {
    Pending,
    Processing,
    Shipped,
    Delivered,
    Cancelled,
    Refunded,
}

#[derive(Debug)]
pub struct Customer {
    pub email: String,
    pub premium: bool,
    pub satisfaction: Option<u8>,
}

impl Customer {
    pub fn is_premium(&self) -> bool {
        self.premium
    }

    pub fn satisfaction_rating(&self) -> Option<u8> {
        self.satisfaction
    }
}

#[derive(Debug)]
pub struct OrderItem {
    pub category: String,
    pub price: f64,
}

#[derive(Debug)]
pub struct OrderSummary {
    data: HashMap<String, u32>,
}

impl OrderSummary {
    pub fn new() -> Self {
        Self {
            data: HashMap::new(),
        }
    }

    pub fn add_premium_order(&mut self, _amount: f64) {
        *self.data.entry("premium_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_regular_order(&mut self, _amount: f64) {
        *self.data.entry("regular_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_small_order(&mut self, _amount: f64) {
        *self.data.entry("small_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_processing_order(&mut self) {
        *self.data.entry("processing_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_shipped_order(&mut self) {
        *self.data.entry("shipped_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_delivered_order(&mut self) {
        *self.data.entry("delivered_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_cancelled_order(&mut self) {
        *self.data.entry("cancelled_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_refunded_order(&mut self) {
        *self.data.entry("refunded_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_express_shipment(&mut self) {
        *self.data.entry("express_shipments".to_string()).or_insert(0) += 1;
    }

    pub fn add_high_value_item(&mut self) {
        *self.data.entry("high_value_items".to_string()).or_insert(0) += 1;
    }

    pub fn add_medium_value_item(&mut self) {
        *self.data.entry("medium_value_items".to_string()).or_insert(0) += 1;
    }

    pub fn add_low_value_item(&mut self) {
        *self.data.entry("low_value_items".to_string()).or_insert(0) += 1;
    }

    pub fn add_book_order(&mut self) {
        *self.data.entry("book_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_other_order(&mut self) {
        *self.data.entry("other_orders".to_string()).or_insert(0) += 1;
    }

    pub fn add_satisfied_customer(&mut self) {
        *self.data.entry("satisfied_customers".to_string()).or_insert(0) += 1;
    }

    pub fn add_neutral_customer(&mut self) {
        *self.data.entry("neutral_customers".to_string()).or_insert(0) += 1;
    }

    pub fn add_unsatisfied_customer(&mut self) {
        *self.data.entry("unsatisfied_customers".to_string()).or_insert(0) += 1;
    }

    pub fn add_unrated_customer(&mut self) {
        *self.data.entry("unrated_customers".to_string()).or_insert(0) += 1;
    }

    pub fn add_quality_issue(&mut self) {
        *self.data.entry("quality_issues".to_string()).or_insert(0) += 1;
    }

    pub fn add_delivery_issue(&mut self) {
        *self.data.entry("delivery_issues".to_string()).or_insert(0) += 1;
    }

    pub fn add_other_issue(&mut self) {
        *self.data.entry("other_issues".to_string()).or_insert(0) += 1;
    }
}

#[derive(Debug)]
pub enum ProcessingError {
    InvalidAmount,
    MissingEmail,
}

impl std::fmt::Display for ProcessingError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ProcessingError::InvalidAmount => write!(f, "Invalid order amount"),
            ProcessingError::MissingEmail => write!(f, "Customer email is required"),
        }
    }
}

impl std::error::Error for ProcessingError {}