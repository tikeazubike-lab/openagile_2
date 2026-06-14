// EPM Phase 2 — Auth store.
// Initial state: user is NULL (requires authentication).
// Populated by GET /api/v1/auth/me in _app.tsx beforeLoad after login cookie set.

import { create } from "zustand";
import type { User } from "@/types";

interface AuthStore {
  user: User | null;
  isAdmin: () => boolean;
  setUser: (user: User) => void;
  clearUser: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  // Phase 2: null on startup — _app.tsx beforeLoad hydrates from cookie via /api/v1/auth/me
  user: null,
  isAdmin: () => get().user?.role === "admin",
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null }),
}));
