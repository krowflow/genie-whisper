/**
 * Schedule Tool Tests
 * 
 * Tests for the Schedule Tool application using our browser tools.
 */

import { test, expect } from '@playwright/test';
import * as browser from '../../tools/browser';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Schedule Tool Tests', () => {
  // Create results directory for test artifacts
  const resultsDir = path.join(__dirname, '..', '..', 'test-results', 'scheduler');
  
  test.beforeAll(async () => {
    // Ensure results directory exists
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
  });
  
  test('should load the Schedule Tool application', async ({ page }) => {
    // Navigate to the Schedule Tool
    await browser.navigateTo(page, 'http://localhost:5173/');
    
    // Wait for the page to load
    await browser.waitForNetworkIdle(page);
    
    // Get the page title
    const title = await browser.getPageTitle(page);
    console.log(`Page title: ${title}`);
    
    // Take a screenshot of the initial state
    const screenshotPath = path.join(resultsDir, 'scheduler-initial.png');
    await browser.takeScreenshot(page, screenshotPath);
    
    // Verify the screenshot was created
    expect(fs.existsSync(screenshotPath)).toBeTruthy();
  });
  
  test('should check for UI elements in the Schedule Tool', async ({ page }) => {
    // Navigate to the Schedule Tool
    await browser.navigateTo(page, 'http://localhost:5173/');
    
    // Wait for the page to load
    await browser.waitForNetworkIdle(page);
    
    // Check for navigation elements
    const hasNavigation = await browser.elementExists(page, 'nav');
    console.log(`Has navigation: ${hasNavigation}`);
    
    // Check for buttons
    const hasButtons = await browser.elementExists(page, 'button');
    console.log(`Has buttons: ${hasButtons}`);
    expect(hasButtons).toBeTruthy();
    
    // Check for calendar if it exists
    const hasCalendar = await browser.elementExists(page, '.fc-view-harness');
    console.log(`Has calendar: ${hasCalendar}`);
    
    if (hasCalendar) {
      // Take a screenshot of the calendar
      await browser.scrollToElement(page, '.fc-view-harness');
      const calendarScreenshotPath = path.join(resultsDir, 'calendar.png');
      await browser.takeScreenshot(page, calendarScreenshotPath);
    }
  });
  
  test('should interact with UI elements in the Schedule Tool', async ({ page }) => {
    // Navigate to the Schedule Tool
    await browser.navigateTo(page, 'http://localhost:5173/');
    
    // Wait for the page to load
    await browser.waitForNetworkIdle(page);
    
    // Find and click on a button if it exists
    const hasButton = await browser.elementExists(page, 'button');
    
    if (hasButton) {
      // Get the text of the first button
      const buttonText = await browser.getElementText(page, 'button');
      console.log(`Button text: ${buttonText}`);
      
      // Click the button
      await browser.clickElement(page, 'button');
      
      // Take a screenshot after clicking
      const afterClickScreenshotPath = path.join(resultsDir, 'after-click.png');
      await browser.takeScreenshot(page, afterClickScreenshotPath);
    }
  });
});
