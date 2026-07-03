// EPM Phase 2 — Authenticated app shell.
// beforeLoad: tries to hydrate auth state from the httpOnly JWT cookie via
//   GET /api/v1/auth/me. If the cookie is absent / expired → redirect to /login.
// Per Claude's architectural note: this guard belongs here (not in __root.tsx)
//   because __root.tsx also runs on the public /login route.

import { Outlet, redirect, createFileRoute } from "@tanstack/react-router";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { ToastContainer } from "@/components/shared/ToastContainer";
import { useAuthStore } from "@/store/authStore";
import type { User } from "@/types";

export const Route = createFileRoute("/_app")({
  beforeLoad: async ({ location }) => {
    // Fast-path: store is already populated (e.g. already visited an app page
    // in this session — Zustand holds state in memory).
    if (useAuthStore.getState().user) return;

    // Attempt to hydrate from the server-issued httpOnly cookie.
    // The cookie is sent automatically because credentials: "include" is set.
    let res: Response;
    try {
      res = await fetch("/api/v1/auth/me", {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
    } catch {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }

    if (!res.ok) {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }

    const { data }: { data: User } = await res.json();
    useAuthStore.getState().setUser(data);
  },
  component: AppShell,
});

function AppShell() {
  return (
    <div className="min-h-screen flex bg-[var(--bg-canvas)]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-4 md:p-6 overflow-x-auto">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
    </div>
  );
}
