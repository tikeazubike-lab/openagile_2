import { act } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useUIStore } from "../../../src/store/uiStore";

beforeEach(() => {
  useUIStore.setState({ sidebarOpen: false });
});

describe("uiStore", () => {
  it("starts with sidebar closed", () => {
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it("toggles sidebar state", () => {
    act(() => useUIStore.getState().toggleSidebar());
    expect(useUIStore.getState().sidebarOpen).toBe(true);
    act(() => useUIStore.getState().toggleSidebar());
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });
});
