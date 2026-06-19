import type { LucideIcon } from "lucide-react";
import { Construction } from "lucide-react";

export function StubPage({
  title,
  description,
  Icon = Construction,
}: {
  title: string;
  description?: string;
  Icon?: LucideIcon;
}) {
  return (
    <div className="bg-[var(--bg-surface)] rounded-xl shadow-card p-12 text-center">
      <div
        className="w-14 h-14 mx-auto rounded-full flex items-center justify-center"
        style={{ background: "color-mix(in oklab, var(--accent-lavender) 18%, transparent)" }}
      >
        <Icon className="w-7 h-7 text-[var(--accent-lavender)]" />
      </div>
      <h2 className="mt-4 text-[20px] font-semibold text-[var(--text-primary)]">{title}</h2>
      {description && (
        <p className="mt-2 text-[14px] text-[var(--text-secondary)] max-w-md mx-auto">
          {description}
        </p>
      )}
      <p className="mt-4 text-[12px] text-[var(--text-muted)]">
        This page is scaffolded. Build it out next.
      </p>
    </div>
  );
}
