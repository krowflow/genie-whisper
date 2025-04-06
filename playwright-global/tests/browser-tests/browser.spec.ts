/**
 * Browser Tools Tests
 * 
 * Tests for the browser interaction tools.
 */

import { test, expect } from '@playwright/test';
import * as browser from '../../tools/browser';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Browser Interaction Tools', () => {
  // Create results directory for test artifacts
  const resultsDir = path.join(__dirname, '..', '..', 'test-results', 'browser');
  
  test.beforeAll(async () => {
    // Ensure results directory exists
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
  });
  
  test('should navigate to a URL and get page title', async ({ page }) => {
    // Navigate to a test website
    await browser.navigateTo(page, 'https://playwright.dev/');
    
    // Get the page title
    const title = await browser.getPageTitle(page);
    
    // Verify the title
    expect(title).toContain('Playwright');
    
    // Get the current URL
    const url = await browser.getCurrentUrl(page);
    
    // Verify the URL
    expect(url).toContain('playwright.dev');
  });
  
  test('should take a screenshot of the page', async ({ page }) => {
    // Navigate to a test website
    await browser.navigateTo(page, 'https://playwright.dev/');
    
    // Take a screenshot
    const screenshotPath = path.join(resultsDir, 'screenshot.png');
    await browser.takeScreenshot(page, screenshotPath);
    
    // Verify the screenshot was created
    expect(fs.existsSync(screenshotPath)).toBeTruthy();
  });
  
  test('should scroll to an element and check if it exists', async ({ page }) => {
    // Navigate to a test website
    await browser.navigateTo(page, 'https://playwright.dev/');
    
    // Check if an element exists
    const exists = await browser.elementExists(page, '.navbar__inner');
    expect(exists).toBeTruthy();
    
    // Scroll to the element
    await browser.scrollToElement(page, 'footer');
    
    // Take a screenshot after scrolling
    const screenshotPath = path.join(resultsDir, 'scrolled.png');
    await browser.takeScreenshot(page, screenshotPath);
  });
});
