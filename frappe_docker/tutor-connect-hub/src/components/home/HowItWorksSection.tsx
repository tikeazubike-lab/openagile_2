import { Search, Calendar, Video, CreditCard } from "lucide-react";

const steps = [
  {
    icon: Search,
    title: "Find a Tutor",
    description: "Browse our curated list of qualified tutors. Filter by subject, rating, price, and availability.",
    bg: "bg-accent-yellow-light",
    iconBg: "bg-accent-yellow",
  },
  {
    icon: Calendar,
    title: "Book a Session",
    description: "Choose a convenient time slot that works for both you and the tutor. Add any specific topics or notes.",
    bg: "bg-accent-mint-light",
    iconBg: "bg-accent-mint",
  },
  {
    icon: Video,
    title: "Learn Online",
    description: "Join your session via video call. Get personalized 1-on-1 attention and real-time feedback.",
    bg: "bg-accent-pink-light",
    iconBg: "bg-accent-pink",
  },
  {
    icon: CreditCard,
    title: "Pay Securely",
    description: "Payments are processed securely after session completion. Only pay for sessions you attend.",
    bg: "bg-accent-cyan-light",
    iconBg: "bg-accent-cyan",
  },
];

export function HowItWorksSection() {
  return (
    <section className="relative overflow-hidden py-20 bg-cream">
      <div className="pointer-events-none absolute -right-20 top-20 h-80 w-80 rounded-full bg-primary-200/30 blur-3xl" />
      <div className="pointer-events-none absolute -left-20 bottom-20 h-72 w-72 rounded-full bg-accent-pink/30 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <span className="inline-flex items-center rounded-full bg-white px-4 py-1.5 text-sm font-extrabold text-primary-700 mb-4 shadow-sm">
            How It Works
          </span>
          <h2 className="text-3xl font-extrabold text-foreground sm:text-4xl">
            Start Learning in 4 Easy Steps
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Getting started with TutorConnect is simple. Follow these four easy steps
            to begin your learning journey.
          </p>
        </div>

        <div className="mt-14 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <div key={step.title} className="relative">
              <div className={`rounded-3xl ${step.bg} p-8 text-center transition-transform hover:-translate-y-1 hover:shadow-lg`}>
                <div className="relative mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-white shadow-md">
                  <step.icon className="h-9 w-9 text-primary-500" />
                  <div className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-secondary-400 text-sm font-extrabold text-white shadow-sm">
                    {index + 1}
                  </div>
                </div>
                <h3 className="text-xl font-extrabold text-foreground">{step.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{step.description}</p>
              </div>

              {/* Connector line for desktop */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 h-0.5 w-8 border-t-2 border-dashed border-primary-300" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
