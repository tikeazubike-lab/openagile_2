import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  Search,
  Filter,
  ChevronRight,
  Wallet,
  CheckCircle2,
  Users,
  Database,
  ExternalLink,
  Phone,
  Mail,
  MapPin,
  Globe,
} from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  CartesianGrid,
} from "recharts";
import { apiFetch } from "@/api/queries";
import type { Claim, Registrar } from "@/types";
import { fmtNaira } from "@/lib/format";

export const Route = createFileRoute("/_app/claims")({
  component: ClaimsPage,
});

// ─── Status mapping: lifecycle_status → UI status ─────────────────────────

type UiStatus = "Unresolved" | "Unclaimed" | "Claimed";
type MandateStatus = "Active" | "None";

const statusBadge: Record<UiStatus, string> = {
  Unresolved: "bg-primary/15 text-primary border-primary/30",
  Unclaimed: "bg-warning/15 text-warning border-warning/30",
  Claimed: "bg-success/15 text-success border-success/30",
};

const mandateBadge: Record<MandateStatus, string> = {
  Active: "bg-success/15 text-success border-success/30",
  None: "bg-destructive/15 text-destructive border-destructive/30",
};

function fmtClaimAmount(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return fmtNaira(n);
}

// ─── Page component ──────────────────────────────────────────────────────────

