// F-026 — Registrar dashboard: read-only summary tiles, "Needs attention" list,
// unmapped companies, and the server-paginated global requirements tracker.
// Spec: .context/feature-specs/F-026-registrar-dashboard.md §3 (API contract) and §5 (frontend).
// Data: GET /api/v1/registrars/dashboard-summary and
// GET /api/v1/registrar-requirements/global-tracker?page=&page_size=20.
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { fetchApiEnvelope } from "@/api/queries";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

// ─── API types (as built in backend/app/routers/registrars.py) ─────────────────

interface ActionItem {
  requirement_id: number;
  task_name: string;
  document_title: string;
  registrar_name: string;
  due_date: string | null;
  is_required: boolean;
}

interface RegistrarHealth {
  complete: number;
  attention: number;
  no_data: number;
}

interface UnmappedCompany {
  id: number;
  ticker: string;
  name: string;
}

interface DashboardSummary {
  completion_pct: number;
  total_requirements: number;
  completed_requirements: number;
  pending_requirements: number;
  top_action_items: ActionItem[];
  registrar_health: RegistrarHealth;
  unmapped_companies: { count: number; companies: UnmappedCompany[] };
}

interface LatestDocument {
  id: number;
  file_name: string;
  status: string;
  uploaded_at: string;
}

interface TrackerRow {
  requirement_id: number;
  status: string;
  task_name: string;
  document_title: string;
  registrar_name: string;
  registrar_id: number;
  due_date: string | null;
  is_required: boolean;
  latest_document: LatestDocument | null;
  actions_available: string[];
}

