import { Search, Calendar, Video, CreditCard } from "lucide-react";

const steps = [
  {
    icon: Search,
    title: "Find a Tutor",
    description: "Browse our curated list of qualified tutors. Filter by subject, rating, price, and availability.",
    color: "bg-blue-50 text-blue-600",
  },
  {
    icon: Calendar,
    title: "Book a Session",
    description: "Choose a convenient time slot that works for both you and the tutor. Add any specific topics or notes.",
    color: "bg-emerald-50 text-emerald-600",
  },
  {
    icon: Video,
    title: "Learn Online",
    description: "Join your session via video call. Get personalized 1-on-1 attention and real-time feedback.",
    color: "bg-purple-50 text-purple-600",
  },
  {
    icon: CreditCard,
    title: "Pay Securely",
    description: "Payments are processed securely after session completion. Only pay for sessions you attend.",
    color: "bg-amber-50 text-amber-600",
  },
];

export function HowItWorksSection() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground">How It Works</h2>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            Getting started with TutorConnect is simple. Follow these four easy steps
            to begin your learning journey.
          </p>
        </div>

        <div className="mt-14 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <div key={step.title} className="relative text-center">
              <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-sm border border-border">
                <step.icon className="h-7 w-7 text-primary-500" />
              </div>
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 flex h-7 w-7 items-center justify-center rounded-full bg-primary-500 text-xs font-bold text-white">
                {index + 1}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-foreground">{step.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
