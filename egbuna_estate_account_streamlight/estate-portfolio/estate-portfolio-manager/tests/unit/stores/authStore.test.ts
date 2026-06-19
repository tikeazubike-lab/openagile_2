import { act } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

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
  useAuthStore.setState({ user: null });
});

describe("authStore", () => {
  it("starts with null user", () => {
    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().isAdmin()).toBe(false);
  });

  it("stores an admin user", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    expect(useAuthStore.getState().user).toEqual(ADMIN_USER);
    expect(useAuthStore.getState().isAdmin()).toBe(true);
  });

  it("returns false for readonly user admin check", () => {
    act(() => useAuthStore.getState().setUser(READONLY_USER));
    expect(useAuthStore.getState().isAdmin()).toBe(false);
  });

  it("clears the user", () => {
    act(() => useAuthStore.getState().setUser(ADMIN_USER));
    act(() => useAuthStore.getState().clearUser());
    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().isAdmin()).toBe(false);
  });
});
