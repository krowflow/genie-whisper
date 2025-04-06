/**
 * Visual Testing Tools Tests
 * 
 * Tests for the visual testing tools.
 */

import { test, expect } from '@playwright/test';
import * as visual from '../../tools/visual';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Visual Testing Tools', () => {
  // Create results directory for test artifacts
  const resultsDir = path.join(__dirname, '..', '..', 'test-results', 'visual');
  
  test.beforeAll(async () => {
    // Ensure results directory exists
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
  });
  
  test('should take a screenshot of an element', async ({ page }) => {
    // Navigate to a test website
    await page.goto('https://playwright.dev/');
    
    // Take a screenshot of an element
    const screenshotPath = path.join(resultsDir, 'navbar.png');
    await visual.screenshotElement(page, '.navbar__inner', screenshotPath);
    
    // Verify the screenshot was created
    expect(fs.existsSync(screenshotPath)).toBeTruthy();
  });
  
  test('should check if an element is visible', async ({ page }) => {
    // Navigate to a test website
    await page.goto('https://playwright.dev/');
    
    // Check if an element is visible
    const isVisible = await visual.isElementVisible(page, '.navbar__inner');
    
    // Verify the element is visible
    expect(isVisible).toBeTruthy();
    
    // Check if a non-existent element is not visible
    const nonExistentVisible = await visual.isElementVisible(page, '.non-existent-element');
    
    // Verify the non-existent element is not visible
    expect(nonExistentVisible).toBeFalsy();
  });
  
  test('should check if an element matches a specific size', async ({ page }) => {
    // Navigate to a test website
    await page.goto('https://playwright.dev/');
    
    // Get the bounding box of an element
    const boundingBox = await page.locator('.navbar__inner').boundingBox();
    
    if (!boundingBox) {
      throw new Error('Could not get bounding box for element');
    }
    
    // Check if the element matches its own size (should always be true)
    const matchesSize = await visual.elementMatchesSize(
      page,
      '.navbar__inner',
      boundingBox.width,
      boundingBox.height
    );
    
    // Verify the element matches its own size
    expect(matchesSize).toBeTruthy();
  });
  
  test('should run a visual test', async ({ page }) => {
    // Navigate to a test website
    await page.goto('https://playwright.dev/');
    
    // Run a visual test
    const result = await visual.runVisualTest(page, 'playwright-homepage', '.navbar__inner');
    
    // Verify the test result
    expect(result.name).toBe('playwright-homepage');
    expect(result.screenshotPath).toBeTruthy();
    expect(result.referencePath).toBeTruthy();
  });
  
  test('should check if a page matches a specific viewport size', async ({ page }) => {
    // Set viewport size
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Navigate to a test website
    await page.goto('https://playwright.dev/');
    
    // Check if the page matches the viewport size
    const matchesViewport = await visual.pageMatchesViewport(page, 1280, 720);
    
    // Verify the page matches the viewport size
    expect(matchesViewport).toBeTruthy();
  });
});
