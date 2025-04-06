import { defineConfig } from '@playwright/test';

/**
 * Playwright configuration for global tools
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directory where tests are located
  testDir: './tests',
  
  // Maximum time one test can run for
  timeout: 30000,
  
  // Expect assertion timeout
  expect: {
    timeout: 5000
  },
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'test-reports/html-report' }],
    ['list']
  ],
  
  // Global setup for all tests
  use: {
    // Maximum time each action such as `click()` can take
    actionTimeout: 0,
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Capture screenshot only when test fails
    screenshot: 'only-on-failure'
  },
  
  // Directory for test artifacts like screenshots, videos, traces, etc.
  outputDir: 'test-results',
  
  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
      },
    },
  ],
});
