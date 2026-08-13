import frappe
from frappe.model.document import Document


class SessionSchedule(Document):
    def validate(self):
        self.calculate_duration()
        self.validate_status_transition()

    def calculate_duration(self):
        if self.scheduled_start_at_utc and self.scheduled_end_at_utc:
            diff = self.scheduled_end_at_utc - self.scheduled_start_at_utc
            self.duration_minutes = int(diff.total_seconds() / 60)

    def validate_status_transition(self):
        if not self.has_value_changed("status"):
            return
        allowed_transitions = {
            "Scheduled": ["In Progress", "Cancelled"],
            "In Progress": ["Attendance Review", "Cancelled", "No Show"],
            "Attendance Review": ["Completed", "Disputed"],
            "Completed": ["Payout Eligible"],
            "Disputed": ["Completed", "Cancelled"],
        }
        old_status = self.get_doc_before_save()
        if old_status and old_status.status in allowed_transitions:
            if self.status not in allowed_transitions[old_status.status]:
                frappe.throw(
                    f"Cannot transition from '{old_status.status}' to '{self.status}'. "
                    f"Allowed: {', '.join(allowed_transitions[old_status.status])}"
                )
