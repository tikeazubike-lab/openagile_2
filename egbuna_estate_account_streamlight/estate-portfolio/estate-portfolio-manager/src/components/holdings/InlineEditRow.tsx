import { useState, useEffect } from "react";
import { Save, X } from "lucide-react";
import type { Holding } from "@/types";
import { fmtNaira } from "@/lib/format";
import { SectorBadge, StatusBadge, ReturnText } from "@/components/shared/Badges";
import { cn } from "@/lib/utils";

interface InlineEditRowProps {
  holding: Holding;
  onSave: (id: number, data: { num_shares: number; avg_purchase_price: string }) => Promise<void>;
  onCancel: () => void;
  onValidationError: (msg: string) => void;
}

export function InlineEditRow({ holding, onSave, onCancel, onValidationError }: InlineEditRowProps) {
  const [shares, setShares] = useState(String(holding.shares));
  const [avgPurchasePrice, setAvgPurchasePrice] = useState(String(holding.avg_cost));
  const [saving, setSaving] = useState(false);

  // Sync form if holding prop changes while editing
  useEffect(() => {
    setShares(String(holding.shares));
    setAvgPurchasePrice(String(holding.avg_cost));
  }, [holding.shares, holding.avg_cost]);

  const handleSave = async () => {
    const parsedShares = Number(shares);
    const parsedAvgCost = parseFloat(avgPurchasePrice);

    if (!Number.isInteger(parsedShares) || parsedShares <= 0) {
      onValidationError("Shares must be a whole number greater than zero");
      return;
    }
    if (isNaN(parsedAvgCost) || parsedAvgCost <= 0) {
      onValidationError("Average cost must be a positive number");
      return;
    }

    setSaving(true);
    try {
      await onSave(holding.id, {
        num_shares: parsedShares,
        avg_purchase_price: parsedAvgCost.toFixed(2),
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <tr className="border-t border-[var(--border)] bg-[color-mix(in_oklab,var(--accent-lavender)_6%,transparent)]">
        {/* Ticker */}
        <td className="px-3 py-3 whitespace-nowrap">
          <span className="font-mono font-semibold text-[14px]">{holding.ticker}</span>
        </td>
        {/* Company */}
        <td className="px-3 py-3 whitespace-nowrap">
          <span className="text-[14px]">{holding.company}</span>
        </td>
        {/* Sector */}
        <td className="px-3 py-3 whitespace-nowrap">
          <SectorBadge sector={holding.sector} />
        </td>
        {/* Shares (editable) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <input
            type="number"
            min="1"
            step="1"
            className="w-24 px-2 py-1 text-right bg-background border rounded font-mono text-[13px]"
            value={shares}
            onChange={(e) => setShares(e.target.value)}
          />
        </td>
        {/* Avg Cost (editable) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <input
            type="number"
            min="0.01"
            step="0.01"
            className="w-24 px-2 py-1 text-right bg-background border rounded font-mono text-[13px]"
            value={avgPurchasePrice}
            onChange={(e) => setAvgPurchasePrice(e.target.value)}
          />
        </td>
        {/* Curr Price (read-only) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="text-right font-mono">{fmtNaira(holding.curr_price)}</div>
        </td>
        {/* Curr Value (read-only) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="text-right font-mono font-semibold">{fmtNaira(holding.curr_value)}</div>
        </td>
        {/* Cost Basis (read-only) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="text-right font-mono">{fmtNaira(holding.cost_basis)}</div>
        </td>
        {/* Return % (read-only) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="text-right">
            <ReturnText value={holding.return_pct} />
          </div>
        </td>
        {/* Div Yield (read-only) */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="text-right font-mono">
            {holding.div_yield != null ? `${holding.div_yield.toFixed(1)}%` : "-"}
          </div>
        </td>
        {/* Status (admin only, read-only) */}
        {holding.status && (
          <td className="px-3 py-3 whitespace-nowrap">
            <StatusBadge status={holding.status} />
          </td>
        )}
        {/* Actions */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="flex items-center gap-1 justify-end">
            <button
              onClick={handleSave}
              disabled={saving}
              className={cn(
                "w-7 h-7 rounded hover:bg-[var(--bg-subtle)] flex items-center justify-center text-green-600",
                saving && "opacity-50 cursor-not-allowed"
              )}
            >
              <Save className="w-4 h-4" />
            </button>
            <button
              onClick={onCancel}
              disabled={saving}
              className="w-7 h-7 rounded hover:bg-[var(--bg-subtle)] flex items-center justify-center text-[var(--text-secondary)]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </td>
      </tr>
    </>
  );
}
