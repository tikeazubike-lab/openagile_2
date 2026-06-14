// frontend/tests/unit/components/Sidebar.test.tsx
/**
 * Stage 1B.5 — Sidebar Component Unit Tests
 *
 * CRITICAL TEST in this file:
 *   test_sidebar_logout_button_calls_api_before_clearing_store()
 *   test_sidebar_logout_clears_store_even_if_api_fails()
 *
 * These are regression guards for the confirmed logout bug from Phase 2A:
 * the Sidebar was clearing Zustand state without calling POST /api/v1/auth/logout
 * or triggering TanStack Router navigation.
 *
 * Architecture note (Codex handover):
 *   - auth router lives at app/routers/auth.py
 *   - POST /api/v1/auth/logout clears the httpOnly epm_token cookie
 *   - Sidebar calls clearUser() and useNavigate({ to: "/login" }) AFTER API call
 *   - finally{} block ensures clearUser fires even on network failure
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

import { Sidebar } from "../../../src/components/layout/Sidebar";
import { useAuthStore } from "../../../src/store/authStore";
import { useUIStore } from "../../../src/store/uiStore";

// ---------------------------------------------------------------------------
// MSW server
// ---------------------------------------------------------------------------
const server = setupServer(
  http.post("/api/v1/auth/logout", () => {
    return HttpResponse.json({ data: null, error: null }, { status: 200 });
  })
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  useAuthStore.setState({ user: null });
  useUIStore.setState({ editMode: false, sidebarOpen: false });
});
afterAll(() => server.close());

// ---------------------------------------------------------------------------
// Mock TanStack Router
// ---------------------------------------------------------------------------
const mockNavigate = vi.fn();
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: "/dashboard" }),
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
}));

const ADMIN = { id: 1, username: "zubbyik", name: "Zubby", role: "admin" as const };
const VIEWER = { id: 2, username: "viewer", name: "Viewer", role: "readonly" as const };

beforeEach(() => mockNavigate.mockClear());

// ===========================================================================
// Navigation items
// ===========================================================================

describe("Sidebar — navigation", () => {
  it("renders all main nav items", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Sidebar />);
    const expectedLabels = [
      /dashboard/i, /holdings/i, /companies/i, /dividends/i,
      /price history/i, /transactions/i, /registrars/i,
      /watchlist/i, /nav history/i, /rebalancing/i,
    ];
    for (const label of expectedLabels) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
  });

  it("renders admin section for admin role", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Sidebar />);
    expect(screen.getByText(/price entry/i)).toBeInTheDocument();
    expect(screen.getByText(/user management/i)).toBeInTheDocument();
    expect(screen.getByText(/deleted records/i)).toBeInTheDocument();
  });

  it("hides admin section for readonly role", () => {
    useAuthStore.setState({ user: VIEWER });
    render(<Sidebar />);
    expect(screen.queryByText(/price entry/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/user management/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/deleted records/i)).not.toBeInTheDocument();
  });

  it("highlights the active route", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Sidebar />);
    // /dashboard is the mocked current route
    const dashLink = screen.getByText(/^dashboard$/i).closest("a, [role=link], li");
    expect(dashLink).toHaveClass(/active|bg-\[var\(--accent-lavender\)\]/);
  });
});

// ===========================================================================
// LOGOUT — regression suite for Phase 2A confirmed bug
// ===========================================================================

describe("Sidebar — logout (regression)", () => {
  it("logout button calls POST /api/v1/auth/logout before clearing store", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });

    let apiCallReceived = false;
    server.use(
      http.post("/api/v1/auth/logout", () => {
        apiCallReceived = true;
        return HttpResponse.json({ data: null, error: null });
      })
    );

    render(<Sidebar />);
    await user.click(screen.getByRole("button", { name: /log out|sign out/i }));

    await waitFor(() => expect(apiCallReceived).toBe(true));
  });

  it("clears Zustand store after API responds", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Sidebar />);

    await user.click(screen.getByRole("button", { name: /log out|sign out/i }));

    await waitFor(() => {
      expect(useAuthStore.getState().user).toBeNull();
    });
  });

  it("navigates to /login after logout", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Sidebar />);

    await user.click(screen.getByRole("button", { name: /log out|sign out/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.objectContaining({ to: "/login" })
      );
    });
  });

  it("clears store even if API call fails (finally block guard)", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });

    // Make logout API fail with network error
    server.use(
      http.post("/api/v1/auth/logout", () => {
        return HttpResponse.error();
      })
    );

    render(<Sidebar />);
    await user.click(screen.getByRole("button", { name: /log out|sign out/i }));

    // Even on failure, user must be cleared and navigation must fire
    await waitFor(() => {
      expect(useAuthStore.getState().user).toBeNull();
    });
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.objectContaining({ to: "/login" })
      );
    });
  });

  it("does NOT clear store before API call returns", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });

    let resolveLogout!: () => void;
    server.use(
      http.post("/api/v1/auth/logout", () => {
        return new Promise<Response>((resolve) => {
          resolveLogout = () =>
            resolve(HttpResponse.json({ data: null, error: null }));
        });
      })
    );

    render(<Sidebar />);
    await user.click(screen.getByRole("button", { name: /log out|sign out/i }));

    // While API is pending, store must still have the user
    expect(useAuthStore.getState().user).not.toBeNull();

    // Now resolve the API
    resolveLogout();
    await waitFor(() => expect(useAuthStore.getState().user).toBeNull());
  });
});
