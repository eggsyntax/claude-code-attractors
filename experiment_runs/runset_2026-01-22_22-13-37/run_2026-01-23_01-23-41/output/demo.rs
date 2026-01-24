#!/usr/bin/env rust-script

//! Demo script to showcase CodeMetrics capabilities
//!
//! This script demonstrates the kind of analysis CodeMetrics can perform
//! on real-world code examples.

use std::collections::HashMap;

/// Complex e-commerce order processing function
/// This function intentionally has high complexity for demo purposes
pub fn process_order(
    order_id: u64,
    customer_id: u64,
    items: Vec<OrderItem>,
    payment_method: PaymentMethod,
    shipping_address: Address,
    billing_address: Option<Address>,
    promo_codes: Vec<String>,
    customer_tier: CustomerTier,
    special_instructions: Option<String>,
) -> Result<ProcessedOrder, OrderError> {
    // Validation phase
    if order_id == 0 {
        return Err(OrderError::InvalidOrderId);
    }

    if customer_id == 0 {
        return Err(OrderError::InvalidCustomerId);
    }

    if items.is_empty() {
        return Err(OrderError::EmptyCart);
    }

    // Check inventory for each item
    for item in &items {
        if item.quantity == 0 {
            return Err(OrderError::InvalidQuantity(item.product_id));
        }

        // Complex inventory checking logic
        match check_inventory(item.product_id, item.quantity) {
            InventoryStatus::Available => {},
            InventoryStatus::LowStock(available) => {
                if available < item.quantity {
                    return Err(OrderError::InsufficientStock {
                        product_id: item.product_id,
                        requested: item.quantity,
                        available,
                    });
                }
            },
            InventoryStatus::OutOfStock => {
                return Err(OrderError::OutOfStock(item.product_id));
            },
            InventoryStatus::Discontinued => {
                return Err(OrderError::ProductDiscontinued(item.product_id));
            },
        }

        // Check for special handling requirements
        if item.requires_special_handling {
            match customer_tier {
                CustomerTier::Basic => {
                    // Basic customers can't order special handling items
                    if item.value > 1000.0 {
                        return Err(OrderError::SpecialHandlingNotAllowed);
                    }
                },
                CustomerTier::Premium => {
                    // Premium customers have some restrictions
                    if item.value > 5000.0 {
                        // Need additional verification
                        if !verify_premium_customer(customer_id) {
                            return Err(OrderError::VerificationRequired);
                        }
                    }
                },
                CustomerTier::Enterprise => {
                    // Enterprise customers can order anything
                    // but need pre-approval for very expensive items
                    if item.value > 25000.0 {
                        if !has_enterprise_preapproval(customer_id, item.product_id) {
                            return Err(OrderError::PreApprovalRequired);
                        }
                    }
                },
            }
        }
    }

    // Calculate totals
    let mut subtotal = 0.0;
    let mut total_weight = 0.0;
    let mut hazmat_items = false;

    for item in &items {
        let item_total = item.unit_price * item.quantity as f64;

        // Apply item-level discounts
        let discounted_price = match item.category {
            ProductCategory::Electronics => {
                if item_total > 500.0 {
                    item_total * 0.95 // 5% discount
                } else if item_total > 100.0 {
                    item_total * 0.98 // 2% discount
                } else {
                    item_total
                }
            },
            ProductCategory::Books => {
                if item.quantity >= 3 {
                    item_total * 0.90 // 10% discount for 3+ books
                } else {
                    item_total
                }
            },
            ProductCategory::Clothing => {
                // Seasonal discounts
                if is_end_of_season() {
                    item_total * 0.70 // 30% discount
                } else if is_holiday_season() {
                    item_total * 0.85 // 15% discount
                } else {
                    item_total
                }
            },
            ProductCategory::Home => {
                // Bundle discounts
                let home_items_count = items.iter()
                    .filter(|i| matches!(i.category, ProductCategory::Home))
                    .count();

                if home_items_count >= 5 {
                    item_total * 0.80 // 20% discount for 5+ home items
                } else if home_items_count >= 3 {
                    item_total * 0.90 // 10% discount for 3+ home items
                } else {
                    item_total
                }
            },
            ProductCategory::Hazmat => {
                hazmat_items = true;
                // Hazmat items don't get discounts but have handling fees
                item_total + 25.0 // $25 hazmat handling fee per item
            },
        };

        subtotal += discounted_price;
        total_weight += item.weight * item.quantity as f64;
    }

    // Apply customer tier discounts
    let tier_discount = match customer_tier {
        CustomerTier::Basic => 0.0,
        CustomerTier::Premium => subtotal * 0.05, // 5% discount
        CustomerTier::Enterprise => subtotal * 0.10, // 10% discount
    };

    // Apply promo codes
    let mut promo_discount = 0.0;
    for promo_code in &promo_codes {
        match validate_promo_code(promo_code, customer_id, &items) {
            PromoValidation::Valid(discount) => {
                match discount {
                    PromoDiscount::Percentage(pct) => {
                        promo_discount += subtotal * (pct / 100.0);
                    },
                    PromoDiscount::FixedAmount(amount) => {
                        promo_discount += amount;
                    },
                    PromoDiscount::FreeShipping => {
                        // Handle free shipping later
                    },
                    PromoDiscount::BuyOneGetOne => {
                        // Complex BOGO logic
                        for item in &items {
                            if item.quantity >= 2 && item.eligible_for_bogo {
                                let free_items = item.quantity / 2;
                                promo_discount += item.unit_price * free_items as f64;
                            }
                        }
                    },
                }
            },
            PromoValidation::Expired => {
                return Err(OrderError::PromoCodeExpired(promo_code.clone()));
            },
            PromoValidation::Invalid => {
                return Err(OrderError::InvalidPromoCode(promo_code.clone()));
            },
            PromoValidation::AlreadyUsed => {
                return Err(OrderError::PromoCodeAlreadyUsed(promo_code.clone()));
            },
            PromoValidation::MinimumNotMet(minimum) => {
                return Err(OrderError::PromoMinimumNotMet {
                    code: promo_code.clone(),
                    minimum,
                    current: subtotal,
                });
            },
        }
    }

    // Calculate shipping
    let shipping_cost = calculate_shipping_cost(
        &shipping_address,
        total_weight,
        hazmat_items,
        customer_tier,
        &promo_codes,
    )?;

    // Calculate tax
    let tax_rate = get_tax_rate(&shipping_address)?;
    let taxable_amount = subtotal - tier_discount - promo_discount;
    let tax_amount = taxable_amount * tax_rate;

    // Final total
    let total = taxable_amount + tax_amount + shipping_cost;

    // Payment processing
    let payment_result = match payment_method {
        PaymentMethod::CreditCard(ref card) => {
            validate_credit_card(card)?;

            // Additional validation for high-value orders
            if total > 10000.0 {
                match verify_high_value_transaction(customer_id, total) {
                    VerificationResult::Approved => {},
                    VerificationResult::RequiresAdditionalAuth => {
                        return Err(OrderError::AdditionalAuthRequired);
                    },
                    VerificationResult::Declined => {
                        return Err(OrderError::PaymentDeclined);
                    },
                }
            }

            process_credit_card_payment(card, total)?
        },
        PaymentMethod::PayPal(ref account) => {
            validate_paypal_account(account)?;
            process_paypal_payment(account, total)?
        },
        PaymentMethod::BankTransfer(ref details) => {
            if total < 100.0 {
                return Err(OrderError::BankTransferMinimumNotMet);
            }
            validate_bank_details(details)?;
            initiate_bank_transfer(details, total)?
        },
        PaymentMethod::Cryptocurrency(ref wallet) => {
            if matches!(customer_tier, CustomerTier::Basic) {
                return Err(OrderError::CryptoNotAllowedForBasicTier);
            }
            validate_crypto_wallet(wallet)?;
            process_crypto_payment(wallet, total)?
        },
    };

    // Create the processed order
    let processed_order = ProcessedOrder {
        order_id,
        customer_id,
        items: items.clone(),
        subtotal,
        tier_discount,
        promo_discount,
        tax_amount,
        shipping_cost,
        total,
        payment_result,
        estimated_delivery: calculate_delivery_date(&shipping_address, hazmat_items),
        tracking_number: generate_tracking_number(),
        special_instructions,
    };

    // Log the order for audit trail
    log_order_processed(&processed_order);

    // Send confirmation email
    if let Err(e) = send_confirmation_email(customer_id, &processed_order) {
        // Log email failure but don't fail the order
        log_email_failure(customer_id, e);
    }

    // Update inventory
    for item in &items {
        if let Err(e) = update_inventory(item.product_id, item.quantity) {
            // This is critical - we need to handle inventory update failures
            log_inventory_update_failure(item.product_id, item.quantity, e);
            // In a real system, you might want to implement compensation logic
        }
    }

    Ok(processed_order)
}

