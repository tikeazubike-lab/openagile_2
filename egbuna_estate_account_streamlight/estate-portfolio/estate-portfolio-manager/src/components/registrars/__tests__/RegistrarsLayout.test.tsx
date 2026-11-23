// Spec: F-026-registrar-dashboard.md | AC-7 | Then the /registrars page renders the
// dashboard at the top with the existing list/details layout unchanged.
// NOTE: no @testing-library/jest-dom import (package missing — AUDIT R10);
// plain vitest matchers + Testing Library queries only.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
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

describe("RegistrarsLayout (F-026 wiring)", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
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
      }),
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then the /registrars page renders the
  // dashboard above the unchanged list/details layout
  it("renders the dashboard above the existing list/details layout", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(
      <QueryClientProvider client={queryClient}>
        <RegistrarsLayout />
      </QueryClientProvider>,
    );

    // Dashboard at the top of /registrars
    expect(await screen.findByText("62.5%")).toBeTruthy();
    expect(screen.getByText("Registrar Dashboard")).toBeTruthy();
    // Existing list/details layout unchanged
    expect(screen.getByText("Registrars")).toBeTruthy();
    expect(screen.getByText("Select a registrar to view details")).toBeTruthy();
  });
});
