// frontend/tests/unit/hooks/useTheme.test.ts
/**
 * Stage 1B.2 — useTheme Hook Unit Tests
 * Tests system default detection, manual override, localStorage persistence,
 * and anti-FOUC class application on the <html> element.
 */
import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useTheme } from "../../../src/hooks/useTheme";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mockMatchMedia(prefersDark: boolean) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: prefersDark && query === "(prefers-color-scheme: dark)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

beforeEach(() => {
  // Reset DOM and localStorage
  document.documentElement.classList.remove("dark");
  localStorage.removeItem("epm-theme");
  mockMatchMedia(false); // default: system = light
});

afterEach(() => {
  vi.restoreAllMocks();
});

// ===========================================================================
// System preference detection
// ===========================================================================

describe("useTheme — system preference", () => {
  it("default theme reads system preference light", () => {
    mockMatchMedia(false);
    const { result } = renderHook(() => useTheme());
    expect(result.current.resolvedTheme).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("default theme reads system preference dark", () => {
    mockMatchMedia(true);
    const { result } = renderHook(() => useTheme());
    expect(result.current.resolvedTheme).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("resolved theme is light when system is light and no override", () => {
    mockMatchMedia(false);
    const { result } = renderHook(() => useTheme());
    expect(result.current.resolvedTheme).toBe("light");
  });
});

// ===========================================================================
// Manual override
// ===========================================================================

describe("useTheme — manual toggle", () => {
  it("toggle from light saves dark to localStorage", () => {
    mockMatchMedia(false);
    const { result } = renderHook(() => useTheme());

    act(() => result.current.toggleTheme());

    expect(localStorage.getItem("epm-theme")).toBe("dark");
  });

  it("toggle from dark saves system to localStorage", () => {
    localStorage.setItem("epm-theme", "dark");
    const { result } = renderHook(() => useTheme());

    act(() => result.current.toggleTheme());

    expect(localStorage.getItem("epm-theme")).toBe("system");
  });

  it("resolved theme is dark when forced", () => {
    localStorage.setItem("epm-theme", "dark");
    const { result } = renderHook(() => useTheme());
    expect(result.current.resolvedTheme).toBe("dark");
  });
});

// ===========================================================================
// DOM class application
// ===========================================================================

describe("useTheme — DOM class", () => {
  it("persisted dark preference applies dark class on mount", () => {
    localStorage.setItem("epm-theme", "dark");
    renderHook(() => useTheme());
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("persisted system preference reads matchMedia on mount", () => {
    localStorage.setItem("epm-theme", "system");
    mockMatchMedia(true);
    renderHook(() => useTheme());
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("theme change adds dark class on html element", () => {
    mockMatchMedia(false);
    const { result } = renderHook(() => useTheme());
    expect(document.documentElement.classList.contains("dark")).toBe(false);

    act(() => result.current.toggleTheme());
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("returning to system removes dark class when system is light", () => {
    localStorage.setItem("epm-theme", "dark");
    mockMatchMedia(false); // system = light
    const { result } = renderHook(() => useTheme());

    act(() => result.current.toggleTheme()); // dark → system

    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
