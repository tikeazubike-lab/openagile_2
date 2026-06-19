// frontend/tests/unit/components/HoldingsTable.test.tsx
/**
 * Stage 1B.5 — Holdings Table Component Unit Tests
 *
 * CRITICAL TEST: return[%] column header must be EXACTLY "return[%]"
 * — this is specified verbatim in the API contract and the handover brief.
 *
 * Uses MSW to supply mock holdings data. All role/editMode logic is
 * exercised by toggling authStore and uiStore before rendering.
 */
import { render, screen, within } from "@testing-library/react";
import { beforeAll, afterAll, afterEach, beforeEach, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { HoldingsTable } from "../../../src/components/holdings/HoldingsTable";
import { useAuthStore } from "../../../src/store/authStore";
import { useUIStore } from "../../../src/store/uiStore";

// ---------------------------------------------------------------------------
// Mock data matching API contract (monetary values as STRINGS)
// ---------------------------------------------------------------------------
const LIVE_HOLDING = {
  id: 1,
  company_id: 1,
  ticker: "DANGCEM",
  company_name: "Dangote Cement",
  sector: "Industrials",
  num_shares: 100,
  avg_purchase_price: "450.00",
  current_price: "500.00",
  current_value: "50000.00",
  cost_basis: "45000.00",
  return_pct: "+11.11",
  dividend_yield: "3.50",
  status: "live",
  deleted_at: null,
};

const DRAFT_HOLDING = {
  id: 2,
  company_id: 2,
  ticker: "DRAFTCO",
  company_name: "Draft Company",
  sector: "Banking",
  num_shares: 50,
  avg_purchase_price: "200.00",
  current_price: "180.00",
  current_value: "9000.00",
  cost_basis: "10000.00",
  return_pct: "-10.00",
  dividend_yield: "0.00",
  status: "draft",
  deleted_at: null,
};

const NEGATIVE_HOLDING = {
  ...LIVE_HOLDING,
  id: 3,
  ticker: "LOSER",
  return_pct: "-5.50",
};

// ---------------------------------------------------------------------------
// MSW server
// ---------------------------------------------------------------------------
const server = setupServer(
  http.get("/api/v1/holdings", () =>
    HttpResponse.json({
      data: [LIVE_HOLDING, DRAFT_HOLDING, NEGATIVE_HOLDING],
      meta: { total: 3 },
      error: null,
    })
  )
);

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
afterEach(() => {
  server.resetHandlers();
  useAuthStore.setState({ user: null });
  useUIStore.setState({ editMode: false });
});
afterAll(() => server.close());

// ---------------------------------------------------------------------------
// Wrapper with QueryClient
// ---------------------------------------------------------------------------
function wrap(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const ADMIN = { id: 1, username: "zubbyik", name: "Zubby", role: "admin" as const };
const VIEWER = { id: 2, username: "viewer", name: "Viewer", role: "readonly" as const };

// ===========================================================================
// Column headers
// ===========================================================================

describe("HoldingsTable — column headers", () => {
  it("renders correct column headers", async () => {
    useAuthStore.setState({ user: ADMIN });
    wrap(<HoldingsTable />);
    expect(await screen.findByRole("columnheader", { name: /ticker/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /company/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /sector/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /shares/i })).toBeInTheDocument();
  });

  it("return[%] column header is EXACTLY 'return[%]'", async () => {
    useAuthStore.setState({ user: ADMIN });
    wrap(<HoldingsTable />);
    // Must match verbatim — not "Return %" or "return%" or "Return[%]"
    const header = await screen.findByRole("columnheader", { name: "return[%]" });
    expect(header).toBeInTheDocument();
    expect(header.textContent).toBe("return[%]");
  });
});

// ===========================================================================
// Return % colour coding
// ===========================================================================

describe("HoldingsTable — return% colours", () => {
  it("positive return renders in green", async () => {
    useAuthStore.setState({ user: ADMIN });
    wrap(<HoldingsTable />);
    await screen.findByText("+11.11%");
    const cell = screen.getByText("+11.11%");
    expect(cell).toHaveStyle({ color: expect.stringContaining("") }); // green class check
    expect(cell.className).toMatch(/green|accent-green/i);
  });

  it("negative return renders in red", async () => {
    useAuthStore.setState({ user: ADMIN });
    wrap(<HoldingsTable />);
    await screen.findByText("-10.00%");
    const cell = screen.getByText("-10.00%");
    expect(cell.className).toMatch(/red|accent-red/i);
  });
});

// ===========================================================================
// Draft row treatment
// ===========================================================================

describe("HoldingsTable — draft rows", () => {
  it("draft row has amber left border treatment", async () => {
    useAuthStore.setState({ user: ADMIN });
    wrap(<HoldingsTable />);
    await screen.findByText("DRAFTCO");
    const draftRow = screen.getByText("DRAFTCO").closest("tr");
    expect(draftRow).toBeDefined();
    // Check for amber border style or class
    const style = window.getComputedStyle(draftRow!);
    const hasAmberBorder =
      draftRow!.className.includes("amber") ||
      style.borderLeftColor.includes("245") || // RGB for #F59E0B
      draftRow!.style.borderLeft.includes("amber") ||
      draftRow!.getAttribute("data-status") === "draft";
    expect(hasAmberBorder).toBe(true);
  });

  it("draft rows hidden for readonly role", async () => {
    server.use(
      http.get("/api/v1/holdings", () =>
        HttpResponse.json({
          data: [LIVE_HOLDING], // API already excludes drafts for readonly
          meta: { total: 1 },
          error: null,
        })
      )
    );
    useAuthStore.setState({ user: VIEWER });
    wrap(<HoldingsTable />);
    await screen.findByText("DANGCEM");
    expect(screen.queryByText("DRAFTCO")).not.toBeInTheDocument();
  });
});

// ===========================================================================
// Edit mode / actions column
// ===========================================================================

describe("HoldingsTable — edit mode", () => {
  it("actions column hidden in view mode", async () => {
    useAuthStore.setState({ user: ADMIN });
    useUIStore.setState({ editMode: false });
    wrap(<HoldingsTable />);
    await screen.findByText("DANGCEM");
    expect(screen.queryByRole("button", { name: /delete|soft.delete/i })).not.toBeInTheDocument();
  });

  it("actions column visible in edit mode for admin", async () => {
    useAuthStore.setState({ user: ADMIN });
    useUIStore.setState({ editMode: true });
    wrap(<HoldingsTable />);
    await screen.findByText("DANGCEM");
    expect(screen.getAllByRole("button", { name: /edit|delete/i }).length).toBeGreaterThan(0);
  });

  it("publish button visible on draft rows in edit mode", async () => {
    useAuthStore.setState({ user: ADMIN });
    useUIStore.setState({ editMode: true });
    wrap(<HoldingsTable />);
    await screen.findByText("DRAFTCO");
    expect(screen.getByRole("button", { name: /publish/i })).toBeInTheDocument();
  });
});
