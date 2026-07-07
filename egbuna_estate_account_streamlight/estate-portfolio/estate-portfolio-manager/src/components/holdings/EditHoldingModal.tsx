import { useState } from "react";
import { X } from "lucide-react";
import type { Holding } from "@/types";
import { fmtNaira } from "@/lib/format";
import { useUpdateHolding } from "@/api/queries";

interface EditHoldingModalProps {
  holding: Holding;
  onClose: () => void;
}

export function EditHoldingModal({ holding, onClose }: EditHoldingModalProps) {
  const updateHolding = useUpdateHolding();

  const [shares, setShares] = useState(String(holding.shares));
  const [avgPurchasePrice, setAvgPurchasePrice] = useState(String(holding.avg_cost));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsedShares = Number(shares);
    const parsedAvgCost = parseFloat(avgPurchasePrice);

    if (!Number.isInteger(parsedShares) || parsedShares <= 0) {
      setError("Shares must be a whole number greater than zero");
      return;
    }
    if (isNaN(parsedAvgCost) || parsedAvgCost <= 0) {
      setError("Average cost must be a positive number");
      return;
    }

    setSaving(true);
    try {
      await updateHolding.mutateAsync({
        id: holding.id,
        num_shares: parsedShares,
        avg_purchase_price: parsedAvgCost.toFixed(2),
      });
      onClose();
    } catch (e: any) {
      setError(e.message || "Failed to update holding.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-3 border-b border-[var(--border)]">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            Edit Holding
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[var(--bg-subtle)] text-[var(--text-secondary)]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-5">
          {/* Read-only info */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-[var(--text-muted)]">{holding.ticker}</span>
            <span className="font-mono text-[var(--text-primary)]">
              {holding.company}
            </span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-[var(--text-muted)]">Current Value</span>
            <span className="font-mono font-semibold text-[var(--text-primary)]">
              {fmtNaira(holding.curr_value)}
            </span>
          </div>

          <hr className="border-[var(--border)]" />

          {/* Editable fields */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
              Shares
            </label>
            <input
              type="number"
              min="1"
              step="1"
              value={shares}
              onChange={(e) => setShares(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] font-mono text-[var(--text-primary)]"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
              Average Purchase Price (₦)
            </label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={avgPurchasePrice}
              onChange={(e) => setAvgPurchasePrice(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-[var(--bg-subtle)] border border-transparent focus:border-[var(--accent-lavender)] focus-ring text-[14px] font-mono text-[var(--text-primary)]"
              required
            />
          </div>

          {/* Error */}
          {error && (
            <div className="text-sm text-[var(--accent-red)] bg-red-50/50 px-3 py-2 rounded-md">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="h-9 px-4 rounded-md border border-[var(--border)] text-[13px] text-[var(--text-secondary)] hover:bg-[var(--bg-subtle)]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="h-9 px-4 rounded-md bg-[var(--accent-lavender)] text-[#1A1A1A] text-[13px] font-semibold hover:opacity-90 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
