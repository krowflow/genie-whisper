import { Page, BrowserContext, Browser, ElementHandle, Locator } from '@playwright/test';

/**
 * Browser Interaction Tool Types
 */
export interface ScreenshotOptions {
  fullPage?: boolean;
  clip?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  omitBackground?: boolean;
  quality?: number;
  timeout?: number;
}

export interface ScrollOptions {
  smooth?: boolean;
  timeout?: number;
}

export interface WaitOptions {
  timeout?: number;
}

export interface HoverOptions {
  waitTime?: number;
  position?: { x: number; y: number };
  timeout?: number;
}

/**
 * PDF Testing Tool Types
 */
export interface PdfOptions {
  format?: string;
  width?: number | string;
  height?: number | string;
  margin?: {
    top?: string | number;
    right?: string | number;
    bottom?: string | number;
    left?: string | number;
  };
  printBackground?: boolean;
  landscape?: boolean;
  scale?: number;
  preferCSSPageSize?: boolean;
  displayHeaderFooter?: boolean;
  headerTemplate?: string;
  footerTemplate?: string;
  pageRanges?: string;
}

export interface PdfCaptureOptions {
  waitForSelector?: string;
  beforeCapture?: (page: Page) => Promise<void>;
  pdfOptions?: PdfOptions;
  timeout?: number;
}

export interface PdfComparisonOptions {
  visualComparison?: boolean;
  outputDir?: string;
}

/**
 * Visual Testing Tool Types
 */
export interface ViewportSize {
  width: number;
  height: number;
  name: string;
}

export interface ComparisonResult {
  identical: boolean;
  diffPercentage?: number;
  diffPixels?: number;
  newReference?: boolean;
}

export interface VisualTestResult {
  name: string;
  screenshotPath: string;
  referencePath: string;
  diffPath?: string;
  identical: boolean;
  diffPercentage?: number;
  diffPixels?: number;
  newReference?: boolean;
}

/**
 * Accessibility Testing Tool Types
 */
export interface AccessibilityViolation {
  id: string;
  impact: "critical" | "serious" | "moderate" | "minor";
  description: string;
  help: string;
  helpUrl: string;
  nodes: Array<{
    html: string;
    failureSummary: string;
  }>;
}

export interface AccessibilityResults {
  violations: AccessibilityViolation[];
  passes: Array<{
    id: string;
    description: string;
    help: string;
    helpUrl: string;
  }>;
  incomplete: any[];
  inapplicable: any[];
  url: string;
  timestamp: string;
}

export interface AccessibilityReportOptions {
  includePasses?: boolean;
}

/**
 * Performance Testing Tool Types
 */
export interface PerformanceMetrics {
  lcp?: number;
  fid?: number;
  cls?: number;
  domContentLoaded: number;
  load: number;
  firstByte: number;
  domInteractive: number;
  resourceCount: number;
  totalResourceSize: number;
}

export interface PerformanceResults {
  url: string;
  navigationTime: number;
  statusCode: number | null;
  tracePath?: string;
  timestamp: string;
  metrics: PerformanceMetrics;
  resources: Array<{
    name: string;
    type: string;
    duration: number;
    size: number;
  }>;
}

export interface PerformanceTestOptions {
  waitUntil?: "load" | "domcontentloaded" | "networkidle";
  timeout?: number;
  additionalWaitTime?: number;
  tracingOptions?: {
    screenshots?: boolean;
    snapshots?: boolean;
    sources?: boolean;
  };
  tracePath?: string;
  reportPath?: string;
  interactionSelector?: string;
}

/**
 * Data Extraction Tool Types
 */
export interface TableExtractionOptions {
  includeHeaders?: boolean;
  headerRowIndex?: number;
  startRowIndex?: number;
  endRowIndex?: number;
  rowSelector?: string;
  headerSelector?: string;
  cellSelector?: string;
  asObjects?: boolean;
}

export interface TableData {
  headers?: string[];
  data: Array<Record<string, string> | string[]>;
}

export interface StructuredDataSelector {
  selector: string;
  attribute?: string;
  method?: "property" | "attribute" | "text" | "html" | "count";
  transform?: (value: any) => any;
}

export interface StructuredDataOptions {
  waitForVisible?: boolean;
  timeout?: number;
  attributes?: Record<string, string>;
}

export interface LinkExtractionOptions {
  selector?: string;
  includePattern?: string;
  excludePattern?: string;
}

export interface ImageExtractionOptions {
  selector?: string;
  includePattern?: string;
  excludePattern?: string;
}

export interface TextExtractionOptions {
  waitForVisible?: boolean;
  timeout?: number;
  includeHidden?: boolean;
  recursive?: boolean;
}

export interface Metadata {
  title: string;
  description: string;
  keywords: string;
  canonical: string;
  ogTags: Record<string, string>;
  twitterTags: Record<string, string>;
}

/**
 * Form Automation Tool Types
 */
export interface FormOptions {
  formSelector?: string;
  fieldSelectors?: Record<string, string>;
  clearFields?: boolean;
  delay?: number;
  continueOnError?: boolean;
  waitForForm?: boolean;
  timeout?: number;
  fieldTimeout?: number;
}

export interface FormSubmitOptions {
  formSelector?: string;
  submitSelector?: string;
  waitUntil?: "load" | "domcontentloaded" | "networkidle";
  timeout?: number;
  navigationTimeout?: number;
  waitAfterSubmit?: number;
}

