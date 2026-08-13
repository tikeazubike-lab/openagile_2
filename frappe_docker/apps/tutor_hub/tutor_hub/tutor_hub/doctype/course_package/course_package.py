import frappe
from frappe.model.document import Document


class CoursePackage(Document):
    def validate(self):
        if self.original_price and self.discounted_price and self.original_price > 0:
            discount = ((self.original_price - self.discounted_price) / self.original_price) * 100
            self.discount_percentage = round(discount, 1)
