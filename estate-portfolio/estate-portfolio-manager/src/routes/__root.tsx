// EPM Phase 2 — Root route (SPA mode, no TanStack Start SSR).
// shellComponent, HeadContent, Scripts are TanStack Start concepts — removed.
// Google Fonts + anti-FOUC script now live in index.html.
// QueryClient is provided here so all child routes can use TanStack Query.

import { Outlet, createRootRoute, Link } from "@tanstack/react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { useTheme } from "@/hooks/useTheme";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--bg-canvas)] px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-[var(--text-primary)] font-mono">404</h1>
        <h2 className="mt-4 text-xl font-semibold text-[var(--text-primary)]">Page not found</h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          The page you're looking for doesn't exist.
        </p>
        <div className="mt-6">
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center rounded-md bg-[var(--accent-lavender)] px-4 py-2 text-sm font-semibold text-[#1A1A1A] hover:opacity-90"
          >
            Go to dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}

function RootComponent() {
  // useTheme() reactively manages the .dark class on <html> and listens for
  // OS-level theme changes. The anti-FOUC script in index.html handles the
  // very first paint before React hydrates.
  useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  );
}

export const Route = createRootRoute({
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
});
