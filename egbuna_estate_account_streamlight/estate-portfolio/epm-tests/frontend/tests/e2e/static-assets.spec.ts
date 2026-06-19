// frontend/tests/e2e/static-assets.spec.ts
/**
 * Stage 4B — Static Asset Delivery E2E Tests
 */
import { test, expect } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL!;

test("index.html cache control is no-cache", async ({ request }) => {
  const response = await request.get(`${BASE}/`);
  const cc = response.headers()["cache-control"] ?? "";
  expect(cc).toMatch(/no-cache|no-store/i);
});

test("asset bundles return 200", async ({ page }) => {
  const failedAssets: string[] = [];
  page.on("response", (res) => {
    if (res.url().includes("/assets/") && res.status() !== 200) {
      failedAssets.push(res.url());
    }
  });
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  expect(failedAssets).toHaveLength(0);
});

test("deep link refresh on /holdings returns SPA not 404", async ({ page }) => {
  await page.goto(`${BASE}/holdings`, { waitUntil: "networkidle" });
  // Should render the React app (login redirect), not a FastAPI 404
  const body = await page.textContent("body");
  expect(body).not.toContain('"detail"'); // FastAPI 404 JSON signature
  // Page should have loaded the React shell
  await expect(page.locator("html")).not.toBeEmpty();
});

test("deep link refresh on /settings/price-entry returns SPA not 404", async ({ page }) => {
  await page.goto(`${BASE}/settings/price-entry`, { waitUntil: "networkidle" });
  const body = await page.textContent("body");
  expect(body).not.toContain('"detail"');
});

test("unknown route shows React 404 not FastAPI JSON", async ({ page }) => {
  await page.goto(`${BASE}/this-route-does-not-exist-xyz`);
  const contentType = (await page.evaluate(() =>
    document.contentType
  )) as string | undefined;
  // Must be HTML (React rendered), not JSON
  expect(contentType ?? "text/html").not.toContain("application/json");
  // FastAPI 404 JSON body signature must be absent
  const text = await page.textContent("body");
  expect(text).not.toContain('"detail":"Not Found"');
});
