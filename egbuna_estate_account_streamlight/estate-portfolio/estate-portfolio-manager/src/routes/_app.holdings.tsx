import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, Fragment } from "react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  createColumnHelper,
  type SortingState,
} from "@tanstack/react-table";
import { Search, Plus, Download, Pencil, Trash2, Check } from "lucide-react";
import {
  useHoldings,
  useAddHolding,
  useDeleteHolding,
  usePublishHolding,
  useCompanies,
} from "@/api/queries";
import type { Holding, Sector } from "@/types";
import { fmtNaira } from "@/lib/format";
import { SectorBadge, StatusBadge, ReturnText } from "@/components/shared/Badges";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";
import { AddHoldingDrawer } from "@/components/holdings/AddHoldingDrawer";
import { EditHoldingModal } from "@/components/holdings/EditHoldingModal";

export const Route = createFileRoute("/_app/holdings")({
  component: HoldingsPage,
});

const ch = createColumnHelper<Holding>();

function HoldingsPage() {
  const { data, isLoading } = useHoldings();
  const { data: companies } = useCompanies();
  const isAdmin = useAuthStore((s) => s.isAdmin)();

  const addHolding = useAddHolding();
  const deleteHolding = useDeleteHolding();
  const publishHolding = usePublishHolding();

  const [globalFilter, setGlobalFilter] = useState("");
  const [sectorFilter, setSectorFilter] = useState<Sector | "All">("All");
  const [statusFilter, setStatusFilter] = useState<"All" | "LIVE" | "DRAFT">("All");
  const [sorting, setSorting] = useState<SortingState>([{ id: "curr_value", desc: true }]);

  const [editingHolding, setEditingHolding] = useState<Holding | null>(null);
  const [addDrawerOpen, setAddDrawerOpen] = useState(false);

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.filter((h) => {
      if (sectorFilter !== "All" && h.sector !== sectorFilter) return false;
      if (statusFilter !== "All" && h.status !== statusFilter) return false;
      if (!globalFilter) return true;
      const q = globalFilter.toLowerCase();
      return h.ticker.toLowerCase().includes(q) || h.company.toLowerCase().includes(q);
    });
  }, [data, globalFilter, sectorFilter, statusFilter]);

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this holding?")) {
      await deleteHolding.mutateAsync(id);
    }
  };

  const columns = useMemo(
    () => [
      ch.accessor("ticker", {
        header: "Ticker",
        cell: (i) => <span className="font-mono font-semibold text-[14px]">{i.getValue()}</span>,
      }),
      ch.accessor("company", {
        header: "Company",
        cell: (i) => <span className="text-[14px]">{i.getValue()}</span>,
      }),
      ch.accessor("sector", {
        header: "Sector",
        cell: (i) => <SectorBadge sector={i.getValue()} />,
      }),
      ch.accessor("shares", {
        header: () => <div className="text-right">Shares</div>,
        cell: (i) => (
          <div className="text-right font-mono">{i.getValue().toLocaleString()}</div>
        ),
      }),
      ch.accessor("avg_cost", {
        header: () => <div className="text-right">Avg Cost</div>,
        cell: (i) => (
          <div className="text-right font-mono">{fmtNaira(i.getValue())}</div>
        ),
      }),
      ch.accessor("curr_price", {
        header: () => <div className="text-right">Curr Price</div>,
        cell: (i) => <div className="text-right font-mono">{fmtNaira(i.getValue())}</div>,
      }),
      ch.accessor("curr_value", {
        header: () => <div className="text-right">Curr Value</div>,
        cell: (i) => (
          <div className="text-right font-mono font-semibold">{fmtNaira(i.getValue())}</div>
        ),
      }),
      ch.accessor("cost_basis", {
        header: () => <div className="text-right">Cost Basis</div>,
        cell: (i) => <div className="text-right font-mono">{fmtNaira(i.getValue())}</div>,
      }),
      ch.accessor("return_pct", {
        header: () => <div className="text-right">return[%]</div>,
        cell: (i) => (
          <div className="text-right">
            <ReturnText value={i.getValue()} />
          </div>
        ),
      }),
      ch.accessor("div_yield", {
        header: () => <div className="text-right">Div Yield</div>,
        cell: (i) => {
          const v = i.getValue();
          return <div className="text-right font-mono">{v != null ? `${v.toFixed(1)}%` : "-"}</div>;
        },
      }),
      ...(isAdmin
        ? [
            ch.accessor("status", {
              header: "Status",
              cell: (i) => <StatusBadge status={i.getValue()} />,
            }),
          ]
        : []),
      ...(isAdmin
        ? [
            ch.display({
              id: "actions",
              header: () => <div className="text-right">Actions</div>,
              cell: (i) => {
                const holding = i.row.original;
                return (
                  <div className="flex items-center gap-1 justify-end">
                    <button
                      onClick={() => setEditingHolding(holding)}
                      className="w-7 h-7 rounded hover:bg-[var(--bg-subtle)] flex items-center justify-center text-[var(--text-secondary)]"
                      title="Edit holding"
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </button>
                    {holding.status === "DRAFT" && (
                      <button
                        onClick={() => publishHolding.mutate(holding.id)}
                        className="h-7 px-2 rounded-full bg-[var(--accent-lavender)] text-[#1A1A1A] text-[11px] font-semibold flex items-center gap-1"
                      >
                        <Check className="w-3 h-3" /> Publish
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(holding.id)}
                      className="w-7 h-7 rounded hover:bg-[var(--bg-subtle)] flex items-center justify-center text-[var(--text-secondary)]"
                      title="Delete holding"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              },
            }),
          ]
        : []),
    ],
    [isAdmin, handleDelete, publishHolding]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3 flex-wrap">
        <h2 className="text-[14px] text-[var(--text-secondary)]">
          ({data?.length ?? 0} positions)
        </h2>
        <div className="ml-auto flex items-center gap-2">
          {isAdmin && (
            <button
              onClick={() => setAddDrawerOpen(true)}
              className="h-9 px-3 rounded-md bg-[var(--accent-lavender)] text-[#1A1A1A] text-[13px] font-semibold flex items-center gap-1.5 hover:opacity-90"
            >
              <Plus className="w-4 h-4" /> Add Holding
            </button>
          )}
          <button className="h-9 px-3 rounded-md border border-[var(--border)] text-[13px] text-[var(--text-secondary)] hover:bg-[var(--bg-subtle)] flex items-center gap-1.5">
            <Download className="w-4 h-4" /> Export
          </button>
        </div>
      </div>

      {/* Filter row */}
      <div className="bg-[var(--bg-surface)] rounded-xl shadow-card px-4 py-3 flex items-center gap-2 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
          <input
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search ticker or company..."
            className="w-full h-9 pl-9 pr-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[13px]"
          />
        </div>
        <Select value={sectorFilter} onChange={(v) => setSectorFilter(v as Sector | "All")}>
          <option value="All">All sectors</option>
          {(
            [
              "Banking",
              "Consumer Goods",
              "Oil & Gas",
              "Industrials",
              "Healthcare",
              "Telecoms",
              "Conglomerate",
              "Insurance",
            ] as Sector[]
          ).map((s) => (
            <option key={s}>{s}</option>
          ))}
        </Select>
        {isAdmin && (
          <Select
            value={statusFilter}
            onChange={(v) => setStatusFilter(v as "All" | "LIVE" | "DRAFT")}
          >
            <option value="All">All status</option>
            <option value="LIVE">Live</option>
            <option value="DRAFT">Draft</option>
          </Select>
        )}
      </div>

      {/* Table */}
      <div className="bg-[var(--bg-surface)] rounded-xl shadow-card overflow-hidden">
        {isLoading ? (
          <div className="p-4 space-y-2">
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton h-10" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-[14px]">
              <thead className="bg-[var(--bg-subtle)]">
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id}>
                    {hg.headers.map((h) => (
                      <th
                        key={h.id}
                        onClick={h.column.getToggleSortingHandler()}
                        className="h-10 px-3 text-[11px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold text-left whitespace-nowrap select-none cursor-pointer"
                      >
                        {flexRender(h.column.columnDef.header, h.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row, idx) => {
                  const holding = row.original;
                  const draft = holding.status === "DRAFT";

                  return (
                    <Fragment key={row.id}>
                      <tr
                        className={cn(
                          "border-t border-[var(--border)] transition-colors",
                          idx % 2 === 1 && !draft && "bg-[var(--bg-subtle)]/50",
                          "hover:bg-[color-mix(in_oklab,var(--accent-lavender)_10%,transparent)]"
                        )}
                        style={
                          draft
                            ? {
                                borderLeft: "3px solid var(--accent-amber)",
                                background:
                                  "color-mix(in oklab, var(--accent-amber) 4%, transparent)",
                                opacity: 0.85,
                              }
                            : undefined
                        }
                      >
                        {row.getVisibleCells().map((cell) => (
                          <td
                            key={cell.id}
                            className="px-3 py-3 text-[var(--text-primary)] whitespace-nowrap"
                          >
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        ))}
                      </tr>
                    </Fragment>
                  );
                })}
                {table.getRowModel().rows.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="text-center py-10 text-[var(--text-muted)]">
                      No holdings match your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <AddHoldingDrawer
        isOpen={addDrawerOpen}
        onClose={() => setAddDrawerOpen(false)}
      />

      {editingHolding && (
        <EditHoldingModal
          holding={editingHolding}
          onClose={() => setEditingHolding(null)}
        />
      )}
    </div>
  );
}

function Select({
  value,
  onChange,
  children,
}: {
  value: string;
  onChange: (v: string) => void;
  children: React.ReactNode;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-9 px-3 pr-8 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[13px] text-[var(--text-primary)]"
    >
      {children}
    </select>
  );
}
