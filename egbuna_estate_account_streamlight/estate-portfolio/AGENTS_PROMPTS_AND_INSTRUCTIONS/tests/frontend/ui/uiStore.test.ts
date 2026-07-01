// frontend/tests/unit/stores/uiStore.test.ts
/**
 * Stage 1B.1 — Zustand uiStore Unit Tests
 * Tests editMode toggle (admin-only enforcement) and sidebar state.
 */
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

describe("uiStore — editMode", () => {
  it("edit mode defaults to false", () => {
    expect(useUIStore.getState().editMode).toBe(false);
  });

  it("toggle edit mode works for admin role", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    act(() => useUIStore.getState().toggleEditMode());
    expect(useUIStore.getState().editMode).toBe(true);
  });

  it("toggle edit mode does nothing for readonly role", () => {
    act(() => useAuthStore.getState().setUser(READONLY_USER));
    act(() => useUIStore.getState().toggleEditMode());
    expect(useUIStore.getState().editMode).toBe(false);
  });

  it("toggle edit mode does nothing when no user", () => {
    act(() => useUIStore.getState().toggleEditMode());
    expect(useUIStore.getState().editMode).toBe(false);
  });

  it("toggle edit mode toggles back off for admin", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    act(() => useUIStore.getState().toggleEditMode());
    act(() => useUIStore.getState().toggleEditMode());
    expect(useUIStore.getState().editMode).toBe(false);
  });
});

describe("uiStore — sidebar", () => {
  it("sidebar open defaults to false", () => {
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it("toggle sidebar flips from false to true", () => {
    act(() => useUIStore.getState().toggleSidebar());
    expect(useUIStore.getState().sidebarOpen).toBe(true);
  });

  it("toggle sidebar flips back to false", () => {
    act(() => useUIStore.getState().toggleSidebar());
    act(() => useUIStore.getState().toggleSidebar());
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });
});
