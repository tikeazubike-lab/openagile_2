import { cn } from "@/lib/utils";
import { SECTOR_BADGE } from "@/api/mock";
import type { Sector, TransactionType, HoldingStatus } from "@/types";

export function SectorBadge({ sector }: { sector: Sector }) {
  const c = SECTOR_BADGE[sector] ?? { bg: "#F5F5F7", text: "#374151" };
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium"
      style={{ backgroundColor: c.bg, color: c.text }}
    >
      {sector}
    </span>
  );
}

export function TxTypeBadge({ type }: { type: TransactionType }) {
  const safeType = (type || "UNKNOWN").toUpperCase();
  const styles = {
    BUY: { bg: "#DCFCE7", text: "#16A34A" },
    SELL: { bg: "#FEE2E2", text: "#DC2626" },
    BONUS_ISSUE: { bg: "#EDE9FE", text: "#7C3AED" },
    RIGHTS_ISSUE: { bg: "#DBEAFE", text: "#2563EB" },
    DIVIDEND: { bg: "#FEF9C3", text: "#CA8A04" },
    STOCK_SPLIT: { bg: "#E0E7FF", text: "#4338CA" },
  }[safeType] || { bg: "#F3F4F6", text: "#4B5563" };
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide"
      style={{ backgroundColor: styles.bg, color: styles.text }}
    >
      {type}
    </span>
  );
}

export function StatusBadge({ status }: { status: HoldingStatus }) {
  const styles =
    status === "LIVE" ? { bg: "#DCFCE7", text: "#16A34A" } : { bg: "#FEF3C7", text: "#D97706" };
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold"
      style={{ backgroundColor: styles.bg, color: styles.text }}
    >
      {status}
    </span>
  );
}

export function ReturnText({
  value,
  className,
}: {
  value: number | null | undefined;
  className?: string;
}) {
  if (value === null || value === undefined) {
    return <span className={cn("text-[var(--text-muted)]", className)}>-</span>;
  }

  const positive = value > 0;
  const negative = value < 0;
  return (
    <span
      className={cn(
        "font-mono tabular-nums",
        positive && "text-[var(--accent-green)]",
        negative && "text-[var(--accent-red)]",
        !positive && !negative && "text-[var(--text-muted)]",
        className,
      )}
    >
      {positive && "+"}
      {value.toFixed(2)}%
    </span>
  );
}
