// HUD Waveform Augment - Audio Listener Service

import { useState, useEffect } from 'react';

/**
 * Configuration options for the audio listener
 */
interface AudioListenerConfig {
  /** Amplitude threshold to determine if sound is detected (0-1000) */
  threshold: number;
  /** Interval in ms to check audio levels */
  checkInterval: number;
  /** Decay rate for audio level (0-1) - higher means faster decay */
  decayRate: number;
}

/**
 * Default configuration for audio listener
 */
const DEFAULT_CONFIG: AudioListenerConfig = {
  threshold: 500,
  checkInterval: 100,
  decayRate: 0.3
};

/**
 * Simulates audio frame analysis and loudness detection
 * 
 * This is a placeholder that will be replaced with actual audio processing
 * in a future implementation. Currently generates random audio levels.
 * 
 * @returns Current audio level (0-1000)
 */
function simulateAudioFrame(): number {
  // Simulate microphone input with occasional spikes
  // Base level is 0-300, with 10% chance of a "speech" spike of 400-1000
  const baseLevel = Math.random() * 300;
  const isSpeaking = Math.random() < 0.1; // 10% chance of speech
  
  if (isSpeaking) {
    // Add a "speech" spike (400-1000 range)
    return baseLevel + 400 + Math.random() * 600;
  }
  
  return baseLevel;
}

/**
 * React hook for audio listening functionality
 * 
 * Simulates listening to microphone and detecting when audio levels
 * exceed a specified threshold.
 * 
 * @param config Optional configuration parameters
 * @returns Object containing listening state and current audio level
 */
export function useAudioListener(config: Partial<AudioListenerConfig> = {}) {
  // Merge provided config with defaults
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  
  // State for tracking if we're detecting sound above threshold
  const [listening, setListening] = useState<boolean>(false);
  
  // State for tracking current audio level
  const [audioLevel, setAudioLevel] = useState<number>(0);
  
  useEffect(() => {
    // Track the last audio level for smooth transitions
    let currentLevel = 0;
    
    // Set up interval to check audio levels
    const intervalId = setInterval(() => {
      // Get simulated audio frame level
      const newFrameLevel = simulateAudioFrame();
      
      // Apply some smoothing with decay for more natural transitions
      // Current level moves toward new frame level, but with some inertia
      currentLevel = currentLevel * (1 - mergedConfig.decayRate) + 
                     newFrameLevel * mergedConfig.decayRate;
      
      // Update state with current level
      setAudioLevel(Math.round(currentLevel));
      
      // Update listening state based on threshold
      setListening(currentLevel > mergedConfig.threshold);
      
    }, mergedConfig.checkInterval);
    
    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [mergedConfig.threshold, mergedConfig.checkInterval, mergedConfig.decayRate]);
  
  return {
    listening,
    audioLevel
  };
}

/**
 * Standalone audio listener class (alternative to the hook)
 * 
 * Can be used in non-React contexts or for more complex scenarios.
 */
export class AudioListenerService {
  private config: AudioListenerConfig;
  private intervalId: NodeJS.Timeout | null = null;
  private currentLevel: number = 0;
  private onListeningChange: ((listening: boolean) => void) | null = null;
  private onLevelChange: ((level: number) => void) | null = null;
  
  constructor(config: Partial<AudioListenerConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }
  
  /**
   * Start listening for audio
   */
  public start(): void {
    if (this.intervalId) {
      return; // Already started
    }
    
    this.intervalId = setInterval(() => {
      // Get simulated audio frame level
      const newFrameLevel = simulateAudioFrame();
      
      // Apply smoothing with decay
      this.currentLevel = this.currentLevel * (1 - this.config.decayRate) + 
                         newFrameLevel * this.config.decayRate;
      
      // Determine if we're listening based on threshold
      const isListening = this.currentLevel > this.config.threshold;
      
      // Notify listeners
      if (this.onLevelChange) {
        this.onLevelChange(Math.round(this.currentLevel));
      }
      
      if (this.onListeningChange) {
        this.onListeningChange(isListening);
      }
      
    }, this.config.checkInterval);
  }
  
  /**
   * Stop listening for audio
   */
  public stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
  
  /**
   * Set callback for listening state changes
   */
  public setOnListeningChange(callback: (listening: boolean) => void): void {
    this.onListeningChange = callback;
  }
  
  /**
   * Set callback for audio level changes
   */
  public setOnLevelChange(callback: (level: number) => void): void {
    this.onLevelChange = callback;
  }
  
  /**
   * Update configuration
   */
  public updateConfig(config: Partial<AudioListenerConfig>): void {
    this.config = { ...this.config, ...config };
  }
  
  /**
   * Get current audio level
   */
  public getAudioLevel(): number {
    return Math.round(this.currentLevel);
  }
  
  /**
   * Check if currently listening (above threshold)
   */
  public isListening(): boolean {
    return this.currentLevel > this.config.threshold;
  }
}

// Export a singleton instance for easy import
export const audioListener = new AudioListenerService();

// Default export for the hook
export default useAudioListener;
