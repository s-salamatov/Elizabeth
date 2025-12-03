import { test, expect } from '@playwright/test';
import { mockBackend, primeLocalAuth } from './mockApi';

async function setup(page) {
  await primeLocalAuth(page);
  await mockBackend(page);
}

test.describe('App smoke checks', () => {
  test('search submits and shows results table', async ({ page }) => {
    await setup(page);
    await page.goto('/');
    await page.fill('textarea', 'A001\nB222');
    await page.getByRole('button', { name: /найти/i }).click();

    await expect(page.getByRole('table')).toBeVisible({ timeout: 10_000 });
    const rows = await page.getByRole('row').all();
    expect(rows.length).toBeGreaterThan(1);
  });
});
