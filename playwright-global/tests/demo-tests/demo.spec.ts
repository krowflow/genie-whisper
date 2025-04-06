/**
 * Demo Test
 * 
 * A comprehensive test demonstrating all our Playwright tools.
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Import all our tools
import { browser, visual, pdf, accessibility, performance, data, forms, auth, api, mobile } from '../../tools';

test.describe('Playwright Global Tools Demo', () => {
  test('should demonstrate browser tools', async ({ page }) => {
    // Navigate to a website
    await page.goto('https://playwright.dev/');
    
    // Take a screenshot
    const screenshotPath = path.join('test-results', 'demo', 'screenshot.png');
    await browser.takeScreenshot(page, screenshotPath);
    
    // Verify the screenshot was created
    expect(fs.existsSync(screenshotPath)).toBeTruthy();
    
    // Scroll to an element
    await browser.scrollToElement(page, 'text=Get Started');
    
    // Wait for network idle
    await browser.waitForNetworkIdle(page);
    
    // Get page title
    const title = await browser.getPageTitle(page);
    console.log(`Page title: ${title}`);
    expect(title).toContain('Playwright');
  });
  
  test('should demonstrate visual testing tools', async ({ page }) => {
    // Navigate to a website
    await page.goto('https://playwright.dev/');
    
    // Take a screenshot of an element
    const elementScreenshotPath = path.join('test-results', 'demo', 'element.png');
    await visual.screenshotElement(page, '.navbar__inner', elementScreenshotPath);
    
    // Verify the screenshot was created
    expect(fs.existsSync(elementScreenshotPath)).toBeTruthy();
  });
  
  test('should demonstrate data extraction tools', async ({ page }) => {
    // Navigate to a website
    await page.goto('https://playwright.dev/');
    
    // Extract links
    const links = await data.extractLinks(page);
    
    // Verify links were extracted
    expect(links.length).toBeGreaterThan(0);
    console.log(`Found ${links.length} links on the page`);
    
    // Extract metadata
    const metadata = await data.extractMetadata(page);
    
    // Verify metadata was extracted
    expect(metadata.title).toBeDefined();
    console.log(`Page title: ${metadata.title}`);
    console.log(`Page description: ${metadata.description}`);
  });
  
  test('should demonstrate performance tools', async ({ page }) => {
    // Measure page load performance
    const results = await performance.measurePageLoad(page, 'https://playwright.dev/');
    
    // Verify results
    expect(results.url).toBe('https://playwright.dev/');
    expect(results.metrics).toBeDefined();
    
    // Log performance metrics
    console.log('Performance Metrics:');
    console.log(`- Time to First Byte: ${results.metrics.firstByte}ms`);
    console.log(`- DOM Content Loaded: ${results.metrics.domContentLoaded}ms`);
    console.log(`- Load Complete: ${results.metrics.load}ms`);
  });
});
