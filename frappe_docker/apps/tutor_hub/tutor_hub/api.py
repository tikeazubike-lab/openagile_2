import frappe
from frappe import _
from datetime import datetime

from tutor_hub.tutor_hub.payments import handle_stripe_webhook
from tutor_hub.tutor_hub.stripe_client import create_checkout_session as _create_checkout_session


# ---------------------------------------------------------------------------
# Stripe Webhook Endpoint
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True, csrf=False, methods=["POST"])
def stripe_webhook():
	"""Receive and process Stripe webhook events.

	Stripe doesn't send CSRF tokens, so csrf=False is required.
	Signature verification happens inside handle_stripe_webhook.

	Webhook URL: https://tutor.zubbystudio.site/api/method/tutor_hub.tutor_hub.api.stripe_webhook
	"""
	payload = frappe.request.get_data()
	sig_header = frappe.request.headers.get("Stripe-Signature", "")

	try:
		result = handle_stripe_webhook(payload, sig_header)
		frappe.response["http_status_code"] = 200
		return result
	except Exception:
		frappe.log_error(title="Stripe Webhook Error", message=frappe.get_traceback())
		frappe.response["http_status_code"] = 400
		return {"status": "error", "message": "Webhook processing failed."}


# ---------------------------------------------------------------------------
# Checkout Session Creator
# ---------------------------------------------------------------------------

@frappe.whitelist()
def create_checkout_session(session_name: str):
	"""Create a Stripe Checkout Session for a student's booking.

	Args:
		session_name: The name (ID) of a Session Schedule document.

	Returns:
		dict with checkout_url and session_id.
	"""
	session_doc = frappe.get_doc("Session Schedule", session_name)

	# Permission check: only the booked student or an admin can initiate payment
	if frappe.session.user != "Administrator" and not frappe.has_role("System Manager"):
		student_user = frappe.db.get_value("Student Profile", session_doc.student, "user")
		if student_user != frappe.session.user:
			frappe.throw(_("You do not have permission to pay for this session."))

	tutor_profile = frappe.get_doc("Tutor Profile", session_doc.tutor)
	connected_account_id = tutor_profile.stripe_account_id

	settings = frappe.get_single("Marketplace Settings")
	amount = int(session_doc.price * 100)  # Convert to smallest currency unit

	site_url = frappe.utils.get_url()
	metadata = {
		"session_name": session_name,
		"session_title": session_doc.session_title or f"Tutoring: {session_doc.subject}",
		"student": session_doc.student,
		"tutor": session_doc.tutor,
		"payment_type": "session",
	}

	checkout = _create_checkout_session(
		amount=amount,
		currency=session_doc.currency or settings.currency or "NGN",
		metadata=metadata,
		success_url=f"{site_url}/tutor_hub/payment-success?session_id={session_name}",
		cancel_url=f"{site_url}/tutor_hub/payment-cancel?session_id={session_name}",
		connected_account_id=connected_account_id or None,
	)

	# Create Payment Transaction record
	txn = frappe.get_doc(
		{
			"doctype": "Payment Transaction",
			"session": session_name,
			"student": session_doc.student,
			"tutor": session_doc.tutor,
			"currency": session_doc.currency or "NGN",
			"gross_amount": session_doc.price,
			"payment_status": "Pending",
			"payment_intent_id": checkout.payment_intent,
		}
	)
	txn.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"checkout_url": checkout.url,
		"session_id": checkout.id,
		"payment_transaction": txn.name,
	}


# ---------------------------------------------------------------------------
# Book Session (Atomic Slot Reservation)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def book_session(
	tutor: str,
	student: str,
	subject: str,
	start_time: str,
	end_time: str,
	timezone: str = "Africa/Lagos",
):
	"""Book a tutoring session with atomic slot reservation.

	Creates a Session Schedule and a pending Payment Transaction in a
	single database transaction to prevent double-booking.

	Args:
		tutor: Tutor Profile name.
		student: Student Profile name.
		subject: Subject name.
		start_time: ISO 8601 datetime string (e.g. '2026-08-20T14:00:00').
		end_time: ISO 8601 datetime string.
		timezone: Student's timezone (default Africa/Lagos).

	Returns:
		dict with session_name, checkout_url.
	"""
	# Parse datetimes
	start_dt = datetime.fromisoformat(start_time)
	end_dt = datetime.fromisoformat(end_time)

	if end_dt <= start_dt:
		frappe.throw(_("End time must be after start time."))

	# Validate tutor exists and is active
	tutor_doc = frappe.get_doc("Tutor Profile", tutor)
	if tutor_doc.status != "Active":
		frappe.throw(_("This tutor is not currently accepting bookings."))

	# Atomic: check for overlapping slots then insert within same commit scope
	# Frappe's ORM doesn't support SELECT FOR UPDATE natively, so we use
	# a direct SQL query with FOR UPDATE to lock the row range.
	overlap = frappe.db.sql(
		"""
		SELECT name FROM `tabSession Schedule`
		WHERE tutor = %s
		  AND status NOT IN ('Cancelled', 'No Show')
		  AND scheduled_start_at_utc < %s
		  AND scheduled_end_at_utc > %s
		FOR UPDATE
		""",
		(tutor, end_dt, start_dt),
	)

	if overlap:
		frappe.throw(
			_("Tutor is not available at the selected time. Conflicting session: {0}").format(
				overlap[0][0]
			)
		)

	# Create Session Schedule
	session_doc = frappe.get_doc(
		{
			"doctype": "Session Schedule",
			"tutor": tutor,
			"student": student,
			"subject": subject,
			"scheduled_start_at_utc": start_dt,
			"scheduled_end_at_utc": end_dt,
			"tutor_timezone": tutor_doc.get("timezone") or "Africa/Lagos",
			"student_timezone": timezone,
			"status": "Scheduled",
			"price": tutor_doc.hourly_rate,
			"currency": tutor_doc.currency or "NGN",
			"session_type": "1-on-1",
		}
	)
	session_doc.insert(ignore_permissions=True)

	# Create Stripe Checkout Session
	site_url = frappe.utils.get_url()
	settings = frappe.get_single("Marketplace Settings")
	amount = int(session_doc.price * 100)

	metadata = {
		"session_name": session_doc.name,
		"session_title": session_doc.session_title
		or f"Tutoring: {subject}",
		"student": student,
		"tutor": tutor,
		"payment_type": "session",
	}

	connected_account_id = tutor_doc.stripe_account_id

	checkout = _create_checkout_session(
		amount=amount,
		currency=session_doc.currency or settings.currency or "NGN",
		metadata=metadata,
		success_url=f"{site_url}/tutor_hub/payment-success?session_id={session_doc.name}",
		cancel_url=f"{site_url}/tutor_hub/payment-cancel?session_id={session_doc.name}",
		connected_account_id=connected_account_id or None,
	)

	# Create Payment Transaction
	txn = frappe.get_doc(
		{
			"doctype": "Payment Transaction",
			"session": session_doc.name,
			"student": student,
			"tutor": tutor,
			"currency": session_doc.currency or "NGN",
			"gross_amount": session_doc.price,
			"payment_status": "Pending",
			"payment_intent_id": checkout.payment_intent,
		}
	)
	txn.insert(ignore_permissions=True)

	frappe.db.commit()

	return {
		"session_name": session_doc.name,
		"checkout_url": checkout.url,
		"payment_transaction": txn.name,
	}


