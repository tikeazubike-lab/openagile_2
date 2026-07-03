import { useState } from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import {
  UploadCloud, Building2, Search, CheckCircle, XCircle, AlertTriangle,
  DollarSign, FileSpreadsheet, Download,
} from "lucide-react";
import {
  useCompanies, useUploadCompaniesPdf,
  useCostBasisRecords, useQuickCostBasis, useBulkCsvCostBasis,
} from "@/api/queries";
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

const TABS = [
  { id: "companies", label: "Companies", icon: Building2 },
  { id: "cost-basis", label: "Cost Basis", icon: DollarSign },
] as const;

type TabId = (typeof TABS)[number]["id"];

function DataUploadPage() {
  const [activeTab, setActiveTab] = useState<TabId>("companies");

  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-[1200px] mx-auto space-y-6">
      <div>
        <h1 className="text-[20px] font-bold text-white tracking-tight flex items-center gap-2">
          <UploadCloud className="w-5 h-5 text-[var(--accent-lavender)]" />
          Data Upload
        </h1>
        <p className="text-[13px] text-white/50 mt-1">
          Upload NGX company data and historical cost basis.
        </p>
      </div>

      <div className="flex gap-1 bg-white/5 rounded-lg p-1 w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-md text-[13px] font-medium transition-colors",
              activeTab === tab.id
                ? "bg-[var(--accent-lavender)] text-[#1A1A1A]"
                : "text-white/60 hover:text-white hover:bg-white/10",
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "companies" && <CompaniesSection />}
      {activeTab === "cost-basis" && <CostBasisSection />}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMPANIES SECTION
// ═══════════════════════════════════════════════════════════════════════════════

function CompaniesSection() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div className="lg:col-span-5">
        <CompanyPdfUpload />
      </div>
      <div className="lg:col-span-7">
        <CompanyListPanel />
      </div>
    </div>
  );
}

function CompanyPdfUpload() {
  const { mutate: uploadPdf, isPending } = useUploadCompaniesPdf();
  const addToast = useUIStore((s) => s.addToast);

  const [result, setResult] = useState<{
    total: number; inserted: number; updated: number; errors: string[];
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
        addToast({ title: "Upload Complete", description: `${res.data.summary.inserted} new, ${res.data.summary.updated} updated`, type: "success" });
      },
      onError: (err: Error) => addToast({ title: "Upload Failed", description: err.message, type: "error" }),
    });
    e.target.value = "";
  };

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden flex flex-col">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">NGX Companies Upload</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">PDF</span>
      </div>
      <div className="p-5 space-y-6">
        <div className="border border-[var(--border)] rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-white font-medium text-[14px]">
            <UploadCloud className="w-4 h-4 text-[var(--accent-lavender)]" />
            Upload NGX Daily Official List
          </div>
          <p className="text-[13px] text-white/60 leading-relaxed">
            Upload the NGX Daily Official List PDF. Companies are automatically extracted (ticker, name, sector).
          </p>
          <div className="relative">
            <input type="file" accept=".pdf" onChange={handleFile}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
              disabled={isPending} />
            <div className={cn(
              "border-2 border-dashed rounded-xl p-6 text-center transition-colors flex flex-col items-center justify-center gap-2",
              isPending ? "border-[var(--accent-lavender)]/50 bg-[var(--accent-lavender)]/5" : "border-white/10 hover:border-white/20 hover:bg-white/[0.02]",
            )}>
              <UploadCloud className={cn("w-6 h-6", isPending ? "text-[var(--accent-lavender)] animate-pulse" : "text-white/30")} />
              <div className="text-[13px] font-medium text-white mb-0.5">
                {isPending ? "Uploading & Parsing PDF..." : "Drop PDF here or click to browse"}
              </div>
              <div className="text-[11px] text-white/40">.pdf accepted</div>
            </div>
          </div>
        </div>
        {result && <UploadResultSummary result={result} />}
      </div>
    </div>
  );
}

function UploadResultSummary({ result }: { result: { total: number; inserted: number; updated: number; errors: string[] } }) {
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
      {result.errors.length > 0 && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 space-y-1">
          <div className="text-[12px] font-medium text-red-400 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            {result.errors.length} error(s)
          </div>
          {result.errors.slice(0, 5).map((err, i) => (
            <div key={i} className="text-[11px] text-red-300/80 ml-5">{err}</div>
          ))}
        </div>
      )}
    </div>
  );
}

