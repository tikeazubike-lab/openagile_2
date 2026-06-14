// frontend/tests/unit/components/Navbar.test.tsx
/**
 * Stage 1B.5 — Navbar Component Unit Tests
 * Tests Edit Mode toggle (admin-only), theme toggle (all roles),
 * bell icon visibility, and avatar dropdown content.
 *
 * Architecture note (from Codex handover):
 *   authStore: src/store/authStore.ts  — Zustand, role-based isAdmin()
 *   uiStore:   src/store/uiStore.ts    — editMode boolean, toggleEditMode()
 *   useTheme:  src/hooks/useTheme.ts   — resolvedTheme + toggleTheme()
 */
import { render, screen, fireEvent, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Navbar } from "../../../src/components/layout/Navbar";
import { useAuthStore } from "../../../src/store/authStore";
import { useUIStore } from "../../../src/store/uiStore";

// ---------------------------------------------------------------------------
// Mock TanStack Router (Navbar reads current route for page title)
// ---------------------------------------------------------------------------
vi.mock("@tanstack/react-router", () => ({
  useLocation: () => ({ pathname: "/dashboard" }),
  useNavigate: () => vi.fn(),
  Link: ({ children }: { children: React.ReactNode }) => <a>{children}</a>,
}));

// ---------------------------------------------------------------------------
// Mock useTheme — we test the hook independently in useTheme.test.ts
// ---------------------------------------------------------------------------
const mockToggleTheme = vi.fn();
vi.mock("../../../src/hooks/useTheme", () => ({
  useTheme: () => ({
    resolvedTheme: "light",
    toggleTheme: mockToggleTheme,
  }),
}));

const ADMIN = { id: 1, username: "zubbyik", name: "Zubby", role: "admin" as const };
const VIEWER = { id: 2, username: "viewer", name: "Viewer", role: "readonly" as const };

beforeEach(() => {
  useAuthStore.setState({ user: null });
  useUIStore.setState({ editMode: false, sidebarOpen: false });
  mockToggleTheme.mockClear();
});

// ===========================================================================
// Page title
// ===========================================================================

describe("Navbar — page title", () => {
  it("renders page title for current route", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    // /dashboard → "Dashboard"
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });
});

// ===========================================================================
// Edit Mode toggle
// ===========================================================================

describe("Navbar — Edit Mode toggle", () => {
  it("shows edit mode toggle for admin", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    expect(screen.getByRole("button", { name: /viewing|editing/i })).toBeInTheDocument();
  });

  it("hides edit mode toggle for readonly role", () => {
    useAuthStore.setState({ user: VIEWER });
    render(<Navbar />);
    expect(screen.queryByRole("button", { name: /viewing|editing/i })).not.toBeInTheDocument();
  });

  it("shows Viewing state by default", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    expect(screen.getByText(/viewing/i)).toBeInTheDocument();
  });

  it("shows Editing state when editMode is true", () => {
    useAuthStore.setState({ user: ADMIN });
    useUIStore.setState({ editMode: true });
    render(<Navbar />);
    expect(screen.getByText(/editing/i)).toBeInTheDocument();
  });

  it("clicking toggle calls toggleEditMode", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    const toggle = screen.getByRole("button", { name: /viewing|editing/i });
    await user.click(toggle);
    expect(useUIStore.getState().editMode).toBe(true);
  });
});

// ===========================================================================
// Theme toggle
// ===========================================================================

describe("Navbar — theme toggle", () => {
  it("shows Moon icon in light mode", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    // Moon icon has aria-label or test-id "theme-toggle"
    const btn = screen.getByTestId("theme-toggle");
    expect(btn).toBeInTheDocument();
    // In light mode the accessible label should mention "dark mode"
    expect(btn).toHaveAccessibleName(/switch to dark/i);
  });

  it("theme toggle is visible to admin", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    expect(screen.getByTestId("theme-toggle")).toBeInTheDocument();
  });

  it("theme toggle is visible to readonly role", () => {
    useAuthStore.setState({ user: VIEWER });
    render(<Navbar />);
    expect(screen.getByTestId("theme-toggle")).toBeInTheDocument();
  });

  it("clicking theme toggle calls toggleTheme", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    await user.click(screen.getByTestId("theme-toggle"));
    expect(mockToggleTheme).toHaveBeenCalledOnce();
  });
});

// ===========================================================================
// Bell icon
// ===========================================================================

describe("Navbar — bell icon", () => {
  it("shows bell icon for admin", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    expect(screen.getByTestId("nav-bell")).toBeInTheDocument();
  });

  it("hides bell icon for readonly role", () => {
    useAuthStore.setState({ user: VIEWER });
    render(<Navbar />);
    expect(screen.queryByTestId("nav-bell")).not.toBeInTheDocument();
  });
});

// ===========================================================================
// Avatar dropdown
// ===========================================================================

describe("Navbar — avatar dropdown", () => {
  it("clicking avatar opens dropdown with Sign Out", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    await user.click(screen.getByTestId("user-avatar"));
    expect(screen.getByRole("menuitem", { name: /sign out/i })).toBeInTheDocument();
  });

  it("dropdown contains Profile option", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    await user.click(screen.getByTestId("user-avatar"));
    expect(screen.getByRole("menuitem", { name: /profile/i })).toBeInTheDocument();
  });

  it("dropdown contains Change Password option", async () => {
    const user = userEvent.setup();
    useAuthStore.setState({ user: ADMIN });
    render(<Navbar />);
    await user.click(screen.getByTestId("user-avatar"));
    expect(screen.getByRole("menuitem", { name: /change password/i })).toBeInTheDocument();
  });
});