@frappe.whitelist(allow_guest=True)
def get_landing_page_data():
	"""
	Returns all content for the tutor_hub landing page.

	Image paths are absolute URLs resolved via Frappe's /assets/ static file serving.
	The volume mount in compose.frontend-custom-apps.yaml maps:
	  ./apps/tutor_hub/tutor_hub/public  →  /assets/tutor_hub/

	Future: replace static dicts with DocType queries once Tutor/Subject DocTypes are populated.
	"""
	base_img = "/assets/tutor_hub/images"

	return {
		"hero_title": "Your Child's Success Starts Here",
		"hero_subtitle": (
			"Connect with Nigeria's top-rated tutors for personalized 1-on-1 sessions. "
			"JAMB prep, primary school, secondary school, and beyond."
		),
		"cta_primary": {"text": "Find a Tutor", "href": "#tutors"},
		"cta_secondary": {"text": "How It Works", "href": "#how-it-works"},
		"stats": [
			{"label": "Students", "value": "50k+"},
			{"label": "Tutors", "value": "2,000+"},
			{"label": "Rating", "value": "4.9★"},
		],
		"subjects": [
			{"name": "Mathematics", "icon": "calculator"},
			{"name": "English", "icon": "book-open"},
			{"name": "Physics", "icon": "atom"},
			{"name": "Chemistry", "icon": "flask-conical"},
			{"name": "Biology", "icon": "leaf"},
			{"name": "Computer Science", "icon": "monitor"},
			{"name": "Music", "icon": "music"},
			{"name": "Business Studies", "icon": "briefcase"},
		],
		"featured_tutors": [
			{
				"name": "Adaeze Okonkwo",
				"subjects": ["Mathematics", "Physics"],
				"rate_naira": 6000,
				"bio": "10+ years teaching JAMB and WAEC candidates across Lagos.",
				"rating": 4.9,
				"image": f"{base_img}/tutor-1.jpg",
			},
			{
				"name": "Emeka Adekunle",
				"subjects": ["English", "Literature"],
				"rate_naira": 5500,
				"bio": "University of Ibadan graduate. Specialises in essay writing and comprehension.",
				"rating": 4.8,
				"image": f"{base_img}/tutor-2.jpg",
			},
			{
				"name": "Ngozi Amadi",
				"subjects": ["Chemistry", "Biology"],
				"rate_naira": 5000,
				"bio": "BSc Biochemistry, UNIPORT. Makes science accessible for secondary students.",
				"rating": 4.9,
				"image": f"{base_img}/tutor-3.jpg",
			},
			{
				"name": "Chinedu Okoro",
				"subjects": ["Computer Science", "Mathematics"],
				"rate_naira": 6000,
				"bio": "Software engineer by day, passionate educator. Coding bootcamps and JAMB prep.",
				"rating": 5.0,
				"image": f"{base_img}/tutor-4.jpg",
			},
		],
		"how_it_works": [
			{
				"step": 1,
				"title": "Search",
				"description": "Browse verified tutors by subject, location, or availability.",
			},
			{
				"step": 2,
				"title": "Book",
				"description": "Schedule a session at a time that works for you. Pay securely online.",
			},
			{
				"step": 3,
				"title": "Learn",
				"description": "Meet your tutor for focused 1-on-1 sessions and track your child's progress.",
			},
		],
		"testimonials": [
			{
				"name": "Mrs. Funke Adeleke",
				"role": "Parent, Lagos",
				"text": "My son went from a C to an A in Mathematics in just 3 months. The tutors here are exceptional.",
				"rating": 5,
			},
			{
				"name": "Tunde Balogun",
				"role": "JAMB Candidate, 2025",
				"text": "I scored 312 in JAMB after sessions with Adaeze. Could not have done it without TutorHub.",
				"rating": 5,
			},
			{
				"name": "Mrs. Chioma Obi",
				"role": "Parent, Abuja",
				"text": "Flexible scheduling made it possible for my daughter to study around her school timetable.",
				"rating": 4,
			},
		],
	}
