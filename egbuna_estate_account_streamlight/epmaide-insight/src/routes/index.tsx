import { createFileRoute } from "@tanstack/react-router";
import {
  LayoutGrid,
  Briefcase,
  Building2,
  Coins,
  LineChart,
  ArrowLeftRight,
  ClipboardList,
  Eye,
  TrendingUp,
  Scale,
  Search,
  Sun,
  Bell,
  LogOut,
  TrendingUp as TrendUp,
  DollarSign,
  BarChart3,
} from "lucide-react";
import { AiAssistant } from "@/components/AiAssistant";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "EPM — Estate Portfolio Manager" },
      { name: "description", content: "Dark-themed Nigerian stock portfolio dashboard with an AI assistant." },
    ],
  }),
  component: Dashboard,
});

const NAV = [
  { icon: LayoutGrid, label: "Dashboard", active: true },
  { icon: Briefcase, label: "Holdings", dot: true },
  { icon: Building2, label: "Companies" },
  { icon: Coins, label: "Dividends" },
  { icon: LineChart, label: "Price History" },
  { icon: ArrowLeftRight, label: "Transactions", dot: true },
  { icon: ClipboardList, label: "Registrars" },
  { icon: Eye, label: "Watchlist" },
  { icon: TrendingUp, label: "NAV History" },
  { icon: Scale, label: "Rebalancing" },
];

const SECTORS = [
  { label: "Consumer Goods", value: 78.61, color: "oklch(0.78 0.10 295)" },
  { label: "Conglomerate", value: 7.51, color: "oklch(0.78 0.08 85)" },
  { label: "Industrials", value: 7.29, color: "oklch(0.72 0.17 150)" },
  { label: "Agriculture", value: 5.41, color: "oklch(0.74 0.16 60)" },
  { label: "Hospitality", value: 0.39, color: "oklch(0.65 0.22 25)" },
  { label: "Oil & Gas", value: 0.26, color: "oklch(0.70 0.14 230)" },
  { label: "Insurance", value: 0.22, color: "oklch(0.65 0.18 295)" },
  { label: "Banking", value: 0.19, color: "oklch(0.70 0.18 150)" },
  { label: "Healthcare", value: 0.07, color: "oklch(0.80 0.08 295)" },
  { label: "Services", value: 0.04, color: "oklch(0.78 0.10 85)" },
  { label: "Real Estate", value: 0.01, color: "oklch(0.72 0.17 150)" },
];

const HOLDINGS = [
  { ticker: "NESTLE", value: 29.4 },
  { ticker: "VITAFOAM", value: 8.1 },
  { ticker: "UACN", value: 4.3 },
  { ticker: "OKOMUOIL", value: 3.2 },
  { ticker: "NB", value: 1.2 },
];

const TX = [
  { date: "2025-12-29", ticker: "OKOMUOIL", shares: 1530 },
  { date: "2025-12-29", ticker: "TEXACO", shares: 2839 },
  { date: "2025-12-29", ticker: "IKEJAHOTEL", shares: 4320 },
  { date: "2025-12-29", ticker: "UACNPROP", shares: 1000 },
  { date: "2025-12-29", ticker: "METALBOX", shares: 300 },
];

