// Spec: F-026-registrar-dashboard.md | AC-7 | Then the /registrars dashboard tiles and
// global tracker render from GET /api/v1/registrars/dashboard-summary and
// GET /api/v1/registrar-requirements/global-tracker, with no inline edit controls.
// NOTE: no @testing-library/jest-dom import (package missing — AUDIT R10);
// plain vitest matchers + Testing Library queries only.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RegistrarsDashboard } from "../RegistrarsDashboard";

// Envelope-shaped fixtures matching backend/app/routers/registrars.py (_envelope → {data, meta, error}).
const summaryBody = {
  data: {
    completion_pct: 62.5,
    total_requirements: 8,
    completed_requirements: 5,
    pending_requirements: 3,
    top_action_items: [
      {
        requirement_id: 21,
        task_name: "File annual return",
        document_title: "CAC Form 7",
        registrar_name: "Cardinal Registrars",
        due_date: "2026-12-01",
        is_required: true,
      },
    ],
    registrar_health: { complete: 1, attention: 2, no_data: 1 },
    unmapped_companies: {
      count: 3,
      companies: [
        { id: 1, ticker: "DANGCEM", name: "Dangote Cement" },
        { id: 2, ticker: "MTNN", name: "MTN Nigeria" },
        { id: 3, ticker: "ZENBANK", name: "Zenith Bank" },
      ],
    },
  },
  meta: {},
  error: null,
};

const trackerBody = {
  data: {
    rows: [
      {
        requirement_id: 30,
        status: "rejected",
        task_name: "Submit audited accounts",
        document_title: "Audited Financials",
        registrar_name: "Meristem Registrars",
        registrar_id: 9,
        due_date: "2026-12-15",
        is_required: true,
        latest_document: {
          id: 99,
          file_name: "afs-2026.pdf",
          status: "rejected",
          uploaded_at: "2026-11-02T09:30:00",
        },
        actions_available: ["upload"],
      },
    ],
    total: 45,
    page: 1,
    page_size: 20,
    total_pages: 3,
  },
  meta: {},
  error: null,
};

// Page 2 rows exercise the null renders: due_date null and latest_document null → "—".
const trackerBodyPage2 = {
  data: {
    rows: [
      {
        requirement_id: 31,
        status: "pending",
        task_name: "File AGM minutes",
        document_title: "AGM Minutes",
        registrar_name: "Cardinal Registrars",
        registrar_id: 7,
        due_date: null,
        is_required: false,
        latest_document: null,
        actions_available: ["upload", "remind"],
      },
    ],
    total: 45,
    page: 2,
    page_size: 20,
    total_pages: 3,
  },
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

function renderDashboard() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <RegistrarsDashboard />
    </QueryClientProvider>,
  );
}