// Supporting types and functions (simplified for demo)

#[derive(Debug, Clone)]
pub struct OrderItem {
    pub product_id: u64,
    pub quantity: u32,
    pub unit_price: f64,
    pub weight: f64,
    pub category: ProductCategory,
    pub requires_special_handling: bool,
    pub eligible_for_bogo: bool,
    pub value: f64,
}

#[derive(Debug, Clone)]
pub enum ProductCategory {
    Electronics,
    Books,
    Clothing,
    Home,
    Hazmat,
}

#[derive(Debug, Clone)]
pub enum PaymentMethod {
    CreditCard(CreditCard),
    PayPal(PayPalAccount),
    BankTransfer(BankDetails),
    Cryptocurrency(CryptoWallet),
}

#[derive(Debug, Clone)]
pub struct CreditCard {
    pub number: String,
    pub expiry: String,
    pub cvv: String,
    pub name: String,
}

#[derive(Debug, Clone)]
pub struct PayPalAccount {
    pub email: String,
}

#[derive(Debug, Clone)]
pub struct BankDetails {
    pub account_number: String,
    pub routing_number: String,
    pub bank_name: String,
}

#[derive(Debug, Clone)]
pub struct CryptoWallet {
    pub address: String,
    pub currency: String,
}

#[derive(Debug, Clone)]
pub struct Address {
    pub street: String,
    pub city: String,
    pub state: String,
    pub zip: String,
    pub country: String,
}

