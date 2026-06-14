import { motion } from "framer-motion";
import type { Stat } from "@/types/landing";

interface StatsSectionProps {
  stats: Stat[];
}

export default function StatsSection({ stats }: StatsSectionProps) {
  return (
    <section className="border-y bg-muted/30 py-12">
      <div className="container">
        <div className="grid grid-cols-3 gap-8 text-center">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col gap-1"
            >
              <span className="text-3xl font-bold font-serif text-primary md:text-4xl">
                {stat.value}
              </span>
              <span className="text-sm text-muted-foreground font-medium uppercase tracking-wider">
                {stat.label}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
