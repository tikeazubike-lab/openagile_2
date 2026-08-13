import frappe
from frappe.model.document import Document


class TutorProfile(Document):
    def validate(self):
        self.validate_availability()

    def validate_availability(self):
        if not self.availability:
            return
        days = [a.day_of_week for a in self.availability]
        if len(days) != len(set(days)):
            frappe.throw("Duplicate availability entries for the same day are not allowed.")
