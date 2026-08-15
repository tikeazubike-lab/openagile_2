import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Search, ArrowRight, Star, Users, BookOpen, Sparkles } from "lucide-react";

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden bg-cream">
      {/* Decorative blobs */}
      <div className="pointer-events-none absolute -left-20 top-20 h-64 w-64 rounded-full bg-accent-yellow/40 blur-3xl" />
      <div className="pointer-events-none absolute right-0 top-0 h-96 w-96 rounded-full bg-primary-200/40 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-accent-pink/30 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-8">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-extrabold text-primary-600 shadow-sm border border-primary-100 mb-6">
              <Sparkles className="h-4 w-4 fill-accent-yellow text-accent-yellow" />
              Trusted by 500+ students
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl lg:text-6xl leading-[1.15]">
              Find the Perfect{" "}
              <span className="text-primary-500">Tutor</span> for Your Learning Journey
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-xl leading-relaxed">
              Connect with qualified, experienced tutors in Mathematics, Sciences, Languages, and more.
              Personalized 1-on-1 sessions tailored to your learning pace and goals.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
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
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-accent-yellow text-xs font-extrabold text-foreground shadow-sm"
                    >
                      {String.fromCharCode(64 + i)}
                    </div>
                  ))}
                </div>
                <span className="text-sm font-bold text-muted-foreground">+200 active tutors</span>
              </div>
              <div className="flex items-center gap-1.5 rounded-full bg-white px-3 py-1.5 shadow-sm border border-border">
                <Star className="h-4 w-4 fill-accent-yellow text-accent-yellow" />
                <span className="text-sm font-extrabold text-foreground">4.9/5</span>
                <span className="text-xs text-muted-foreground">student rating</span>
              </div>
            </div>
          </div>

          <div className="relative hidden lg:block">
            <div className="relative rounded-[2.5rem] bg-white p-8 shadow-xl border-2 border-primary-100">
              <div className="space-y-5">
                <div className="flex items-center gap-4 rounded-2xl bg-accent-yellow-light p-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-secondary-400 shadow-md">
                    <BookOpen className="h-7 w-7 text-white" />
                  </div>
                  <div>
                    <p className="text-lg font-extrabold text-foreground">Mathematics</p>
                    <p className="text-sm text-muted-foreground">Calculus & Algebra</p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="flex items-center gap-1 text-secondary-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-extrabold">4.9</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 rounded-2xl bg-accent-mint-light p-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary-500 shadow-md">
                    <Users className="h-7 w-7 text-white" />
                  </div>
                  <div>
                    <p className="text-lg font-extrabold text-foreground">Physics</p>
                    <p className="text-sm text-muted-foreground">Mechanics & Waves</p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="flex items-center gap-1 text-secondary-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-extrabold">4.8</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 rounded-2xl bg-accent-pink-light p-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent-cyan shadow-md">
                    <BookOpen className="h-7 w-7 text-foreground" />
                  </div>
                  <div>
                    <p className="text-lg font-extrabold text-foreground">English</p>
                    <p className="text-sm text-muted-foreground">Essay Writing</p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="flex items-center gap-1 text-secondary-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-extrabold">4.7</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Decorative doodles */}
            <div className="absolute -right-4 -top-6 flex h-16 w-16 items-center justify-center rounded-full bg-accent-yellow text-2xl shadow-lg">
              ✏️
            </div>
            <div className="absolute -bottom-5 -left-5 flex h-14 w-14 items-center justify-center rounded-full bg-accent-pink text-2xl shadow-lg">
              💡
            </div>
            <div className="absolute -right-8 bottom-16 flex h-12 w-12 items-center justify-center rounded-full bg-primary-300 text-xl shadow-lg">
              ⭐
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
