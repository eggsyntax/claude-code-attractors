// Complex JavaScript function for testing our analyzer
function calculateOrderTotal(cart, customerType, promoCode) {
    let total = 0;
    let discount = 0;

    // Iterate through cart items
    for (let item of cart.items) {
        if (item.price > 0 && item.quantity > 0) {
            let itemTotal = item.price * item.quantity;

            // Apply item-specific discounts
            if (item.category === 'electronics') {
                if (item.price > 500) {
                    itemTotal *= 0.95; // 5% discount for expensive electronics
                } else if (item.price > 100) {
                    itemTotal *= 0.98; // 2% discount for moderate electronics
                }
            } else if (item.category === 'books') {
                if (item.quantity >= 3) {
                    itemTotal *= 0.9; // 10% discount for 3+ books
                }
            }

            total += itemTotal;
        }
    }

    // Apply customer type discounts
    if (customerType === 'premium') {
        discount = total * 0.1;
    } else if (customerType === 'gold') {
        discount = total * 0.15;
    } else if (customerType === 'member') {
        discount = total * 0.05;
    }

    // Apply promo code discounts
    if (promoCode) {
        switch (promoCode.toLowerCase()) {
            case 'save10':
                discount += total * 0.1;
                break;
            case 'save20':
                discount += total * 0.2;
                break;
            case 'freeship':
                // Free shipping doesn't affect total, just a flag
                break;
            default:
                console.warn('Invalid promo code:', promoCode);
        }
    }

    const finalTotal = Math.max(0, total - discount);

    // Complex nested validation
    if (finalTotal > 1000) {
        if (customerType === 'new') {
            // New customer protection for large orders
            if (!confirmLargeOrder(finalTotal)) {
                throw new Error('Large order not confirmed');
            }
        }
    }

    return {
        subtotal: total,
        discount: discount,
        total: finalTotal,
        shipping: calculateShipping(finalTotal, customerType),
        tax: calculateTax(finalTotal)
    };
}

async function confirmLargeOrder(amount) {
    // Simulate async confirmation
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(amount < 5000); // Auto-approve under $5000
        }, 100);
    });
}

function calculateShipping(total, customerType) {
    if (customerType === 'premium' || customerType === 'gold') {
        return 0; // Free shipping for premium customers
    }

    if (total > 50) {
        return 0; // Free shipping for orders over $50
    }

    return 9.99;
}

function calculateTax(total) {
    const TAX_RATE = 0.0825; // 8.25%
    return total * TAX_RATE;
}