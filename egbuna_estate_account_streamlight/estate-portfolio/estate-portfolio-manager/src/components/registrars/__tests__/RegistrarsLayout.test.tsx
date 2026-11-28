// Spec: F-026-registrar-dashboard.md | §9 tabs amendment (2026-11-24)
// AC-8: the Registrars tab is active on load; the dashboard is not rendered and
// its two endpoints are not requested.
// AC-7: activating the Dashboard tab renders the dashboard tiles and tracker
// from the two endpoints.
// NOTE: no @testing-library/jest-dom import (package missing — AUDIT R10);
// plain vitest matchers + Testing Library queries only. Radix tabs activate on
// mouseDown (left button) or keyboard, not on click, and @testing-library/
// user-event is not installed — use fireEvent.mouseDown(tab, { button: 0 }).
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RegistrarsLayout } from "../RegistrarsLayout";

const summaryBody = {
  data: {
    completion_pct: 62.5,
    total_requirements: 8,
    completed_requirements: 5,
    pending_requirements: 3,
    top_action_items: [],
    registrar_health: { complete: 1, attention: 0, no_data: 0 },
    unmapped_companies: { count: 0, companies: [] },
  },
  meta: {},
  error: null,
};

const trackerBody = {
  data: { rows: [], total: 0, page: 1, page_size: 20, total_pages: 1 },
  meta: {},
  error: null,
};

function jsonResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

describe("RegistrarsLayout tabs (F-026 §9)", () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/registrars/dashboard-summary")) {
        return jsonResponse(summaryBody);
      }
      if (url.includes("/api/v1/registrar-requirements/global-tracker")) {
        return jsonResponse(trackerBody);
      }
      if (url.includes("/api/v1/registrars")) {
        // RegistrarList (useRegistrars → apiFetch unwraps the envelope)
        return jsonResponse({ data: [], meta: {}, error: null });
      }
      throw new Error(`Unexpected fetch in test: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  function renderLayout() {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(
      <QueryClientProvider client={queryClient}>
        <RegistrarsLayout />
      </QueryClientProvider>,
    );
  }

  function dashboardFetchCount() {
    return fetchMock.mock.calls.filter((call) => {
      const url = String(call[0]);
      return url.includes("dashboard-summary") || url.includes("global-tracker");
    }).length;
  }

  // Spec: F-026-registrar-dashboard.md | AC-8 | Then the Registrars tab is active
  // on load, the list heading and details placeholder are shown, and the
  // dashboard is neither rendered nor requested.
  it("loads with the Registrars tab selected and no dashboard fetches (AC-8)", async () => {
    renderLayout();

    // The "Registrars" tab is the selected one on first render
    const tab = screen.getByRole("tab", { name: "Registrars" });
    expect(tab.getAttribute("aria-selected")).toBe("true");

    // List/details layout is visible (as before F-026)
    expect(await screen.findByRole("heading", { name: "Registrars" })).toBeTruthy();
    expect(screen.getByText("Select a registrar to view details")).toBeTruthy();

    // The dashboard is not mounted on the Registrars tab
    expect(screen.queryByText("Registrar Dashboard")).toBeNull();

    // ...and its two endpoints were never requested
    expect(dashboardFetchCount()).toBe(0);
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then selecting the Dashboard tab
  // renders the dashboard tiles and tracker from the two endpoints.
  it("renders the dashboard after activating the Dashboard tab (AC-7)", async () => {
    renderLayout();

    // Radix activates tabs on mouseDown (left button), not click
    fireEvent.mouseDown(screen.getByRole("tab", { name: "Dashboard" }), {
      button: 0,
    });

    expect(await screen.findByText("Registrar Dashboard")).toBeTruthy();
    expect(await screen.findByText("62.5%")).toBeTruthy();
  });
});
