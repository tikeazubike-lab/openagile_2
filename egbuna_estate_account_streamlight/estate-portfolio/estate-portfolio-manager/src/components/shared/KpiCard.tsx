import { useCountUp } from "@/hooks/useCountUp";
import { fmtNaira } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface KpiProps {
  label: string;
  value: number;
  Icon: LucideIcon;
  accent: "lavender" | "gold" | "green" | "red";
  formatter?: (n: number) => string;
  subtitle?: React.ReactNode;
  integer?: boolean;
}

const ACCENT: Record<KpiProps["accent"], string> = {
  lavender: "var(--accent-lavender)",
  gold: "var(--accent-gold)",
  green: "var(--accent-green)",
  red: "var(--accent-red)",
};

export function KpiCard({
  label,
  value,
  Icon,
  accent,
  formatter = (n) => fmtNaira(n),
  subtitle,
  integer,
}: KpiProps) {
  const v = useCountUp(value, 800);
  const display = integer ? Math.round(v).toLocaleString() : formatter(v);

  return (
    <div
      className="bg-[var(--bg-surface)] rounded-xl p-6 shadow-card relative overflow-hidden"
    >
      <div className="flex items-start justify-between">
        <div className="text-[12px] uppercase tracking-wider text-[var(--text-secondary)]">
          {label}
        </div>
        <Icon className="w-5 h-5" style={{ color: ACCENT[accent] }} />
      </div>
      <div
        className={cn(
          "mt-3 font-mono text-[22px] md:text-[24px] font-semibold text-[var(--text-primary)] tabular-nums leading-none pr-4",
        )}
      >
        {display}
      </div>
      {subtitle && (
        <div className="mt-2 text-[13px] font-mono text-[var(--text-secondary)]">{subtitle}</div>
      )}
    </div>
  );
}