function Dashboard() {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 flex flex-col bg-sidebar border-r border-sidebar-border">
        <div className="px-5 pt-5 pb-4">
          <div className="text-2xl font-bold tracking-tight">EPM</div>
          <div className="text-xs text-muted-foreground">Estate Portfolio</div>
        </div>
        <div className="px-3 pb-3">
          <div className="flex items-center gap-2 rounded-md bg-background/40 border border-border px-2.5 py-1.5">
            <Search className="h-3.5 w-3.5 text-muted-foreground" />
            <input
              placeholder="Search..."
              className="flex-1 bg-transparent text-xs outline-none placeholder:text-muted-foreground"
            />
            <kbd className="text-[10px] px-1.5 py-0.5 rounded border border-border text-muted-foreground">/</kbd>
          </div>
        </div>
        <div className="px-5 pt-2 pb-1 text-[10px] uppercase tracking-wider text-muted-foreground">Main</div>
        <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className={`flex items-center gap-2.5 rounded-md px-3 py-2 text-sm cursor-pointer transition-colors ${
                  item.active
                    ? "bg-primary/20 text-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="flex-1">{item.label}</span>
                {item.dot && <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />}
              </div>
            );
          })}
        </nav>
        <div className="px-5 pt-3 pb-1 text-[10px] uppercase tracking-wider text-muted-foreground">Admin</div>
        <div className="m-3 flex items-center gap-2.5 rounded-lg border border-border bg-card/60 p-2.5">
          <div className="grid h-8 w-8 place-items-center rounded-full bg-primary/20 text-primary text-xs font-semibold">
            z
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">Zubby</div>
            <div className="text-[11px] text-muted-foreground">Admin</div>
          </div>
          <button className="text-muted-foreground hover:text-foreground">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 min-w-0 p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <div className="flex items-center gap-2">
            <button className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground">
              <Sun className="h-4 w-4" />
            </button>
            <button className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground">
              <Bell className="h-4 w-4" />
            </button>
            <div className="grid h-8 w-8 place-items-center rounded-full bg-primary/20 text-primary text-xs font-semibold">
              z
            </div>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <Kpi label="Total Portfolio Value" value="₦49,480,693.09" sub="Unrealised gain +₦49.5M" icon={TrendUp} />
          <Kpi label="Total Invested" value="₦0.00" sub="Cost basis" icon={DollarSign} />
          <Kpi
            label="Unrealised Gain/Loss"
            value="+ ₦49,480,693.09"
            sub="0.00% overall"
            subClass="text-[oklch(0.74_0.16_150)]"
            icon={BarChart3}
          />
          <Kpi label="Total Holdings" value="72" sub="72 live · 0 draft" icon={Briefcase} />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <Card title="Sector Allocation" right={<span className="text-xs text-muted-foreground">Monthly ▾</span>}>
            <div className="flex items-center gap-6">
              <DonutChart items={SECTORS} />
              <ul className="flex-1 space-y-1.5 min-w-0">
                {SECTORS.map((s) => (
                  <li key={s.label} className="flex items-center gap-2 text-sm">
                    <span className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
                    <span className="flex-1 truncate text-foreground/90">{s.label}</span>
                    <span className="tabular text-muted-foreground text-xs">{s.value.toFixed(2)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>

          <Card
            title="Top Holdings"
            right={
              <div className="flex text-xs rounded-md border border-border overflow-hidden">
                <span className="px-2.5 py-1 bg-muted text-foreground">By Value</span>
                <span className="px-2.5 py-1 text-muted-foreground">By Shares</span>
              </div>
            }
          >
            <div className="space-y-3">
              {HOLDINGS.map((h) => {
                const max = HOLDINGS[0].value;
                return (
                  <div key={h.ticker} className="flex items-center gap-3 text-xs">
                    <span className="w-20 text-muted-foreground tabular">{h.ticker}</span>
                    <div className="flex-1 h-6 bg-muted/30 rounded">
                      <div
                        className="h-full rounded bg-primary/80"
                        style={{ width: `${(h.value / max) * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              <div className="flex justify-between text-[10px] text-muted-foreground pl-[88px] pt-1 tabular">
                <span>₦0.00</span>
                <span>₦7.5M</span>
                <span>₦15.0M</span>
                <span>₦22.5M</span>
                <span>₦30.0M</span>
              </div>
            </div>
          </Card>
        </div>

        {/* Bottom row */}
        <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-4">
          <Card title="Recent Transactions" right={<a className="text-xs text-primary">View all →</a>}>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground grid grid-cols-[1.2fr_1.2fr_0.8fr_0.8fr_0.8fr] gap-3 px-1 pb-2 border-b border-border">
              <span>Date</span>
              <span>Ticker</span>
              <span>Type</span>
              <span className="text-right">Shares</span>
              <span className="text-right">Amount</span>
            </div>
            <div className="divide-y divide-border">
              {TX.map((t, i) => (
                <div
                  key={i}
                  className="grid grid-cols-[1.2fr_1.2fr_0.8fr_0.8fr_0.8fr] gap-3 px-1 py-2.5 text-sm items-center tabular"
                >
                  <span className="text-muted-foreground">{t.date}</span>
                  <span className="font-medium">{t.ticker}</span>
                  <span>
                    <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] bg-[oklch(0.74_0.16_150/0.15)] text-[oklch(0.78_0.16_150)] border border-[oklch(0.74_0.16_150/0.25)]">
                      buy
                    </span>
                  </span>
                  <span className="text-right">{t.shares.toLocaleString()}</span>
                  <span className="text-right text-muted-foreground">—</span>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Action Items" right={<Bell className="h-4 w-4 text-muted-foreground" />}>
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <div className="grid h-12 w-12 place-items-center rounded-full border-2 border-[oklch(0.74_0.16_150)] text-[oklch(0.78_0.16_150)] mb-3">
                ✓
              </div>
              <div className="text-sm">Portfolio up to date</div>
              <div className="text-[11px] text-muted-foreground mt-4">
                Last updated: Sun, 21 Jun 2026, 09:18 WAT
              </div>
            </div>
          </Card>
        </div>
      </main>

      {/* Floating AI Assistant */}
      <AiAssistant />
    </div>
  );
}

function Kpi({
  label,
  value,
  sub,
  subClass,
  icon: Icon,
}: {
  label: string;
  value: string;
  sub: string;
  subClass?: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>
        <Icon className="h-4 w-4 text-primary/70" />
      </div>
      <div className="text-2xl font-semibold tabular break-all">{value}</div>
      <div className={`text-xs mt-2 ${subClass ?? "text-muted-foreground"}`}>{sub}</div>
    </div>
  );
}

function Card({
  title,
  right,
  children,
}: {
  title: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold">{title}</h2>
        {right}
      </div>
      {children}
    </div>
  );
}

function DonutChart({ items }: { items: { label: string; value: number; color?: string }[] }) {
  const total = items.reduce((s, i) => s + i.value, 0);
  const radius = 60;
  const stroke = 22;
  const c = 2 * Math.PI * radius;
  let offset = 0;
  return (
    <div className="relative shrink-0" style={{ width: 160, height: 160 }}>
      <svg width={160} height={160} viewBox="0 0 160 160" className="-rotate-90">
        <circle cx={80} cy={80} r={radius} fill="none" stroke="oklch(0.22 0.014 270)" strokeWidth={stroke} />
        {items.map((it) => {
          const len = (it.value / total) * c;
          const dasharray = `${len} ${c - len}`;
          const el = (
            <circle
              key={it.label}
              cx={80}
              cy={80}
              r={radius}
              fill="none"
              stroke={it.color}
              strokeWidth={stroke}
              strokeDasharray={dasharray}
              strokeDashoffset={-offset}
            />
          );
          offset += len;
          return el;
        })}
      </svg>
      <div className="absolute inset-0 grid place-items-center text-center">
        <div>
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Total</div>
          <div className="text-sm font-semibold tabular">₦49.5M</div>
        </div>
      </div>
    </div>
  );
}
