import { useState, useRef, useCallback } from "react";
import { ArrowRight } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface ProgrammeCardProps {
  items: string[];
  icon: LucideIcon;
  bgClass: string;
  chipClass: string;
}

export function ProgrammeCard({ items, icon: Icon, bgClass, chipClass }: ProgrammeCardProps) {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [hovered, setHovered] = useState(false);
  const timers = useRef<number[]>([]);

  const clearTimers = useCallback(() => {
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];
  }, []);

  const runCycle = useCallback(() => {
    if (!hovered || items.length <= 1) return;

    setFlipped(true);
    const t1 = window.setTimeout(() => {
      setIndex((i) => (i + 1) % items.length);
      setFlipped(false);
    }, 250);

    const t2 = window.setTimeout(() => {
      const t3 = window.setTimeout(runCycle, 900);
      timers.current.push(t3);
    }, 500);

    timers.current.push(t1, t2);
  }, [hovered, items.length]);

  const handleEnter = () => {
    setHovered(true);
  };

  const handleLeave = () => {
    setHovered(false);
    clearTimers();
    setFlipped(false);
  };

  const handleTap = () => {
    if (items.length <= 1) return;
    if (flipped) return;
    setFlipped(true);
    window.setTimeout(() => {
      setIndex((i) => (i + 1) % items.length);
      setFlipped(false);
    }, 250);
  };

  const label = items[index] ?? items[0];

  return (
    <div
      className="group [perspective:1000px]"
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      onClick={handleTap}
    >
      <div
        className={[
          "relative flex min-h-[360px] flex-col items-center gap-4 rounded-[2.5rem] p-8 text-center shadow-lg transition-all duration-300 [transform-style:preserve-3d]",
          "hover:-translate-y-2 hover:shadow-2xl",
          bgClass,
          flipped ? "[transform:rotateY(90deg)]" : "[transform:rotateY(0deg)]",
        ].join(" ")}
        style={{ transitionDuration: flipped ? "250ms" : "250ms" }}
      >
        {/* Large icon chip */}
        <div
          className={[
            "flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl shadow-md transition-transform group-hover:scale-110",
            chipClass,
          ].join(" ")}
        >
          <Icon className="h-10 w-10" />
        </div>

        {/* Programme name */}
        <h3 className="text-2xl font-black text-foreground leading-tight min-h-[4rem] flex items-center justify-center">
          {label}
        </h3>

        {/* Decorative line */}
        <div className="h-1 w-16 rounded-full bg-white/60" />

        {/* Description */}
        <p className="text-sm font-semibold text-foreground/70 leading-relaxed">
          Expert tutors ready to help you master this subject and excel in your exams.
        </p>

        {/* CTA */}
        <span className="mt-auto inline-flex items-center gap-1 text-sm font-black text-primary-600 transition-transform group-hover:translate-x-1">
          Learn More <ArrowRight className="h-4 w-4" />
        </span>
      </div>
    </div>
  );
}