interface TrackerPage {
  rows: TrackerRow[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const STATUS_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  completed: "default",
  rejected: "destructive",
  in_progress: "secondary",
  pending: "outline",
};

function StatusBadge({ status }: { status: string }) {
  return <Badge variant={STATUS_VARIANT[status] ?? "outline"}>{status}</Badge>;
}

// ─── Summary tiles ────────────────────────────────────────────────────────────

function SummaryTiles({ summary }: { summary: DashboardSummary }) {
  const health = summary.registrar_health ?? { complete: 0, attention: 0, no_data: 0 };
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Completion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-semibold">
            {summary.completion_pct.toFixed(1)}%
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Total Requirements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-semibold">{summary.total_requirements}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-semibold">{summary.completed_requirements}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Pending</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-semibold">{summary.pending_requirements}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Registrar Health</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          <div className="flex items-center justify-between">
            <span>Complete</span>
            <span className="font-mono">{health.complete}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Attention</span>
            <span className="font-mono">{health.attention}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>No data</span>
            <span className="font-mono">{health.no_data}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ─── Needs attention + unmapped companies ────────────────────────────────────

function NeedsAttentionCard({ items }: { items: ActionItem[] }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Needs attention</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="text-sm text-muted-foreground">Nothing needs attention.</div>
        ) : (
          <ul className="space-y-3">
            {items.map((item) => (
              <li key={item.requirement_id} className="rounded-md border p-2">
                <div className="text-sm font-medium">{item.task_name}</div>
                <div className="text-sm text-muted-foreground">{item.document_title}</div>
                <div className="text-xs text-muted-foreground">{item.registrar_name}</div>
                <div className="text-xs text-muted-foreground">{item.due_date ?? "—"}</div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

function UnmappedCompaniesCard({
  unmapped,
}: {
  unmapped: { count: number; companies: UnmappedCompany[] };
}) {
  const companies = (unmapped?.companies ?? []).slice(0, 20);
  const count = unmapped?.count ?? 0;
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">
          {count} unmapped {count === 1 ? "company" : "companies"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {companies.length === 0 ? (
          <div className="text-sm text-muted-foreground">All equity companies are mapped.</div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {companies.map((c) => (
              <span key={c.id} className="rounded-md border px-2 py-0.5 text-xs">
                {c.ticker} — {c.name}
              </span>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Global tracker (TanStack Table, server-side pagination) ─────────────────

const trackerColumnHelper = createColumnHelper<TrackerRow>();

const trackerColumns = [
  trackerColumnHelper.accessor("task_name", {
    header: "Task",
    cell: (info) => <span className="font-medium">{info.getValue()}</span>,
  }),
  trackerColumnHelper.accessor("document_title", {
    header: "Document",
  }),
  trackerColumnHelper.accessor("registrar_name", {
    header: "Registrar",
  }),
  trackerColumnHelper.accessor("status", {
    header: "Status",
    cell: (info) => <StatusBadge status={info.getValue()} />,
  }),
  trackerColumnHelper.accessor("due_date", {
    header: "Due date",
    cell: (info) => info.getValue() ?? "—",
  }),
  trackerColumnHelper.accessor("latest_document", {
    id: "latest_document",
    header: "Latest document",
    cell: (info) => {
      const doc = info.getValue();
      if (!doc) return "—";
      return (
        <span className="inline-flex items-center gap-2">
          <span>{doc.file_name}</span>
          <StatusBadge status={doc.status} />
        </span>
      );
    },
  }),
];

function GlobalTrackerCard({
  tracker,
  onPageChange,
}: {
  tracker: TrackerPage;
  onPageChange: (page: number) => void;
}) {
  const rows = tracker.rows ?? [];

  const table = useReactTable({
    data: rows,
    columns: trackerColumns,
    getCoreRowModel: getCoreRowModel(),
    // Pagination is server-side, driven by the Pagination component below — the
    // table instance renders only the current page's rows (no pagination model),
    // so manualPagination/pageCount would be inert here.
  });

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="border-b text-left text-muted-foreground">
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="pb-2 pr-3 font-medium">
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-b last:border-0">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="py-2 pr-3 align-middle">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan={trackerColumns.length} className="py-4 text-muted-foreground">
                No requirements tracked yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
      {tracker.total_pages > 1 && (
        <Pagination
          page={tracker.page}
          totalPages={tracker.total_pages}
          total={tracker.total}
          onPageChange={onPageChange}
        />
      )}
    </div>
  );
}

function Pagination({
  page,
  totalPages,
  total,
  onPageChange,
}: {
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  return (
    <div className="mt-4 flex items-center justify-between border-t pt-4">
      <span className="text-sm text-muted-foreground">
        Page {page} of {totalPages} ({total} total)
      </span>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}

// ─── Error state ──────────────────────────────────────────────────────────────

function ErrorState({ label, error }: { label: string; error: unknown }) {
  return (
    <div className="rounded-md bg-red-50 p-3 text-sm font-medium text-red-600">
      Failed to load {label}: {error instanceof Error ? error.message : "Unknown error"}
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export function RegistrarsDashboard() {
  const [page, setPage] = useState(1);

  const summaryQuery = useQuery({
    queryKey: ["registrars-dashboard-summary"],
    // fetchApiEnvelope (src/api/queries) covers cookie auth (credentials:
    // "include") and throws on non-OK HTTP (FastAPI `detail`) or an envelope
    // error field; unwrap the { data, meta, error } envelope here — tolerant of
    // unwrapped bodies, as the previous local helper was.
    queryFn: () =>
      fetchApiEnvelope<DashboardSummary>("/api/v1/registrars/dashboard-summary").then(
        (env) => (env.data ?? env) as DashboardSummary,
      ),
  });

  const trackerQuery = useQuery({
    queryKey: ["registrar-global-tracker", page],
    queryFn: () =>
      fetchApiEnvelope<TrackerPage>(
        `/api/v1/registrar-requirements/global-tracker?page=${page}&page_size=20`,
      ).then((env) => (env.data ?? env) as TrackerPage),
  });

  return (
    <section className="space-y-4 p-4" aria-label="Registrar dashboard">
      <h2 className="text-lg font-semibold">Registrar Dashboard</h2>

      {summaryQuery.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : summaryQuery.isError ? (
        <ErrorState label="dashboard summary" error={summaryQuery.error} />
      ) : summaryQuery.data ? (
        <>
          <SummaryTiles summary={summaryQuery.data} />
          <div className="grid gap-4 lg:grid-cols-2">
            <NeedsAttentionCard items={summaryQuery.data.top_action_items ?? []} />
            <UnmappedCompaniesCard unmapped={summaryQuery.data.unmapped_companies} />
          </div>
        </>
      ) : null}

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Global Tracker</CardTitle>
        </CardHeader>
        <CardContent>
          {trackerQuery.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10" />
              ))}
            </div>
          ) : trackerQuery.isError ? (
            <ErrorState label="global tracker" error={trackerQuery.error} />
          ) : trackerQuery.data ? (
            <GlobalTrackerCard tracker={trackerQuery.data} onPageChange={setPage} />
          ) : null}
        </CardContent>
      </Card>
    </section>
  );
}
