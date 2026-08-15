"""Stripe Connect webhook handler for Tutor Hub.

Stripe webhooks are AUTHORITATIVE — the browser is never the source of truth
for payment state. Every processed event gets a unique persisted identifier
for idempotency. Every financial state transition creates an immutable
Payment Audit Event record.

Reference: HO-108 (ChatGPT architecture review)
"""

import json
import traceback

import frappe

from tutor_hub.tutor_hub.stripe_client import verify_webhook_signature


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def is_event_processed(stripe_event_id: str) -> bool:
    """Return True if we have already created an audit record for this event."""
    return frappe.db.exists(
        "Payment Audit Event",
        {"stripe_event_id": stripe_event_id},
    )


# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------

def create_audit_event(
    payment_transaction: str,
    event_type: str,
    previous_state: str | None = None,
    new_state: str | None = None,
    amount: float | None = None,
    currency: str | None = None,
    stripe_event_id: str | None = None,
    actor_type: str = "Webhook",
    actor_id: str | None = None,
    reason: str | None = None,
    metadata: dict | None = None,
) -> str:
    """Create an immutable Payment Audit Event record.

    Audit events are append-only (write permission = create only, no edit).
    Returns the name of the newly created document.
    """
    doc = frappe.get_doc(
        {
            "doctype": "Payment Audit Event",
            "payment_transaction": payment_transaction,
            "event_type": event_type,
            "previous_state": previous_state,
            "new_state": new_state,
            "amount": amount,
            "currency": currency,
            "stripe_event_id": stripe_event_id,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "reason": reason,
            "metadata": json.dumps(metadata) if metadata else None,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------

def verify_and_parse_event(payload: bytes, sig_header: str) -> dict:
    """Verify the Stripe webhook signature and return the parsed event dict.

    Reads the endpoint secret from Marketplace Settings.
    Raises frappe.throw on verification failure.
    """
    settings = frappe.get_single("Marketplace Settings")
    secret = settings.stripe_webhook_endpoint_secret
    if not secret:
        frappe.throw("Stripe Webhook Endpoint Secret is not configured.")

    try:
        event = verify_webhook_signature(payload, sig_header, secret)
    except Exception:
        frappe.log_error(
            title="Stripe Webhook Signature Verification Failed",
            message=traceback.format_exc(),
        )
        frappe.throw("Invalid webhook signature.", frappe.AuthenticationError)

    return event


# ---------------------------------------------------------------------------
# Event processors
# ---------------------------------------------------------------------------

def process_payment_succeeded(event: dict) -> None:
    """Handle payment_intent.succeeded — update Payment Transaction to Succeeded."""
    pi = event["data"]["object"]
    pi_id = pi["id"]

    txn_name = frappe.db.get_value(
        "Payment Transaction",
        {"payment_intent_id": pi_id},
        "name",
    )
    if not txn_name:
        frappe.log_error(
            title="Stripe Webhook: Payment Transaction Not Found",
            message=f"No Payment Transaction with payment_intent_id={pi_id}",
        )
        return

    txn = frappe.get_doc("Payment Transaction", txn_name)
    previous_status = txn.payment_status

    charge_id = None
    latest_charge = pi.get("latest_charge")
    if latest_charge:
        charge_id = latest_charge if isinstance(latest_charge, str) else latest_charge.get("id")

    txn.payment_status = "Succeeded"
    txn.charge_id = txn.charge_id or charge_id
    txn.save(ignore_permissions=True)

    create_audit_event(
        payment_transaction=txn_name,
        event_type="PAYMENT_SUCCEEDED",
        previous_state=previous_status,
        new_state="Succeeded",
        amount=txn.gross_amount,
        currency=txn.currency,
        stripe_event_id=event["id"],
        actor_type="Webhook",
        actor_id=pi_id,
    )

    frappe.db.commit()


def process_payment_failed(event: dict) -> None:
    """Handle payment_intent.payment_failed — update Payment Transaction to Failed."""
    pi = event["data"]["object"]
    pi_id = pi["id"]

    txn_name = frappe.db.get_value(
        "Payment Transaction",
        {"payment_intent_id": pi_id},
        "name",
    )
    if not txn_name:
        frappe.log_error(
            title="Stripe Webhook: Payment Transaction Not Found",
            message=f"No Payment Transaction with payment_intent_id={pi_id}",
        )
        return

    txn = frappe.get_doc("Payment Transaction", txn_name)
    previous_status = txn.payment_status

    failure_message = None
    last_payment_error = pi.get("last_payment_error")
    if last_payment_error:
        failure_message = last_payment_error.get("message")

    txn.payment_status = "Failed"
    txn.save(ignore_permissions=True)

    create_audit_event(
        payment_transaction=txn_name,
        event_type="PAYMENT_FAILED",
        previous_state=previous_status,
        new_state="Failed",
        amount=txn.gross_amount,
        currency=txn.currency,
        stripe_event_id=event["id"],
        actor_type="Webhook",
        actor_id=pi_id,
        reason=failure_message,
    )

    frappe.db.commit()


def process_transfer_created(event: dict) -> None:
    """Handle transfer.created — update payout status to Transfer Pending."""
    transfer = event["data"]["object"]
    transfer_id = transfer["id"]
    pi_id = transfer.get("source_transaction") or transfer.get("metadata", {}).get(
        "payment_intent_id"
    )

    txn_name = None
    if pi_id:
        txn_name = frappe.db.get_value(
            "Payment Transaction",
            {"payment_intent_id": pi_id},
            "name",
        )
    if not txn_name:
        txn_name = frappe.db.get_value(
            "Payment Transaction",
            {"transfer_id": transfer_id},
            "name",
        )
    if not txn_name:
        frappe.log_error(
            title="Stripe Webhook: Transfer Transaction Not Found",
            message=f"No Payment Transaction for transfer {transfer_id}, source={pi_id}",
        )
        return

    txn = frappe.get_doc("Payment Transaction", txn_name)
    previous_payout = txn.payout_status

    txn.transfer_id = transfer_id
    txn.payout_status = "Transfer Pending"
    txn.save(ignore_permissions=True)

    create_audit_event(
        payment_transaction=txn_name,
        event_type="TRANSFER_CREATED",
        previous_state=previous_payout,
        new_state="Transfer Pending",
        amount=transfer["amount"] / 100,
        currency=transfer["currency"].upper(),
        stripe_event_id=event["id"],
        actor_type="Webhook",
        actor_id=transfer_id,
    )

    frappe.db.commit()


def process_transfer_paid(event: dict) -> None:
    """Handle transfer.paid — update payout status to Paid Out."""
    transfer = event["data"]["object"]
    transfer_id = transfer["id"]

    txn_name = frappe.db.get_value(
        "Payment Transaction",
        {"transfer_id": transfer_id},
        "name",
    )
    if not txn_name:
        frappe.log_error(
            title="Stripe Webhook: Transfer Transaction Not Found",
            message=f"No Payment Transaction with transfer_id={transfer_id}",
        )
        return

    txn = frappe.get_doc("Payment Transaction", txn_name)
    previous_payout = txn.payout_status

    payout_id = None
    payout = transfer.get("payout")
    if payout:
        payout_id = payout if isinstance(payout, str) else payout.get("id")

    txn.payout_status = "Paid Out"
    txn.payout_id = txn.payout_id or payout_id
    txn.save(ignore_permissions=True)

    create_audit_event(
        payment_transaction=txn_name,
        event_type="TRANSFER_SUCCEEDED",
        previous_state=previous_payout,
        new_state="Paid Out",
        amount=transfer["amount"] / 100,
        currency=transfer["currency"].upper(),
        stripe_event_id=event["id"],
        actor_type="Webhook",
        actor_id=transfer_id,
    )

    frappe.db.commit()


def process_refund(event: dict) -> None:
    """Handle charge.refunded — update refund status and amount."""
    charge = event["data"]["object"]
    charge_id = charge["id"]
    refund_amount = charge.get("amount_refunded", 0) / 100

    txn_name = frappe.db.get_value(
        "Payment Transaction",
        {"charge_id": charge_id},
        "name",
    )
    if not txn_name:
        frappe.log_error(
            title="Stripe Webhook: Refund Transaction Not Found",
            message=f"No Payment Transaction with charge_id={charge_id}",
        )
        return

    txn = frappe.get_doc("Payment Transaction", txn_name)
    previous_refund = txn.refund_status

    is_full_refund = charge.get("refunded", False)
    txn.refund_status = "Succeeded" if is_full_refund else "Requested"
    txn.refunded_amount = refund_amount
    txn.save(ignore_permissions=True)

    event_type = "REFUND_SUCCEEDED" if is_full_refund else "REFUND_REQUESTED"

    reason = None
    refunds = charge.get("refunds", {}).get("data", [])
    if refunds:
        reason = refunds[0].get("reason")

    create_audit_event(
        payment_transaction=txn_name,
        event_type=event_type,
        previous_state=previous_refund,
        new_state=txn.refund_status,
        amount=refund_amount,
        currency=txn.currency,
        stripe_event_id=event["id"],
        actor_type="Webhook",
        actor_id=charge_id,
        reason=reason,
    )

    frappe.db.commit()


def process_dispute(event: dict) -> None:
    """Handle charge.dispute.created — update dispute status."""
    dispute = event["data"]["object"]
    charge_id = dispute.get("charge")

    txn_name = frappe.db.get_value(
        "Payment Transaction",
        {"charge_id": charge_id},
        "name",
    )
    if not txn_name:
        frappe.log_error(
            title="Stripe Webhook: Dispute Transaction Not Found",
            message=f"No Payment Transaction with charge_id={charge_id}",
        )
        return

    txn = frappe.get_doc("Payment Transaction", txn_name)
    previous_dispute = txn.dispute_status

    txn.dispute_status = "Opened"
    txn.save(ignore_permissions=True)

    create_audit_event(
        payment_transaction=txn_name,
        event_type="DISPUTE_OPENED",
        previous_state=previous_dispute,
        new_state="Opened",
        amount=dispute.get("amount", 0) / 100,
        currency=dispute.get("currency", "ngn").upper(),
        stripe_event_id=event["id"],
        actor_type="Webhook",
        actor_id=charge_id,
        reason=dispute.get("reason"),
    )

    frappe.db.commit()


# ---------------------------------------------------------------------------
# Main webhook handler (called from api.py)
# ---------------------------------------------------------------------------

EVENT_PROCESSORS = {
    "payment_intent.succeeded": process_payment_succeeded,
    "payment_intent.payment_failed": process_payment_failed,
    "transfer.created": process_transfer_created,
    "transfer.paid": process_transfer_paid,
    "charge.refunded": process_refund,
    "charge.dispute.created": process_dispute,
}


def handle_stripe_webhook(payload: bytes, sig_header: str) -> dict:
    """Entry point for Stripe webhook processing.

    Args:
        payload: Raw request body bytes.
        sig_header: Stripe-Signature header value.

    Returns:
        dict with status and message.
    """
    event = verify_and_parse_event(payload, sig_header)
    event_type = event["type"]
    stripe_event_id = event["id"]

    # Idempotency: skip if already processed
    if is_event_processed(stripe_event_id):
        return {"status": "ok", "message": f"Event {stripe_event_id} already processed."}

    processor = EVENT_PROCESSORS.get(event_type)
    if processor:
        processor(event)
        return {"status": "ok", "message": f"Processed {event_type} ({stripe_event_id})."}

    # Unhandled event type — acknowledge receipt to avoid Stripe retries
    frappe.logger().info(f"Stripe webhook: unhandled event type '{event_type}' — skipping.")
    return {"status": "ok", "message": f"Unhandled event type: {event_type}."}
