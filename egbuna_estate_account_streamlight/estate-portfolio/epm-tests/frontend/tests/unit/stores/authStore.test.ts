// frontend/tests/unit/stores/authStore.test.ts
/**
 * Stage 1B.1 — Zustand authStore Unit Tests
 * Tests store logic in pure isolation. No React, no API calls.
 */
import { act } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

// Adjust import path to match your actual store location
import { useAuthStore } from "../../../src/store/authStore";

const ADMIN_USER = {
  id: 1,
  username: "zubbyik",
  name: "Zubby",
  role: "admin" as const,
};

const READONLY_USER = {
  id: 2,
  username: "viewer",
  name: "Viewer",
  role: "readonly" as const,
};

beforeEach(() => {
  // Reset store to initial state before each test
  useAuthStore.setState({ user: null });
});

describe("authStore — initial state", () => {
  it("initial state is null user", () => {
    const { user } = useAuthStore.getState();
    expect(user).toBeNull();
  });

  it("isAdmin returns false when no user", () => {
    expect(useAuthStore.getState().isAdmin()).toBe(false);
  });
});

describe("authStore — setUser", () => {
  it("set user populates store", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    expect(useAuthStore.getState().user).toEqual(ADMIN_USER);
  });

  it("is admin returns true for admin role", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    expect(useAuthStore.getState().isAdmin()).toBe(true);
  });

  it("is admin returns false for readonly role", () => {
    act(() => useAuthStore.getState().setUser(READONLY_USER));
    expect(useAuthStore.getState().isAdmin()).toBe(false);
  });
});

describe("authStore — clearUser", () => {
  it("clear user resets to null", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    act(() => useAuthStore.getState().clearUser());
    expect(useAuthStore.getState().user).toBeNull();
  });

  it("isAdmin returns false after clearUser", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    act(() => useAuthStore.getState().clearUser());
    expect(useAuthStore.getState().isAdmin()).toBe(false);
  });
});