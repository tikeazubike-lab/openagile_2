import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  createColumnHelper,
  type SortingState,
} from "@tanstack/react-table";
import { Search, Building2 } from "lucide-react";
import { useCompanies } from "@/api/queries";
import type { Company, Sector } from "@/types";
import { SectorBadge } from "@/components/shared/Badges";
import { z } from "zod";

const searchSchema = z.object({
  q: z.string().optional().default(""),
  sector: z.string().optional().default("All"),
});

export const Route = createFileRoute("/_app/companies")({
  validateSearch: searchSchema,
  component: CompaniesPage,
});

const ch = createColumnHelper<Company>();

function companiesSectors(): string[] {
  return [
    "Agriculture",
    "Banking",
    "Consumer Goods",
    "Conglomerate",
    "Construction/Real Estate",
    "Healthcare",
    "Industrial Goods",
    "Insurance",
    "Oil & Gas",
    "Services",
    "Telecoms",
    "Utilities",
  ];
}

function CompaniesPage() {
  const navigate = Route.useNavigate();
  const search = Route.useSearch();
  const { data, isLoading, isError, error } = useCompanies();

  const [sorting, setSorting] = useState<SortingState>([{ id: "ticker", desc: false }]);

  const sectors = useMemo(() => {
    if (!data) return companiesSectors();
    const unique = new Set(data.map((c) => c.sector).filter(Boolean));
    return Array.from(unique).sort();
  }, [data]);

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.filter((c) => {
      if (search.sector !== "All" && c.sector !== search.sector) return false;
      if (!search.q) return true;
      const q = search.q.toLowerCase();
      return c.ticker.toLowerCase().includes(q) || c.name.toLowerCase().includes(q);
    });
  }, [data, search.q, search.sector]);

  const columns = useMemo(
    () => [
      ch.accessor("ticker", {
        header: "Ticker",
        cell: (i) => (
          <span className="font-mono font-semibold text-[14px]">{i.getValue()}</span>
        ),
      }),
      ch.accessor("name", {
        header: "Name",
        cell: (i) => <span className="text-[14px]">{i.getValue()}</span>,
      }),
      ch.accessor("sector", {
        header: "Sector",
        cell: (i) => <SectorBadge sector={i.getValue()} />,
      }),
      ch.accessor("registrar_name", {
        header: "Registrar",
        cell: (i) => (
          <span className="text-[13px] text-[var(--text-secondary)]">
            {i.getValue() ?? "-"}
          </span>
        ),
      }),
      ch.accessor("current_price", {
        header: () => <div className="text-right">Price</div>,
        cell: (i) => {
          const price = i.getValue();
          return (
            <div className="text-right font-mono text-[13px]">
              {price ? `₦${parseFloat(price).toFixed(2)}` : "-"}
            </div>
          );
        },
      }),
    ],
    []
  );

  const table = useReactTable({
    data: filtered,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 flex-wrap">
        <h2 className="text-[14px] text-[var(--text-secondary)]">
          ({data?.length ?? 0} companies)
        </h2>
      </div>

      {/* Filter row */}
      <div className="bg-[var(--bg-surface)] rounded-xl shadow-card px-4 py-3 flex items-center gap-2 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
          <input
            value={search.q}
            onChange={(e) =>
              navigate({ search: (prev: typeof search) => ({ ...prev, q: e.target.value }) })
            }
            placeholder="Search ticker or company..."
            className="w-full h-9 pl-9 pr-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[13px]"
          />
        </div>
        <select
          value={search.sector}
          onChange={(e) =>
            navigate({ search: (prev: typeof search) => ({ ...prev, sector: e.target.value }) })
          }
          className="h-9 px-3 pr-8 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[13px] text-[var(--text-primary)]"
        >
          <option value="All">All sectors</option>
          {sectors.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Error state */}
      {isError && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm font-medium">
          Failed to load companies: {error instanceof Error ? error.message : "Unknown error"}
        </div>
      )}

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
                  const company = row.original;
                  return (
                    <tr
                      key={row.id}
                      onClick={() =>
                        navigate({
                          to: `/companies/${company.id}`,
                          search: { q: search.q, sector: search.sector },
                        })
                      }
                      className="border-t border-[var(--border)] transition-colors cursor-pointer hover:bg-[color-mix(in_oklab,var(--accent-lavender)_10%,transparent)]"
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
                  );
                })}
                {table.getRowModel().rows.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="text-center py-10 text-[var(--text-muted)]">
                      No companies match your filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}