// frontend/tests/unit/components/Login.test.tsx
/**
 * Stage 1B.5 — Login Component Unit Tests
 * Uses MSW to intercept fetch calls — no real API.
 * Tests form rendering, submission states, error display, security guards.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

import { LoginPage } from "../../../src/pages/login";
import { useAuthStore } from "../../../src/store/authStore";

// ---------------------------------------------------------------------------
// MSW Server
// ---------------------------------------------------------------------------

const server = setupServer(
  http.post("/api/v1/auth/login", async ({ request }) => {
    const body = await request.json() as { username: string; password: string };
    if (body.username === "zubbyik" && body.password === "correctpass") {
      return HttpResponse.json({
        data: { user: { id: 1, username: "zubbyik", name: "Zubby", role: "admin" } },
        error: null,
      });
    }
    return HttpResponse.json(
      { data: null, error: { message: "Invalid credentials" } },
      { status: 401 }
    );
  })
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  useAuthStore.setState({ user: null });
});
afterAll(() => server.close());

// ---------------------------------------------------------------------------
// Mock TanStack Router navigate
// ---------------------------------------------------------------------------
const mockNavigate = vi.fn();
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => mockNavigate,
  Link: ({ children }: { children: React.ReactNode }) => <a>{children}</a>,
}));

// ===========================================================================
// Tests
// ===========================================================================

describe("Login — rendering", () => {
  it("renders username and password fields", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("renders sign in button", () => {
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("does NOT contain skip to demo link — regression guard", () => {
    render(<LoginPage />);
    expect(screen.queryByText(/skip to demo/i)).not.toBeInTheDocument();
  });
});

describe("Login — submission", () => {
  it("shows spinner during submission", async () => {
    const user = userEvent.setup();
    // Make login hang so we can catch the loading state
    server.use(
      http.post("/api/v1/auth/login", async () => {
        await new Promise((r) => setTimeout(r, 500));
        return HttpResponse.json({ data: { user: {} }, error: null });
      })
    );

    render(<LoginPage />);
    await user.type(screen.getByLabelText(/username/i), "zubbyik");
    await user.type(screen.getByLabelText(/password/i), "correctpass");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByRole("button", { name: /sign in/i })).toBeDisabled();
  });

  it("shows error message on 401 response", async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    await user.type(screen.getByLabelText(/username/i), "zubbyik");
    await user.type(screen.getByLabelText(/password/i), "wrongpass");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it("navigates to dashboard on successful login", async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    await user.type(screen.getByLabelText(/username/i), "zubbyik");
    await user.type(screen.getByLabelText(/password/i), "correctpass");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.objectContaining({ to: "/dashboard" })
      );
    });
  });
});

describe("Login — security guards", () => {
  it("does not store token in localStorage", async () => {
    const user = userEvent.setup();
    const setItemSpy = vi.spyOn(Storage.prototype, "setItem");

    render(<LoginPage />);
    await user.type(screen.getByLabelText(/username/i), "zubbyik");
    await user.type(screen.getByLabelText(/password/i), "correctpass");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(mockNavigate).toHaveBeenCalled());

    // localStorage.setItem must never be called with a token
    const tokenSetCalls = setItemSpy.mock.calls.filter(
      ([key]) => key.toLowerCase().includes("token") || key.toLowerCase().includes("jwt")
    );
    expect(tokenSetCalls).toHaveLength(0);
  });

  it("does not expose access_token in any DOM element", async () => {
    const user = userEvent.setup();
    render(<LoginPage />);
    await user.type(screen.getByLabelText(/username/i), "zubbyik");
    await user.type(screen.getByLabelText(/password/i), "correctpass");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(mockNavigate).toHaveBeenCalled());

    // No token-like string should appear in the rendered DOM
    const bodyText = document.body.innerHTML;
    expect(bodyText).not.toMatch(/eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/); // JWT pattern
  });
});
