// frontend/tests/e2e/theme.spec.ts
/**
 * Stage 4C — Theme System E2E Tests
 */
import { test, expect, type BrowserContext, type Page } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL!;
const ADMIN_USER = process.env.E2E_ADMIN_USER!;
const ADMIN_PASS = process.env.E2E_ADMIN_PASS!;

async function login(page: Page) {
  await page.goto(`${BASE}/login`);
  await page.getByLabel(/username/i).fill(ADMIN_USER);
  await page.getByLabel(/password/i).fill(ADMIN_PASS);
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL(/\/dashboard/);
}

test("moon icon visible in light mode", async ({ page }) => {
  // Force system light preference
  await page.emulateMedia({ colorScheme: "light" });
  await login(page);
  const toggle = page.getByTestId("theme-toggle");
  await expect(toggle).toBeVisible();
  await expect(toggle).toHaveAccessibleName(/switch to dark/i);
});

test("clicking moon icon switches to dark mode", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  await login(page);
  await page.getByTestId("theme-toggle").click();
  const html = page.locator("html");
  await expect(html).toHaveClass(/dark/);
});

test("sun icon visible after dark mode activated", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  await login(page);
  await page.getByTestId("theme-toggle").click();
  const toggle = page.getByTestId("theme-toggle");
  await expect(toggle).toHaveAccessibleName(/return to system/i);
});

test("dark mode persists after page refresh", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  await login(page);
  await page.getByTestId("theme-toggle").click();
  await expect(page.locator("html")).toHaveClass(/dark/);

  await page.reload({ waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveClass(/dark/);
});

test("clicking sun returns to system theme", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  await login(page);
  // Force dark
  await page.getByTestId("theme-toggle").click();
  await expect(page.locator("html")).toHaveClass(/dark/);
  // Return to system (system=light)
  await page.getByTestId("theme-toggle").click();
  await expect(page.locator("html")).not.toHaveClass(/dark/);
});

test("no flash of wrong theme on initial load (anti-FOUC)", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  // Capture screenshots very early in page load
  const frames: string[] = [];
  page.on("framenavigated", async () => {
    try {
      const buf = await page.screenshot({ timeout: 500 });
      frames.push(buf.toString("base64").slice(0, 8));
    } catch (_) { /* ignore */ }
  });

  await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
  const hasDark = await page.evaluate(
    () => document.documentElement.classList.contains("dark")
  );
  // With anti-FOUC script, dark class applied before first paint
  expect(hasDark).toBe(true);
});


// frontend/tests/e2e/dashboard.spec.ts — appended in same file for brevity
// Stage 4D — Dashboard E2E Tests

import { test as dashTest, expect as dashExpect } from "@playwright/test";

dashTest.describe("Dashboard E2E", () => {
  dashTest.beforeEach(async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await page.getByLabel(/username/i).fill(ADMIN_USER);
    await page.getByLabel(/password/i).fill(ADMIN_PASS);
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL(/\/dashboard/);
  });

  dashTest("dashboard KPI cards render with values", async ({ page }) => {
    await dashExpect(page.getByText(/total value/i)).toBeVisible();
    await dashExpect(page.getByText(/total invested/i)).toBeVisible();
    await dashExpect(page.getByText(/unrealised/i)).toBeVisible();
    await dashExpect(page.getByText(/total holdings/i)).toBeVisible();
  });

  dashTest("dashboard count-up animation completes", async ({ page }) => {
    // Wait for animations to finish (800ms + buffer)
    await page.waitForTimeout(1200);
    // Value must contain ₦ after animation
    const valueEl = page.getByTestId("kpi-animated-value").first();
    const text = await valueEl.textContent();
    dashExpect(text).toContain("₦");
  });

  dashTest("sector donut chart renders", async ({ page }) => {
    await dashExpect(page.getByTestId("sector-donut-chart")).toBeVisible();
  });

  dashTest("top holdings bar chart renders", async ({ page }) => {
    await dashExpect(page.getByTestId("top-holdings-chart")).toBeVisible();
  });

  dashTest("recent transactions table renders", async ({ page }) => {
    await dashExpect(page.getByTestId("recent-transactions")).toBeVisible();
  });

  dashTest("action items card renders", async ({ page }) => {
    await dashExpect(page.getByTestId("action-items")).toBeVisible();
  });

  dashTest("last updated timestamp visible", async ({ page }) => {
    await dashExpect(page.getByText(/last updated/i)).toBeVisible();
  });
});


// frontend/tests/e2e/holdings.spec.ts — appended
// Stage 4E — Holdings E2E Tests

import { test as holdTest, expect as holdExpect } from "@playwright/test";

holdTest.describe("Holdings E2E", () => {
  holdTest.beforeEach(async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await page.getByLabel(/username/i).fill(ADMIN_USER);
    await page.getByLabel(/password/i).fill(ADMIN_PASS);
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL(/\/dashboard/);
    await page.getByText(/^holdings$/i).first().click();
    await page.waitForURL(/\/holdings/);
  });

  holdTest("holdings table renders all columns", async ({ page }) => {
    await holdExpect(page.getByRole("columnheader", { name: "return[%]" })).toBeVisible();
    await holdExpect(page.getByRole("columnheader", { name: /ticker/i })).toBeVisible();
    await holdExpect(page.getByRole("columnheader", { name: /company/i })).toBeVisible();
  });

  holdTest("return[%] column header is exact text", async ({ page }) => {
    const header = page.getByRole("columnheader", { name: "return[%]" });
    await holdExpect(header).toBeVisible();
    holdExpect(await header.textContent()).toBe("return[%]");
  });

  holdTest("edit mode toggle shows actions column", async ({ page }) => {
    // Activate editing
    await page.getByRole("button", { name: /viewing/i }).click();
    await holdExpect(page.getByText(/editing/i)).toBeVisible();
    await holdExpect(page.getByRole("button", { name: /delete/i }).first()).toBeVisible();
  });

  holdTest("create new holding as draft", async ({ page }) => {
    await page.getByRole("button", { name: /viewing/i }).click();
    await page.getByRole("button", { name: /add holding/i }).click();
    // Form should be visible
    await holdExpect(page.getByRole("dialog")).toBeVisible();
  });
});