function ClaimsPage() {
  // ─── API queries ──────────────────────────────────────────────────────────
  const {
    data: claims,
    isLoading,
    error,
    refetch,
  } = useQuery<Claim[]>({
    queryKey: ["claims"],
    queryFn: () => apiFetch<Claim[]>("/api/v1/claims"),
  });

  const { data: registrars } = useQuery<Registrar[]>({
    queryKey: ["registrars"],
    queryFn: () => apiFetch<Registrar[]>("/api/v1/registrars"),
  });

  // ─── Local state ──────────────────────────────────────────────────────────
  const [q, setQ] = useState("");
  const [regFilter, setRegFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [openRow, setOpenRow] = useState<Claim | null>(null);
  const [profileReg, setProfileReg] = useState<Registrar | null>(null);

  // ─── Derived / memoised ──────────────────────────────────────────────────

  const enriched = useMemo(() => {
    if (!claims) return [];
    return claims.map((c) => {
      const ls = c.lifecycle_status ?? "unresolved";
      const uiStatus: UiStatus = (ls.charAt(0).toUpperCase() + ls.slice(1)) as UiStatus;
      const mandate: MandateStatus = uiStatus === "Claimed" ? "Active" : "None";
      const ref = c.claim_reference || (c.holding ? `${c.holding.company_ticker}-${c.id}` : `C-${c.id}`);
      const amount = c.actual_payout ?? c.expected_payout ?? 0;
      const year =
        c.payout_date
          ? new Date(c.payout_date).getFullYear()
          : c.date_filed
            ? new Date(c.date_filed).getFullYear()
            : undefined;
      const lastUpdated = c.payout_date ?? c.date_filed;
      return {
        claim: c,
        ref,
        company: c.holding?.company_ticker ?? "—",
        registrar: c.holding?.registrar_name ?? "Unknown",
        shares: c.holding?.num_shares ?? 0,
        uiStatus,
        mandate,
        amount,
        year,
        lastUpdated,
        notes: c.notes ?? "",
      };
    });
  }, [claims]);

  const filtered = useMemo(
    () =>
      enriched.filter(
        (r) =>
          (regFilter === "all" || r.registrar === regFilter) &&
          (statusFilter === "all" || r.uiStatus === statusFilter) &&
          (q === "" ||
            r.ref.toLowerCase().includes(q.toLowerCase()) ||
            r.company.toLowerCase().includes(q.toLowerCase())),
      ),
    [enriched, q, regFilter, statusFilter],
  );

  const totals = useMemo(() => {
    const unclaimedValue = enriched
      .filter((r) => r.uiStatus === "Unclaimed")
      .reduce((s, r) => s + r.amount, 0);
    const claimedValue = enriched
      .filter((r) => r.uiStatus === "Claimed")
      .reduce((s, r) => s + r.amount, 0);
    return {
      unclaimedValue,
      claimedValue,
      totalRecords: enriched.length,
      unclaimedCount: enriched.filter((r) => r.uiStatus === "Unclaimed").length,
      registrars: new Set(enriched.map((r) => r.registrar)).size,
    };
  }, [enriched]);

  const registrarStats = useMemo(() => {
    const map: Record<
      string,
      { unclaimed: number; claimed: number; uValue: number; cValue: number }
    > = {};
    enriched.forEach((r) => {
      if (!map[r.registrar])
        map[r.registrar] = { unclaimed: 0, claimed: 0, uValue: 0, cValue: 0 };
      if (r.uiStatus === "Claimed") {
        map[r.registrar].claimed++;
        map[r.registrar].cValue += r.amount;
      } else {
        map[r.registrar].unclaimed++;
        map[r.registrar].uValue += r.amount;
      }
    });
    return Object.entries(map).map(([name, v]) => ({
      ...v,
      name,
      total: v.unclaimed + v.claimed,
      rate: v.total > 0 ? Math.round((v.claimed / v.total) * 100) : 0,
    }));
  }, [enriched]);

  const regOptions = useMemo(() => {
    const names = new Set(enriched.map((r) => r.registrar));
    return Array.from(names).sort();
  }, [enriched]);

  // ─── Chart data ───────────────────────────────────────────────────────────

  const donutData = registrarStats.map((r) => ({ name: r.name, value: r.uValue }));
  const barData = [...registrarStats]
    .sort((a, b) => b.uValue - a.uValue)
    .slice(0, 5)
    .map((r) => ({ name: r.name.split(" ")[0].toUpperCase(), value: r.uValue }));
  const splitData = [
    { name: "Unclaimed", value: totals.unclaimedValue },
    { name: "Claimed", value: totals.claimedValue },
  ];

  const chartColors = [
    "var(--chart-1)",
    "var(--chart-2)",
    "var(--chart-3)",
    "var(--chart-4)",
    "var(--chart-5)",
    "#7C7AE6",
  ];

  // ─── Loading state ────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-28 animate-pulse rounded-xl bg-[var(--bg-surface)] border border-[var(--border)]"
            />
          ))}
        </div>
        <div className="h-80 animate-pulse rounded-xl bg-[var(--bg-surface)] border border-[var(--border)]" />
        <div className="h-64 animate-pulse rounded-xl bg-[var(--bg-surface)] border border-[var(--border)]" />
      </div>
    );
  }

  // ─── Error state ──────────────────────────────────────────────────────────

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="rounded-xl bg-[var(--accent-red)]/10 border border-[var(--accent-red)]/30 p-4 text-center max-w-md">
          <p className="text-[var(--accent-red)] font-medium text-sm">
            Failed to load claims data
          </p>
          <p className="text-[var(--text-muted)] text-xs mt-1">
            {error instanceof Error ? error.message : "An unknown error occurred"}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  // ─── Empty state ──────────────────────────────────────────────────────────

  if (!enriched.length) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <Database className="w-12 h-12 text-[var(--text-muted)]" />
        <p className="text-[var(--text-muted)] text-sm">
          No dividend records found. Claims will appear here once dividend data is recorded.
        </p>
      </div>
    );
  }

  // ─── Main render ──────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="TOTAL UNCLAIMED VALUE"
          value={fmtClaimAmount(totals.unclaimedValue)}
          sub={
            <span>
              <span className="text-[var(--accent-amber)]">Unclaimed</span> across{" "}
              {totals.unclaimedCount} records
            </span>
          }
          icon={<Wallet className="h-4 w-4 text-[var(--text-muted)]" />}
        />
        <KpiCard
          label="TOTAL CLAIMED VALUE"
          value={fmtClaimAmount(totals.claimedValue)}
          sub={
            <span>
              <span className="text-[var(--accent-green)]">Recovered</span> across{" "}
              {totals.totalRecords - totals.unclaimedCount} records
            </span>
          }
          icon={<CheckCircle2 className="h-4 w-4 text-[var(--text-muted)]" />}
        />
        <KpiCard
          label="REGISTRARS"
          value={String(totals.registrars)}
          sub={<>{registrarStats.length} active</>}
          icon={<Users className="h-4 w-4 text-[var(--text-muted)]" />}
        />
        <KpiCard
          label="TOTAL CLAIMS"
          value={String(totals.totalRecords)}
          sub={
            <span>
              {totals.unclaimedCount} pending recovery
            </span>
          }
          icon={<Database className="h-4 w-4 text-[var(--text-muted)]" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <ChartCard title="Unclaimed by Registrar" subtitle="Distribution">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={donutData}
                dataKey="value"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                stroke="var(--bg-surface)"
                strokeWidth={2}
              >
                {donutData.map((_, i) => (
                  <Cell key={i} fill={chartColors[i % chartColors.length]} />
                ))}
              </Pie>
              <RTooltip
                contentStyle={{
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                formatter={(v: number) => fmtClaimAmount(v)}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
            {registrarStats.map((r, i) => (
              <div key={r.name} className="flex items-center gap-2">
                <span
                  className="h-2 w-2 rounded-full shrink-0"
                  style={{ background: chartColors[i % chartColors.length] }}
                />
                <span className="text-[var(--text-muted)] truncate flex-1">
                  {r.name.split(" ")[0]}
                </span>
                <span className="text-[var(--text-primary)]/80">
                  {totals.unclaimedValue > 0
                    ? ((r.uValue / totals.unclaimedValue) * 100).toFixed(1)
                    : "0.0"}
                  %
                </span>
              </div>
            ))}
          </div>
        </ChartCard>

        <ChartCard title="Top Registrars by Unclaimed Value" subtitle="Ranked">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData} layout="vertical" margin={{ left: 10, right: 20 }}>
              <CartesianGrid horizontal={false} stroke="var(--border)" />
              <XAxis
                type="number"
                tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                tickFormatter={(v: number) => `₦${(v / 1_000_000).toFixed(1)}M`}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <RTooltip
                cursor={{ fill: "var(--accent-lavender)", opacity: 0.3 }}
                contentStyle={{
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                formatter={(v: number) => fmtClaimAmount(v)}
              />
              <Bar dataKey="value" fill="var(--accent-lavender)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Claimed vs Unclaimed" subtitle="Portfolio split">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={splitData}
                dataKey="value"
                innerRadius={60}
                outerRadius={90}
                stroke="var(--bg-surface)"
                strokeWidth={2}
              >
                <Cell fill="var(--accent-lavender)" />
                <Cell fill="var(--accent-green)" />
              </Pie>
              <RTooltip
                contentStyle={{
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                formatter={(v: number) => fmtClaimAmount(v)}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 space-y-2 text-xs">
            <SplitRow
              color="var(--accent-lavender)"
              label="Unclaimed"
              value={totals.unclaimedValue}
              total={totals.unclaimedValue + totals.claimedValue}
            />
            <SplitRow
              color="var(--accent-green)"
              label="Claimed"
              value={totals.claimedValue}
              total={totals.unclaimedValue + totals.claimedValue}
            />
          </div>
        </ChartCard>
      </div>

      {/* Registrar summary table */}
      <section className="glass-card p-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-base font-semibold text-[var(--text-primary)]">
              Claim Summary by Registrar
            </h2>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">
              Click a row to view registrar profile
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="text-[var(--accent-lavender)] hover:text-[var(--accent-lavender)] hover:bg-[var(--accent-lavender)]/10 text-xs"
          >
            Export CSV <ExternalLink className="ml-1 h-3 w-3" />
          </Button>
        </div>
        <div className="overflow-x-auto -mx-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)] border-b border-[var(--border)]">
                <th className="text-left px-6 py-3">REGISTRAR</th>
                <th className="text-right px-4 py-3">UNCLAIMED</th>
                <th className="text-right px-4 py-3">CLAIMED</th>
                <th className="text-right px-4 py-3">TOTAL</th>
                <th className="text-left px-4 py-3 w-[220px]">RECOVERY PROGRESS</th>
                <th className="text-right px-4 py-3">UNCLAIMED VALUE</th>
                <th className="text-right px-6 py-3">CLAIMED VALUE</th>
              </tr>
            </thead>
            <tbody>
              {registrarStats.map((r) => {
                const pct = r.total > 0 ? (r.claimed / r.total) * 100 : 0;
                const matchedReg = registrars?.find(
                  (reg) => reg.name === r.name,
                );
                return (
                  <tr
                    key={r.name}
                    onClick={() => {
                      if (matchedReg) setProfileReg(matchedReg);
                    }}
                    className="border-b border-[var(--border)]/50 hover:bg-[var(--accent-lavender)]/5 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-lg bg-[var(--accent-lavender)]/15 text-[var(--accent-lavender)] grid place-items-center text-xs font-semibold">
                          {r.name.slice(0, 2).toUpperCase()}
                        </div>
                        <span className="font-medium text-[var(--text-primary)]">
                          {r.name}
                        </span>
                      </div>
                    </td>
                    <td className="text-right px-4 py-4 text-[var(--accent-amber)]">
                      {r.unclaimed}
                    </td>
                    <td className="text-right px-4 py-4 text-[var(--accent-green)]">
                      {r.claimed}
                    </td>
                    <td className="text-right px-4 py-4 text-[var(--text-primary)]">
                      {r.total}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <Progress value={pct} className="h-1.5 bg-[var(--bg-subtle)]" />
                        <span className="text-[10px] text-[var(--text-muted)] tabular-nums w-9">
                          {pct.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="text-right px-4 py-4 tabular-nums text-[var(--text-primary)]">
                      {fmtClaimAmount(r.uValue)}
                    </td>
                    <td className="text-right px-6 py-4 tabular-nums text-[var(--text-muted)]">
                      {fmtClaimAmount(r.cValue)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Records table */}
      <section className="glass-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div>
            <h2 className="text-base font-semibold text-[var(--text-primary)]">
              Claim Records
            </h2>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">
              Showing {filtered.length} of {enriched.length} records
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--text-muted)]" />
              <Input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search account or company..."
                className="pl-9 h-9 w-64 bg-[var(--bg-surface)] border-[var(--border)] text-xs"
              />
            </div>
            <Select value={regFilter} onValueChange={setRegFilter}>
              <SelectTrigger className="h-9 w-[190px] bg-[var(--bg-surface)] border-[var(--border)] text-xs">
                <Filter className="h-3 w-3 mr-1 text-[var(--text-muted)]" />
                <SelectValue placeholder="Registrar" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All registrars</SelectItem>
                {regOptions.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-9 w-[140px] bg-[var(--bg-surface)] border-[var(--border)] text-xs">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                <SelectItem value="Unclaimed">Unclaimed</SelectItem>
                <SelectItem value="Claimed">Claimed</SelectItem>
                <SelectItem value="Unresolved">Unresolved</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="overflow-x-auto -mx-6">
          <table className="w-full text-sm">
            <thead className="sticky top-0">
              <tr className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)] border-b border-[var(--border)]">
                <th className="text-left px-6 py-3">ACCOUNT #</th>
                <th className="text-left px-4 py-3">COMPANY</th>
                <th className="text-left px-4 py-3">REGISTRAR</th>
                <th className="text-left px-4 py-3">STATUS</th>
                <th className="text-left px-4 py-3">LAST UPDATED</th>
                <th className="text-right px-6 py-3">ACTION</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, idx) => (
                <tr
                  key={r.ref + idx}
                  className="border-b border-[var(--border)]/50 hover:bg-[var(--accent-lavender)]/5 transition-colors"
                >
                  <td className="px-6 py-4 tabular-nums text-[var(--text-muted)]">
                    {r.ref}
                  </td>
                  <td className="px-4 py-4 font-medium text-[var(--text-primary)]">
                    {r.company}
                  </td>
                  <td className="px-4 py-4 text-[var(--text-muted)]">
                    {r.registrar}
                  </td>
                  <td className="px-4 py-4">
                    <StatusBadge status={r.uiStatus} />
                  </td>
                  <td className="px-4 py-4 text-[var(--text-muted)] tabular-nums">
                    {r.lastUpdated
                      ? new Date(r.lastUpdated).toLocaleDateString("en-NG", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })
                      : "—"}
                  </td>
                  <td className="text-right px-6 py-4">
                    <button
                      onClick={() => setOpenRow(r.claim)}
                      className="text-[var(--accent-lavender)] hover:text-[var(--accent-lavender)]/80 text-xs font-medium inline-flex items-center gap-1"
                    >
                      View Details <ChevronRight className="h-3 w-3" />
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="text-center py-16 text-[var(--text-muted)] text-sm"
                  >
                    No records match your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between pt-4 mt-2 border-t border-[var(--border)] text-xs text-[var(--text-muted)]">
          <span>Page 1 of 1</span>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" className="h-8 text-xs" disabled>
              Previous
            </Button>
            <Button variant="ghost" size="sm" className="h-8 text-xs" disabled>
              Next
            </Button>
          </div>
        </div>
      </section>

      {/* Detail Drawer */}
      <Sheet open={!!openRow} onOpenChange={(o) => !o && setOpenRow(null)}>
        <SheetContent className="w-full sm:max-w-md bg-[var(--bg-surface)] border-l border-[var(--border)] text-[var(--text-primary)] overflow-y-auto">
          {openRow && (() => {
            const r = enriched.find((e) => e.claim.id === openRow.id);
            if (!r) return null;
            return (
              <>
                <SheetHeader className="text-left">
                  <div className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)]">
                    CLAIM RECORD
                  </div>
                  <SheetTitle className="text-xl text-[var(--text-primary)]">
                    {r.company}
                  </SheetTitle>
                  <SheetDescription className="text-xs text-[var(--text-muted)]">
                    Account {r.ref}
                  </SheetDescription>
                </SheetHeader>

                <div className="mt-6 space-y-1 rounded-lg border border-[var(--border)] overflow-hidden">
                  <DetailRow label="Account Number" value={r.ref} />
                  <DetailRow label="Company" value={r.company} />
                  <DetailRow label="Registrar" value={r.registrar} />
                  <DetailRow
                    label="Share Quantity"
                    value={r.shares.toLocaleString()}
                  />
                  <DetailRow
                    label="Claim Year"
                    value={r.year ? String(r.year) : "—"}
                  />
                  <DetailRow
                    label="Claim Amount"
                    value={fmtClaimAmount(r.amount)}
                    highlight
                  />
                  <DetailRow
                    label="Status"
                    value={<StatusBadge status={r.uiStatus} />}
                  />
                  <DetailRow
                    label="E-Dividend Mandate"
                    value={<MandateBadge s={r.mandate} />}
                  />
                  <DetailRow
                    label="Last Updated"
                    value={
                      r.lastUpdated
                        ? new Date(r.lastUpdated).toLocaleDateString("en-NG", {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          })
                        : "—"
                    }
                  />
                </div>

                <div className="mt-5">
                  <div className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)] mb-2">
                    NOTES
                  </div>
                  <p className="text-sm text-[var(--text-primary)]/80 leading-relaxed p-4 rounded-lg bg-[var(--bg-subtle)] border border-[var(--border)]">
                    {r.notes || "No notes."}
                  </p>
                </div>

                <div className="mt-8">
                  <Button
                    className="w-full h-11 bg-[var(--accent-lavender)] text-[var(--bg-canvas)] hover:bg-[var(--accent-lavender)]/90 font-medium"
                    onClick={() => {
                      const matchedReg = registrars?.find(
                        (reg) => reg.name === r.registrar,
                      );
                      setOpenRow(null);
                      if (matchedReg) setProfileReg(matchedReg);
                    }}
                  >
                    View Registrar Holdings
                  </Button>
                </div>
              </>
            );
          })()}
        </SheetContent>
      </Sheet>

      {/* Registrar Profile Drawer */}
      <Sheet open={!!profileReg} onOpenChange={(o) => !o && setProfileReg(null)}>
        <SheetContent className="w-full sm:max-w-2xl bg-[var(--bg-surface)] border-l border-[var(--border)] text-[var(--text-primary)] overflow-y-auto">
          {profileReg && (
            <>
              <SheetHeader className="text-left">
                <div className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)]">
                  REGISTRAR PROFILE
                </div>
                <SheetTitle className="text-xl text-[var(--text-primary)]">
                  {profileReg.name}
                </SheetTitle>
              </SheetHeader>

              {/* Info card */}
              <div className="mt-5 rounded-xl border border-[var(--border)] bg-[var(--bg-subtle)] p-5">
                <div className="flex items-start gap-4">
                  <div className="h-14 w-14 rounded-xl bg-[var(--accent-lavender)]/15 text-[var(--accent-lavender)] grid place-items-center text-lg font-semibold">
                    {profileReg.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div className="flex-1 space-y-2 text-xs">
                    {profileReg.website && (
                      <div className="flex items-center gap-2 text-[var(--text-muted)]">
                        <Globe className="h-3.5 w-3.5 text-[var(--accent-lavender)] shrink-0" />
                        {profileReg.website}
                      </div>
                    )}
                    {profileReg.phone && (
                      <div className="flex items-center gap-2 text-[var(--text-muted)]">
                        <Phone className="h-3.5 w-3.5 text-[var(--accent-lavender)] shrink-0" />
                        {profileReg.phone}
                      </div>
                    )}
                    {profileReg.email && (
                      <div className="flex items-center gap-2 text-[var(--text-muted)]">
                        <Mail className="h-3.5 w-3.5 text-[var(--accent-lavender)] shrink-0" />
                        {profileReg.email}
                      </div>
                    )}
                    {profileReg.address && (
                      <div className="flex items-center gap-2 text-[var(--text-muted)]">
                        <MapPin className="h-3.5 w-3.5 text-[var(--accent-lavender)] shrink-0" />
                        {profileReg.address}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="mt-4 grid grid-cols-2 gap-3">
                {(() => {
                  const stats = registrarStats.find(
                    (s) => s.name === profileReg.name,
                  );
                  return (
                    <>
                      <MiniStat
                        label="TOTAL RECORDS"
                        value={String(stats?.total ?? 0)}
                      />
                      <MiniStat
                        label="CLAIMED"
                        value={String(stats?.claimed ?? 0)}
                        accent="success"
                      />
                      <MiniStat
                        label="UNCLAIMED"
                        value={String(stats?.unclaimed ?? 0)}
                        accent="warning"
                      />
                      <MiniStat
                        label="UNCLAIMED VALUE"
                        value={fmtClaimAmount(stats?.uValue ?? 0)}
                        accent="primary"
                      />
                    </>
                  );
                })()}
              </div>

              {/* Holdings */}
              <div className="mt-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                    Claims Held by Registrar
                  </h3>
                </div>
                <div className="rounded-lg border border-[var(--border)] overflow-hidden">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)] bg-[var(--bg-subtle)]">
                        <th className="text-left px-3 py-2.5">COMPANY</th>
                        <th className="text-left px-3 py-2.5">ACCOUNT</th>
                        <th className="text-right px-3 py-2.5">AMOUNT</th>
                        <th className="text-left px-3 py-2.5">YEAR</th>
                        <th className="text-left px-3 py-2.5">STATUS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {enriched
                        .filter((r) => r.registrar === profileReg.name)
                        .map((r, idx) => (
                          <tr
                            key={r.ref + idx}
                            className="border-t border-[var(--border)]/50"
                          >
                            <td className="px-3 py-2.5 font-medium text-[var(--text-primary)]">
                              {r.company}
                            </td>
                            <td className="px-3 py-2.5 text-[var(--text-muted)]">
                              {r.ref}
                            </td>
                            <td className="px-3 py-2.5 text-right tabular-nums text-[var(--text-primary)]">
                              {fmtClaimAmount(r.amount)}
                            </td>
                            <td className="px-3 py-2.5 text-[var(--text-muted)]">
                              {r.year ? String(r.year) : "—"}
                            </td>
                            <td className="px-3 py-2.5">
                              <StatusBadge status={r.uiStatus} />
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

// ─── Subcomponents ───────────────────────────────────────────────────────────

function KpiCard({
  label,
  value,
  sub,
  icon,
}: {
  label: string;
  value: string;
  sub: React.ReactNode;
  icon: React.ReactNode;
}) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-start justify-between">
        <div className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)]">
          {label}
        </div>
        <div>{icon}</div>
      </div>
      <div className="mt-3 text-3xl font-semibold tabular-nums tracking-tight text-[var(--text-primary)]">
        {value}
      </div>
      <div className="mt-1.5 text-xs text-[var(--text-muted)]">{sub}</div>
    </div>
  );
}

function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-sm font-semibold text-[var(--text-primary)]">
            {title}
          </div>
          {subtitle && (
            <div className="text-xs text-[var(--text-muted)] mt-0.5">
              {subtitle}
            </div>
          )}
        </div>
      </div>
      {children}
    </div>
  );
}

function SplitRow({
  color,
  label,
  value,
  total,
}: {
  color: string;
  label: string;
  value: number;
  total: number;
}) {
  const pct = total > 0 ? (value / total) * 100 : 0;
  return (
    <div className="flex items-center gap-2">
      <span
        className="h-2 w-2 rounded-full shrink-0"
        style={{ background: color }}
      />
      <span className="text-[var(--text-muted)] flex-1">{label}</span>
      <span className="tabular-nums text-[var(--text-primary)]">
        {fmtClaimAmount(value)}
      </span>
      <span className="text-[var(--text-muted)] tabular-nums w-12 text-right">
        {pct.toFixed(1)}%
      </span>
    </div>
  );
}

function StatusBadge({ status }: { status: UiStatus }) {
  return (
    <Badge
      variant="outline"
      className={`${statusBadge[status]} font-medium text-[10px] px-2 py-0.5`}
    >
      {status.toLowerCase()}
    </Badge>
  );
}

function MandateBadge({ s }: { s: MandateStatus }) {
  return (
    <Badge
      variant="outline"
      className={`${mandateBadge[s]} text-[10px] px-2 py-0.5`}
    >
      {s}
    </Badge>
  );
}

function DetailRow({
  label,
  value,
  highlight,
}: {
  label: string;
  value: React.ReactNode;
  highlight?: boolean;
}) {
  return (
    <div className="flex items-center justify-between px-4 py-3 bg-[var(--bg-subtle)] border-b border-[var(--border)] last:border-b-0">
      <span className="text-xs text-[var(--text-muted)]">{label}</span>
      <span
        className={`text-sm ${
          highlight ? "text-[var(--accent-lavender)] font-semibold" : ""
        }`}
      >
        {value}
      </span>
    </div>
  );
}

function MiniStat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: "primary" | "success" | "warning";
}) {
  const colorMap: Record<string, string> = {
    primary: "text-[var(--accent-lavender)]",
    success: "text-[var(--accent-green)]",
    warning: "text-[var(--accent-amber)]",
  };
  const color = accent ? colorMap[accent] ?? "" : "";
  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-subtle)] p-4">
      <div className="text-[10px] font-semibold tracking-widest text-[var(--text-muted)]">
        {label}
      </div>
      <div className={`mt-2 text-xl font-semibold tabular-nums ${color}`}>
        {value}
      </div>
    </div>
  );
}
