// frontend/tests/unit/hooks/useCountUp.test.ts
/**
 * Stage 1B.3 — useCountUp Hook Unit Tests
 * Tests animation behaviour using fake timers.
 */
import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useCountUp } from "../../../src/hooks/useCountUp";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("useCountUp", () => {
  it("count up starts at zero", () => {
    const { result } = renderHook(() => useCountUp(1000, 800));
    // Before animation begins, value should be 0
    expect(result.current).toBe(0);
  });

  it("count up reaches target value after duration", () => {
    const { result } = renderHook(() => useCountUp(1000, 800));

    act(() => {
      vi.advanceTimersByTime(1000); // advance past full duration
    });

    expect(result.current).toBe(1000);
  });

  it("count up resets and replays when target changes", () => {
    const { result, rerender } = renderHook(
      ({ target }: { target: number }) => useCountUp(target, 800),
      { initialProps: { target: 1000 } }
    );

    act(() => vi.advanceTimersByTime(1000));
    expect(result.current).toBe(1000);

    // Change target
    rerender({ target: 2000 });

    // Should reset to 0 and start counting up again
    expect(result.current).toBe(0);

    act(() => vi.advanceTimersByTime(1000));
    expect(result.current).toBe(2000);
  });

  it("count up handles zero target without animation", () => {
    const { result } = renderHook(() => useCountUp(0, 800));
    act(() => vi.advanceTimersByTime(1000));
    expect(result.current).toBe(0);
  });

  it("count up handles negative values", () => {
    const { result } = renderHook(() => useCountUp(-500, 800));
    act(() => vi.advanceTimersByTime(1000));
    expect(result.current).toBe(-500);
  });
});
