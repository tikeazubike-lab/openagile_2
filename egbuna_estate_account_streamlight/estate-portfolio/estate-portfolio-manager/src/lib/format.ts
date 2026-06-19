// EPM Phase 2 — Number formatting utilities.
// Extracted from mock.ts (was imported there alongside mock data — bad coupling).
// Import these from here in ALL components. Never import fmtNaira from mock.ts.

/**
 * Format a number as Nigerian Naira.
 *
 * @example
 *   fmtNaira(12345678)              → "₦12,345,678.00"
 *   fmtNaira(1500000, { compact })  → "₦1.5M"
 *   fmtNaira(1245, { sign: true })  → "+₦1,245.00"
 */
function toNumber(value: number | string | null | undefined): number {
  if (value === null || value === undefined) return NaN;
  return typeof value === "string" ? Number(value) : value;
}

export function fmtNaira(
  n: number | string | null | undefined,
  opts?: { compact?: boolean; sign?: boolean },
): string {
  if (n === null || n === undefined) return "-";
  const value = toNumber(n);
  if (isNaN(value)) return "-";

  const sign = opts?.sign && value > 0 ? "+" : "";
  if (opts?.compact) {
    if (Math.abs(value) >= 1_000_000) return `${sign}₦${(value / 1_000_000).toFixed(1)}M`;
    if (Math.abs(value) >= 1_000) return `${sign}₦${(value / 1_000).toFixed(1)}K`;
  }
  return `${sign}₦${value.toLocaleString("en-NG", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/**
 * Format a percentage value with optional leading sign.
 *
 * @example
 *   fmtPct(11.22)          → "+11.22%"
 *   fmtPct(-3.5)           → "-3.50%"
 *   fmtPct(5, false)       → "5.00%"
 */
export function fmtPct(n: number | string, withSign = true): string {
  const value = toNumber(n);
  const s = withSign && value > 0 ? "+" : "";
  return `${s}${value.toFixed(2)}%`;
}

/**
 * Format a date string (ISO 8601) into a human-readable form.
 *
 * @example
 *   fmtDate("2026-04-14")  → "Apr 14, 2026"
 */
export function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-NG", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a datetime string (ISO 8601) with time and WAT label.
 *
 * @example
 *   fmtDateTime("2026-04-14T18:02:00Z")  → "Mon, Apr 14, 2026, 07:02 PM WAT"
 */
export function fmtDateTime(iso: string): string {
  return (
    new Date(iso).toLocaleString("en-NG", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }) + " WAT"
  );
}
