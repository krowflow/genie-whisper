/**
 * TranscriptionHelper.ts
 * Utility functions for handling transcription text formatting
 */

/**
 * Formats a transcription string by:
 * - Trimming whitespace
 * - Capitalizing the first letter
 * - Ensuring the string ends with a period
 *
 * @param text The input transcription text
 * @returns The formatted transcription text
 */
export function formatTranscript(text: string): string {
  // Trim whitespace from the input string
  let formatted = text.trim();

  // If the string is empty after trimming, return an empty string
  if (formatted.length === 0) {
    return '';
  }

  // Capitalize the first letter
  formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1);

  // Ensure the string ends with a period
  if (!formatted.endsWith('.') &&
      !formatted.endsWith('!') &&
      !formatted.endsWith('?')) {
    formatted += '.';
  }

  return formatted;
}

/**
 * Sanitizes a transcription string by:
 * - Trimming leading and trailing whitespace
 * - Removing tabs and newline characters
 * - Collapsing multiple consecutive spaces into a single space
 *
 * @example
 * // Returns "Hello world this is a test."
 * sanitizeTranscript("   Hello\tworld\n\nthis   is   a    test. ");
 *
 * @param text The input transcription text
 * @returns The sanitized transcription text
 */
export function sanitizeTranscript(text: string): string {
  // Trim leading and trailing whitespace
  let sanitized = text.trim();

  // Remove tabs and newline characters
  sanitized = sanitized.replace(/[\t\n\r]/g, ' ');

  // Collapse multiple consecutive spaces into a single space
  sanitized = sanitized.replace(/\s+/g, ' ');

  return sanitized;
}

/**
 * Splits a transcription string into an array of sentences.
 * - Splits on periods (.)
 * - Trims whitespace from each sentence
 * - Filters out empty sentences
 *
 * @example
 * // Returns ["Hello world.", "This is a test.", "Another sentence."]
 * splitTranscriptIntoSentences("Hello world. This is a test. Another sentence.");
 *
 * @param text The input transcription text
 * @returns An array of sentences
 */
export function splitTranscriptIntoSentences(text: string): string[] {
  // If the input is empty, return an empty array
  if (!text || text.trim() === '') {
    return [];
  }

  // Split the text by periods
  const sentences = text.split('.');

  // Process each sentence: trim whitespace and add back the period
  return sentences
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length > 0)
    .map(sentence => `${sentence}.`);
}
