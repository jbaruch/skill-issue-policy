"""Payment processing module."""


def process_payment(amount: float, currency: str = "USD") -> dict:
    """Process a payment and return a result dict.

    Args:
        amount: The payment amount (must be positive).
        currency: ISO 4217 currency code.

    Returns:
        dict with keys: success (bool), amount, currency, message
    """
    if amount < 0:
        return {
            "success": False,
            "amount": amount,
            "currency": currency,
            "message": "Amount must be non-negative",
        }

    # TODO: integrate with payment gateway
    return {
        "success": True,
        "amount": amount,
        "currency": currency,
        "message": "Payment processed",
    }
