// frontend/tests/unit/lib/format.test.ts
/**
 * Stage 1B.4 — Utility Function Unit Tests (lib/format.ts)
 * Tests fmtNaira and fmtPct with all edge cases including
 * string inputs (as returned by the API — not floats).
 */
import { describe, expect, it } from "vitest";

import { fmtNaira, fmtPct } from "../../../src/lib/format";

// ===========================================================================
// fmtNaira
// ===========================================================================

describe("fmtNaira", () => {
  it("formats positive number with ₦ symbol", () => {
    const result = fmtNaira("12345.50");
    expect(result).toContain("₦");
    expect(result).toContain("12,345");
  });

  it("formats zero correctly", () => {
    const result = fmtNaira("0.00");
    expect(result).toContain("₦");
    expect(result).toContain("0");
  });

  it("formats negative as loss with minus sign", () => {
    const result = fmtNaira("-1000.00");
    expect(result).toContain("-");
    expect(result).toContain("₦");
  });

  it("handles string input from API without throwing", () => {
    // API returns strings not floats — this must work
    expect(() => fmtNaira("12345.00")).not.toThrow();
    const result = fmtNaira("12345.00");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("handles large values with correct comma separation", () => {
    const result = fmtNaira("1234567.89");
    expect(result).toContain("1,234,567");
  });

  it("always shows 2 decimal places", () => {
    const result = fmtNaira("100.00");
    expect(result).toMatch(/\.00$/);
  });
});

// ===========================================================================
// fmtPct
// ===========================================================================

describe("fmtPct", () => {
  it("formats positive with plus prefix", () => {
    const result = fmtPct("+12.34");
    expect(result).toMatch(/^\+/);
    expect(result).toContain("12.34");
    expect(result).toContain("%");
  });

  it("formats negative with minus prefix", () => {
    const result = fmtPct("-3.21");
    expect(result).toMatch(/^-/);
    expect(result).toContain("3.21");
    expect(result).toContain("%");
  });

  it("formats zero", () => {
    const result = fmtPct("0.00");
    expect(result).toContain("0.00");
    expect(result).toContain("%");
  });

  it("handles string input without throwing", () => {
    expect(() => fmtPct("+5.50")).not.toThrow();
  });

  it("always appends percent sign", () => {
    expect(fmtPct("+10.00")).toContain("%");
    expect(fmtPct("-10.00")).toContain("%");
    expect(fmtPct("0.00")).toContain("%");
  });
});