import { Search, Calendar, Video, CreditCard } from "lucide-react";
import { ScallopEdge, HeartDoodle, LightbulbDoodle } from "@/components/ui/doodles";

const steps = [
  {
    icon: Search,
    title: "Find a Tutor",
    description: "Browse our curated list of qualified tutors. Filter by subject, rating, price, and availability.",
    chip: "bg-accent-yellow text-foreground",
  },
  {
    icon: Calendar,
    title: "Book a Session",
    description: "Choose a convenient time slot that works for both you and the tutor. Add any specific topics or notes.",
    chip: "bg-secondary-400 text-white",
  },
  {
    icon: Video,
    title: "Learn Online",
    description: "Join your session via video call. Get personalized 1-on-1 attention and real-time feedback.",
    chip: "bg-primary-500 text-white",
  },
  {
    icon: CreditCard,
    title: "Pay Securely",
    description: "Payments are processed securely after session completion. Only pay for sessions you attend.",
    chip: "bg-accent-pink text-foreground",
  },
];

export function HowItWorksSection() {
  return (
    <section className="relative bg-white pb-32 pt-20 sm:pt-28">
      <HeartDoodle className="absolute right-8 top-16 h-12 w-12 -rotate-12 opacity-80 sm:right-24" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          {/* Image side with blob frame + floating badge */}
          <div className="relative mx-auto w-full max-w-lg">
            <div className="absolute -left-6 -top-6 h-full w-full rounded-[3rem] bg-accent-yellow" />
            <img
              src="/images/online-lesson-girl.jpg"
              alt="Student learning online with a tutor"
              className="relative w-full rounded-[3rem] border-4 border-white object-cover shadow-2xl"
            />
            {/* Floating experience badge */}
            <div className="absolute -bottom-8 -right-4 flex h-28 w-28 flex-col items-center justify-center rounded-full bg-primary-500 text-white shadow-xl sm:-right-8 sm:h-32 sm:w-32 border-4 border-white">
              <span className="text-3xl font-black sm:text-4xl">38+</span>
              <span className="text-xs font-extrabold uppercase tracking-wide">Top Tutors</span>
            </div>
            <LightbulbDoodle className="absolute -top-10 right-6 h-14 w-14 rotate-12 drop-shadow-md" />
          </div>

          {/* Steps side */}
          <div>
            <span className="inline-flex items-center rounded-full bg-primary-100 px-5 py-2 text-sm font-black text-primary-700">
              How It Works
            </span>
            <h2 className="mt-5 text-3xl font-black text-foreground sm:text-4xl lg:text-5xl leading-tight">
              Start Learning in 4 Easy Steps
            </h2>
            <p className="mt-4 text-lg font-semibold text-muted-foreground">
              Getting started with TutorConnect is simple. Follow these easy steps
              to begin your learning journey.
            </p>

            <div className="mt-10 space-y-6">
              {steps.map((step, index) => (
                <div key={step.title} className="group flex items-start gap-4">
                  <div className="relative shrink-0">
                    <div
                      className={`flex h-14 w-14 items-center justify-center rounded-2xl shadow-md transition-transform group-hover:scale-110 group-hover:-rotate-6 ${step.chip}`}
                    >
                      <step.icon className="h-7 w-7" />
                    </div>
                    <div className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-foreground text-xs font-black text-white shadow">
                      {index + 1}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-black text-foreground">{step.title}</h3>
                    <p className="mt-1 text-sm font-semibold leading-relaxed text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Scalloped bottom into cream Testimonials section */}
      <div className="absolute bottom-0 left-0 right-0">
        <ScallopEdge fill="#FFFBEB" />
      </div>
    </section>
  );
}
