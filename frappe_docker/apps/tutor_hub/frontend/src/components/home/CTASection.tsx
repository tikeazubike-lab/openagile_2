import { motion } from "framer-motion";
import type { CtaLink } from "@/types/landing";

interface CTASectionProps {
  cta: CtaLink;
}

const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
  if (href.startsWith("#")) {
    e.preventDefault();
    document.querySelector(href)?.scrollIntoView({ behavior: "smooth" });
  }
};

export default function CTASection({ cta }: CTASectionProps) {
  return (
    <section className="py-24 bg-primary text-primary-foreground">
      <div className="container text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-center gap-6 max-w-2xl mx-auto"
        >
          <h2 className="font-serif text-3xl font-bold md:text-4xl">
            Ready to Unlock Your Child's Potential?
          </h2>
          <p className="text-primary-foreground/80 text-lg max-w-md">
            Join 50,000+ students already learning with Nigeria's best tutors.
          </p>
          <a
            href={cta.href}
            onClick={(e) => handleAnchorClick(e, cta.href)}
            className="inline-flex h-12 items-center justify-center rounded-md bg-background text-foreground px-8 text-sm font-bold shadow-lg hover:bg-background/90 transition-colors"
          >
            {cta.text} — It's Free to Browse
          </a>
        </motion.div>
      </div>
    </section>
  );
}