function CompanyListPanel() {
  const { data: companies, isLoading } = useCompanies();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

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
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">{companies?.length ?? 0} total</span>
      </div>
      <div className="px-5 py-3 border-b border-[var(--border)] flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/40" />
          <input placeholder="Search by ticker or name..." value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-8 pl-8 pr-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white placeholder:text-white/30 focus:outline-none focus:border-[var(--accent-lavender)]" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="h-8 px-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white focus:outline-none focus:border-[var(--accent-lavender)]">
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
                <tr key={c.id} className="border-b border-[var(--border)] hover:bg-white/[0.02] transition-colors">
                  <td className="px-4 py-2.5 font-mono text-white font-medium">{c.ticker}</td>
                  <td className="px-4 py-2.5 text-white/80">{c.name}</td>
                  <td className="px-4 py-2.5 text-white/60">{c.sector ?? "—"}</td>
                  <td className="px-4 py-2.5 text-center"><StatusBadge status={c.status} /></td>
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
    <span className={cn("inline-block px-2 py-0.5 rounded text-[10px] font-medium border capitalize", colorMap[status] ?? "bg-white/5 text-white/50 border-white/10")}>
      {status}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// COST BASIS SECTION
// ═══════════════════════════════════════════════════════════════════════════════

function CostBasisSection() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div className="lg:col-span-5 space-y-6">
        <CostBasisQuickForm />
        <CostBasisCsvUpload />
      </div>
      <div className="lg:col-span-7">
        <CostBasisListPanel />
      </div>
    </div>
  );
}

function CostBasisQuickForm() {
  const { data: companies } = useCompanies();
  const { mutate: quickSubmit, isPending } = useQuickCostBasis();
  const addToast = useUIStore((s) => s.addToast);

  const [ticker, setTicker] = useState("");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("");
  const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().slice(0, 10));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) { addToast({ title: "Validation", description: "Ticker is required", type: "error" }); return; }
    if (!price || parseFloat(price) <= 0) { addToast({ title: "Validation", description: "Valid price required", type: "error" }); return; }
    if (!quantity || parseInt(quantity) <= 0) { addToast({ title: "Validation", description: "Valid quantity required", type: "error" }); return; }

    quickSubmit({ ticker: ticker.trim().toUpperCase(), avg_purchase_price: price, quantity, purchase_date: purchaseDate }, {
      onSuccess: () => {
        addToast({ title: "Cost Basis Added", description: `${ticker.toUpperCase()}: ${quantity} shares at ₦${price}`, type: "success" });
        setTicker(""); setPrice(""); setQuantity("");
      },
      onError: (err: Error) => addToast({ title: "Error", description: err.message, type: "error" }),
    });
  };

  const selectedCompany = (companies ?? []).find((c) => c.ticker.toUpperCase() === ticker.toUpperCase());
  const holdingType = selectedCompany && (selectedCompany.status === "delisted" || selectedCompany.status === "defunct") ? "claim" : "active";

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">Quick Entry</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">SINGLE</span>
      </div>
      <form onSubmit={handleSubmit} className="p-5 space-y-4">
        <div>
          <label className="text-[12px] text-white/60 mb-1 block">Ticker</label>
          <input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g. DANGCEM"
            list="ticker-suggestions"
            className="w-full h-9 px-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white placeholder:text-white/30 focus:outline-none focus:border-[var(--accent-lavender)]" />
          <datalist id="ticker-suggestions">
            {(companies ?? []).map((c) => (
              <option key={c.id} value={c.ticker} />
            ))}
          </datalist>
          {selectedCompany && (
            <div className="mt-1 text-[11px] text-white/50">{selectedCompany.name} — <StatusBadge status={selectedCompany.status} /></div>
          )}
          {selectedCompany && (
            <div className={cn(
              "mt-1.5 text-[11px] px-2 py-0.5 rounded inline-block",
              holdingType === "active" ? "bg-green-900/30 text-green-300" : "bg-yellow-900/30 text-yellow-300",
            )}>
              Will be classified as: {holdingType}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-[12px] text-white/60 mb-1 block">Avg Purchase Price (₦)</label>
            <input type="number" step="0.01" min="0.01" value={price} onChange={(e) => setPrice(e.target.value)}
              placeholder="245.50"
              className="w-full h-9 px-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white placeholder:text-white/30 focus:outline-none focus:border-[var(--accent-lavender)]" />
          </div>
          <div>
            <label className="text-[12px] text-white/60 mb-1 block">Quantity (Shares)</label>
            <input type="number" step="1" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)}
              placeholder="500"
              className="w-full h-9 px-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white placeholder:text-white/30 focus:outline-none focus:border-[var(--accent-lavender)]" />
          </div>
        </div>
        <div>
          <label className="text-[12px] text-white/60 mb-1 block">Purchase Date</label>
          <input type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)}
            className="w-full h-9 px-3 rounded-md bg-white/5 border border-white/10 text-[13px] text-white focus:outline-none focus:border-[var(--accent-lavender)]" />
        </div>
        <button type="submit" disabled={isPending}
          className="w-full h-9 rounded-md bg-[var(--accent-lavender)] text-[#1A1A1A] text-[13px] font-semibold hover:opacity-90 disabled:opacity-50 transition-opacity">
          {isPending ? "Submitting..." : "Add Cost Basis"}
        </button>
      </form>
    </div>
  );
}

