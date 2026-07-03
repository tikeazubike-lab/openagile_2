import { useState } from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { UploadCloud, Building2, Search, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { useCompanies, useUploadCompaniesPdf } from "@/api/queries";
import { useUIStore } from "@/store/uiStore";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";
import type { Company } from "@/types";

export const Route = createFileRoute("/_app/settings/data-upload")({
  beforeLoad: () => {
    const user = useAuthStore.getState().user;
    if (!user) throw redirect({ to: "/login" });
    if (user.role !== "admin") throw redirect({ to: "/dashboard" });
  },
  component: DataUploadPage,
});

function DataUploadPage() {
  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-[1200px] mx-auto space-y-6">
      <div>
        <h1 className="text-[20px] font-bold text-white tracking-tight flex items-center gap-2">
          <Building2 className="w-5 h-5 text-[var(--accent-lavender)]" />
          Data Upload
        </h1>
        <p className="text-[13px] text-white/50 mt-1">
          Upload NGX Daily Official List PDF to populate companies database.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-5">
          <CompanyPdfUpload />
        </div>
        <div className="lg:col-span-7">
          <CompanyListPanel />
        </div>
      </div>
    </div>
  );
}

function CompanyPdfUpload() {
  const { mutate: uploadPdf, isPending } = useUploadCompaniesPdf();
  const addToast = useUIStore((s) => s.addToast);

  const [result, setResult] = useState<{
    total: number;
    inserted: number;
    updated: number;
    errors: string[];
  } | null>(null);

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      addToast({ title: "Invalid File", description: "Only .pdf files accepted", type: "error" });
      return;
    }

    setResult(null);
    uploadPdf(file, {
      onSuccess: (res) => {
        setResult(res.data.summary);
        addToast({
          title: "Upload Complete",
          description: `${res.data.summary.inserted} new, ${res.data.summary.updated} updated`,
          type: "success",
        });
      },
      onError: (err: Error) => {
        addToast({ title: "Upload Failed", description: err.message, type: "error" });
      },
    });
    e.target.value = "";
  };

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden flex flex-col">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">NGX Companies Upload</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">
          PDF
        </span>
      </div>

      <div className="p-5 space-y-6">
        <div className="border border-[var(--border)] rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-white font-medium text-[14px]">
            <UploadCloud className="w-4 h-4 text-[var(--accent-lavender)]" />
            Upload NGX Daily Official List
          </div>
          <p className="text-[13px] text-white/60 leading-relaxed">
            Upload the NGX Daily Official List PDF. Companies are automatically
            extracted (ticker, name, sector) and saved to the database. Existing
            companies are updated; new ones are added.
          </p>

          <div className="relative">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFile}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
              disabled={isPending}
            />
            <div
              className={cn(
                "border-2 border-dashed rounded-xl p-6 text-center transition-colors flex flex-col items-center justify-center gap-2",
                isPending
                  ? "border-[var(--accent-lavender)]/50 bg-[var(--accent-lavender)]/5"
                  : "border-white/10 hover:border-white/20 hover:bg-white/[0.02]",
              )}
            >
              <UploadCloud
                className={cn(
                  "w-6 h-6",
                  isPending
                    ? "text-[var(--accent-lavender)] animate-pulse"
                    : "text-white/30",
                )}
              />
              <div>
                <div className="text-[13px] font-medium text-white mb-0.5">
                  {isPending
                    ? "Uploading & Parsing PDF..."
                    : "Drop PDF here or click to browse"}
                </div>
                <div className="text-[11px] text-white/40">.pdf accepted</div>
              </div>
            </div>
          </div>
        </div>

        {result && <UploadResultSummary result={result} />}
      </div>
    </div>
  );
}

