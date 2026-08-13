import frappe
from frappe.model.document import Document


class PaymentTransaction(Document):
    def validate(self):
        self.calculate_amounts()

    def calculate_amounts(self):
        settings = frappe.get_single("Marketplace Settings")
        fee_pct = settings.platform_fee_percentage or 15
        self.platform_fee = self.gross_amount * (fee_pct / 100)
        self.tutor_amount = self.gross_amount - self.platform_fee - self.stripe_fee

    def before_insert(self):
        self.payment_status = "Created"

    def on_update(self):
        self.create_audit_event("PAYMENT_CREATED")

    def create_audit_event(self, event_type):
        frappe.get_doc({
            "doctype": "Payment Audit Event",
            "payment_transaction": self.name,
            "event_type": event_type,
            "previous_state": self.get_doc_before_save().payment_status if self.get_doc_before_save() else None,
            "new_state": self.payment_status,
            "amount": self.gross_amount,
            "currency": self.currency,
            "actor_type": "System",
        }).insert(ignore_permissions=True)
