import frappe

@frappe.whitelist(allow_guest=True)
def get_landing_page_data():
    """
    Fetch data for the landing page hero section.
    In the future, this can fetch from a specific DocType (e.g., 'Edu Theme Settings').
    """
    return {
        "hero_title": "Empowering Minds<br/>Shaping <span class='text-brand-yellow underline decoration-wavy underline-offset-8'>Tomorrow</span>",
        "hero_subtitle": "Welcome to the OpenAgile Education Portal. Manage your curriculum, track progress, and access world-class resources through our unified digital campus.",
        "cta_text": "Get Started Now",
        "cta_link": "/login",
        "featured_courses": [
            {
                "title": "Computer Science 101",
                "instructor": "Dr. Alan Turing",
                "description": "Introduction to algorithms, data structures, and the fundamentals of computing.",
                "level": "Beginner",
                "image": "https://placehold.co/600x400/CBDEFF/1F2937?text=Computer+Science"
            },
            {
                "title": "Advanced Mathematics",
                "instructor": "Prof. Ada Lovelace",
                "description": "Deep dive into calculus, linear algebra, and complex numbers.",
                "level": "Advanced",
                "image": "https://placehold.co/600x400/FDE047/1F2937?text=Mathematics"
            },
            {
                "title": "Digital Art & Design",
                "instructor": "Ms. Frida Kahlo",
                "description": "Explore the intersection of technology and creativity using modern tools.",
                "level": "Intermediate",
                "image": "https://placehold.co/600x400/E0F2FE/1F2937?text=Digital+Art"
            }
        ]
    }
