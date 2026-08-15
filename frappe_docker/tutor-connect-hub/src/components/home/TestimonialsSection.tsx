import { Star } from "lucide-react";

const testimonials = [
  {
    name: "Adebayo M.",
    role: "Student, SS3",
    text: "My math grades went from C to A in just two months. The tutors here really know how to explain complex topics in simple terms.",
    rating: 5,
  },
  {
    name: "Chioma E.",
    role: "Parent",
    text: "I love how easy it is to track my daughter's progress. The scheduling is flexible and the tutors are very professional.",
    rating: 5,
  },
  {
    name: "Dr. Fatima A.",
    role: "Tutor, Chemistry",
    text: "Teaching through TutorConnect has been amazing. The platform handles payments seamlessly so I can focus on what I love — teaching.",
    rating: 5,
  },
];

export function TestimonialsSection() {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground">What Our Users Say</h2>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            Join thousands of satisfied students and tutors on the TutorConnect platform.
          </p>
        </div>

        <div className="mt-12 grid gap-8 md:grid-cols-3">
          {testimonials.map((t) => (
            <div
              key={t.name}
              className="rounded-xl border border-border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex gap-1 mb-4">
                {Array.from({ length: t.rating }).map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" />
                ))}
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">"{t.text}"</p>
              <div className="mt-5 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-sm font-medium text-primary-700">
                  {t.name[0]}
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
