import { motion } from "framer-motion";
import type { Testimonial } from "@/types/landing";
import RatingStars from "@/components/common/RatingStars";

interface TestimonialsSectionProps {
  testimonials: Testimonial[];
}

export default function TestimonialsSection({
  testimonials,
}: TestimonialsSectionProps) {
  return (
    <section className="py-20">
      <div className="container">
        <div className="text-center mb-12">
          <h2 className="font-serif text-3xl font-bold md:text-4xl">
            What Parents &amp; Students Say
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            Real results from families across Nigeria.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col gap-4 rounded-xl border bg-card p-6 shadow-sm"
            >
              {/* Opening quote mark */}
              <span className="text-4xl text-primary/30 font-serif leading-none select-none">
                &ldquo;
              </span>

              <p className="text-sm leading-relaxed text-muted-foreground -mt-4">
                {t.text}
              </p>

              <div className="mt-auto flex flex-col gap-1">
                <RatingStars rating={t.rating} size="sm" />
                <p className="font-semibold text-sm">{t.name}</p>
                <p className="text-xs text-muted-foreground">{t.role}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