#[derive(Debug, Clone)]
pub enum CustomerTier {
    Basic,
    Premium,
    Enterprise,
}

#[derive(Debug)]
pub struct ProcessedOrder {
    pub order_id: u64,
    pub customer_id: u64,
    pub items: Vec<OrderItem>,
    pub subtotal: f64,
    pub tier_discount: f64,
    pub promo_discount: f64,
    pub tax_amount: f64,
    pub shipping_cost: f64,
    pub total: f64,
    pub payment_result: PaymentResult,
    pub estimated_delivery: String,
    pub tracking_number: String,
    pub special_instructions: Option<String>,
}

#[derive(Debug)]
pub enum OrderError {
    InvalidOrderId,
    InvalidCustomerId,
    EmptyCart,
    InvalidQuantity(u64),
    InsufficientStock { product_id: u64, requested: u32, available: u32 },
    OutOfStock(u64),
    ProductDiscontinued(u64),
    SpecialHandlingNotAllowed,
    VerificationRequired,
    PreApprovalRequired,
    PromoCodeExpired(String),
    InvalidPromoCode(String),
    PromoCodeAlreadyUsed(String),
    PromoMinimumNotMet { code: String, minimum: f64, current: f64 },
    AdditionalAuthRequired,
    PaymentDeclined,
    BankTransferMinimumNotMet,
    CryptoNotAllowedForBasicTier,
    ShippingError(String),
    TaxCalculationError(String),
    PaymentProcessingError(String),
}

// Simplified stub implementations
enum InventoryStatus { Available, LowStock(u32), OutOfStock, Discontinued }
enum PromoValidation { Valid(PromoDiscount), Expired, Invalid, AlreadyUsed, MinimumNotMet(f64) }
enum PromoDiscount { Percentage(f64), FixedAmount(f64), FreeShipping, BuyOneGetOne }
enum VerificationResult { Approved, RequiresAdditionalAuth, Declined }
#[derive(Debug)] struct PaymentResult { transaction_id: String, status: String }

