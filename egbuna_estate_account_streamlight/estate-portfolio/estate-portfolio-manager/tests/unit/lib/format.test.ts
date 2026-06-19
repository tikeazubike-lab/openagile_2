import { describe, expect, it } from "vitest";

import { fmtNaira, fmtPct } from "../../../src/lib/format";

describe("fmtNaira", () => {
  it("formats numeric input", () => {
    expect(fmtNaira(12345.5)).toContain("₦");
    expect(fmtNaira(12345.5)).toContain("12,345");
  });

  it("accepts string input from the API layer", () => {
    expect(fmtNaira("12345.00")).toContain("₦");
    expect(fmtNaira("12345.00")).toContain("12,345");
  });

  it("formats compact values", () => {
    expect(fmtNaira(1_500_000, { compact: true })).toBe("₦1.5M");
  });
});

describe("fmtPct", () => {
  it("formats positive values with a plus sign by default", () => {
    expect(fmtPct(12.34)).toBe("+12.34%");
  });

  it("accepts string input", () => {
    expect(fmtPct("-3.21")).toBe("-3.21%");
  });

  it("can suppress the plus sign", () => {
    expect(fmtPct(5, false)).toBe("5.00%");
  });
});