function CostBasisCsvUpload() {
  const { mutate: uploadCsv, isPending } = useBulkCsvCostBasis();
  const addToast = useUIStore((s) => s.addToast);

  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);

  const handleSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".csv")) {
      addToast({ title: "Invalid File", description: "Only .csv files accepted", type: "error" }); return;
    }
    setFile(f);
    uploadCsv({ file: f, commit: false }, {
      onSuccess: (res) => { setPreview(res.data); setStep(2); },
      onError: (err: Error) => { addToast({ title: "Upload Failed", description: err.message, type: "error" }); setFile(null); },
    });
    e.target.value = "";
  };

  const handleCommit = () => {
    if (!file) return;
    uploadCsv({ file, commit: true }, {
      onSuccess: (res) => { setPreview(res.data); setStep(3); },
      onError: (err: Error) => addToast({ title: "Commit Failed", description: err.message, type: "error" }),
    });
  };

  const reset = () => { setFile(null); setPreview(null); setStep(1); };

  const downloadTemplate = () => {
    const content = "ticker,company_name,avg_purchase_price,quantity,purchase_date\nDANGCEM,Dangote Cement Plc,245.50,500,2024-01-15\nGTCO,Guaranty Trust Holding Co,33.20,1000,2024-03-01\n";
    const blob = new Blob([content], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url;
    a.download = `cost_basis_template_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click(); URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">Bulk CSV Upload</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">STEP {step}/3</span>
      </div>
      <div className="p-5 space-y-4">
        {step === 1 && (
          <>
            <div className="text-[13px] text-white/60 leading-relaxed">
              Upload a CSV with columns: <code className="text-white/80">ticker, company_name, avg_purchase_price, quantity, purchase_date</code>
            </div>
            <button onClick={downloadTemplate}
              className="flex items-center gap-2 text-[12px] text-[var(--accent-lavender)] hover:underline">
              <Download className="w-3.5 h-3.5" /> Download Template
            </button>
            <div className="relative">
              <input type="file" accept=".csv" onChange={handleSelect}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={isPending} />
              <div className="border-2 border-dashed border-white/10 hover:border-white/20 rounded-xl p-6 text-center transition-colors">
                <FileSpreadsheet className="w-6 h-6 mx-auto text-white/30 mb-2" />
                <div className="text-[13px] font-medium text-white mb-0.5">
                  {isPending ? "Uploading..." : "Click to select CSV file"}
                </div>
                <div className="text-[11px] text-white/40">.csv accepted · max 5MB</div>
              </div>
            </div>
          </>
        )}
        {step === 2 && preview && (
          <div className="space-y-4 animate-in fade-in zoom-in-95 duration-200">
            <div className="bg-[var(--bg-subtle)] rounded-lg p-3 flex items-center justify-between">
              <div>
                <span className="text-green-400 font-medium text-[13px]">{(preview as any).valid ?? 0} valid</span>
                <span className="text-white/30 mx-2">·</span>
                <span className="text-red-400 text-[13px]">{(preview as any).errors ?? 0} errors</span>
              </div>
              <span className="text-[11px] text-white/40">{file?.name}</span>
            </div>
            {(preview as any).preview_rows?.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-[12px]">
                  <thead>
                    <tr className="text-white/50 border-b border-[var(--border)]">
                      <th className="text-left px-2 py-1 font-medium">Ticker</th>
                      <th className="text-left px-2 py-1 font-medium">Company</th>
                      <th className="text-right px-2 py-1 font-medium">Price</th>
                      <th className="text-right px-2 py-1 font-medium">Qty</th>
                      <th className="text-center px-2 py-1 font-medium">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(preview as any).preview_rows.map((r: any, i: number) => (
                      <tr key={i} className="border-b border-[var(--border)]">
                        <td className="px-2 py-1.5 font-mono text-white">{r.ticker}</td>
                        <td className="px-2 py-1.5 text-white/70">{r.company_name}</td>
                        <td className="px-2 py-1.5 text-right text-white">₦{r.avg_purchase_price}</td>
                        <td className="px-2 py-1.5 text-right text-white/70">{r.quantity}</td>
                        <td className="px-2 py-1.5 text-center">
                          <span className={cn(
                            "text-[10px] px-1.5 py-0.5 rounded",
                            r.holding_type === "active" ? "bg-green-900/30 text-green-300" : "bg-yellow-900/30 text-yellow-300",
                          )}>{r.holding_type}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {(preview as any).error_rows?.length > 0 && (
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                <div className="text-[12px] font-medium text-red-400 mb-1">Error details:</div>
                {(preview as any).error_rows.slice(0, 3).map((er: any, i: number) => (
                  <div key={i} className="text-[11px] text-red-300/80 ml-2">Row {er.row}: {er.errors?.join(", ")}</div>
                ))}
              </div>
            )}
            <div className="flex gap-3">
              <button onClick={reset}
                className="flex-1 h-9 rounded-md border border-white/20 text-[13px] text-white/70 hover:bg-white/5 transition-colors">
                Cancel
              </button>
              <button onClick={handleCommit} disabled={isPending || ((preview as any).valid ?? 0) === 0}
                className="flex-1 h-9 rounded-md bg-green-600 text-white text-[13px] font-semibold hover:bg-green-500 disabled:opacity-50 transition-colors">
                {isPending ? "Committing..." : `Commit ${(preview as any).valid ?? 0} rows`}
              </button>
            </div>
          </div>
        )}
        {step === 3 && preview && (
          <div className="space-y-4 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center gap-2 text-green-400">
              <CheckCircle className="w-4 h-4" />
              <span className="text-[14px] font-medium">Upload Complete</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-[var(--bg-subtle)] rounded-lg p-3 text-center">
                <div className="text-[20px] font-bold text-green-400">{(preview as any).summary?.active_holdings_created ?? 0}</div>
                <div className="text-[11px] text-white/50">Active Holdings</div>
              </div>
              <div className="bg-[var(--bg-subtle)] rounded-lg p-3 text-center">
                <div className="text-[20px] font-bold text-yellow-400">{(preview as any).summary?.claims_created ?? 0}</div>
                <div className="text-[11px] text-white/50">Claims</div>
              </div>
            </div>
            <div className="text-[12px] text-white/50 text-center">
              {(preview as any).summary?.new_companies_created ?? 0} new companies created
            </div>
            <button onClick={reset}
              className="w-full h-9 rounded-md border border-white/20 text-[13px] text-white/70 hover:bg-white/5 transition-colors">
              Upload Another
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function CostBasisListPanel() {
  const { data: records, isLoading } = useCostBasisRecords();

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden flex flex-col h-full">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">Cost Basis Records</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">{records?.length ?? 0} records</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-8 text-center text-white/40 text-[13px]">Loading...</div>
        ) : !records || records.length === 0 ? (
          <div className="p-8 text-center text-white/40 text-[13px]">No cost basis records yet. Add one above.</div>
        ) : (
          <table className="w-full text-[13px]">
            <thead>
              <tr className="border-b border-[var(--border)] text-white/50 text-[11px] uppercase tracking-wider">
                <th className="text-left px-4 py-2 font-medium">Ticker</th>
                <th className="text-right px-4 py-2 font-medium">Price</th>
                <th className="text-right px-4 py-2 font-medium">Qty</th>
                <th className="text-right px-4 py-2 font-medium">Total</th>
                <th className="text-center px-4 py-2 font-medium">Type</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r: any) => (
                <tr key={r.id} className="border-b border-[var(--border)] hover:bg-white/[0.02] transition-colors">
                  <td className="px-4 py-2.5 font-mono text-white font-medium">{r.ticker}</td>
                  <td className="px-4 py-2.5 text-right text-white">₦{r.avg_purchase_price}</td>
                  <td className="px-4 py-2.5 text-right text-white/70">{r.quantity}</td>
                  <td className="px-4 py-2.5 text-right text-white/70">₦{r.total_cost}</td>
                  <td className="px-4 py-2.5 text-center">
                    <span className={cn(
                      "text-[10px] px-2 py-0.5 rounded font-medium",
                      r.holding_type === "active" ? "bg-green-900/40 text-green-300 border border-green-700/50" : "bg-yellow-900/40 text-yellow-300 border border-yellow-700/50",
                    )}>
                      {r.holding_type}
                    </span>
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
