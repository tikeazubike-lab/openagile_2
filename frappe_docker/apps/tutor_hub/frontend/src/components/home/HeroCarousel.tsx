// Draggable carousel using framer-motion. Images come from API response as
// absolute paths (/assets/tutor_hub/images/tutor-N.jpg) — no local imports.

import { useRef } from "react";
import { motion } from "framer-motion";
import type { Tutor } from "@/types/landing";
import RatingStars from "@/components/common/RatingStars";
import SubjectBadge from "@/components/common/SubjectBadge";

interface HeroCarouselProps {
  tutors: Tutor[];
}

export default function HeroCarousel({ tutors }: HeroCarouselProps) {
  const constraintsRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={constraintsRef}
      className="relative overflow-hidden rounded-2xl h-[420px] bg-muted/30"
    >
      <motion.div
        drag="x"
        dragConstraints={constraintsRef}
        className="flex gap-4 p-4 cursor-grab active:cursor-grabbing h-full items-center"
        style={{ width: `${tutors.length * 240}px` }}
      >
        {tutors.map((tutor) => (
          <TutorCard key={tutor.name} tutor={tutor} />
        ))}
      </motion.div>

      {/* Drag hint — fades after first interaction via CSS */}
      <div className="pointer-events-none absolute inset-y-0 right-0 w-16 bg-gradient-to-l from-background/80 to-transparent" />
    </div>
  );
}

function TutorCard({ tutor }: { tutor: Tutor }) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className="flex-shrink-0 w-52 rounded-xl border bg-card shadow-sm overflow-hidden flex flex-col"
    >
      <img
        src={tutor.image}
        alt={tutor.name}
        className="w-full h-36 object-cover"
        loading="lazy"
        onError={(e) => {
          // Graceful fallback if image missing — show initials placeholder
          const target = e.currentTarget;
          target.style.display = "none";
          const parent = target.parentElement;
          if (parent) {
            const fallback = document.createElement("div");
            fallback.className =
              "w-full h-36 bg-primary/10 flex items-center justify-center text-2xl font-bold text-primary";
            fallback.textContent = tutor.name
              .split(" ")
              .map((n) => n[0])
              .join("")
              .slice(0, 2);
            parent.prepend(fallback);
          }
        }}
      />

      <div className="p-3 flex flex-col gap-2 flex-1">
        <p className="font-semibold text-sm leading-tight">{tutor.name}</p>

        <RatingStars rating={tutor.rating} size="sm" />

        <div className="flex flex-wrap gap-1">
          {tutor.subjects.slice(0, 2).map((s) => (
            <SubjectBadge key={s} name={s} />
          ))}
        </div>

        <p className="text-xs text-muted-foreground line-clamp-2 mt-auto">
          {tutor.bio}
        </p>

        <p className="text-sm font-bold text-primary">
          ₦{tutor.rate_naira.toLocaleString()}/hr
        </p>
      </div>
    </motion.div>
  );
}