function UploadResultSummary({
  result,
}: {
  result: { total: number; inserted: number; updated: number; errors: string[] };
}) {
  const hasErrors = result.errors.length > 0;

  return (
    <div className="border border-[var(--border)] rounded-xl p-5 space-y-4 animate-in fade-in zoom-in-95 duration-200">
      <h3 className="text-[14px] font-semibold text-white flex items-center gap-2">
        <CheckCircle className="w-4 h-4 text-green-400" />
        Upload Summary
      </h3>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[var(--bg-subtle)] rounded-lg p-3 text-center">
          <div className="text-[22px] font-bold text-white">{result.total}</div>
          <div className="text-[11px] text-white/50">Total Parsed</div>
        </div>
        <div className="bg-[var(--bg-subtle)] rounded-lg p-3 text-center">
          <div className="text-[22px] font-bold text-green-400">{result.inserted}</div>
          <div className="text-[11px] text-white/50">New Companies</div>
        </div>
        <div className="bg-[var(--bg-subtle)] rounded-lg p-3 text-center">
          <div className="text-[22px] font-bold text-[var(--accent-amber)]">{result.updated}</div>
          <div className="text-[11px] text-white/50">Updated</div>
        </div>
      </div>
      {hasErrors && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 space-y-1">
          <div className="text-[12px] font-medium text-red-400 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            {result.errors.length} error(s)
          </div>
          {result.errors.slice(0, 5).map((err, i) => (
            <div key={i} className="text-[11px] text-red-300/80 ml-5">
              {err}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CompanyListPanel() {
  const { data: companies, isLoading } = useCompanies();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  const filtered = (companies ?? []).filter((c) => {
    if (statusFilter && c.status !== statusFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!c.ticker.toLowerCase().includes(q) && !c.name.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden flex flex-col h-full">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">Registered Companies</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">
          {companies?.length ?? 0} total
        </span>
      </div>

      <div className="px-5 py-3 border-b border-[var(--border)] flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/40" />
          <input
            placeholder="Search by ticker or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-8 pl-8 pr-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white placeholder:text-white/30 focus:outline-none focus:border-[var(--accent-lavender)]"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-8 px-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white focus:outline-none focus:border-[var(--accent-lavender)]"
        >
          <option value="">All status</option>
          <option value="listed">Listed</option>
          <option value="delisted">Delisted</option>
          <option value="defunct">Defunct</option>
          <option value="merged">Merged</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-8 text-center text-white/40 text-[13px]">Loading...</div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-white/40 text-[13px]">
            {search || statusFilter ? "No companies match your filters." : "No companies found. Upload a PDF to get started."}
          </div>
        ) : (
          <table className="w-full text-[13px]">
            <thead>
              <tr className="border-b border-[var(--border)] text-white/50 text-[11px] uppercase tracking-wider">
                <th className="text-left px-4 py-2 font-medium">Ticker</th>
                <th className="text-left px-4 py-2 font-medium">Name</th>
                <th className="text-left px-4 py-2 font-medium">Sector</th>
                <th className="text-center px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c: Company) => (
                <tr
                  key={c.id}
                  className="border-b border-[var(--border)] hover:bg-white/[0.02] transition-colors"
                >
                  <td className="px-4 py-2.5 font-mono text-white font-medium">{c.ticker}</td>
                  <td className="px-4 py-2.5 text-white/80">{c.name}</td>
                  <td className="px-4 py-2.5 text-white/60">{c.sector ?? "—"}</td>
                  <td className="px-4 py-2.5 text-center">
                    <StatusBadge status={c.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    listed: "bg-green-900/40 text-green-300 border-green-700/50",
    delisted: "bg-red-900/40 text-red-300 border-red-700/50",
    defunct: "bg-gray-800 text-gray-400 border-gray-700/50",
    merged: "bg-blue-900/40 text-blue-300 border-blue-700/50",
  };

  return (
    <span
      className={cn(
        "inline-block px-2 py-0.5 rounded text-[10px] font-medium border capitalize",
        colorMap[status] ?? "bg-white/5 text-white/50 border-white/10",
      )}
    >
      {status}
    </span>
  );
}
