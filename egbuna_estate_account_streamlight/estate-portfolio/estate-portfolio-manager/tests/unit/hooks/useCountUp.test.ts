import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useCountUp } from "../../../src/hooks/useCountUp";

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubGlobal("requestAnimationFrame", (callback: FrameRequestCallback) => {
    return setTimeout(() => callback(performance.now()), 16) as unknown as number;
  });
  vi.stubGlobal("cancelAnimationFrame", (handle: number) => {
    clearTimeout(handle);
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("useCountUp", () => {
  it("starts at zero", () => {
    const { result } = renderHook(() => useCountUp(1000, 800));
    expect(result.current).toBe(0);
  });

  it("reaches the target value after the duration", () => {
    const { result } = renderHook(() => useCountUp(1000, 800));
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(Math.round(result.current)).toBe(1000);
  });

  it("resets when the target changes", () => {
    const { result, rerender } = renderHook(
      ({ target }: { target: number }) => useCountUp(target, 800),
      { initialProps: { target: 1000 } },
    );

    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(Math.round(result.current)).toBe(1000);

    rerender({ target: 2000 });
    expect(result.current).toBe(0);

    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(Math.round(result.current)).toBe(2000);
  });
});
