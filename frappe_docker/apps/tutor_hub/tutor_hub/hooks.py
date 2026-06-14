app_name = "tutor_hub"
app_title = "Tutor Hub"
app_publisher = "zubbyik"
app_description = "Nigeria's #1 Tutoring Platform — Connect with top tutors"
app_email = "mack@zubbystudio.shop"
app_license = "mit"
app_version = "0.0.1"

# Registers /landing as a Frappe web page served from www/landing.html
website_route_rules = [
	{"from_route": "/landing", "to_route": "landing"},
]

# No global CSS/JS injection — React handles everything
app_include_css = []
app_include_js = []
