"""Thin wrapper around the Stripe API for Tutor Hub.

All Stripe operations go through this module so the rest of the codebase
never imports stripe directly. Configuration is pulled from
Marketplace Settings (stripe_secret_key, stripe_webhook_endpoint_secret).

Requires `stripe` in requirements — add to pyproject.toml / requirements.txt.
"""

import frappe
import stripe


def _get_client() -> stripe.Stripe:
    """Return a configured Stripe client using the secret key from settings."""
    settings = frappe.get_single("Marketplace Settings")
    secret_key = settings.stripe_secret_key
    if not secret_key:
        frappe.throw("Stripe Secret Key is not configured in Marketplace Settings.")
    stripe.api_key = secret_key
    return stripe


def create_checkout_session(
    amount: int,
    currency: str,
    metadata: dict,
    success_url: str,
    cancel_url: str,
    connected_account_id: str | None = None,
) -> stripe.checkout.Session:
    """Create a Stripe Checkout Session.

    Args:
        amount: Amount in the smallest currency unit (e.g. kobo for NGN).
        currency: Three-letter ISO currency code.
        metadata: Arbitrary key-value pairs attached to the session.
        success_url: Redirect URL after successful payment.
        cancel_url: Redirect URL if the customer cancels.
        connected_account_id: Tutor's Stripe Connect account ID (for destination charges).

    Returns:
        The created Stripe Checkout Session object.
    """
    client = _get_client()

    session_params = {
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price_data": {
                    "currency": currency,
                    "unit_amount": amount,
                    "product_data": {
                        "name": metadata.get("session_title", "Tutoring Session"),
                    },
                },
                "quantity": 1,
            }
        ],
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": metadata,
    }

    if connected_account_id:
        session_params["payment_intent_data"] = {
            "transfer_data": {
                "destination": connected_account_id,
            },
        }

    return client.checkout.Session.create(**session_params)


def create_transfer(
    amount: int,
    currency: str,
    destination: str,
    metadata: dict | None = None,
) -> stripe.Transfer:
    """Create a Stripe Transfer to a connected account.

    Used for post-payment payouts when not using destination charges.

    Args:
        amount: Amount in the smallest currency unit.
        currency: Three-letter ISO currency code.
        destination: Stripe Connect account ID of the tutor.
        metadata: Optional key-value pairs.

    Returns:
        The created Stripe Transfer object.
    """
    client = _get_client()
    params = {
        "amount": amount,
        "currency": currency,
        "destination": destination,
    }
    if metadata:
        params["metadata"] = metadata
    return client.Transfer.create(**params)


def verify_webhook_signature(payload: bytes, sig_header: str, secret: str) -> stripe.Event:
    """Verify a Stripe webhook signature and return the parsed event.

    Args:
        payload: Raw request body bytes.
        sig_header: The Stripe-Signature header value.
        secret: The webhook endpoint signing secret.

    Returns:
        The verified Stripe Event object.

    Raises:
        stripe.SignatureVerificationError: If verification fails.
    """
    return stripe.Webhook.construct_event(payload, sig_header, secret)
