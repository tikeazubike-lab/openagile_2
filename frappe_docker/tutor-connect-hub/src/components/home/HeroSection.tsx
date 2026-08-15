import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Search, ArrowRight, Star } from "lucide-react";
import {
  CrownDoodle,
  LightbulbDoodle,
  FlowerDoodle,
  SunDoodle,
  ScallopEdge,
} from "@/components/ui/doodles";

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden">
      {/* Full-width background photo */}
      <div className="absolute inset-0">
        <img
          src="/images/hero-classroom.jpg"
          alt="Happy pupils raising their hands in a classroom"
          className="h-full w-full object-cover object-center"
        />
        {/* Warm cream overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-cream via-cream/85 to-accent-yellow/20" />
        <div className="absolute inset-0 bg-gradient-to-t from-cream/60 via-transparent to-transparent" />
      </div>

      {/* Floating doodles */}
      <CrownDoodle className="absolute left-6 top-10 h-12 w-14 -rotate-12 drop-shadow-md sm:left-16 sm:h-16 sm:w-20" />
      <LightbulbDoodle className="absolute right-8 top-16 h-14 w-14 rotate-12 drop-shadow-md sm:right-24 sm:h-20 sm:w-20" />
      <FlowerDoodle className="absolute bottom-24 left-6 h-14 w-14 rotate-6 drop-shadow-md sm:bottom-32 sm:left-24 sm:h-20 sm:w-20" />
      <SunDoodle className="absolute bottom-24 right-8 h-16 w-16 drop-shadow-md sm:bottom-40 sm:right-40 sm:h-24 sm:w-24" />

      <div className="relative mx-auto max-w-7xl px-4 pb-28 pt-16 sm:px-6 sm:pb-36 sm:pt-24 lg:px-8">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-extrabold text-primary-600 shadow-md border-2 border-primary-200 mb-6">
            <Star className="h-4 w-4 fill-accent-yellow text-accent-yellow" />
            Trusted by 500+ students
          </div>

          <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-6xl lg:text-7xl leading-[1.08]">
            Find the Perfect{" "}
            <span className="relative inline-block text-primary-500">
              Tutor
              <svg
                viewBox="0 0 220 20"
                aria-hidden="true"
                className="absolute -bottom-2 left-0 w-full"
              >
                <path
                  d="M4,14 C50,4 120,4 216,12"
                  fill="none"
                  stroke="#FF8C42"
                  strokeWidth="7"
                  strokeLinecap="round"
                />
              </svg>
            </span>{" "}
            for Your Learning Journey
          </h1>

          <p className="mt-6 max-w-xl text-lg font-semibold text-foreground/70 sm:text-xl leading-relaxed">
            Connect with qualified, experienced tutors in Mathematics, Sciences,
            Languages, and more. Personalized 1-on-1 sessions tailored to your
            learning pace and goals.
          </p>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row">
            <Button size="lg" onClick={() => navigate("/register/student")}>
              <Search className="mr-2 h-5 w-5" />
              Find a Tutor
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate("/register/tutor")}>
              Become a Tutor
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          <div className="mt-10 flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="flex -space-x-3">
                {[
                  "/images/avatar-parent.jpg",
                  "/images/avatar-student.jpg",
                  "/images/avatar-tutor.jpg",
                  "/images/boy-studying.jpg",
                ].map((src, i) => (
                  <img
                    key={i}
                    src={src}
                    alt=""
                    className="h-11 w-11 rounded-full border-[3px] border-white object-cover shadow-md"
                  />
                ))}
              </div>
              <span className="text-sm font-extrabold text-foreground/70">
                +200 active tutors
              </span>
            </div>
            <div className="flex items-center gap-1.5 rounded-full bg-white px-4 py-2 shadow-md border-2 border-accent-yellow">
              <Star className="h-4 w-4 fill-accent-yellow text-accent-yellow" />
              <span className="text-sm font-black text-foreground">4.9/5</span>
              <span className="text-xs font-bold text-muted-foreground">student rating</span>
            </div>
          </div>
        </div>
      </div>

      {/* Enrollment ribbon (Kidza "Admission Open" motif) */}
      <div className="absolute right-6 top-1/2 hidden -translate-y-1/2 rotate-6 lg:block xl:right-24">
        <div className="relative">
          <div className="rounded-2xl bg-primary-500 px-8 py-3 text-center shadow-xl">
            <span className="text-xl font-black tracking-widest text-white">
              ENROLLMENT
            </span>
          </div>
          <div className="mx-auto -mt-1 w-max rounded-2xl bg-secondary-400 px-10 py-3 text-center shadow-xl">
            <span className="text-2xl font-black tracking-widest text-white">OPEN</span>
          </div>
          <div className="absolute -left-6 top-1/2 h-0 w-0 -translate-y-1/2 border-y-[14px] border-r-[24px] border-y-transparent border-r-primary-700" />
        </div>
      </div>

      {/* Scalloped wave bottom into Subjects section (orange) */}
      <div className="absolute bottom-0 left-0 right-0">
        <ScallopEdge fill="#FF8C42" />
      </div>
    </section>
  );
}