fn check_inventory(_: u64, _: u32) -> InventoryStatus { InventoryStatus::Available }
fn verify_premium_customer(_: u64) -> bool { true }
fn has_enterprise_preapproval(_: u64, _: u64) -> bool { true }
fn is_end_of_season() -> bool { false }
fn is_holiday_season() -> bool { false }
fn validate_promo_code(_: &str, _: u64, _: &[OrderItem]) -> PromoValidation { PromoValidation::Valid(PromoDiscount::Percentage(10.0)) }
fn calculate_shipping_cost(_: &Address, _: f64, _: bool, _: CustomerTier, _: &[String]) -> Result<f64, OrderError> { Ok(9.99) }
fn get_tax_rate(_: &Address) -> Result<f64, OrderError> { Ok(0.0825) }
fn validate_credit_card(_: &CreditCard) -> Result<(), OrderError> { Ok(()) }
fn verify_high_value_transaction(_: u64, _: f64) -> VerificationResult { VerificationResult::Approved }
fn process_credit_card_payment(_: &CreditCard, _: f64) -> Result<PaymentResult, OrderError> { Ok(PaymentResult { transaction_id: "txn_123".to_string(), status: "approved".to_string() }) }
fn validate_paypal_account(_: &PayPalAccount) -> Result<(), OrderError> { Ok(()) }
fn process_paypal_payment(_: &PayPalAccount, _: f64) -> Result<PaymentResult, OrderError> { Ok(PaymentResult { transaction_id: "pp_123".to_string(), status: "approved".to_string() }) }
fn validate_bank_details(_: &BankDetails) -> Result<(), OrderError> { Ok(()) }
fn initiate_bank_transfer(_: &BankDetails, _: f64) -> Result<PaymentResult, OrderError> { Ok(PaymentResult { transaction_id: "bt_123".to_string(), status: "pending".to_string() }) }
fn validate_crypto_wallet(_: &CryptoWallet) -> Result<(), OrderError> { Ok(()) }
fn process_crypto_payment(_: &CryptoWallet, _: f64) -> Result<PaymentResult, OrderError> { Ok(PaymentResult { transaction_id: "crypto_123".to_string(), status: "confirmed".to_string() }) }
fn calculate_delivery_date(_: &Address, _: bool) -> String { "2024-01-15".to_string() }
fn generate_tracking_number() -> String { "TRK123456789".to_string() }
fn log_order_processed(_: &ProcessedOrder) {}
fn send_confirmation_email(_: u64, _: &ProcessedOrder) -> Result<(), String> { Ok(()) }
fn log_email_failure(_: u64, _: String) {}
fn update_inventory(_: u64, _: u32) -> Result<(), String> { Ok(()) }
fn log_inventory_update_failure(_: u64, _: u32, _: String) {}

/// Additional complex function with recursive calls for demo
pub fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => {
            if n < 20 {
                fibonacci(n - 1) + fibonacci(n - 2)
            } else {
                // Optimized version for larger numbers
                let mut a = 0;
                let mut b = 1;
                for _ in 2..=n {
                    let temp = a + b;
                    a = b;
                    b = temp;
                }
                b
            }
        }
    }
}

/// Async function example
pub async fn fetch_user_data(user_id: u64) -> Result<HashMap<String, String>, String> {
    // Simulated async work
    if user_id == 0 {
        return Err("Invalid user ID".to_string());
    }

    let mut user_data = HashMap::new();
    user_data.insert("id".to_string(), user_id.to_string());
    user_data.insert("name".to_string(), "Demo User".to_string());
    user_data.insert("email".to_string(), "demo@example.com".to_string());

    Ok(user_data)
}

fn main() {
    println!("This is a demo file to showcase CodeMetrics analysis capabilities.");
    println!("The process_order function has intentionally high complexity for demonstration.");
    println!("It includes:");
    println!("  - High cyclomatic complexity (many decision points)");
    println!("  - Deep nesting levels");
    println!("  - Many parameters (9 parameters)");
    println!("  - Complex business logic");
    println!("  - Error handling");
    println!("  - Multiple enum pattern matching");
    println!("");
    println!("This would be flagged by CodeMetrics as needing refactoring!");
}