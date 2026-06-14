import { create } from "zustand";
import { useAuthStore } from "./authStore";

export interface Toast {
  id: string;
  title: string;
  description?: string;
  type: "success" | "error" | "info" | "warning";
  /** When set, overrides default 5s auto-dismiss. */
  durationMs?: number;
}

interface UIStore {
  editMode: boolean;
  toggleEditMode: () => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (v: boolean) => void;
  // Toast notifications
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void; // id added internally; pass durationMs to override 5s
  removeToast: (id: string) => void;
  // Dashboard
  holdingsChartView: "value" | "shares";
  setHoldingsChartView: (v: "value" | "shares") => void;
}

export const useUIStore = create<UIStore>((set) => ({
  editMode: false,
  toggleEditMode: () => {
    if (!useAuthStore.getState().isAdmin()) return;
    set((s) => ({ editMode: !s.editMode }));
  },
  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
  // Toasts
  toasts: [],
  addToast: (toast) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const { durationMs, ...rest } = toast;
    const dismissMs = durationMs ?? 5000;
    set((s) => ({ toasts: [...s.toasts, { ...rest, id }] }));
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, dismissMs);
  },
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
  // Dashboard
  holdingsChartView: "value",
  setHoldingsChartView: (v) => set({ holdingsChartView: v }),
}));
