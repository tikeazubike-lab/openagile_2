import { Calculator, Atom, BookText, TrendingUp } from "lucide-react";
import { ProgrammeCard } from "./ProgrammeCard";
import { SparkleDoodle, HeartDoodle, LightningDoodle, Wave } from "@/components/ui/doodles";

const programmes = [
  {
    icon: Calculator,
    bgClass: "bg-accent-yellow-light",
    chipClass: "bg-secondary-400 text-white",
    items: [
      "Mathematics",
      "English Language",
      "Further Mathematics",
      "Statistics",
      "JAMB / UTME",
      "SAT",
    ],
  },
  {
    icon: Atom,
    bgClass: "bg-accent-cyan-light",
    chipClass: "bg-primary-500 text-white",
    items: [
      "Physics",
      "Chemistry",
      "Biology",
      "Agricultural Science",
      "Computer Science & ICT",
      "Technical Drawing / Basic Technology",
    ],
  },
  {
    icon: BookText,
    bgClass: "bg-accent-pink-light",
    chipClass: "bg-accent-yellow text-foreground",
    items: [
      "Literature-in-English",
      "Geography",
      "History",
      "French",
      "Igbo",
      "Yoruba",
      "Hausa",
      "Arabic",
      "Christian Religious Studies",
      "Islamic Religious Studies",
      "Visual Arts / Fine Art",
      "Music",
    ],
  },
  {
    icon: TrendingUp,
    bgClass: "bg-accent-mint-light",
    chipClass: "bg-secondary-500 text-white",
    items: [
      "Economics",
      "Accounting",
      "Commerce",
      "Business Studies",
      "Government",
      "Home Economics",
      "Food & Nutrition",
      "Technical / Workshop subjects",
      "WAEC",
      "NECO",
      "BECE",
      "Common Entrance",
      "IELTS",
      "TOEFL",
    ],
  },
];

export function SubjectsSection() {
  return (
    <section className="relative bg-white pb-32 pt-20 sm:pt-24">
      <SparkleDoodle className="absolute left-[8%] top-12 h-8 w-8 opacity-60" />
      <HeartDoodle className="absolute right-[10%] top-20 h-10 w-10 -rotate-12 opacity-70" />
      <LightningDoodle className="absolute left-[6%] bottom-24 h-8 w-6 rotate-12 opacity-60" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <span className="inline-flex items-center rounded-full bg-primary-100 px-5 py-2 text-sm font-black text-primary-700">
            Our Programmes
          </span>
          <h2 className="mt-5 text-3xl font-black text-foreground sm:text-5xl">
            Explore Subjects With Expert Tutors
          </h2>
          <p className="mt-4 text-lg font-semibold text-muted-foreground">
            Whether you need help with exam prep or mastering new concepts,
            we have you covered across a wide range of programmes.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {programmes.map((p, i) => (
            <ProgrammeCard key={i} {...p} />
          ))}
        </div>
      </div>

      {/* Wave bottom into cream HowItWorks section */}
      <div className="absolute bottom-0 left-0 right-0">
        <Wave fill="#FFFBEB" />
      </div>
    </section>
  );
}
