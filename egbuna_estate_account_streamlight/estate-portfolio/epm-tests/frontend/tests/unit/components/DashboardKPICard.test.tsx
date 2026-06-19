// frontend/tests/unit/components/DashboardKPICard.test.tsx
/**
 * Stage 1B.5 — Dashboard KPI Card Component Unit Tests
 * Tests rendering, count-up animation, positive/negative colour coding,
 * and admin-only draft count display.
 */
import { render, screen, act } from "@testing-library/react";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";

import { KPICard, KPICardProps } from "../../../src/components/dashboard/KPICard";
import { useAuthStore } from "../../../src/store/authStore";

const ADMIN = { id: 1, username: "zubbyik", name: "Zubby", role: "admin" as const };
const VIEWER = { id: 2, username: "viewer", name: "Viewer", role: "readonly" as const };

beforeEach(() => {
  vi.useFakeTimers();
  useAuthStore.setState({ user: null });
});
afterEach(() => vi.useRealTimers());

// ---------------------------------------------------------------------------
// Default props for a total-value card
// ---------------------------------------------------------------------------
const baseProps: KPICardProps = {
  label: "TOTAL VALUE",
  value: 12345678,
  formattedValue: "₦12,345,678.00",
  change: "+11.22",
  changePositive: true,
  accentColor: "lavender",
  icon: "TrendingUp",
};

// ===========================================================================
// Rendering
// ===========================================================================

describe("KPICard — rendering", () => {
  it("renders label and value", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<KPICard {...baseProps} />);
    expect(screen.getByText(/total value/i)).toBeInTheDocument();
  });

  it("renders formatted ₦ value", async () => {
    useAuthStore.setState({ user: ADMIN });
    render(<KPICard {...baseProps} />);
    act(() => vi.advanceTimersByTime(1000));
    expect(screen.getByText(/₦12,345,678\.00/)).toBeInTheDocument();
  });
});

// ===========================================================================
// Count-up animation
// ===========================================================================

describe("KPICard — count-up animation", () => {
  it("count-up animation fires on mount", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<KPICard {...baseProps} />);

    // Immediately after mount, displayed value should be 0 or small
    const valueEl = screen.getByTestId("kpi-animated-value");
    const initialText = valueEl.textContent || "";
    const initialNum = parseFloat(initialText.replace(/[^0-9.]/g, ""));
    expect(initialNum).toBeLessThan(baseProps.value);
  });

  it("count-up reaches target value after 800ms", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<KPICard {...baseProps} />);
    act(() => vi.advanceTimersByTime(900));
    const valueEl = screen.getByTestId("kpi-animated-value");
    const finalText = valueEl.textContent || "";
    const finalNum = parseFloat(finalText.replace(/[^0-9.,₦]/g, "").replace(",", ""));
    expect(finalNum).toBeCloseTo(baseProps.value, -2);
  });
});

// ===========================================================================
// Positive / negative colour coding
// ===========================================================================

describe("KPICard — change indicator colours", () => {
  it("positive change renders in green", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<KPICard {...baseProps} changePositive={true} change="+11.22" />);
    const changeEl = screen.getByTestId("kpi-change");
    expect(changeEl.className).toMatch(/green|accent-green/i);
    expect(changeEl.textContent).toContain("+");
  });

  it("negative change renders in red", () => {
    useAuthStore.setState({ user: ADMIN });
    render(
      <KPICard
        {...baseProps}
        label="UNREALISED GAIN/LOSS"
        changePositive={false}
        change="-3.21"
      />
    );
    const changeEl = screen.getByTestId("kpi-change");
    expect(changeEl.className).toMatch(/red|accent-red/i);
    expect(changeEl.textContent).toContain("-");
  });
});

// ===========================================================================
// Admin-only draft count
// ===========================================================================

describe("KPICard — draft count", () => {
  it("shows draft count subtitle for admin when draftCount provided", () => {
    useAuthStore.setState({ user: ADMIN });
    render(
      <KPICard
        {...baseProps}
        label="TOTAL HOLDINGS"
        formattedValue="24"
        draftCount={2}
      />
    );
    expect(screen.getByText(/22 live/i)).toBeInTheDocument();
    expect(screen.getByText(/2 draft/i)).toBeInTheDocument();
  });

  it("hides draft count for readonly role", () => {
    useAuthStore.setState({ user: VIEWER });
    render(
      <KPICard
        {...baseProps}
        label="TOTAL HOLDINGS"
        formattedValue="24"
        draftCount={2}
      />
    );
    expect(screen.queryByText(/draft/i)).not.toBeInTheDocument();
  });

  it("hides draft count when draftCount is zero or undefined", () => {
    useAuthStore.setState({ user: ADMIN });
    render(<KPICard {...baseProps} label="TOTAL HOLDINGS" formattedValue="24" />);
    expect(screen.queryByText(/draft/i)).not.toBeInTheDocument();
  });
});
