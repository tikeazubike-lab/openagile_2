// frontend/tests/e2e/auth.spec.ts
/**
 * Stage 4A — E2E Authentication Flow Tests (Playwright)
 * Runs against live staging: demo.estate.zubbystudio.shop
 * Real FastAPI backend, real shared Postgres, real httpOnly cookie.
 *
 * Env vars required (GitHub Actions secrets):
 *   E2E_BASE_URL      — https://demo.estate.zubbystudio.shop
 *   E2E_ADMIN_USER    — admin username
 *   E2E_ADMIN_PASS    — admin password
 *   E2E_VIEWER_USER   — readonly username
 *   E2E_VIEWER_PASS   — readonly password
 */
import { test, expect, type Page } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL!;
const ADMIN_USER = process.env.E2E_ADMIN_USER!;
const ADMIN_PASS = process.env.E2E_ADMIN_PASS!;
const VIEWER_USER = process.env.E2E_VIEWER_USER ?? "viewer";
const VIEWER_PASS = process.env.E2E_VIEWER_PASS ?? "viewerpass";

// ---------------------------------------------------------------------------
// Helper: perform login via UI
// ---------------------------------------------------------------------------
async function loginAs(page: Page, username: string, password: string) {
  await page.goto(`${BASE}/login`);
  await page.getByLabel(/username/i).fill(username);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign in/i }).click();
}

// ===========================================================================
// Login flow
// ===========================================================================

test("login with valid credentials reaches dashboard", async ({ page }) => {
  await loginAs(page, ADMIN_USER, ADMIN_PASS);
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/total value/i)).toBeVisible();
});

test("login with invalid credentials shows error message", async ({ page }) => {
  await loginAs(page, ADMIN_USER, "WRONGPASSWORD_xyz");
  await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  await expect(page).toHaveURL(/\/login/);
});

test("login form shows loading state during API call", async ({ page }) => {
  await page.goto(`${BASE}/login`);
  await page.getByLabel(/username/i).fill(ADMIN_USER);
  await page.getByLabel(/password/i).fill(ADMIN_PASS);

  // Slow down network to catch loading state
  await page.route("**/api/v1/auth/login", async (route) => {
    await new Promise((r) => setTimeout(r, 300));
    await route.continue();
  });

  const btn = page.getByRole("button", { name: /sign in/i });
  await btn.click();
  await expect(btn).toBeDisabled();
});

// ===========================================================================
// Route guards
// ===========================================================================

test("direct URL to /dashboard while logged out redirects to /login", async ({ page }) => {
  await page.goto(`${BASE}/dashboard`);
  await expect(page).toHaveURL(/\/login/);
});

test("direct URL to /holdings while logged out redirects to /login", async ({ page }) => {
  await page.goto(`${BASE}/holdings`);
  await expect(page).toHaveURL(/\/login/);
});

test("hard refresh on dashboard preserves session", async ({ page }) => {
  await loginAs(page, ADMIN_USER, ADMIN_PASS);
  await expect(page).toHaveURL(/\/dashboard/);

  // Hard reload
  await page.reload({ waitUntil: "networkidle" });
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/total value/i)).toBeVisible();
});

// ===========================================================================
// Settings access — role guard
// ===========================================================================

test("settings price entry blocked for readonly role", async ({ page }) => {
  await loginAs(page, VIEWER_USER, VIEWER_PASS);
  await expect(page).toHaveURL(/\/dashboard/);

  // Sidebar must not show Price Entry link
  await expect(page.getByText(/price entry/i)).not.toBeVisible();

  // Direct URL access must be blocked
  await page.goto(`${BASE}/settings/price-entry`);
  await expect(page).not.toHaveURL(/\/settings\/price-entry/);
});

// ===========================================================================
// Logout — regression suite (matches unit test regression in Sidebar.test.tsx)
// ===========================================================================

test("logout clears cookie and redirects to /login", async ({ page, context }) => {
  await loginAs(page, ADMIN_USER, ADMIN_PASS);
  await expect(page).toHaveURL(/\/dashboard/);

  // Confirm cookie exists
  const cookiesBefore = await context.cookies();
  expect(cookiesBefore.some((c) => c.name === "epm_token")).toBe(true);

  // Click logout
  await page.getByRole("button", { name: /log out|sign out/i }).click();

  // Must redirect to login
  await expect(page).toHaveURL(/\/login/);

  // Cookie must be cleared
  const cookiesAfter = await context.cookies();
  const tokenCookie = cookiesAfter.find((c) => c.name === "epm_token");
  expect(!tokenCookie || tokenCookie.value === "").toBe(true);
});

test("after logout, browser back button does not restore dashboard", async ({ page }) => {
  await loginAs(page, ADMIN_USER, ADMIN_PASS);
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("button", { name: /log out|sign out/i }).click();
  await expect(page).toHaveURL(/\/login/);

  await page.goBack();
  // Should still be on login — not dashboard
  await expect(page).toHaveURL(/\/login/);
});

test("after logout, pasting dashboard URL redirects to login", async ({ page }) => {
  await loginAs(page, ADMIN_USER, ADMIN_PASS);
  await page.getByRole("button", { name: /log out|sign out/i }).click();
  await expect(page).toHaveURL(/\/login/);

  await page.goto(`${BASE}/dashboard`);
  await expect(page).toHaveURL(/\/login/);
});

// ===========================================================================
// Cookie security
// ===========================================================================

test("epm_token cookie is httpOnly — not accessible via JS", async ({ page }) => {
  await loginAs(page, ADMIN_USER, ADMIN_PASS);
  await expect(page).toHaveURL(/\/dashboard/);

  // document.cookie must NOT contain epm_token (httpOnly = invisible to JS)
  const cookieStr = await page.evaluate(() => document.cookie);
  expect(cookieStr).not.toContain("epm_token");
});
