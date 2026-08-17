import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, GraduationCap } from "lucide-react";
import { Wave, SunDoodle, SparkleDoodle, HeartDoodle, CrownDoodle } from "@/components/ui/doodles";

const photos = [
  { src: "/images/students-library.jpg", alt: "Students celebrating in the library" },
  { src: "/images/boy-studying.jpg", alt: "Young pupil studying in class" },
  { src: "/images/online-lesson-girl.jpg", alt: "Student in an online lesson" },
];

export function CTASection() {
  const navigate = useNavigate();

  return (
    <section className="relative bg-primary-500 pb-32 pt-20 sm:pt-24">
      <SunDoodle className="absolute left-[8%] top-16 h-14 w-14 opacity-80" />
      <SparkleDoodle className="absolute right-[10%] top-20 h-8 w-8 opacity-70" />
      <HeartDoodle className="absolute left-[6%] bottom-32 h-10 w-10 -rotate-12 opacity-70" />
      <CrownDoodle className="absolute right-[8%] bottom-40 h-10 w-12 rotate-12 opacity-70" />
      <div className="pointer-events-none absolute -left-10 bottom-24 h-40 w-40 rounded-full bg-white/10" />
      <div className="pointer-events-none absolute -right-10 top-10 h-56 w-56 rounded-full bg-accent-yellow/20" />

      <div className="relative mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-accent-yellow text-foreground shadow-lg">
          <GraduationCap className="h-8 w-8" />
        </div>
        <h2 className="mt-6 text-3xl font-black text-white sm:text-5xl">
          Ready to Start Learning?
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-lg font-semibold text-white/85">
          Join TutorConnect today and get access to the best tutors in Nigeria.
          Your first session could be just a few clicks away.
        </p>

        <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
          <Button
            size="lg"
            className="bg-secondary-400 text-white hover:bg-secondary-500"
            onClick={() => navigate("/register/student")}
          >
            Sign Up as Student
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            size="lg"
            className="bg-white text-primary-600 hover:bg-primary-50"
            onClick={() => navigate("/register/tutor")}
          >
            Apply as Tutor
          </Button>
        </div>

        <div className="mt-14 grid grid-cols-3 gap-4 sm:gap-6">
          {photos.map((p, i) => (
            <div
              key={i}
              className={`overflow-hidden rounded-3xl border-4 border-white/80 shadow-xl transition-transform hover:-translate-y-2 ${
                i === 1 ? "-translate-y-3" : "translate-y-2"
              }`}
            >
              <img src={p.src} alt={p.alt} className="h-28 w-full object-cover sm:h-40" />
            </div>
          ))}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0">
        <Wave fill="#3A2E8A" />
      </div>
    </section>
  );
}
