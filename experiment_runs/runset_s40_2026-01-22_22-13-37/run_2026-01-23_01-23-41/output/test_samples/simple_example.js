// Simple JavaScript example
function calculateTax(price, taxRate) {
    return price * taxRate;
}

function processOrder(items, customer) {
    let total = 0;

    for (const item of items) {
        if (item.price > 0) {
            total += item.price;
        }
    }

    if (customer.isPremium) {
        total *= 0.9; // 10% discount
    }

    const tax = calculateTax(total, 0.08);
    return total + tax;
}

// More complex function with nested conditions
function validatePayment(paymentInfo) {
    if (!paymentInfo) {
        throw new Error('Payment info required');
    }

    if (paymentInfo.type === 'credit') {
        if (!paymentInfo.cardNumber) {
            return false;
        }
        if (paymentInfo.cardNumber.length < 13) {
            return false;
        }
        if (!paymentInfo.expiryDate) {
            return false;
        }
    } else if (paymentInfo.type === 'debit') {
        if (!paymentInfo.accountNumber) {
            return false;
        }
    } else if (paymentInfo.type === 'paypal') {
        if (!paymentInfo.email) {
            return false;
        }
    } else {
        return false;
    }

    return true;
}