import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, Building2, TrendingUp, Loader2 } from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from "recharts";
import { format } from "date-fns";
import { useCompany, useHoldingsByCompany, usePriceHistory } from "@/api/queries";
import { SectorBadge } from "@/components/shared/Badges";
import { fmtNaira, fmtDate } from "@/lib/format";

export const Route = createFileRoute("/_app/companies/$id")({
  component: CompanyProfilePage,
});
  const { id } = Route.useParams();
  const search = Route.useSearch();
  const companyId = Number(id);

  const { data: company, isLoading: loadingCompany, isError: companyError } = useCompany(companyId);
  const { data: holdings, isLoading: loadingHoldings } = useHoldingsByCompany(companyId);
  const { data: history, isLoading: loadingHistory } = usePriceHistory(companyId, 365);

  if (loadingCompany) {
    return (
      <div className="flex justify-center py-24">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--accent-lavender)]"></div>
      </div>
    );
  }

  if (companyError || !company) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-md text-sm font-medium">
        Failed to load company details.
        <Link to="/companies" className="ml-2 underline">Back to companies</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Back link */}
      <Link
        to="/companies"
        search={(prev: any) => ({ ...prev })}
        className="inline-flex items-center gap-1.5 text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Companies
      </Link>

      {/* Company Header */}
      <div className="bg-[var(--bg-surface)] rounded-xl shadow-card p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{company.name}</h1>
              <span className="font-mono font-semibold text-lg text-[var(--text-secondary)]">
                [{company.ticker}]
              </span>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <SectorBadge sector={company.sector} />
              <span className="text-[13px] text-[var(--text-secondary)]">
                Status: {company.status}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          <DetailField label="Registrar" value={company.registrar?.name ?? "-"} />
          <DetailField label="ISIN" value={company.isin ?? "-"} />
          <DetailField
            label="Market Cap"
            value={company.market_cap ? fmtNaira(company.market_cap, { compact: true }) : "-"}
          />
          <DetailField
            label="Outstanding Shares"
            value={company.outstanding_shares?.toLocaleString() ?? "-"}
          />
          <DetailField label="Date Listed" value={company.date_listed ? fmtDate(company.date_listed) : "-"} />
          <DetailField
            label="Current Price"
            value={company.current_price ? fmtNaira(company.current_price) : "-"}
          />
        </div>
      </div>

      {/* Price History Chart */}
      <div className="bg-[var(--bg-surface)] rounded-xl shadow-card p-6">
        <h3 className="text-base font-semibold mb-4">Price History (1Y)</h3>
        {loadingHistory ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-[var(--text-muted)]" />
          </div>
        ) : !history || history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg border-dashed bg-[var(--bg-subtle)]/50">
            <TrendingUp className="h-10 w-10 text-[var(--text-muted)] mb-2" />
            <p className="text-sm text-[var(--text-muted)]">No price history available.</p>
          </div>
        ) : (
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={history.map((d: any) => ({ ...d, price: parseFloat(d.price) }))}
                margin={{ top: 10, right: 30, left: 40, bottom: 40 }}
              >
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#BCBDFA" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#BCBDFA" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="recorded_date"
                  tickFormatter={(val: string) => format(new Date(val), "MMM d")}
                  tick={{ fontFamily: "DM Mono", fontSize: 11, fill: "#c5cbe0" }}
                  stroke="#6b7280"
                  axisLine={true}
                  height={30}
                />
                <YAxis
                  domain={["dataMin - 0.05", "dataMax + 0.05"]}
                  tickCount={4}
                  tickFormatter={(val: any) => `₦${val}`}
                  tick={{ fontFamily: "DM Mono", fontSize: 11, fill: "#c5cbe0" }}
                  stroke="#6b7280"
                  width={55}
                />
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.15)" />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    borderColor: "hsl(var(--border))",
                    borderRadius: "0.5rem",
                    fontFamily: "DM Mono",
                  }}
                  labelFormatter={(label: string) => format(new Date(label), "MMM d, yyyy")}
                  formatter={(value: any) => [`₦${Number(value).toFixed(2)}`, "Price"] as [string, string]}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#BCBDFA"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorPrice)"
                  activeDot={{ r: 5, fill: "#BCBDFA", stroke: "hsl(var(--background))", strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Holdings Section */}
      <div className="bg-[var(--bg-surface)] rounded-xl shadow-card p-6">
        <h3 className="text-base font-semibold mb-4">Your Holdings</h3>
        {loadingHoldings ? (
          <div className="flex justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-[var(--text-muted)]" />
          </div>
        ) : !holdings || holdings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center border rounded-lg border-dashed bg-[var(--bg-subtle)]/50">
            <Building2 className="h-10 w-10 text-[var(--text-muted)] mb-2" />
            <p className="text-sm text-[var(--text-muted)]">No holdings for this company.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-[14px]">
              <thead className="bg-[var(--bg-subtle)]">
                <tr>
                  <th className="h-10 px-3 text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold text-left">Shares</th>
                  <th className="h-10 px-3 text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold text-right">Avg Cost</th>
                  <th className="h-10 px-3 text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold text-right">Curr Value</th>
                  <th className="h-10 px-3 text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold text-right">Return</th>
                  <th className="h-10 px-3 text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold text-left">Type</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((h: any, idx: number) => (
                  <tr key={h.id} className="border-t border-[var(--border)]">
                    <td className="px-3 py-3 font-mono">{h.shares.toLocaleString()}</td>
                    <td className="px-3 py-3 font-mono text-right">{fmtNaira(h.avg_cost)}</td>
                    <td className="px-3 py-3 font-mono text-right">{fmtNaira(h.curr_value)}</td>
                    <td className="px-3 py-3 text-right">
                      {h.return_pct != null ? (
                        <span
                          className={`font-mono ${
                            h.return_pct > 0
                              ? "text-[var(--accent-green)]"
                              : h.return_pct < 0
                              ? "text-[var(--accent-red)]"
                              : ""
                          }`}
                        >
                          {h.return_pct > 0 ? "+" : ""}
                          {h.return_pct.toFixed(2)}%
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-3 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          h.status === "LIVE"
                            ? "bg-green-100 text-green-700"
                            : "bg-amber-100 text-amber-700"
                        }`}
                      >
                        {h.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-1">
        {label}
      </p>
      <p className="font-mono text-[14px]">{value}</p>
    </div>
  );
}