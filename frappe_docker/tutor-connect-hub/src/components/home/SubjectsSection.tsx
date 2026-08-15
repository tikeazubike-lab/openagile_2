import {
  Calculator,
  Atom,
  FlaskConical,
  Leaf,
  BookText,
  Code2,
  TrendingUp,
  DollarSign,
  Globe,
  MapPin,
  Clock,
  Languages,
  ArrowRight,
} from "lucide-react";
import { ScallopEdge, SparkleDoodle, LightningDoodle } from "@/components/ui/doodles";

const toppers = [
  "bg-accent-yellow-light",
  "bg-accent-pink-light",
  "bg-accent-cyan-light",
  "bg-accent-mint-light",
  "bg-accent-lavender-light",
  "bg-accent-yellow-light",
];
const iconChips = [
  "bg-secondary-400 text-white",
  "bg-primary-500 text-white",
  "bg-accent-yellow text-foreground",
  "bg-primary-300 text-white",
];

const subjects = [
  { name: "Mathematics", icon: Calculator, count: 45 },
  { name: "Physics", icon: Atom, count: 32 },
  { name: "Chemistry", icon: FlaskConical, count: 28 },
  { name: "Biology", icon: Leaf, count: 24 },
  { name: "English", icon: BookText, count: 38 },
  { name: "Computer Science", icon: Code2, count: 20 },
  { name: "Economics", icon: TrendingUp, count: 18 },
  { name: "Accounting", icon: DollarSign, count: 15 },
  { name: "French", icon: Languages, count: 12 },
  { name: "Geography", icon: Globe, count: 14 },
  { name: "History", icon: Clock, count: 16 },
  { name: "Yoruba", icon: MapPin, count: 10 },
];

export function SubjectsSection() {
  return (
    <section className="relative bg-secondary-400 pb-32 pt-14 sm:pt-20">
      {/* Doodles on orange */}
      <SparkleDoodle className="absolute left-10 top-16 h-8 w-8 opacity-60" />
      <LightningDoodle className="absolute right-12 top-24 h-10 w-8 rotate-12 opacity-60" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <span className="inline-flex items-center rounded-full bg-white px-5 py-2 text-sm font-black text-secondary-500 shadow-md">
            Our Subjects
          </span>
          <h2 className="mt-5 text-3xl font-black text-white sm:text-5xl">
            Explore Subjects With Expert Tutors
          </h2>
          <p className="mt-4 text-lg font-semibold text-white/85">
            Whether you need help with exam prep or mastering new concepts,
            we have you covered across a wide range of subjects.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-4">
          {subjects.map((subject, i) => (
            <button
              key={subject.name}
              className="group flex flex-col overflow-hidden rounded-3xl bg-white text-left shadow-lg transition-all hover:-translate-y-2 hover:shadow-2xl"
            >
              {/* Cartoon illustration topper */}
              <div className={`relative flex h-28 items-center justify-center ${toppers[i % toppers.length]}`}>
                <div
                  className={`flex h-16 w-16 items-center justify-center rounded-2xl shadow-md transition-transform group-hover:scale-110 group-hover:-rotate-6 ${iconChips[i % iconChips.length]}`}
                >
                  <subject.icon className="h-8 w-8" />
                </div>
                <SparkleDoodle className="absolute right-3 top-3 h-5 w-5 opacity-70" />
                <div className="absolute bottom-3 left-3 h-3 w-3 rounded-full bg-white/70" />
              </div>

              <div className="flex flex-1 flex-col items-center gap-1 px-4 pb-5 pt-4 text-center">
                <p className="text-base font-black text-foreground">{subject.name}</p>
                <p className="text-sm font-bold text-muted-foreground">
                  {subject.count} tutors
                </p>
                <span className="mt-2 inline-flex items-center text-sm font-black text-primary-600 opacity-0 transition-opacity group-hover:opacity-100">
                  Learn More <ArrowRight className="ml-1 h-4 w-4" />
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Scalloped bottom into white HowItWorks section */}
      <div className="absolute bottom-0 left-0 right-0">
        <ScallopEdge fill="#FFFFFF" />
      </div>
    </section>
  );
}
