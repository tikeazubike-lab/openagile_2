import { Star, Quote } from "lucide-react";

const testimonials = [
  {
    name: "Adebayo M.",
    role: "Student, SS3",
    text: "My math grades went from C to A in just two months. The tutors here really know how to explain complex topics in simple terms.",
    rating: 5,
    bg: "bg-accent-yellow-light",
  },
  {
    name: "Chioma E.",
    role: "Parent",
    text: "I love how easy it is to track my daughter's progress. The scheduling is flexible and the tutors are very professional.",
    rating: 5,
    bg: "bg-accent-pink-light",
  },
  {
    name: "Dr. Fatima A.",
    role: "Tutor, Chemistry",
    text: "Teaching through TutorConnect has been amazing. The platform handles payments seamlessly so I can focus on what I love — teaching.",
    rating: 5,
    bg: "bg-accent-mint-light",
  },
];

export function TestimonialsSection() {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <span className="inline-flex items-center rounded-full bg-primary-100 px-4 py-1.5 text-sm font-extrabold text-primary-700 mb-4">
            Testimonials
          </span>
          <h2 className="text-3xl font-extrabold text-foreground sm:text-4xl">
            What Our Users Say
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Join thousands of satisfied students and tutors on the TutorConnect platform.
          </p>
        </div>

        <div className="mt-14 grid gap-8 md:grid-cols-3">
          {testimonials.map((t) => (
            <div
              key={t.name}
              className={`relative rounded-3xl ${t.bg} p-8 transition-transform hover:-translate-y-1 hover:shadow-lg`}
            >
              <Quote className="absolute right-6 top-6 h-10 w-10 text-white/60" />
              <div className="flex gap-1 mb-4">
                {Array.from({ length: t.rating }).map((_, i) => (
                  <Star key={i} className="h-5 w-5 fill-accent-yellow text-accent-yellow" />
                ))}
              </div>
              <p className="text-base leading-relaxed text-foreground font-medium">"{t.text}"</p>
              <div className="mt-6 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-lg font-extrabold text-primary-600 shadow-sm">
                  {t.name[0]}
                </div>
                <div>
                  <p className="text-base font-extrabold text-foreground">{t.name}</p>
                  <p className="text-sm text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