describe("RegistrarsDashboard (F-026)", () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/registrars/dashboard-summary")) {
        return jsonResponse(summaryBody);
      }
      if (url.includes("/api/v1/registrar-requirements/global-tracker")) {
        return jsonResponse(url.includes("page=2") ? trackerBodyPage2 : trackerBody);
      }
      throw new Error(`Unexpected fetch in test: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then summary tiles render from dashboard-summary
  it("renders summary tiles from dashboard-summary", async () => {
    renderDashboard();

    // Completion % shown to 1 dp with a percent sign
    expect(await screen.findByText("62.5%")).toBeTruthy();
    // Requirement count tiles
    expect(screen.getByText("Total Requirements")).toBeTruthy();
    expect(screen.getByText("Completed")).toBeTruthy();
    expect(screen.getByText("Pending")).toBeTruthy();
    // Registrar health buckets
    expect(screen.getByText("Registrar Health")).toBeTruthy();
    expect(screen.getByText("Complete")).toBeTruthy();
    expect(screen.getByText("Attention")).toBeTruthy();
    expect(screen.getByText("No data")).toBeTruthy();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then a "Needs attention" item renders with
  // task, document, registrar and due date
  it("renders a needs-attention item from top_action_items", async () => {
    renderDashboard();

    expect(await screen.findByText("File annual return")).toBeTruthy();
    expect(screen.getByText("CAC Form 7")).toBeTruthy();
    expect(screen.getByText("Cardinal Registrars")).toBeTruthy();
    expect(screen.getByText("2026-12-01")).toBeTruthy();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then a global tracker row renders with task,
  // document, registrar, status, due date and latest document file + status
  it("renders a global tracker row with latest document", async () => {
    renderDashboard();

    expect(await screen.findByText("Submit audited accounts")).toBeTruthy();
    expect(screen.getByText("Audited Financials")).toBeTruthy();
    expect(screen.getByText("Meristem Registrars")).toBeTruthy();
    expect(screen.getByText("2026-12-15")).toBeTruthy();
    // Row status badge + latest-document status badge
    expect(screen.getAllByText("rejected").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("afs-2026.pdf")).toBeTruthy();
    // Server-side pagination metadata
    expect(screen.getByText(/Page 1 of 3/)).toBeTruthy();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then the tracker paginates server-side:
  // Next refetches ?page=2&page_size=20, and null due_date / null latest_document render "—"
  it("paginates the tracker server-side (page, page_size=20)", async () => {
    renderDashboard();

    await screen.findByText(/Page 1 of 3/);
    fireEvent.click(screen.getByRole("button", { name: /next/i }));

    expect(await screen.findByText(/Page 2 of 3/)).toBeTruthy();
    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(
      urls.some((u) => u.includes("/api/v1/registrar-requirements/global-tracker?page=2&page_size=20")),
    ).toBe(true);
    // Page-2 fixture row has null due_date and null latest_document → both render "—"
    expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(2);
  });

  // Spec: F-026-registrar-dashboard.md | AC-5 | Then requests to both endpoints are
  // cookie-authenticated (credentials: "include")
  it("sends cookie-authenticated requests to both endpoints", async () => {
    renderDashboard();

    await screen.findByText("62.5%");
    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(urls.some((u) => u.includes("/api/v1/registrars/dashboard-summary"))).toBe(true);
    expect(urls.some((u) => u.includes("/api/v1/registrar-requirements/global-tracker"))).toBe(true);
    for (const call of fetchMock.mock.calls) {
      expect((call[1] as RequestInit | undefined)?.credentials).toBe("include");
    }
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then a failed dashboard-summary shows the
  // error state instead of tiles
  it("shows an error state when dashboard-summary fails", async () => {
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/registrars/dashboard-summary")) {
        return jsonResponse({ detail: "summary unavailable" }, 500);
      }
      return jsonResponse(trackerBody);
    });

    renderDashboard();

    expect(await screen.findByText(/Failed to load dashboard summary/)).toBeTruthy();
    expect(screen.queryByText("62.5%")).toBeNull();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then a failed global tracker shows the
  // error state instead of rows
  it("shows an error state when the global tracker fails", async () => {
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/registrar-requirements/global-tracker")) {
        return jsonResponse({ detail: "tracker unavailable" }, 500);
      }
      return jsonResponse(summaryBody);
    });

    renderDashboard();

    expect(await screen.findByText(/Failed to load global tracker/)).toBeTruthy();
    expect(screen.queryByText("Submit audited accounts")).toBeNull();
  });

  // Spec: F-026-registrar-dashboard.md | AC-7 | Then the dashboard is read-only
  // (no inline edit controls — no buttons, inputs, selects or links)
  it("renders unmapped companies and stays read-only", async () => {
    renderDashboard();

    expect(await screen.findByText(/3 unmapped compan/)).toBeTruthy();
    expect(screen.getByText(/DANGCEM/)).toBeTruthy();
    expect(screen.getByText(/MTNN/)).toBeTruthy();
    // No inline edit controls — only pagination buttons may exist
    expect(screen.queryByRole("button", { name: /edit|upload|remind|delete|save/i })).toBeNull();
    expect(screen.queryAllByRole("textbox")).toHaveLength(0);
    expect(screen.queryAllByRole("combobox")).toHaveLength(0);
    expect(screen.queryAllByRole("link")).toHaveLength(0);
  });
});
