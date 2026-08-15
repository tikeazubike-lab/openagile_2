import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Search, ArrowRight, Star, Users, BookOpen } from "lucide-react";

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-primary-50">
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-8 items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 mb-6">
              <Star className="h-4 w-4 fill-primary-500 text-primary-500" />
              Trusted by 500+ students
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Find the Perfect{" "}
              <span className="text-primary-500">Tutor</span> for Your Learning Journey
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-xl">
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

            <div className="mt-10 flex items-center gap-8">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="h-8 w-8 rounded-full border-2 border-white bg-primary-100 flex items-center justify-center text-xs font-medium text-primary-700"
                    >
                      {String.fromCharCode(64 + i)}
                    </div>
                  ))}
                </div>
                <span className="text-sm text-muted-foreground">+200 active tutors</span>
              </div>
            </div>
          </div>

          <div className="relative hidden lg:block">
            <div className="relative rounded-2xl bg-white p-8 shadow-xl border border-border">
              <div className="space-y-6">
                <div className="flex items-center gap-4 rounded-xl bg-primary-50 p-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-500">
                    <BookOpen className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">Mathematics</p>
                    <p className="text-sm text-muted-foreground">Calculus & Algebra</p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="flex items-center gap-1 text-amber-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-medium">4.9</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 rounded-xl bg-gray-50 p-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100">
                    <Users className="h-6 w-6 text-emerald-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">Physics</p>
                    <p className="text-sm text-muted-foreground">Mechanics & Waves</p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="flex items-center gap-1 text-amber-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-medium">4.8</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 rounded-xl bg-gray-50 p-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-violet-100">
                    <BookOpen className="h-6 w-6 text-violet-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">English</p>
                    <p className="text-sm text-muted-foreground">Essay Writing</p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="flex items-center gap-1 text-amber-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-medium">4.7</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {/* Decorative blobs */}
            <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-primary-200 opacity-50" />
            <div className="absolute -bottom-4 -left-4 h-16 w-16 rounded-full bg-primary-300 opacity-30" />
          </div>
        </div>
      </div>
    </section>
  );
}