export interface FormValidationOptions {
  formSelector?: string;
  errorSelectors?: string[];
  waitForErrors?: boolean;
  waitTime?: number;
}

export interface FormSuccessOptions {
  successSelectors?: string[];
  errorSelectors?: string[];
  timeout?: number;
}

export interface FieldDefinition {
  type: "text" | "email" | "number" | "date" | "select" | "checkbox" | "radio" | "phone" | "name" | "address";
  options?: {
    length?: number;
    min?: number;
    max?: number;
    start?: string | Date;
    end?: string | Date;
    values?: any[];
    checked?: boolean;
    value?: any;
    format?: string;
    full?: boolean;
  };
}

/**
 * Authentication Tool Types
 */
export interface LoginCredentials {
  username: string;
  email?: string;
  password: string;
  twoFactorCode?: string;
}

export interface LoginOptions {
  usernameSelector?: string;
  passwordSelector?: string;
  submitSelector?: string;
  twoFactorRequired?: boolean;
  twoFactorSelector?: string;
  successUrl?: string;
  successSelector?: string;
  failureSelector?: string;
  waitUntil?: "load" | "domcontentloaded" | "networkidle";
  timeout?: number;
  formTimeout?: number;
  twoFactorTimeout?: number;
  navigationTimeout?: number;
}

export interface LoggedInOptions {
  loggedInSelector?: string;
  loggedOutSelector?: string;
  checkUrl?: boolean;
  loggedInSelectors?: string[];
  loggedOutSelectors?: string[];
  timeout?: number;
}

export interface LogoutOptions {
  logoutSelector?: string;
  successUrl?: string;
  successSelector?: string;
  timeout?: number;
}

export interface CaptchaOptions {
  captchaSelector?: string;
  successSelector?: string;
  manualSolving?: boolean;
  manualTimeout?: number;
  timeout?: number;
}

export interface RegistrationData {
  email?: string;
  username?: string;
  password?: string;
  firstName?: string;
  lastName?: string;
  name?: string;
  phone?: string;
  additionalFields?: Record<string, any>;
}

export interface RegistrationOptions {
  formSelector?: string;
  emailField?: string;
  usernameField?: string;
  passwordField?: string;
  confirmPasswordField?: string;
  firstNameField?: string;
  lastNameField?: string;
  nameField?: string;
  phoneField?: string;
  termsSelector?: string;
  submitSelector?: string;
  successUrl?: string;
  successSelector?: string;
  failureSelector?: string;
  handleCaptcha?: boolean;
  captchaOptions?: CaptchaOptions;
  waitUntil?: "load" | "domcontentloaded" | "networkidle";
  timeout?: number;
  fieldTimeout?: number;
  navigationTimeout?: number;
}

export interface CredentialOptions {
  username?: string;
  email?: string;
  passwordLength?: number;
  useSpecialChars?: boolean;
  useNumbers?: boolean;
  useUppercase?: boolean;
  useLowercase?: boolean;
  generateName?: boolean;
  domain?: string;
}

/**
 * API Testing Tool Types
 */
export interface ApiRequestOptions {
  method?: string;
  headers?: Record<string, string>;
  data?: any;
  params?: Record<string, string>;
}

export interface ApiResponse {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  data: any;
  ok: boolean;
  error?: string;
}

export interface GraphQLOptions extends ApiRequestOptions {
  operationName?: string;
}

export interface ApiSchema {
  status?: number;
  headers?: Record<string, string>;
  data?: any;
}

export interface ApiTestCase {
  name?: string;
  url: string;
  options?: ApiRequestOptions;
  graphql?: {
    query: string;
    variables?: Record<string, any>;
  };
  schema?: ApiSchema;
  expectedStatus?: number;
  assertions?: Array<(response: ApiResponse) => boolean>;
}

export interface ApiTestResult {
  name?: string;
  passed: boolean;
  request: {
    url: string;
    method: string;
    headers?: Record<string, string>;
    data?: any;
  };
  response: ApiResponse;
  validation?: {
    valid: boolean;
    errors: string[];
  };
  error?: string;
  duration?: number;
}

export interface ApiTestSuiteOptions {
  stopOnFailure?: boolean;
  delay?: number;
  reportPath?: string;
}

/**
 * Mobile Emulation Tool Types
 */
export interface DeviceConfig {
  name: string;
  userAgent: string;
  viewport: {
    width: number;
    height: number;
    deviceScaleFactor: number;
    isMobile: boolean;
    hasTouch: boolean;
    isLandscape: boolean;
  };
}

export interface SwipeOptions {
  direction?: "up" | "down" | "left" | "right";
  distance?: number;
  steps?: number;
}

export interface ResponsiveTestOptions {
  takeScreenshots?: boolean;
  screenshotDir?: string;
  generateReport?: boolean;
  reportPath?: string;
  checkElements?: string[];
  waitForSelector?: string;
  waitUntil?: "load" | "domcontentloaded" | "networkidle";
  timeout?: number;
  selectorTimeout?: number;
  fullPageScreenshot?: boolean;
}

export interface ResponsiveTestResults {
  url: string;
  devices: Array<{
    name: string;
    viewport: {
      width: number;
      height: number;
      deviceScaleFactor: number;
      isMobile: boolean;
      hasTouch: boolean;
      isLandscape: boolean;
    };
    userAgent: string;
    screenshotPath?: string;
    elementChecks?: Record<string, boolean>;
  }>;
  screenshots: Record<string, string>;
  timestamp: string;
}
