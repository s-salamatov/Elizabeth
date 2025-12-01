import { defineConfig, devices } from '@playwright/test';

const baseURL = 'http://localhost:8000';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  fullyParallel: false,
  reporter: 'list',
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } }
  ],
  webServer: {
    command: 'cd .. && python manage.py runserver 0.0.0.0:8000',
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  },
  globalSetup: './tests/e2e/setup.js'
});
