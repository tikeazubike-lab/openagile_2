import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Search, ArrowRight, Star, Play } from "lucide-react";
import {
  CrownDoodle,
  LightbulbDoodle,
  FlowerDoodle,
  SparkleDoodle,
  LightningDoodle,
  Wave,
} from "@/components/ui/doodles";

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-cream via-cream to-secondary-100">
      {/* Floating doodles */}
      <CrownDoodle className="absolute left-[5%] top-[10%] h-10 w-12 -rotate-12 drop-shadow-sm sm:h-14 sm:w-16" />
      <LightbulbDoodle className="absolute right-[8%] top-[12%] h-12 w-12 rotate-12 drop-shadow-sm sm:h-16 sm:w-16" />
      <FlowerDoodle className="absolute bottom-[18%] left-[4%] h-12 w-12 rotate-6 drop-shadow-sm sm:h-16 sm:w-16" />
      <SparkleDoodle className="absolute right-[15%] top-[40%] h-6 w-6 opacity-70" />
      <LightningDoodle className="absolute left-[45%] top-[6%] h-8 w-6 -rotate-12 opacity-70" />

      <div className="relative mx-auto max-w-7xl px-4 pb-24 pt-16 sm:px-6 sm:pb-32 sm:pt-24 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-8">
          {/* Left text panel */}
          <div className="relative z-10 max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-black text-primary-600 shadow-md border-2 border-primary-100">
              <Star className="h-4 w-4 fill-accent-yellow text-accent-yellow" />
              Trusted by 500+ students
            </div>

            <h1 className="mt-6 text-4xl font-black tracking-tight text-foreground sm:text-5xl lg:text-6xl leading-[1.08]">
              Find the Perfect{" "}
              <span className="relative inline-block text-primary-500">
                Tutor
                <svg viewBox="0 0 200 18" aria-hidden="true" className="absolute -bottom-1 left-0 w-full">
                  <path d="M4,12 C50,2 140,2 196,10" fill="none" stroke="#FF8C42" strokeWidth="6" strokeLinecap="round" />
                </svg>
              </span>{" "}
              for Your Learning Journey
            </h1>

            <p className="mt-5 text-lg font-semibold text-foreground/70 leading-relaxed">
              Connect with qualified, experienced tutors in Mathematics, Sciences,
              Languages, and more. Personalized 1-on-1 sessions tailored to your
              learning pace and goals.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row">
              <Button size="lg" onClick={() => navigate("/register/student")}>
                <Search className="mr-2 h-5 w-5" />
                Find a Tutor
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-2 border-primary-500 text-primary-600 hover:bg-primary-50"
                onClick={() => navigate("/register/tutor")}
              >
                <Play className="mr-2 h-4 w-4 fill-current" />
                Become a Tutor
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>

            <div className="mt-10 flex flex-wrap items-center gap-5">
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
                      className="h-10 w-10 rounded-full border-[3px] border-white object-cover shadow-md sm:h-11 sm:w-11"
                    />
                  ))}
                </div>
                <span className="text-sm font-black text-foreground/70">+200 active tutors</span>
              </div>
              <div className="flex items-center gap-1.5 rounded-full bg-white px-4 py-2 shadow-md border-2 border-accent-yellow">
                <Star className="h-4 w-4 fill-accent-yellow text-accent-yellow" />
                <span className="text-sm font-black text-foreground">4.9/5</span>
                <span className="text-xs font-bold text-muted-foreground">student rating</span>
              </div>
            </div>
          </div>

          {/* Right collage */}
          <div className="relative mx-auto h-[380px] w-full max-w-lg sm:h-[480px] lg:max-w-none">
            {/* Dominant writing/studying image */}
            <div className="absolute left-[5%] top-[5%] h-[75%] w-[78%] overflow-hidden rounded-[2.5rem] border-4 border-white shadow-2xl sm:left-[8%]">
              <img
                src="/images/hero-writing.jpg"
                alt="Student focused on writing and studying"
                className="h-full w-full object-cover brightness-110 contrast-105 saturate-110"
              />
              <div className="absolute inset-0 bg-gradient-to-tr from-cream/30 via-transparent to-white/20" />
            </div>

            {/* Supporting: painting boy */}
            <div className="absolute -left-2 bottom-[8%] h-[35%] w-[38%] overflow-hidden rounded-[2rem] border-4 border-white shadow-xl rotate-[-6deg] transition-transform hover:rotate-0 sm:left-0 sm:h-[38%] sm:w-[34%]">
              <img
                src="/images/hero-paint.jpg"
                alt="Boy painting"
                className="h-full w-full object-cover brightness-110 contrast-105 saturate-110"
              />
            </div>

            {/* Supporting: robotics/electronics */}
            <div className="absolute -right-2 bottom-[22%] h-[30%] w-[34%] overflow-hidden rounded-[2rem] border-4 border-white shadow-xl rotate-[6deg] transition-transform hover:rotate-0 sm:right-0 sm:h-[32%] sm:w-[30%]">
              <img
                src="/images/hero-robotics.jpg"
                alt="Children learning electronics"
                className="h-full w-full object-cover brightness-110 contrast-105 saturate-110"
              />
            </div>

            {/* ENROLLMENT OPEN ribbon */}
            <div className="absolute right-[5%] top-[2%] hidden rotate-6 flex-col gap-1 sm:flex lg:right-[8%]">
              <div className="rounded-xl bg-primary-500 px-5 py-2 text-center shadow-lg">
                <span className="text-sm font-black tracking-widest text-white">ENROLLMENT</span>
              </div>
              <div className="mx-auto -mt-1 w-max rounded-xl bg-secondary-400 px-7 py-2 text-center shadow-lg">
                <span className="text-lg font-black tracking-widest text-white">OPEN</span>
              </div>
            </div>

            {/* Attribution */}
            <p className="absolute bottom-0 right-[5%] text-[10px] font-semibold text-foreground/40 sm:text-xs">
              Photo by{" "}
              <a
                href="https://unsplash.com/@w_lissa071"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-foreground/70"
              >
                Wadi Lissa
              </a>{" "}
              on Unsplash
            </p>
          </div>
        </div>
      </div>

      {/* Wave bottom into white Subjects section */}
      <div className="absolute bottom-0 left-0 right-0">
        <Wave fill="#FFFFFF" />
      </div>
    </section>
  );
}
