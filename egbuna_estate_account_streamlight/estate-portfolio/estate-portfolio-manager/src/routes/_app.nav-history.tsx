import { createFileRoute } from "@tanstack/react-router";
import { TrendingDown, TrendingUp, Minus, LineChart, AlertCircle } from "lucide-react";
import { useState, useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from "recharts";
import { format, parseISO, subMonths, startOfYear } from "date-fns";
import { useNavHistory } from "@/api/queries";
import { fmtNaira, fmtPct, fmtDate } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { NavDataPoint, NavSummary, CoverageInfo } from "@/types";

export const Route = createFileRoute("/_app/nav-history")({
  component: NavHistoryPage,
});

const RANGES = [
  { label: "1M", months: 1 },
  { label: "3M", months: 3 },
  { label: "6M", months: 6 },
  { label: "1Y", months: 12 },
  { label: "All", months: Infinity },
] as const;

type RangeLabel = (typeof RANGES)[number]["label"];

function getRangeStart(range: RangeLabel): string | undefined {
  if (range === "All") return "2026-01-01";
  const d = subMonths(new Date(), RANGES.find((r) => r.label === range)!.months);
  return d.toISOString().slice(0, 10);
}

function ChangeBadge({ label, value }: { label: string; value: string }) {
  const num = parseFloat(value);
  const isPos = num > 0;
  const isNeg = num < 0;
  const isZero = num === 0;

  return (
    <div className="flex flex-col items-center gap-1 p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-color)] min-w-[100px]">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span
        className={cn(
          "text-sm font-semibold flex items-center gap-1",
          isPos && "text-green-600",
          isNeg && "text-red-600",
          isZero && "text-muted-foreground"
        )}
      >
        {isPos && <TrendingUp className="h-3.5 w-3.5" />}
        {isNeg && <TrendingDown className="h-3.5 w-3.5" />}
        {isZero && <Minus className="h-3.5 w-3.5" />}
        {isZero ? "—" : `${isPos ? "+" : ""}${num.toFixed(2)}%`}
      </span>
    </div>
  );
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
}) {
  if (!active || !payload?.length || !label) return null;
  return (
    <div className="rounded-lg border bg-card p-3 shadow-md text-sm">
      <p className="font-medium mb-1">{fmtDate(label)}</p>
      <p className="text-muted-foreground">
        NAV: <span className="font-semibold text-foreground">{fmtNaira(payload[0].value)}</span>
      </p>
    </div>
  );
}

function NavHistoryPage() {
  const today = new Date().toISOString().slice(0, 10);
  const [range, setRange] = useState<RangeLabel>("6M");
  const rangeStart = getRangeStart(range);

  const { data: raw, isLoading, error } = useNavHistory(rangeStart, today);

  const navData = raw as unknown as { data_points: NavDataPoint[]; summary: NavSummary | null; coverage: CoverageInfo } | undefined;

  const chartData = useMemo(() => {
    if (!navData?.data_points) return [];
    return navData.data_points.map((dp) => ({
      date: dp.snapshot_date,
      nav: parseFloat(dp.total_value),
    }));
  }, [navData]);

  const summary = navData?.summary;
  const coverage = navData?.coverage;
  const isEmpty = !isLoading && !error && chartData.length === 0;

  const coveragePct = coverage
    ? Math.round((coverage.priced_holdings_count / coverage.total_active_holdings_count) * 100)
    : null;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">NAV History</h1>

      {isLoading && (
        <div className="flex items-center justify-center py-20 text-muted-foreground">
          Loading NAV history...
        </div>
      )}

      {error && (
        <div className="flex items-center justify-center py-20 text-red-500">
          Failed to load NAV history. Please try again.
        </div>
      )}

      {isEmpty && (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
          <LineChart className="h-16 w-16 mb-4 opacity-40" />
          <h2 className="text-lg font-semibold mb-2">No NAV History Yet</h2>
          <p className="text-sm max-w-md text-center">
            NAV history will appear here once daily prices are available. Prices
            are uploaded from the NGX Daily Official List each trading day.
          </p>
        </div>
      )}

      {!isLoading && !error && !isEmpty && chartData.length > 0 && (
        <>
          {/* Summary Row */}
          {summary && (
            <div className="space-y-3">
              <div className="flex flex-wrap items-end gap-6">
                <div>
                  <span className="text-sm text-muted-foreground">Current NAV</span>
                  <div className="text-3xl font-bold">{fmtNaira(parseFloat(summary.current_nav))}</div>
                </div>
                {coverage && coveragePct !== null && (
                  <div className="text-xs text-muted-foreground pb-1">
                    Based on {coverage.priced_holdings_count} of {coverage.total_active_holdings_count} holdings
                    with price data ({coveragePct}%)
                  </div>
                )}
              </div>
              <div className="flex flex-wrap gap-3">
                <ChangeBadge label="7D Change" value={summary.change_7d} />
                <ChangeBadge label="30D Change" value={summary.change_30d} />
                <ChangeBadge label="YTD Change" value={summary.change_ytd} />
              </div>
            </div>
          )}

          {/* Chart */}
          <div className="rounded-xl border bg-card">
            <div className="p-4 border-b flex items-center justify-between">
              <span className="text-sm font-medium">Portfolio NAV</span>
              <div className="flex gap-1">
                {RANGES.map((r) => (
                  <button
                    key={r.label}
                    onClick={() => setRange(r.label)}
                    className={cn(
                      "px-3 py-1 text-xs rounded-md transition-colors",
                      range === r.label
                        ? "bg-primary text-primary-foreground"
                        : "bg-[var(--bg-surface)] hover:bg-accent text-muted-foreground"
                    )}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="p-4">
              <div style={{ width: "100%", height: 350 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="navGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--accent-lavender, #8b5cf6)" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="var(--accent-lavender, #8b5cf6)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.4} />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(v: string) => format(parseISO(v), "MMM yy")}
                      interval="preserveStartEnd"
                      minTickGap={50}
                    />
                    <YAxis
                      tick={{ fontSize: 11 }}
                      tickFormatter={(v: number) => fmtNaira(v)}
                      width={90}
                    />
                    <RechartsTooltip content={<ChartTooltip />} />
                    <Area
                      type="monotone"
                      dataKey="nav"
                      stroke="var(--accent-lavender, #8b5cf6)"
                      fill="url(#navGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Coverage disclosure repeated below chart for visibility */}
          {coverage && coveragePct !== null && (
            <div className="flex items-start gap-2 text-xs text-muted-foreground p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-color)]">
              <AlertCircle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
              <span>
                NAV is calculated from {coverage.priced_holdings_count} of{" "}
                {coverage.total_active_holdings_count} active holdings that have price data (
                {coveragePct}% coverage). The remaining {coverage.total_active_holdings_count - coverage.priced_holdings_count}{" "}
                holdings have no price history and are excluded from the NAV total.
              </span>
            </div>
          )}
        </>
      )}
    </div>
  );
}
