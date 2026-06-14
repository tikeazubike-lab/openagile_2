import frappe


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
