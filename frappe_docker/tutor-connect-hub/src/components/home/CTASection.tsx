import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, GraduationCap } from "lucide-react";

export function CTASection() {
  const navigate = useNavigate();

  return (
    <section className="py-20 bg-primary-500">
      <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
        <GraduationCap className="mx-auto h-12 w-12 text-primary-200" />
        <h2 className="mt-6 text-3xl font-bold text-white sm:text-4xl">
          Ready to Start Learning?
        </h2>
        <p className="mt-4 text-lg text-primary-100 max-w-2xl mx-auto">
          Join TutorConnect today and get access to the best tutors in Nigeria.
          Your first session could be just a few clicks away.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
          <Button
            size="lg"
            className="bg-white text-primary-600 hover:bg-primary-50"
            onClick={() => navigate("/register/student")}
          >
            Sign Up as Student
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-white text-white hover:bg-primary-600"
            onClick={() => navigate("/register/tutor")}
          >
            Apply as Tutor
          </Button>
        </div>
      </div>
    </section>
  );
}
