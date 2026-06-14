import type { Tutor, CtaLink } from "@/types/landing";
import HeroCarousel from "./HeroCarousel";

interface HeroSectionProps {
  title: string;
  subtitle: string;
  ctaPrimary: CtaLink;
  ctaSecondary: CtaLink;
  tutors: Tutor[];
}

const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
  if (href.startsWith("#")) {
    e.preventDefault();
    document.querySelector(href)?.scrollIntoView({ behavior: "smooth" });
  }
};

export default function HeroSection({
  title,
  subtitle,
  ctaPrimary,
  ctaSecondary,
  tutors,
}: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden bg-background py-20 md:py-28">
      {/* Subtle background gradient */}
      <div
        className="absolute inset-0 -z-10 opacity-40"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 60% 40%, hsl(var(--primary) / 0.12), transparent)",
        }}
      />

      <div className="container grid grid-cols-1 gap-12 lg:grid-cols-2 lg:gap-8 items-center">
        {/* Left: Copy */}
        <div className="flex flex-col gap-6">
          <h1 className="font-serif text-4xl font-bold leading-tight tracking-tight md:text-5xl lg:text-6xl">
            {title}
          </h1>
          <p className="text-lg text-muted-foreground max-w-md leading-relaxed">
            {subtitle}
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <a
              href={ctaPrimary.href}
              onClick={(e) => handleAnchorClick(e, ctaPrimary.href)}
              className="inline-flex h-11 items-center justify-center rounded-md bg-primary px-6 text-sm font-semibold text-primary-foreground shadow hover:bg-primary/90 transition-colors"
            >
              {ctaPrimary.text}
            </a>
            <a
              href={ctaSecondary.href}
              onClick={(e) => handleAnchorClick(e, ctaSecondary.href)}
              className="inline-flex h-11 items-center justify-center rounded-md border border-input bg-background px-6 text-sm font-semibold hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              {ctaSecondary.text}
            </a>
          </div>
        </div>

        {/* Right: Draggable tutor card carousel */}
        <div className="w-full">
          <HeroCarousel tutors={tutors} />
        </div>
      </div>
    </section>
  );
}
