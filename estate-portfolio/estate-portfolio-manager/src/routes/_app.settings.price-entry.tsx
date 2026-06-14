import { useMemo, useState } from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import {
  Zap,
  Download,
  UploadCloud,
  Info,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  RotateCcw,
  ChevronsUpDown,
  Check,
} from "lucide-react";
import {
  useCompanies,
  usePriceAudit,
  useQuickPriceUpdate,
  useRevertPrice,
  useBulkCsvImport,
  useUploadNGXPdf,
} from "@/api/queries";
import { useUIStore } from "@/store/uiStore";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";
import type { Company } from "@/types";
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
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const MAX_CSV_BYTES = 5 * 1024 * 1024;

function companyOptionLabel(c: Company) {
  const px =
    c.current_price != null && String(c.current_price) !== ""
      ? `₦${c.current_price}`
      : "No price yet";
  return `[${c.ticker}] ${c.name} — ${px}`;
}

// --- Route Definition ---
export const Route = createFileRoute("/_app/settings/price-entry")({
  beforeLoad: () => {
    const user = useAuthStore.getState().user;
    if (!user) throw redirect({ to: "/login" });
    if (user.role !== "admin") throw redirect({ to: "/dashboard" });
  },
  component: PriceEntryPage,
});

// --- Main Page Component ---
function PriceEntryPage() {
  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-[1200px] mx-auto space-y-6">
      <div>
        <h1 className="text-[20px] font-bold text-white tracking-tight flex items-center gap-2">
          <Zap className="w-5 h-5 text-[var(--accent-lavender)]" />
          Price Entry
        </h1>
        <p className="text-[13px] text-white/50 mt-1">
          Quick single price update and bulk NGX CSV import.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 space-y-6">
          <QuickUpdatePanel />
          <AuditLogPanel />
        </div>
        <div className="lg:col-span-5">
          <BulkImportPanel />
        </div>
      </div>
    </div>
  );
}

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
            "w-full h-10 justify-between border-white/10 bg-white/5 text-[14px] font-normal text-white hover:bg-white/10 hover:text-white",
            !value && "text-white/50",
          )}
        >
          <span className="truncate">
            {selected ? companyOptionLabel(selected) : "Search by ticker or name…"}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        className="w-[var(--radix-popover-trigger-width)] max-h-[min(320px,50vh)] p-0 border border-[var(--border)] bg-[var(--bg-surface)] text-white shadow-lg z-50"
        align="start"
      >
        <Command
          className="bg-[var(--bg-surface)] text-white [&_[cmdk-input-wrapper]_svg]:text-white/50 [&_[cmdk-input]]:text-white"
          filter={(value, search) => {
            const q = search.trim().toLowerCase();
            if (!q) return 1;
            return value.toLowerCase().includes(q) ? 1 : 0;
          }}
        >
          <CommandInput
            placeholder="Search by ticker or name…"
            className="h-11 border-white/10 text-white placeholder:text-white/40"
          />
          <CommandList className="max-h-[240px] overflow-y-auto">
            <CommandEmpty className="py-6 text-center text-[13px] text-white/50">
              No company found.
            </CommandEmpty>
            <CommandGroup className="text-white">
              {companies.map((c) => (
                <CommandItem
                  key={c.id}
                  value={`${c.ticker} ${c.name}`}
                  onSelect={() => {
                    onChange(String(c.id));
                    setOpen(false);
                  }}
                  className="cursor-pointer text-white aria-selected:bg-white/10"
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4 shrink-0",
                      value === String(c.id) ? "opacity-100" : "opacity-0",
                    )}
                  />
                  <span className="truncate">{companyOptionLabel(c)}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

// --- Quick Update Panel ---
function QuickUpdatePanel() {
  const { data: companies, isLoading } = useCompanies();
  const { mutate: updatePrice, isPending } = useQuickPriceUpdate();
  const addToast = useUIStore((s) => s.addToast);

  const [companyId, setCompanyId] = useState<string>("");
  const [price, setPrice] = useState<string>("");
  const [dateStr, setDateStr] = useState<string>(new Date().toISOString().slice(0, 10));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyId || !price || !dateStr) return;

    updatePrice(
      { company_id: Number(companyId), price, entry_date: dateStr },
      {
        onSuccess: (res) => {
          const { ticker, old_price, new_price, delta_pct } = res.data;
          let msg = `✓ ${ticker} updated: ₦${new_price}`;
          if (old_price === null) {
            msg = `✓ ${ticker}: first price set to ₦${new_price}`;
          } else if (delta_pct !== null) {
            const sign = Number(delta_pct) >= 0 ? "+" : "";
            msg = `✓ ${ticker} updated: ₦${old_price} → ₦${new_price} (${sign}${delta_pct}%)`;
          }
          addToast({
            title: "Price Updated",
            description: msg,
            type: "success",
            durationMs: 4000,
          });
          setCompanyId("");
          setPrice("");
        },
        onError: (err: Error) => {
          addToast({
            title: "Update Failed",
            description: err.message,
            type: "error",
            durationMs: 4000,
          });
        },
      },
    );
  };

  const emptyLoaded = !isLoading && (!companies || companies.length === 0);

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[var(--border)]">
        <h2 className="text-[14px] font-semibold text-white">Quick Price Update</h2>
      </div>
      <div className="p-5">
        {emptyLoaded ? (
          <div className="rounded-lg border border-white/10 bg-white/[0.03] px-4 py-8 text-center text-[13px] text-white/60">
            No companies found — import Obsidian vault first.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[12px] font-medium text-white/70">Company</label>
              <CompanyCombobox
                companies={companies ?? []}
                value={companyId}
                onChange={setCompanyId}
                disabled={isLoading}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5 sm:col-span-1">
                <label className="text-[12px] font-medium text-white/70">New Price (₦)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="w-full h-14 px-4 font-mono bg-white/5 border border-white/10 rounded-lg text-[32px] leading-none text-white focus:outline-none focus:border-[var(--accent-lavender)] transition-colors"
                  placeholder="0.00"
                  required
                />
              </div>
              <div className="space-y-1.5 sm:col-span-1">
                <label className="text-[12px] font-medium text-white/70">Date</label>
                <input
                  type="date"
                  value={dateStr}
                  onChange={(e) => setDateStr(e.target.value)}
                  max={new Date().toISOString().slice(0, 10)}
                  className="w-full h-14 px-3 bg-white/5 border border-white/10 rounded-lg text-[14px] text-white focus:outline-none focus:border-[var(--accent-lavender)] transition-colors [color-scheme:dark]"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={!companyId || !price || !dateStr || isPending}
              className="w-full h-10 bg-[var(--accent-lavender)] text-[#1A1A1A] text-[14px] font-medium rounded-lg hover:brightness-110 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              {isPending ? "Updating..." : "Update Price"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

type AuditRow = {
  id: number;
  ticker: string;
  company_name: string;
  old_price: string | null;
  new_price: string;
  delta_pct: string | null;
  changed_at: string;
  source: string;
};

// --- Audit Log Panel ---
function AuditLogPanel() {
  const { data: audits, isLoading } = usePriceAudit();
  const { mutate: revertPrice, isPending: isReverting } = useRevertPrice();
  const addToast = useUIStore((s) => s.addToast);

  const [revertTarget, setRevertTarget] = useState<AuditRow | null>(null);

  const auditsDisplay = useMemo(() => (audits ?? []).slice(0, 20), [audits]);

  const confirmRevert = () => {
    if (!revertTarget) return;
    const audit = revertTarget;
    revertPrice(audit.id, {
      onSuccess: () => {
        addToast({
          title: "Price Reverted",
          description: `✓ ${audit.ticker} reverted to ₦${audit.old_price}`,
          type: "success",
          durationMs: 4000,
        });
        setRevertTarget(null);
      },
      onError: (err: Error) => {
        addToast({
          title: "Revert Failed",
          description: err.message,
          type: "error",
          durationMs: 4000,
        });
      },
    });
  };

  return (
    <>
      <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--border)]">
          <h2 className="text-[14px] font-semibold text-white">Recent Price Changes</h2>
          <p className="text-[11px] text-white/40 mt-0.5">Last 20 entries</p>
        </div>
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-8 text-center text-white/50 text-[13px]">Loading history...</div>
          ) : !audits || audits.length === 0 ? (
            <div className="p-8 text-center text-[13px]">
              <div className="text-white/40 mb-1">No price changes recorded yet.</div>
              <div className="text-white/30">Use Quick Update above to add your first price.</div>
            </div>
          ) : (
            <table className="w-full text-left border-collapse min-w-[600px]">
              <thead>
                <tr className="border-b border-white/5 bg-white/[0.02]">
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider">
                    Ticker
                  </th>
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider text-right">
                    Old ₦
                  </th>
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider text-right">
                    New ₦
                  </th>
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider text-right">
                    Δ%
                  </th>
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-4 py-2.5 font-medium text-white/50 text-[11px] uppercase tracking-wider text-right">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="text-[13px]">
                {auditsDisplay.map((a) => (
                  <tr
                    key={a.id}
                    className="border-b border-white/5 hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="px-4 py-3 text-white/70">{a.changed_at}</td>
                    <td className="px-4 py-3 font-medium text-white">{a.ticker}</td>
                    <td className="px-4 py-3 text-right font-mono text-white/60">
                      {a.old_price ?? "-"}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-white">{a.new_price}</td>
                    <td className="px-4 py-3 text-right font-mono">
                      <span
                        className={cn(
                          "px-1.5 py-0.5 rounded",
                          !a.delta_pct
                            ? "text-white/40"
                            : Number(a.delta_pct) > 0
                              ? "text-[var(--accent-emerald)] bg-[var(--accent-emerald)]/10"
                              : Number(a.delta_pct) < 0
                                ? "text-[var(--accent-red)] bg-[var(--accent-red)]/10"
                                : "text-white/60 bg-white/5",
                        )}
                      >
                        {a.delta_pct ? `${Number(a.delta_pct) > 0 ? "+" : ""}${a.delta_pct}%` : "-"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded-full text-[10px] font-medium",
                          a.source === "manual"
                            ? "bg-white/10 text-white/70"
                            : a.source === "csv_upload"
                              ? "bg-blue-500/20 text-blue-300"
                              : "bg-amber-500/20 text-amber-300",
                        )}
                      >
                        {a.source}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        onClick={() => setRevertTarget(a)}
                        disabled={a.old_price === null || isReverting}
                        title={
                          a.old_price === null
                            ? "No previous price to revert to"
                            : `Revert to ₦${a.old_price}`
                        }
                        className="px-2.5 py-1 text-[11px] font-medium bg-white/5 hover:bg-white/10 text-white/70 rounded border border-white/10 disabled:opacity-30 transition-colors inline-flex items-center gap-1"
                      >
                        <RotateCcw className="w-3 h-3" />
                        Revert
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <AlertDialog open={!!revertTarget} onOpenChange={(o) => !o && setRevertTarget(null)}>
        <AlertDialogContent className="border-[var(--border)] bg-[var(--card)] text-white sm:max-w-md">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Revert price change?</AlertDialogTitle>
            <AlertDialogDescription className="text-white/70">
              {revertTarget &&
                `Revert ${revertTarget.ticker} from ₦${revertTarget.new_price} back to ₦${revertTarget.old_price}?`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-white/20 bg-transparent text-white hover:bg-white/10">
              Cancel
            </AlertDialogCancel>
            <Button
              type="button"
              className="bg-[var(--accent-lavender)] text-[#1A1A1A] hover:brightness-110"
              disabled={isReverting}
              onClick={() => confirmRevert()}
            >
              {isReverting ? "Reverting…" : "Yes, Revert"}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

// --- Bulk Import Panel ---
function BulkImportPanel() {
  const { data: companies } = useCompanies();
  const { mutate: uploadCsv, isPending: isCsvPending } = useBulkCsvImport();
  const { mutate: uploadPdf, isPending: isPdfPending } = useUploadNGXPdf();
  const addToast = useUIStore((s) => s.addToast);

  const isPending = isCsvPending || isPdfPending;

  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<Record<string, unknown> | null>(null);
  const [showSkipped, setShowSkipped] = useState(false);
  const [uploadMode, setUploadMode] = useState<"pdf" | "csv" | null>(null);

  const downloadTemplate = () => {
    const list = companies ?? [];
    const rows =
      list.length > 0
        ? list.slice(0, 5).map((c) => `${c.ticker},0.00,${new Date().toISOString().slice(0, 10)}`)
        : ["DANGCEM,0.00,2026-04-30", "ZENITHBANK,0.00,2026-04-30", "GTCO,0.00,2026-04-30"];

    const content = ["ticker,price,date", ...rows].join("\n");
    const blob = new Blob([content], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `epm_price_template_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePdfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith(".pdf")) {
      addToast({ title: "Invalid File", description: "Only .pdf files accepted", type: "error" });
      return;
    }

    setFile(selected);
    setShowSkipped(false);
    setUploadMode("pdf");
    uploadPdf(selected, {
      onSuccess: (res) => {
        setPreviewData(res.data as Record<string, unknown>);
        setStep(3); // PDF is automatically committed on the backend
      },
      onError: (err: Error) => {
        addToast({ title: "Upload Failed", description: err.message, type: "error" });
        setFile(null);
      },
    });
    e.target.value = "";
  };

  const handleCsvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith(".csv")) {
      addToast({ title: "Invalid File", description: "Only .csv files accepted", type: "error" });
      return;
    }

    if (selected.size > MAX_CSV_BYTES) {
      addToast({ title: "File too large", description: "CSV must be at most 5MB.", type: "error" });
      return;
    }

    setFile(selected);
    setShowSkipped(false);
    setUploadMode("csv");
    uploadCsv(
      { file: selected, commit: false },
      {
        onSuccess: (res) => {
          setPreviewData(res.data as Record<string, unknown>);
          setStep(2);
        },
        onError: (err: Error) => {
          addToast({ title: "Upload Failed", description: err.message, type: "error" });
          setFile(null);
        },
      },
    );
    e.target.value = "";
  };

  const handleCommit = () => {
    if (!file) return;
    uploadCsv(
      { file, commit: true },
      {
        onSuccess: (res) => {
          setPreviewData(res.data as Record<string, unknown>);
          setStep(3);
          setShowSkipped(false);
        },
        onError: (err: Error) => {
          addToast({ title: "Commit Failed", description: err.message, type: "error" });
        },
      },
    );
  };

  const reset = () => {
    setFile(null);
    setPreviewData(null);
    setStep(1);
    setShowSkipped(false);
    setUploadMode(null);
  };

  return (
    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden flex flex-col h-full">
      <div className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-white">NGX Price Update</h2>
        <span className="text-[11px] font-mono text-white/40 bg-white/5 px-2 py-0.5 rounded">
          {uploadMode === "pdf" ? "PDF PARSER" : `STEP ${step}/3`}
        </span>
      </div>

      <div className="p-5 flex-1 space-y-6">
        {step === 1 && (
          <div className="space-y-6 animate-in fade-in zoom-in-95 duration-200">
            {/* PDF UPLOAD SECTION */}
            <div className="border border-[var(--border)] rounded-xl p-5 space-y-4">
              <div className="flex items-center gap-2 text-white font-medium text-[14px]">
                <UploadCloud className="w-4 h-4 text-[var(--accent-lavender)]" />
                Primary: Upload NGX PDF
              </div>
              <p className="text-[13px] text-white/60 leading-relaxed">
                Upload the NGX Daily Official List PDF directly. No manual conversion needed —
                prices are extracted automatically.
                <br />
                <a
                  href="https://ngxgroup.com/exchange/data/data-library/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-400 hover:text-blue-300 underline mt-1 inline-block"
                >
                  Download PDF from NGX Data Library
                </a>
              </p>

              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                  disabled={isPending}
                />
                <div
                  className={cn(
                    "border-2 border-dashed rounded-xl p-6 text-center transition-colors flex flex-col items-center justify-center gap-2",
                    isPdfPending
                      ? "border-[var(--accent-lavender)]/50 bg-[var(--accent-lavender)]/5"
                      : "border-white/10 hover:border-white/20 hover:bg-white/[0.02]",
                  )}
                >
                  <UploadCloud
                    className={cn(
                      "w-6 h-6",
                      isPdfPending
                        ? "text-[var(--accent-lavender)] animate-pulse"
                        : "text-white/30",
                    )}
                  />
                  <div>
                    <div className="text-[13px] font-medium text-white mb-0.5">
                      {isPdfPending
                        ? "Uploading & Parsing PDF..."
                        : "Drop NGX PDF here or click to browse"}
                    </div>
                    <div className="text-[11px] text-white/40">.pdf accepted · max 20MB</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-white/10"></div>
              <span className="flex-shrink-0 mx-4 text-white/40 text-[12px] uppercase tracking-wider font-medium">
                OR
              </span>
              <div className="flex-grow border-t border-white/10"></div>
            </div>

            {/* CSV UPLOAD SECTION */}
            <div className="border border-[var(--border)] rounded-xl p-5 space-y-4">
              <div className="flex items-center gap-2 text-white font-medium text-[14px]">
                Alternative: Manual CSV Upload
              </div>
              <p className="text-[13px] text-white/60 leading-relaxed">
                If you prefer CSV format. Required columns: <code>ticker, price, date</code>
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  type="button"
                  onClick={downloadTemplate}
                  className="flex-1 h-9 border border-white/20 text-white/70 hover:text-white hover:bg-white/5 rounded-lg text-[13px] font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  CSV Template
                </button>
                <div className="relative flex-1">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleCsvChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    disabled={isPending}
                  />
                  <button
                    type="button"
                    className="w-full h-9 border border-[var(--accent-lavender)]/50 bg-[var(--accent-lavender)]/10 text-[var(--accent-lavender)] hover:bg-[var(--accent-lavender)]/20 rounded-lg text-[13px] font-medium transition-colors flex items-center justify-center gap-2"
                    disabled={isPending}
                  >
                    <UploadCloud className="w-4 h-4" />
                    {isCsvPending ? "Uploading..." : "Upload CSV"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 2 && previewData && uploadMode === "csv" && (
          <div className="space-y-4 animate-in slide-in-from-right-4 duration-300">
            <div className="flex items-center gap-3 text-[14px]">
              <div className="flex items-center gap-1.5 text-[var(--accent-emerald)] font-medium">
                <span>{previewData.valid as number}</span> valid
              </div>
              <span className="text-white/20">•</span>
              <div className="flex items-center gap-1.5 text-[var(--accent-red)] font-medium">
                <span>{previewData.errors as number}</span> errors
              </div>
            </div>

            <div className="border border-white/10 rounded-lg overflow-hidden bg-black/20 text-[12px] font-mono">
              <div className="px-3 py-2 bg-white/5 border-b border-white/10 text-white/50 text-[11px] uppercase tracking-wider">
                Preview (First 10 Valid)
              </div>
              {(previewData.preview_rows as unknown[] | undefined)?.length === 0 ? (
                <div className="p-4 text-center text-white/30 italic">No valid rows found</div>
              ) : (
                <div className="divide-y divide-white/5 max-h-[160px] overflow-y-auto scrollbar-thin">
                  {((previewData.preview_rows as Array<Record<string, unknown>>) ?? []).map(
                    (r, i) => (
                      <div
                        key={i}
                        className="px-3 py-2 flex items-center justify-between hover:bg-white/5"
                      >
                        <div className="flex items-center gap-4">
                          <span className="text-white w-20 truncate">{String(r.ticker)}</span>
                          <span className="text-white/50">{String(r.date)}</span>
                        </div>
                        <div className="text-right">
                          {r.old_price != null && String(r.old_price) !== "" && (
                            <span className="text-white/40 line-through mr-2">
                              ₦{String(r.old_price)}
                            </span>
                          )}
                          <span className="text-[var(--accent-emerald)]">₦{String(r.price)}</span>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}

              {Array.isArray(previewData.error_rows) && previewData.error_rows.length > 0 && (
                <>
                  <div className="px-3 py-2 bg-red-500/10 border-y border-red-500/20 text-red-400 text-[11px] uppercase tracking-wider">
                    Error Rows ({previewData.error_rows.length})
                  </div>
                  <div className="divide-y divide-red-500/10 max-h-[160px] overflow-y-auto scrollbar-thin">
                    {(previewData.error_rows as Array<Record<string, unknown>>).map((er, i) => (
                      <div
                        key={i}
                        className="px-3 py-2 border-l-2 border-[var(--accent-red)] bg-red-500/5 flex flex-col gap-1"
                      >
                        <div className="flex items-center gap-2 text-white/70">
                          <AlertTriangle className="w-3 h-3 text-[var(--accent-red)]" />
                          <span>
                            Row {String(er.row)}: <strong>{String(er.ticker || "UNKNOWN")}</strong>
                          </span>
                        </div>
                        <div className="text-[var(--accent-red)] pl-5 leading-relaxed">
                          {Array.isArray(er.errors)
                            ? (er.errors as string[]).map((err, j) => <div key={j}>— {err}</div>)
                            : null}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={reset}
                className="px-4 h-10 border border-white/10 hover:bg-white/5 text-white/70 text-[13px] font-medium rounded-lg transition-colors flex items-center gap-2"
                disabled={isPending}
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                type="button"
                onClick={handleCommit}
                disabled={(previewData.valid as number) === 0 || isPending}
                className="flex-1 h-10 bg-[var(--accent-lavender)] text-[#1A1A1A] text-[14px] font-medium rounded-lg hover:brightness-110 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
              >
                {isPending ? "Committing..." : `Commit ${previewData.valid as number} rows`}
                {!isPending && <ArrowRight className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}

        {step === 3 && previewData && (
          <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-300 flex flex-col items-center text-center py-6">
            <div className="w-16 h-16 rounded-full bg-[var(--accent-emerald)]/20 flex items-center justify-center mb-2">
              <div className="w-10 h-10 rounded-full bg-[var(--accent-emerald)] text-black flex items-center justify-center">
                <Check className="w-6 h-6" />
              </div>
            </div>

            <div className="space-y-1">
              <h3 className="text-[18px] font-bold text-white">Import Complete</h3>
              <p className="text-[14px] text-white/60">
                Successfully updated{" "}
                <strong className="text-white">
                  {previewData[uploadMode === "pdf" ? "updated" : "committed"] as number}
                </strong>{" "}
                prices.
              </p>
            </div>

            {((uploadMode === "csv" && (previewData.errors as number) > 0) ||
              (uploadMode === "pdf" &&
                ((previewData.skipped as number) > 0 ||
                  (previewData.parse_errors as number) > 0))) && (
              <div className="w-full max-w-[520px] text-left space-y-2">
                <button
                  type="button"
                  onClick={() => setShowSkipped((v) => !v)}
                  className="w-full flex items-center justify-between text-[13px] text-white/70 hover:text-white transition-colors bg-white/5 border border-white/10 rounded-lg px-3 py-2"
                >
                  <span>
                    ⚠{" "}
                    {uploadMode === "pdf"
                      ? `${(previewData.skipped as number) + (previewData.parse_errors as number)} tickers skipped or failed`
                      : `${previewData.errors as number} rows skipped`}
                  </span>
                  <span className="text-white/50">
                    {showSkipped ? "Hide details ▲" : "Show details ▼"}
                  </span>
                </button>

                {showSkipped && (
                  <div className="border border-white/10 rounded-lg overflow-hidden bg-black/20 text-[12px] font-mono">
                    <div className="px-3 py-2 bg-white/5 border-b border-white/10 text-white/50 text-[11px] uppercase tracking-wider">
                      Skipped Details
                    </div>
                    <div className="divide-y divide-red-500/10 max-h-[220px] overflow-y-auto scrollbar-thin">
                      {uploadMode === "csv" && Array.isArray(previewData.error_rows)
                        ? (previewData.error_rows as Array<Record<string, unknown>>).map(
                            (er, i) => (
                              <div
                                key={i}
                                className="px-3 py-2 border-l-2 border-[var(--accent-red)] bg-red-500/5 flex flex-col gap-1"
                              >
                                <div className="flex items-center gap-2 text-white/70">
                                  <AlertTriangle className="w-3 h-3 text-[var(--accent-red)]" />
                                  <span>
                                    Row {String(er.row)}:{" "}
                                    <strong>{String(er.ticker || "UNKNOWN")}</strong>
                                  </span>
                                </div>
                                <div className="text-[var(--accent-red)] pl-5 leading-relaxed">
                                  {Array.isArray(er.errors) ? (
                                    (er.errors as string[]).map((err, j) => (
                                      <div key={j}>— {err}</div>
                                    ))
                                  ) : (
                                    <div>— Unknown error</div>
                                  )}
                                </div>
                              </div>
                            ),
                          )
                        : uploadMode === "pdf" && Array.isArray(previewData.error_details)
                          ? (previewData.error_details as Array<Record<string, unknown>>).map(
                              (er, i) => (
                                <div
                                  key={i}
                                  className="px-3 py-2 border-l-2 border-[var(--accent-red)] bg-red-500/5 flex flex-col gap-1"
                                >
                                  <div className="flex items-center gap-2 text-white/70">
                                    <AlertTriangle className="w-3 h-3 text-[var(--accent-red)]" />
                                    <span>
                                      <strong>{String(er.ticker || "UNKNOWN")}</strong>
                                    </span>
                                  </div>
                                  <div className="text-[var(--accent-red)] pl-5 leading-relaxed">
                                    — {String(er.reason)}
                                  </div>
                                </div>
                              ),
                            )
                          : null}
                    </div>
                  </div>
                )}
              </div>
            )}

            <button
              type="button"
              onClick={reset}
              className="mt-4 px-6 h-10 bg-white/10 hover:bg-white/15 text-white text-[13px] font-medium rounded-lg transition-colors"
            >
              Upload Another File
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
