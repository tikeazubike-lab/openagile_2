// frontend/tests/e2e/accessibility.spec.ts
/**
 * Stage 5C — Accessibility Tests (axe-core + Playwright)
 * WCAG 2.1 Level AA. Critical + Serious violations fail the build.
 *
 * Install: npm install -D @axe-core/playwright
 */
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

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

// ---------------------------------------------------------------------------
// Helper: run axe and assert no critical/serious violations
// ---------------------------------------------------------------------------
async function checkA11y(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();

  const blocking = results.violations.filter((v) =>
    ["critical", "serious"].includes(v.impact ?? "")
  );

  if (blocking.length > 0) {
    const summary = blocking
      .map(
        (v) =>
          `[${v.impact?.toUpperCase()}] ${v.id}: ${v.description}\n` +
          v.nodes.map((n) => `  → ${n.html}`).join("\n")
      )
      .join("\n\n");
    throw new Error(`Accessibility violations found:\n\n${summary}`);
  }

  expect(blocking).toHaveLength(0);
}

// ===========================================================================
// Tests
// ===========================================================================

test("a11y: login page has no critical violations", async ({ page }) => {
  await page.goto(`${BASE}/login`);
  await checkA11y(page);
});

test("a11y: dashboard has no critical violations", async ({ page }) => {
  await login(page);
  await page.waitForLoadState("networkidle");
  await checkA11y(page);
});

test("a11y: holdings page has no critical violations", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/holdings`);
  await page.waitForLoadState("networkidle");
  await checkA11y(page);
});

test("a11y: dark mode contrast meets WCAG AA", async ({ page }) => {
  await login(page);
  // Switch to dark mode
  await page.getByTestId("theme-toggle").click();
  await page.waitForLoadState("networkidle");
  await checkA11y(page);
});

test("a11y: price entry page has no critical violations", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/settings/price-entry`);
  await page.waitForLoadState("networkidle");
  await checkA11y(page);
});
