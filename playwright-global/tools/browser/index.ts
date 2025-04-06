/**
 * Browser Interaction Tools
 *
 * Tools for common browser interactions and manipulations.
 */

import { Page, ElementHandle, Locator } from '@playwright/test';
import {
  ScreenshotOptions,
  ScrollOptions,
  WaitOptions,
  HoverOptions
} from '../../types';

/**
 * Take a screenshot of the page
 * @param page - Playwright page
 * @param path - Path to save the screenshot
 * @param options - Screenshot options
 * @returns Promise resolving to the screenshot buffer
 */
export async function takeScreenshot(
  page: Page,
  path?: string,
  options: ScreenshotOptions = {}
): Promise<Buffer> {
  console.log(`Taking screenshot${path ? ` and saving to ${path}` : ''}...`);
  
  // Set default options
  const screenshotOptions: ScreenshotOptions = {
    fullPage: options.fullPage !== false,
    ...options
  };
  
  if (path) {
    screenshotOptions.path = path;
  }
  
  // Take screenshot
  return await page.screenshot(screenshotOptions);
}

/**
 * Scroll to an element on the page
 * @param page - Playwright page
 * @param selector - Element selector
 * @param options - Scroll options
 */
export async function scrollToElement(
  page: Page,
  selector: string,
  options: ScrollOptions = {}
): Promise<void> {
  console.log(`Scrolling to element: ${selector}...`);
  
  // Find the element
  const element = await page.locator(selector).first();
  
  // Check if element exists
  if (await element.count() === 0) {
    throw new Error(`Element not found: ${selector}`);
  }
  
  // Scroll to element
  await element.scrollIntoViewIfNeeded();
  
  // Wait a moment for the scroll to complete
  await page.waitForTimeout(500);
}

/**
 * Wait for network activity to be idle
 * @param page - Playwright page
 * @param options - Wait options
 */
export async function waitForNetworkIdle(
  page: Page,
  options: WaitOptions = {}
): Promise<void> {
  console.log('Waiting for network to be idle...');
  
  // Set default timeout
  const timeout = options.timeout || 30000;
  
  // Wait for network idle
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Get the page title
 * @param page - Playwright page
 * @returns Page title
 */
export async function getPageTitle(page: Page): Promise<string> {
  return await page.title();
}

/**
 * Click an element on the page
 * @param page - Playwright page
 * @param selector - Element selector
 * @param options - Click options
 */
export async function clickElement(
  page: Page,
  selector: string,
  options: any = {}
): Promise<void> {
  console.log(`Clicking element: ${selector}...`);
  
  // Set default options
  const clickOptions = {
    timeout: options.timeout || 30000,
    ...options
  };
  
  // Click the element
  await page.click(selector, clickOptions);
  
  // Wait for navigation if specified
  if (options.waitForNavigation) {
    await page.waitForLoadState('networkidle', { timeout: options.timeout || 30000 });
  }
}

/**
 * Hover over an element on the page
 * @param page - Playwright page
 * @param selector - Element selector
 * @param options - Hover options
 */
export async function hoverElement(
  page: Page,
  selector: string,
  options: HoverOptions = {}
): Promise<void> {
  console.log(`Hovering over element: ${selector}...`);
  
  // Set default options
  const hoverOptions = {
    timeout: options.timeout || 30000,
    ...options
  };
  
  // Hover over the element
  await page.hover(selector, hoverOptions);
  
  // Wait a moment if specified
  if (options.waitTime) {
    await page.waitForTimeout(options.waitTime);
  }
}

/**
 * Fill a form field
 * @param page - Playwright page
 * @param selector - Field selector
 * @param value - Value to fill
 * @param options - Fill options
 */
export async function fillField(
  page: Page,
  selector: string,
  value: string,
  options: any = {}
): Promise<void> {
  console.log(`Filling field ${selector} with value: ${value}...`);
  
  // Set default options
  const fillOptions = {
    timeout: options.timeout || 30000,
    ...options
  };
  
  // Fill the field
  await page.fill(selector, value, fillOptions);
}

/**
 * Wait for an element to be visible
 * @param page - Playwright page
 * @param selector - Element selector
 * @param options - Wait options
 * @returns The element handle
 */
export async function waitForElement(
  page: Page,
  selector: string,
  options: WaitOptions = {}
): Promise<Locator> {
  console.log(`Waiting for element: ${selector}...`);
  
  // Set default timeout
  const timeout = options.timeout || 30000;
  
  // Wait for the element to be visible
  const element = page.locator(selector);
  await element.waitFor({ state: 'visible', timeout });
  
  return element;
}

/**
 * Navigate to a URL
 * @param page - Playwright page
 * @param url - URL to navigate to
 * @param options - Navigation options
 */
export async function navigateTo(
  page: Page,
  url: string,
  options: WaitOptions = {}
): Promise<void> {
  console.log(`Navigating to: ${url}...`);
  
  // Set default options
  const waitUntil = options.waitUntil || 'networkidle';
  const timeout = options.timeout || 30000;
  
  // Navigate to the URL
  await page.goto(url, { waitUntil, timeout });
}

/**
 * Get the current URL
 * @param page - Playwright page
 * @returns Current URL
 */
export async function getCurrentUrl(page: Page): Promise<string> {
  return page.url();
}

/**
 * Check if an element exists on the page
 * @param page - Playwright page
 * @param selector - Element selector
 * @returns Whether the element exists
 */
export async function elementExists(
  page: Page,
  selector: string
): Promise<boolean> {
  const count = await page.locator(selector).count();
  return count > 0;
}

/**
 * Get text content of an element
 * @param page - Playwright page
 * @param selector - Element selector
 * @returns Text content
 */
export async function getElementText(
  page: Page,
  selector: string
): Promise<string> {
  return await page.locator(selector).textContent() || '';
}
