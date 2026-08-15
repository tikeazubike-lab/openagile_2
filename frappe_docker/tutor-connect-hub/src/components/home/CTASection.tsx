import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, GraduationCap } from "lucide-react";

export function CTASection() {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden bg-secondary-400 py-20">
      {/* Decorative shapes */}
      <div className="pointer-events-none absolute -left-10 -top-10 h-40 w-40 rounded-full bg-white/10" />
      <div className="pointer-events-none absolute -right-10 -bottom-10 h-56 w-56 rounded-full bg-white/10" />
      <div className="pointer-events-none absolute left-1/4 bottom-0 h-20 w-20 rounded-full bg-accent-yellow/30" />
      <div className="pointer-events-none absolute right-1/4 top-0 h-16 w-16 rounded-full bg-primary-300/30" />

      <div className="relative mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white text-secondary-500 shadow-lg">
          <GraduationCap className="h-8 w-8" />
        </div>
        <h2 className="mt-6 text-3xl font-extrabold text-white sm:text-4xl lg:text-5xl">
          Ready to Start Learning?
        </h2>
        <p className="mt-4 text-lg text-white/90 max-w-2xl mx-auto">
          Join TutorConnect today and get access to the best tutors in Nigeria.
          Your first session could be just a few clicks away.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
          <Button
            size="lg"
            className="bg-white text-secondary-500 hover:bg-cream hover:text-secondary-600"
            onClick={() => navigate("/register/student")}
          >
            Sign Up as Student
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-2 border-white text-white hover:bg-white/10"
            onClick={() => navigate("/register/tutor")}
          >
            Apply as Tutor
          </Button>
        </div>
      </div>
    </section>
  );
}
