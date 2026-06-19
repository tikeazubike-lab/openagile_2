import React, { useState, useEffect } from "react";
import { X, Check } from "lucide-react";
import { useCompanies, useAddHolding } from "@/api/queries";
import { useQueryClient } from "@tanstack/react-query";
import { cn } from "@/lib/utils";

interface AddHoldingDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddHoldingDrawer({ isOpen, onClose }: AddHoldingDrawerProps) {
  const qc = useQueryClient();
  const { data: companies } = useCompanies();
  const addHolding = useAddHolding();

  const [companyId, setCompanyId] = useState<number | "">("");
  const [shares, setShares] = useState("");
  const [avgCost, setAvgCost] = useState("");
  const [purchaseDate, setPurchaseDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<"draft" | "live">("draft");
  const [errorMsg, setErrorMsg] = useState("");

  // Reset form when drawer closes
  useEffect(() => {
    if (!isOpen) {
      setCompanyId("");
      setShares("");
      setAvgCost("");
      setPurchaseDate(new Date().toISOString().split("T")[0]);
      setNotes("");
      setStatus("draft");
      setErrorMsg("");
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const handleSave = async (saveStatus: "draft" | "live") => {
    setErrorMsg("");
    if (!companyId) {
      setErrorMsg("Please select a company.");
      return;
    }
    const numShares = Number(shares);
    const cost = Number(avgCost);

    if (isNaN(numShares) || numShares <= 0 || !Number.isInteger(numShares)) {
      setErrorMsg("Shares must be a positive integer.");
      return;
    }
    if (isNaN(cost) || cost <= 0) {
      setErrorMsg("Average cost must be a positive number.");
      return;
    }

    // Check duplicate in cached holdings
    const cachedHoldings = qc.getQueryData<any[]>(["holdings"]);
    if (cachedHoldings?.find((h) => h.company_id === companyId && h.deleted_at == null)) {
      setErrorMsg("You already have a holding for this company.");
      return;
    }

    try {
      await addHolding.mutateAsync({
        company_id: companyId,
        num_shares: numShares,
        avg_purchase_price: cost,
        holding_type: saveStatus === "live" ? "active" : "draft",
        status: saveStatus === "live" ? "LIVE" : "DRAFT",
        notes,
      });
      onClose();
    } catch (e: any) {
      setErrorMsg(e.message || "Failed to add holding.");
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-[1px] transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-[420px] bg-[var(--bg-surface)] shadow-2xl border-l border-[var(--border)] flex flex-col animate-in slide-in-from-right duration-250">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Add Holding</h2>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              New holdings are created as Draft. Publish when ready.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 -mr-2 rounded hover:bg-[var(--bg-subtle)] text-[var(--text-secondary)] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {errorMsg && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md text-red-600 text-[13px] font-medium">
              {errorMsg}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[13px] font-semibold text-[var(--text-secondary)]">
              Company <span className="text-red-500">*</span>
            </label>
            <select
              value={companyId}
              onChange={(e) => setCompanyId(Number(e.target.value) || "")}
              className="w-full h-10 px-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] text-[var(--text-primary)] transition-shadow"
            >
              <option value="">Select Company...</option>
              {companies?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.ticker} — {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[13px] font-semibold text-[var(--text-secondary)]">
              Number of Shares <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="1"
              step="1"
              value={shares}
              onChange={(e) => setShares(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] text-[var(--text-primary)] font-mono transition-shadow"
              placeholder="e.g. 1000"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[13px] font-semibold text-[var(--text-secondary)]">
              Average Purchase Price (₦) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={avgCost}
              onChange={(e) => setAvgCost(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] text-[var(--text-primary)] font-mono transition-shadow"
              placeholder="e.g. 45.50"
            />
            <p className="text-xs text-[var(--text-muted)]">Weighted average across all purchases</p>
          </div>

          <div className="space-y-1.5">
            <label className="text-[13px] font-semibold text-[var(--text-secondary)]">
              Purchase Date
            </label>
            <input
              type="date"
              value={purchaseDate}
              onChange={(e) => setPurchaseDate(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] text-[var(--text-primary)] transition-shadow"
            />
            <p className="text-xs text-[var(--text-muted)]">Used for XIRR calculation</p>
          </div>

          <div className="space-y-1.5">
            <label className="text-[13px] font-semibold text-[var(--text-secondary)]">
              Notes
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full p-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] text-[var(--text-primary)] transition-shadow resize-none"
              placeholder="e.g. Purchased via Stanbic IBTC, Ref: TXN12345"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[13px] font-semibold text-[var(--text-secondary)]">
              Status
            </label>
            <div className="flex p-1 bg-[var(--bg-subtle)] rounded-lg">
              <button
                onClick={() => setStatus("draft")}
                className={cn(
                  "flex-1 py-1.5 text-[13px] font-medium rounded-md transition-colors",
                  status === "draft"
                    ? "bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm"
                    : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                )}
              >
                Draft
              </button>
              <button
                onClick={() => setStatus("live")}
                className={cn(
                  "flex-1 py-1.5 text-[13px] font-medium rounded-md transition-colors",
                  status === "live"
                    ? "bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm"
                    : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                )}
              >
                Publish now
              </button>
            </div>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              Draft holdings are hidden from portfolio totals
            </p>
          </div>
        </div>

        <div className="p-4 border-t border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 h-10 rounded-md text-[13px] font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-subtle)] transition-colors"
          >
            Cancel
          </button>
          {status === "draft" ? (
            <button
              onClick={() => handleSave("draft")}
              disabled={addHolding.isPending}
              className="px-4 h-10 rounded-md text-[13px] font-medium bg-[var(--bg-subtle)] text-[var(--text-primary)] border border-[var(--border)] hover:bg-[var(--bg-subtle)]/80 transition-colors disabled:opacity-50"
            >
              {addHolding.isPending ? "Saving..." : "Save as Draft"}
            </button>
          ) : (
            <button
              onClick={() => handleSave("live")}
              disabled={addHolding.isPending}
              className="px-4 h-10 rounded-md text-[13px] font-semibold bg-[var(--accent-lavender)] text-[#1A1A1A] hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-1.5"
            >
              <Check className="w-4 h-4" />
              {addHolding.isPending ? "Publishing..." : "Save & Publish"}
            </button>
          )}
        </div>
      </div>
    </>
  );
}
