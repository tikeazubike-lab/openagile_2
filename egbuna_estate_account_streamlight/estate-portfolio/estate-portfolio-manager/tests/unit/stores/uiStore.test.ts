import { act } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "../../../src/store/authStore";
import { useUIStore } from "../../../src/store/uiStore";

const ADMIN_USER = { id: 1, username: "zubbyik", name: "Zubby", role: "admin" as const };
const READONLY_USER = { id: 2, username: "viewer", name: "Viewer", role: "readonly" as const };

beforeEach(() => {
  useAuthStore.setState({ user: null });
  useUIStore.setState({ editMode: false, sidebarOpen: false });
});

describe("uiStore", () => {
  it("starts with edit mode and sidebar closed", () => {
    expect(useUIStore.getState().editMode).toBe(false);
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it("allows admins to toggle edit mode", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    act(() => useUIStore.getState().toggleEditMode());
    expect(useUIStore.getState().editMode).toBe(true);
  });

  it("blocks readonly users from toggling edit mode", () => {
    act(() => useAuthStore.getState().setUser(READONLY_USER));
    act(() => useUIStore.getState().toggleEditMode());
    expect(useUIStore.getState().editMode).toBe(false);
  });

  it("toggles sidebar state", () => {
    act(() => useUIStore.getState().toggleSidebar());
    expect(useUIStore.getState().sidebarOpen).toBe(true);
    act(() => useUIStore.getState().toggleSidebar());
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });
});
