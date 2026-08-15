import { Star, Quote } from "lucide-react";
import { ScallopEdge, FlowerDoodle, PlaneDoodle } from "@/components/ui/doodles";

const testimonials = [
  {
    name: "Adebayo M.",
    role: "Student, SS3",
    text: "My math grades went from C to A in just two months. The tutors here really know how to explain complex topics in simple terms.",
    rating: 5,
    avatar: "/images/avatar-student.jpg",
  },
  {
    name: "Chioma E.",
    role: "Parent",
    text: "I love how easy it is to track my daughter's progress. The scheduling is flexible and the tutors are very professional.",
    rating: 5,
    avatar: "/images/avatar-parent.jpg",
  },
  {
    name: "Dr. Fatima A.",
    role: "Tutor, Chemistry",
    text: "Teaching through TutorConnect has been amazing. The platform handles payments seamlessly so I can focus on what I love — teaching.",
    rating: 5,
    avatar: "/images/avatar-tutor.jpg",
  },
];

export function TestimonialsSection() {
  return (
    <section className="relative bg-cream pb-32 pt-20 sm:pt-28">
      <FlowerDoodle className="absolute left-8 top-20 h-14 w-14 rotate-12 opacity-80 sm:left-24" />
      <PlaneDoodle className="absolute right-10 top-28 h-14 w-14 -rotate-6 opacity-80 sm:right-32" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Purple rounded container (Home 04 motif) */}
        <div className="relative overflow-hidden rounded-[3rem] bg-primary-500 px-6 py-14 shadow-2xl sm:px-12">
          {/* Decorative circles */}
          <div className="pointer-events-none absolute -left-16 -top-16 h-48 w-48 rounded-full bg-white/10" />
          <div className="pointer-events-none absolute -bottom-20 -right-12 h-56 w-56 rounded-full bg-accent-yellow/20" />

          <div className="relative text-center max-w-2xl mx-auto">
            <span className="inline-flex items-center rounded-full bg-accent-yellow px-5 py-2 text-sm font-black text-foreground shadow-md">
              Testimonials
            </span>
            <h2 className="mt-5 text-3xl font-black text-white sm:text-4xl">
              What Our Users Say
            </h2>
            <p className="mt-3 text-lg font-semibold text-white/85">
              Join thousands of satisfied students and tutors on the TutorConnect platform.
            </p>
          </div>

          <div className="relative mt-12 grid gap-6 md:grid-cols-3">
            {testimonials.map((t, i) => (
              <div
                key={t.name}
                className={`relative rounded-3xl bg-white p-7 shadow-lg transition-transform hover:-translate-y-2 ${
                  i === 1 ? "md:-translate-y-4" : ""
                }`}
              >
                <Quote className="absolute right-5 top-5 h-8 w-8 text-primary-100" />
                <div className="flex gap-1">
                  {Array.from({ length: t.rating }).map((_, s) => (
                    <Star key={s} className="h-5 w-5 fill-accent-yellow text-accent-yellow" />
                  ))}
                </div>
                <p className="mt-4 text-sm font-semibold leading-relaxed text-foreground/80">
                  "{t.text}"
                </p>
                <div className="mt-6 flex items-center gap-3">
                  <img
                    src={t.avatar}
                    alt={t.name}
                    className="h-12 w-12 rounded-full border-[3px] border-accent-yellow object-cover shadow-md"
                  />
                  <div>
                    <p className="text-sm font-black text-foreground">{t.name}</p>
                    <p className="text-xs font-bold text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scalloped bottom into purple CTA section */}
      <div className="absolute bottom-0 left-0 right-0">
        <ScallopEdge fill="#6C5CE7" />
      </div>
    </section>
  );
}
