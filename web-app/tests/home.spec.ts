import { test, expect } from "@playwright/test";

test("homepage loads", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL("/");
});

test("shows login when not authenticated", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: /login/i })).toBeVisible();
});

test("navigate to sessions page", async ({ page }) => {
  await page.goto("/sessions");
  await expect(page).toHaveURL(/sessions/);
});

test("sessions page renders", async ({ page }) => {
  await page.goto("/sessions");
  await expect(page.getByText(/sessions/i)).toBeVisible();
});
