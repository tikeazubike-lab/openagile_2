import { createFileRoute } from "@tanstack/react-router";
import { LineChart, Search, ChevronsUpDown, Check } from "lucide-react";
import { useState } from "react";
import { useCompanies, usePriceHistory } from "@/api/queries";
import { useAuthStore } from "@/store/authStore";
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { Company } from "@/types";

export const Route = createFileRoute("/_app/price-history")({
  component: PriceHistoryPage,
});

function CompanyCombobox({
  companies,
  value,
  onChange,
  disabled,
}: {
  companies: Company[];
  value: string;
  onChange: (id: string) => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const selected = companies.find((c) => String(c.id) === value);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn(
            "w-full h-10 justify-between bg-background border rounded-md focus:ring-2 focus:ring-ring font-normal text-foreground hover:bg-muted",
            !value && "text-muted-foreground"
          )}
        >
          <span className="truncate">
            {selected ? `[${selected.ticker}] ${selected.name}` : "Search by ticker or name…"}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        className="w-[var(--radix-popover-trigger-width)] max-h-[min(320px,50vh)] p-0 border border-[var(--border)] bg-popover text-popover-foreground shadow-lg z-50"
        align="start"
      >
        <Command
          className="bg-popover text-popover-foreground"
          filter={(value, search) => {
            const q = search.trim().toLowerCase();
            if (!q) return 1;
            return value.toLowerCase().includes(q) ? 1 : 0;
          }}
        >
          <CommandInput
            placeholder="Search by ticker or name…"
            className="h-11 border-b"
          />
          <CommandList className="max-h-[240px] overflow-y-auto">
            <CommandEmpty className="py-6 text-center text-[13px] text-muted-foreground">
              No company found.
            </CommandEmpty>
            <CommandGroup>
              {companies.map((c) => (
                <CommandItem
                  key={c.id}
                  value={`${c.ticker} ${c.name}`}
                  onSelect={() => {
                    onChange(String(c.id));
                    setOpen(false);
                  }}
                  className="cursor-pointer"
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4 shrink-0",
                      value === String(c.id) ? "opacity-100" : "opacity-0",
                    )}
                  />
                  <span className="truncate">{`[${c.ticker}] ${c.name}`}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

function PriceHistoryPage() {
  const { user } = useAuthStore();
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [daysFilter, setDaysFilter] = useState<number>(30); // 7, 30, 90, 365, 0 (All)

  const { data: companies, isLoading: isLoadingCompanies } = useCompanies();
  const { data: history, isLoading: isLoadingHistory } = usePriceHistory(
    selectedCompanyId,
    daysFilter
  );

  const selectedCompany = companies?.find((c) => c.id === selectedCompanyId);

  const renderSourceBadge = (source: string) => {
    switch (source) {
      case "ngx_pdf_upload":
        return <span className="bg-[#BCBDFA] text-white px-2 py-0.5 rounded-full text-xs font-medium">NGX PDF</span>;
      case "csv_upload":
        return <span className="bg-blue-500 text-white px-2 py-0.5 rounded-full text-xs font-medium">CSV</span>;
      case "manual":
      default:
        return <span className="bg-gray-400 text-white px-2 py-0.5 rounded-full text-xs font-medium">Manual</span>;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Price History</h1>
          <p className="text-muted-foreground mt-1">
            Historical price charts and source breakdown per ticker.
          </p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-center bg-card p-4 rounded-lg border shadow-sm">
        <div className="flex-1 relative max-w-md w-full">
          <CompanyCombobox
            companies={companies ?? []}
            value={selectedCompanyId ? String(selectedCompanyId) : ""}
            onChange={(id) => setSelectedCompanyId(id ? Number(id) : null)}
            disabled={isLoadingCompanies}
          />
        </div>

        {selectedCompanyId && (
          <div className="flex bg-muted p-1 rounded-md">
            {[
              { label: "7D", value: 7 },
              { label: "30D", value: 30 },
              { label: "90D", value: 90 },
              { label: "1Y", value: 365 },
              { label: "All", value: 0 },
            ].map((f) => (
              <button
                key={f.label}
                onClick={() => setDaysFilter(f.value)}
                className={`px-3 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                  daysFilter === f.value
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {!selectedCompanyId ? (
        <div className="flex flex-col items-center justify-center py-24 text-center border rounded-lg border-dashed bg-muted/50">
          <LineChart className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
          <h3 className="text-lg font-medium">No company selected</h3>
          <p className="text-sm text-muted-foreground mt-1 max-w-sm">
            Select a company above to view its price history
          </p>
        </div>
      ) : isLoadingHistory ? (
        <div className="flex justify-center py-24">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : !history || history.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center border rounded-lg border-dashed bg-muted/50">
          <LineChart className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
          <h3 className="text-lg font-medium">No price history for {selectedCompany?.ticker} yet.</h3>
          <p className="text-sm text-muted-foreground mt-1 max-w-sm">
            Upload an NGX PDF or use Quick Price Entry to add prices.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="border rounded-lg bg-card shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium">Price Trend ({selectedCompany?.ticker})</h3>
              {(() => {
                const prices = (history ?? []).map((d) => parseFloat(d.price));
                const min = prices.length ? Math.min(...prices) : 0;
                const max = prices.length ? Math.max(...prices) : 0;
                return (
                  <p className="text-xs text-muted-foreground font-mono">
                    Range: ₦{min.toFixed(2)} – ₦{max.toFixed(2)}
                  </p>
                );
              })()}
            </div>
            <div className="h-[450px] w-full" style={{ minWidth: 0, minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={(history ?? []).map((d) => ({
                    ...d,
                    price: parseFloat(d.price),
                  }))}
                  margin={{ top: 20, right: 40, left: 60, bottom: 60 }}
                >
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#BCBDFA" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#BCBDFA" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="recorded_date"
                    tickFormatter={(val) => format(new Date(val), "MMM d")}
                    tick={{ fontFamily: "DM Mono", fontSize: 12, fill: "#c5cbe0" }}
                    stroke="#6b7280"
                    axisLine={true}
                    height={40}
                    interval={0}
                  />
                  <YAxis
                    domain={["dataMin - 0.05", "dataMax + 0.05"]}
                    tickAmount={5}
                    tickFormatter={(val) => `₦${val}`}
                    tick={{ fontFamily: "DM Mono", fontSize: 12, fill: "#c5cbe0" }}
                    stroke="#6b7280"
                    axisLine={true}
                    width={60}
                  />
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.15)" />
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      borderColor: "hsl(var(--border))",
                      borderRadius: "0.5rem",
                      fontFamily: "DM Mono",
                    }}
                    labelFormatter={(label) => format(new Date(label), "MMM d, yyyy")}
                    formatter={(value: number, name: string, props: any) => [
                      `₦${value.toFixed(2)}`,
                      "Price",
                    ]}
                    content={({ active, payload, label }) => {
                      if (!active || !payload || !payload.length) return null;
                      const data = payload[0].payload;
                      return (
                        <div
                          className="p-3 border rounded-lg shadow-lg"
                          style={{
                            backgroundColor: "hsl(var(--card))",
                            borderColor: "hsl(var(--border))",
                            fontFamily: "DM Mono",
                          }}
                        >
                          <p className="text-sm font-medium">{format(new Date(label), "MMM d, yyyy")}</p>
                          <p className="text-sm">₦{Number(data.price).toFixed(2)}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Source: {data.source === "ngx_pdf_upload" ? "NGX PDF" : data.source === "csv_upload" ? "CSV" : "Manual"}
                          </p>
                        </div>
                      );
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="#BCBDFA"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorPrice)"
                    activeDot={{ r: 6, fill: "#BCBDFA", stroke: "hsl(var(--background))", strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="border rounded-lg bg-card shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground uppercase bg-muted/50 border-b">
                  <tr>
                    <th className="px-6 py-3 font-medium">Date</th>
                    <th className="px-6 py-3 font-medium text-right">Price (₦)</th>
                    <th className="px-6 py-3 font-medium">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {history.map((record) => (
                    <tr key={record.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap font-mono text-sm">
                        {format(new Date(record.recorded_date), "MMM d, yyyy")}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-right">
                        {parseFloat(record.price).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {renderSourceBadge(record.source)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
