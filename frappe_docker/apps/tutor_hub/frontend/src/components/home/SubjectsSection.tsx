// The API returns icon names as strings (e.g. "calculator", "book-open").
// We map them to Lucide components here. Add to iconMap if new subjects are added via DocTypes.

import { motion } from "framer-motion";
import {
  Calculator,
  BookOpen,
  Atom,
  FlaskConical,
  Leaf,
  Monitor,
  Music,
  Briefcase,
  HelpCircle, // fallback for unmapped icons
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { Subject } from "@/types/landing";

const iconMap: Record<string, LucideIcon> = {
  calculator: Calculator,
  "book-open": BookOpen,
  atom: Atom,
  "flask-conical": FlaskConical,
  leaf: Leaf,
  monitor: Monitor,
  music: Music,
  briefcase: Briefcase,
};

interface SubjectsSectionProps {
  subjects: Subject[];
}

export default function SubjectsSection({ subjects }: SubjectsSectionProps) {
  return (
    <section className="py-20">
      <div className="container">
        <div className="text-center mb-12">
          <h2 className="font-serif text-3xl font-bold md:text-4xl">
            Subjects We Cover
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            From JAMB sciences to creative arts — our tutors have every subject covered.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {subjects.map((subject, i) => {
            const Icon = iconMap[subject.icon] ?? HelpCircle;
            return (
              <motion.div
                key={subject.name}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ y: -3 }}
                className="flex flex-col items-center gap-3 rounded-xl border bg-card p-6 shadow-sm cursor-default transition-shadow hover:shadow-md"
              >
                <div className="rounded-full bg-primary/10 p-3">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <span className="text-sm font-semibold text-center">
                  {subject.name}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
