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
