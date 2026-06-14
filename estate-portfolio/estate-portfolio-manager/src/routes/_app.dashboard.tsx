import { createFileRoute } from "@tanstack/react-router";
import {
  TrendingUp,
  DollarSign,
  BarChart2,
  Briefcase,
  Bell,
  ListX,
  CheckCircle2,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LabelList,
} from "recharts";
import { useDashboard } from "@/api/queries";
import { fmtNaira } from "@/lib/format";
import { SECTOR_CHART_COLORS } from "@/api/mock";
import { KpiCard } from "@/components/shared/KpiCard";
import { TxTypeBadge } from "@/components/shared/Badges";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";

export const Route = createFileRoute("/_app/dashboard")({
  component: DashboardPage,
});

function DashboardPage() {
  const { data, isLoading } = useDashboard();
  const isAdmin = useAuthStore((s) => s.isAdmin)();
  const { holdingsChartView, setHoldingsChartView } = useUIStore();

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="skeleton h-[120px] rounded-xl" />
        ))}
      </div>
    );
  }

  const safeParseFloat = (v: string | null | undefined): number =>
    v ? parseFloat(v) : 0;

  const displayValueStr = (v: string | null | undefined): string =>
    v ? fmtNaira(Number(v)) : "—";

  const displayPctStr = (v: string | null | undefined): string =>
    v ? `${v}%` : "—";

  const sectorAllocation = data.sector_allocation ?? [];
  const topHoldings = data.top_holdings ?? [];
  const recentTransactions = data.recent_transactions ?? [];

  const sectorChartData = sectorAllocation.map((s: any) => ({
    name: s.name || s.sector,
    value: safeParseFloat(s.value),
    displayPct: displayPctStr(s.pct),
    displayValue: displayValueStr(s.value),
  }));

  const topHoldingsChartData = topHoldings.map((h: any) => ({
    ticker: h.ticker,
    value: safeParseFloat(h.value),
    return_pct: safeParseFloat(h.return_pct),
    displayValue: displayValueStr(h.value),
    displayReturn: displayPctStr(h.return_pct),
  }));

  const gainPositive = Number(data.unrealised_gain_loss) >= 0;

  return (
    <div className="space-y-6">
      {/* KPI ROW */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Total Portfolio Value"
          value={data.total_portfolio_value}
          Icon={TrendingUp}
          accent="lavender"
          subtitle={`Unrealised gain ${fmtNaira(data.unrealised_gain_loss, { compact: true, sign: true })}`}
        />
        <KpiCard
          label="Total Invested"
          value={data.total_invested}
          Icon={DollarSign}
          accent="gold"
          subtitle="Cost basis"
        />
        <KpiCard
          label="Unrealised Gain/Loss"
          value={data.unrealised_gain_loss}
          Icon={BarChart2}
          accent={gainPositive ? "green" : "red"}
          formatter={(n) => fmtNaira(n, { sign: true })}
          subtitle={
            <span
              className={gainPositive ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]"}
            >
              {data.unrealised_gain_pct > 0 ? "+" : ""}
              {data.unrealised_gain_pct.toFixed(2)}% overall
            </span>
          }
        />
        <KpiCard
          label="Total Holdings"
          value={data.total_holdings}
          Icon={Briefcase}
          accent="lavender"
          integer
          subtitle={
            isAdmin ? `${data.live_holdings} live · ${data.draft_holdings} draft` : undefined
          }
        />
      </div>

      {/* CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card className="lg:col-span-5">
          <CardHeader title="Sector Allocation" right={<PeriodPill />} />
          <div className="flex items-center gap-4">
            <div className="w-[200px] h-[200px] relative shrink-0">
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={sectorChartData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                  >
                    {sectorChartData.map((_, i) => (
                      <Cell key={i} fill={SECTOR_CHART_COLORS[i % SECTOR_CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} formatter={(v, n, props) => props.payload.displayValue} />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <div className="font-mono text-[11px] text-[var(--text-muted)]">TOTAL</div>
                <div className="font-mono text-[13px] text-[var(--text-secondary)]">
                  {fmtNaira(Number(data.total_portfolio_value), { compact: true })}
                </div>
              </div>
            </div>
            <ul className="flex-1 space-y-2 min-w-0">
              {sectorChartData.map((s, i) => (
                <li key={s.name} className="flex items-center gap-2 text-[13px]">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ background: SECTOR_CHART_COLORS[i % SECTOR_CHART_COLORS.length] }}
                  />
                  <span className="flex-1 truncate text-[var(--text-primary)]">{s.name}</span>
                  <span className="font-mono text-[var(--text-secondary)]">
                    {s.displayPct}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </Card>

        <Card className="lg:col-span-7">
          <CardHeader
            title="Top Holdings"
            right={
              <div className="flex bg-muted p-1 rounded-md text-[12px]">
                <button
                  className={`px-2 py-1 rounded-sm ${
                    holdingsChartView === "value" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
                  }`}
                  onClick={() => setHoldingsChartView("value")}
                >
                  By Value
                </button>
                <button
                  className={`px-2 py-1 rounded-sm ${
                    holdingsChartView === "shares" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"
                  }`}
                  onClick={() => setHoldingsChartView("shares")}
                >
                  By Shares
                </button>
              </div>
            }
          />
          <div className="h-[260px]">
            <ResponsiveContainer>
              <BarChart
                data={topHoldingsChartData}
                layout="vertical"
                margin={{ left: 10, right: 60, top: 5, bottom: 5 }}
              >
                <CartesianGrid horizontal={false} stroke="var(--border)" />
                <XAxis
                  type="number"
                  tick={{ fontFamily: "DM Mono", fontSize: 11, fill: "var(--text-muted)" }}
                  tickFormatter={(v) =>
                    holdingsChartView === "value"
                      ? fmtNaira(Number(v), { compact: true }).replace("₦", "₦")
                      : (Number(v) / 1000).toFixed(0) + "k"
                  }
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="ticker"
                  tick={{ fontFamily: "DM Mono", fontSize: 12, fill: "var(--text-primary)" }}
                  axisLine={false}
                  tickLine={false}
                  width={70}
                />
                <Tooltip
                  cursor={{ fill: "var(--bg-subtle)" }}
                  contentStyle={tooltipStyle}
                  formatter={(v, n, props) =>
                    holdingsChartView === "value" ? props.payload.displayValue : Number(v).toLocaleString()
                  }
                />
                <Bar
                  dataKey={holdingsChartView === "value" ? "value" : "shares"}
                  fill="var(--accent-lavender)"
                  radius={[0, 4, 4, 0]}
                >
                  {holdingsChartView === "value" && (
                    <LabelList
                      dataKey="displayReturn"
                      position="right"
                      style={{
                        fill: "var(--text-secondary)",
                        fontSize: 12,
                        fontFamily: "DM Mono",
                      }}
                    />
                  )}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* BOTTOM ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card className="lg:col-span-7">
          <CardHeader
            title="Recent Transactions"
            right={
              <a
                href="/transactions"
                className="text-[13px] text-[var(--accent-lavender)] hover:underline"
              >
                View all →
              </a>
            }
          />
          {data.recent_transactions.length === 0 ? (
            <Empty Icon={ListX} text="No transactions yet" />
          ) : (
            <div className="overflow-x-auto -mx-2">
              <table className="w-full text-[13px]">
                <thead>
                  <tr className="text-[11px] uppercase tracking-wider text-[var(--text-secondary)]">
                    <Th>Date</Th>
                    <Th>Ticker</Th>
                    <Th>Type</Th>
                    <Th right>Shares</Th>
                    <Th right>Amount</Th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_transactions.map((tx, i) => (
                    <tr
                      key={i}
                      className="border-t border-[var(--border)] hover:bg-[var(--bg-subtle)]"
                    >
                      <Td mono>{tx.date}</Td>
                      <Td mono className="font-semibold">
                        {tx.ticker}
                      </Td>
                      <Td>
                        <TxTypeBadge type={tx.type} />
                      </Td>
                      <Td mono right>
                        {tx.shares ? tx.shares.toLocaleString() : "—"}
                      </Td>
                      <Td mono right>
                        {tx.amount ? fmtNaira(tx.amount) : "—"}
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card className="lg:col-span-5">
          <CardHeader
            title="Action Items"
            right={<Bell className="w-4 h-4 text-[var(--text-muted)]" />}
          />
          {data.action_items.filter((a) => a.count > 0).length === 0 ? (
            <div className="text-center py-6">
              <CheckCircle2 className="w-12 h-12 mx-auto text-[var(--accent-green)]" />
              <div className="mt-3 text-[14px] text-[var(--text-secondary)]">
                Portfolio up to date
              </div>
            </div>
          ) : (
            <ul className="space-y-2">
              {data.action_items
                .filter((a) => a.count > 0)
                .map((a) => (
                  <li
                    key={a.id}
                    className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-subtle)] hover:bg-[var(--bg-canvas)] cursor-pointer transition-colors"
                  >
                    {a.severity === "amber" ? (
                      <ArrowUpRight className="w-4 h-4 text-[var(--accent-amber)]" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4 text-[var(--accent-red)]" />
                    )}
                    <span className="flex-1 text-[13px] text-[var(--text-primary)]">
                      <span className="font-mono font-semibold mr-1">{a.count}</span>
                      {a.label}
                    </span>
                    <span
                      className="font-mono text-[11px] font-semibold px-2 py-0.5 rounded-full"
                      style={{
                        background:
                          a.severity === "amber"
                            ? "color-mix(in oklab, var(--accent-amber) 18%, transparent)"
                            : "color-mix(in oklab, var(--accent-red) 18%, transparent)",
                        color: a.severity === "amber" ? "var(--accent-amber)" : "var(--accent-red)",
                      }}
                    >
                      {a.severity === "red" ? "!" : a.count}
                    </span>
                    <ChevronRight className="w-4 h-4 text-[var(--text-muted)]" />
                  </li>
                ))}
            </ul>
          )}
          <div className="mt-4 text-right text-[11px] font-mono text-[var(--text-muted)]">
            Last updated:{" "}
            {new Date(data.last_updated).toLocaleString("en-NG", {
              weekday: "short",
              month: "short",
              day: "numeric",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}{" "}
            WAT
          </div>
        </Card>
      </div>
    </div>
  );
}

const tooltipStyle: React.CSSProperties = {
  background: "var(--bg-surface)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontFamily: "DM Mono",
  fontSize: 12,
  color: "var(--text-primary)",
  boxShadow: "var(--shadow-dropdown)",
};

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-[var(--bg-surface)] rounded-xl p-5 shadow-card ${className}`}>
      {children}
    </div>
  );
}
function CardHeader({ title, right }: { title: string; right?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-[16px] font-semibold text-[var(--text-primary)]">{title}</h3>
      {right}
    </div>
  );
}
function PeriodPill() {
  return (
    <button className="text-[13px] text-[var(--text-secondary)] px-2.5 py-1 rounded-md hover:bg-[var(--bg-subtle)] flex items-center gap-1">
      Monthly <ChevronRight className="w-3 h-3 rotate-90" />
    </button>
  );
}
function Th({ children, right }: { children: React.ReactNode; right?: boolean }) {
  return (
    <th className={`px-2 py-2 font-semibold ${right ? "text-right" : "text-left"}`}>{children}</th>
  );
}
function Td({
  children,
  mono,
  right,
  className = "",
}: {
  children: React.ReactNode;
  mono?: boolean;
  right?: boolean;
  className?: string;
}) {
  return (
    <td
      className={`px-2 py-2.5 ${mono ? "font-mono tabular-nums" : ""} ${right ? "text-right" : ""} text-[var(--text-primary)] ${className}`}
    >
      {children}
    </td>
  );
}
function Empty({ Icon, text }: { Icon: typeof ListX; text: string }) {
  return (
    <div className="text-center py-10">
      <Icon className="w-10 h-10 mx-auto text-[var(--text-muted)]" />
      <div className="mt-2 text-[14px] text-[var(--text-secondary)]">{text}</div>
    </div>
  );
}
