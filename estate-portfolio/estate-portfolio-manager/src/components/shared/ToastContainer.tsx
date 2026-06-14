// ToastContainer — renders active toasts from uiStore in a fixed overlay.
// Toasts auto-dismiss after 5s (set in uiStore.addToast).
// Import this once, at the app shell level.

import { useUIStore, type Toast } from "@/store/uiStore";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

export function ToastContainer() {
  const { toasts, removeToast } = useUIStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const accent =
    toast.type === "success"
      ? "border-[var(--accent-emerald)] bg-[var(--accent-emerald)]/10"
      : toast.type === "error"
        ? "border-[var(--accent-red)] bg-[var(--accent-red)]/10"
        : toast.type === "warning"
          ? "border-amber-400 bg-amber-400/10"
          : "border-[var(--accent-lavender)] bg-[var(--accent-lavender)]/10";

  const icon =
    toast.type === "success"
      ? "✓"
      : toast.type === "error"
        ? "✕"
        : toast.type === "warning"
          ? "⚠"
          : "ℹ";

  const iconColor =
    toast.type === "success"
      ? "text-[var(--accent-emerald)]"
      : toast.type === "error"
        ? "text-[var(--accent-red)]"
        : toast.type === "warning"
          ? "text-amber-400"
          : "text-[var(--accent-lavender)]";

  return (
    <div
      className={cn(
        "pointer-events-auto w-[340px] flex items-start gap-3 px-4 py-3",
        "rounded-xl border shadow-xl backdrop-blur-sm",
        "bg-[var(--card)]/90",
        accent,
        "animate-in slide-in-from-right-4 fade-in duration-200",
      )}
    >
      <span className={cn("text-[15px] font-bold mt-0.5 shrink-0", iconColor)}>{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-semibold text-white truncate">{toast.title}</div>
        {toast.description && (
          <div className="text-[12px] text-white/60 mt-0.5 leading-relaxed line-clamp-2">
            {toast.description}
          </div>
        )}
      </div>
      <button
        onClick={onDismiss}
        className="shrink-0 mt-0.5 text-white/40 hover:text-white transition-colors"
        aria-label="Dismiss notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
