// HUD Waveform Augment - Audio Listener Service

import { useState, useEffect, useRef } from 'react';

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
  /** WebSocket server URL */
  websocketUrl: string;
  /** Reconnection delay in ms */
  reconnectDelay: number;
  /** Maximum number of reconnection attempts */
  maxReconnectAttempts: number;
}

/**
 * WebSocket message format from the Python backend
 */
interface AudioLoudnessMessage {
  /** Message type (e.g., "loudness") */
  type: string;
  /** Audio loudness level (0.0-1.0) */
  value: number;
  /** Timestamp from the server */
  timestamp?: number;
}

/**
 * Default configuration for audio listener
 */
const DEFAULT_CONFIG: AudioListenerConfig = {
  threshold: 500,
  checkInterval: 100,
  decayRate: 0.3,
  websocketUrl: 'ws://localhost:8000',
  reconnectDelay: 2000,
  maxReconnectAttempts: 5
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
 * Connects to a WebSocket server to receive real-time audio loudness levels
 * and detects when audio levels exceed a specified threshold.
 *
 * @param config Optional configuration parameters
 * @returns Object containing listening state, current audio level, and connection status
 */
export function useAudioListener(config: Partial<AudioListenerConfig> = {}) {
  // Merge provided config with defaults
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // State for tracking if we're detecting sound above threshold
  const [listening, setListening] = useState<boolean>(false);

  // State for tracking current audio level
  const [audioLevel, setAudioLevel] = useState<number>(0);

  // State for tracking WebSocket connection status
  const [connected, setConnected] = useState<boolean>(false);

  // Refs for WebSocket and reconnection
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Track the last audio level for smooth transitions
  const currentLevelRef = useRef<number>(0);

  // Function to connect to WebSocket server
  const connectWebSocket = useEffect(() => {
    let fallbackIntervalId: NodeJS.Timeout | null = null;

    const connect = () => {
      try {
        // Close existing connection if any
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close();
        }

        // Create new WebSocket connection
        const ws = new WebSocket(mergedConfig.websocketUrl);
        wsRef.current = ws;

        // Handle WebSocket events
        ws.onopen = () => {
          console.log('WebSocket connected to audio server');
          setConnected(true);
          reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection

          // Clear any fallback interval
          if (fallbackIntervalId) {
            clearInterval(fallbackIntervalId);
            fallbackIntervalId = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            // Parse the message
            const message = JSON.parse(event.data) as AudioLoudnessMessage;

            // Only process loudness messages
            if (message.type === 'loudness') {
              // Apply smoothing with decay for more natural transitions
              // Scale the value from 0-1 to 0-1000 for compatibility with existing code
              const newLevel = message.value * 1000;
              currentLevelRef.current = currentLevelRef.current * (1 - mergedConfig.decayRate) +
                                        newLevel * mergedConfig.decayRate;
            }

            // Update state with current level
            const roundedLevel = Math.round(currentLevelRef.current);
            setAudioLevel(roundedLevel);

            // Update listening state based on threshold
            setListening(currentLevelRef.current > mergedConfig.threshold);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onclose = (event) => {
          console.log(`WebSocket disconnected: ${event.code} ${event.reason}`);
          setConnected(false);

          // Attempt to reconnect if not closed intentionally
          if (reconnectAttemptsRef.current < mergedConfig.maxReconnectAttempts) {
            reconnectAttemptsRef.current++;
            console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${mergedConfig.maxReconnectAttempts})...`);

            // Set timeout for reconnection
            if (reconnectTimeoutRef.current) {
              clearTimeout(reconnectTimeoutRef.current);
            }
            reconnectTimeoutRef.current = setTimeout(connect, mergedConfig.reconnectDelay);
          } else {
            console.log('Maximum reconnection attempts reached. Falling back to simulation.');

            // Fall back to simulation if we can't connect
            fallbackIntervalId = setInterval(() => {
              // Get simulated audio frame level
              const newFrameLevel = simulateAudioFrame();

              // Apply smoothing with decay
              currentLevelRef.current = currentLevelRef.current * (1 - mergedConfig.decayRate) +
                                       newFrameLevel * mergedConfig.decayRate;

              // Update state with current level
              setAudioLevel(Math.round(currentLevelRef.current));

              // Update listening state based on threshold
              setListening(currentLevelRef.current > mergedConfig.threshold);
            }, mergedConfig.checkInterval);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          // The onclose handler will be called after this
        };
      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        setConnected(false);

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < mergedConfig.maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${mergedConfig.maxReconnectAttempts})...`);

          // Set timeout for reconnection
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }
          reconnectTimeoutRef.current = setTimeout(connect, mergedConfig.reconnectDelay);
        }
      }
    };

    // Initial connection
    connect();

    // Clean up on unmount
    return () => {
      // Close WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      // Clear any pending reconnect timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Clear fallback interval if active
      if (fallbackIntervalId) {
        clearInterval(fallbackIntervalId);
        fallbackIntervalId = null;
      }
    };
  }, [
    mergedConfig.websocketUrl,
    mergedConfig.reconnectDelay,
    mergedConfig.maxReconnectAttempts,
    mergedConfig.threshold,
    mergedConfig.decayRate,
    mergedConfig.checkInterval
  ]);

  return {
    listening,
    audioLevel,
    connected
  };
}

/**
 * Standalone audio listener class (alternative to the hook)
 *
 * Can be used in non-React contexts or for more complex scenarios.
 * Connects to a WebSocket server to receive real-time audio loudness levels.
 */
export class AudioListenerService {
  private config: AudioListenerConfig;
  private websocket: WebSocket | null = null;
  private fallbackIntervalId: NodeJS.Timeout | null = null;
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private reconnectAttempts: number = 0;
  private currentLevel: number = 0;
  private isConnected: boolean = false;
  private onListeningChange: ((listening: boolean) => void) | null = null;
  private onLevelChange: ((level: number) => void) | null = null;
  private onConnectionChange: ((connected: boolean) => void) | null = null;

  constructor(config: Partial<AudioListenerConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Start listening for audio via WebSocket
   */
  public start(): void {
    if (this.websocket) {
      return; // Already started
    }

    this.connectWebSocket();
  }

  /**
   * Connect to the WebSocket server
   */
  private connectWebSocket(): void {
    try {
      // Close existing connection if any
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }

      // Create new WebSocket connection
      this.websocket = new WebSocket(this.config.websocketUrl);

      // Handle WebSocket events
      this.websocket.onopen = this.handleWebSocketOpen.bind(this);
      this.websocket.onmessage = this.handleWebSocketMessage.bind(this);
      this.websocket.onclose = this.handleWebSocketClose.bind(this);
      this.websocket.onerror = this.handleWebSocketError.bind(this);
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.setConnectionState(false);
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleWebSocketOpen(): void {
    console.log('WebSocket connected to audio server');
    this.setConnectionState(true);
    this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection

    // Clear any fallback interval
    this.clearFallbackInterval();
  }

  /**
   * Handle WebSocket message event
   */
  private handleWebSocketMessage(event: MessageEvent): void {
    try {
      // Parse the message
      const message = JSON.parse(event.data) as AudioLoudnessMessage;

      // Only process loudness messages
      if (message.type === 'loudness') {
        // Apply smoothing with decay for more natural transitions
        // Scale the value from 0-1 to 0-1000 for compatibility with existing code
        const newLevel = message.value * 1000;
        this.currentLevel = this.currentLevel * (1 - this.config.decayRate) +
                           newLevel * this.config.decayRate;
      }

      // Determine if we're listening based on threshold
      const isListening = this.currentLevel > this.config.threshold;

      // Notify listeners
      if (this.onLevelChange) {
        this.onLevelChange(Math.round(this.currentLevel));
      }

      if (this.onListeningChange) {
        this.onListeningChange(isListening);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket close event
   */
  private handleWebSocketClose(event: CloseEvent): void {
    console.log(`WebSocket disconnected: ${event.code} ${event.reason}`);
    this.setConnectionState(false);
    this.websocket = null;

    // Attempt to reconnect
    this.attemptReconnect();
  }

  /**
   * Handle WebSocket error event
   */
  private handleWebSocketError(event: Event): void {
    console.error('WebSocket error:', event);
    // The onclose handler will be called after this
  }

  /**
   * Attempt to reconnect to the WebSocket server
   */
  private attemptReconnect(): void {
    // Attempt to reconnect if not at max attempts
    if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})...`);

      // Clear any existing timeout
      if (this.reconnectTimeoutId) {
        clearTimeout(this.reconnectTimeoutId);
      }

      // Set timeout for reconnection
      this.reconnectTimeoutId = setTimeout(() => {
        this.connectWebSocket();
      }, this.config.reconnectDelay);
    } else {
      console.log('Maximum reconnection attempts reached. Falling back to simulation.');
      this.startFallbackSimulation();
    }
  }

  /**
   * Start fallback simulation when WebSocket is unavailable
   */
  private startFallbackSimulation(): void {
    // Clear any existing interval
    this.clearFallbackInterval();

    // Start new interval for simulation
    this.fallbackIntervalId = setInterval(() => {
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
   * Clear the fallback interval
   */
  private clearFallbackInterval(): void {
    if (this.fallbackIntervalId) {
      clearInterval(this.fallbackIntervalId);
      this.fallbackIntervalId = null;
    }
  }

  /**
   * Set the connection state and notify listeners
   */
  private setConnectionState(connected: boolean): void {
    this.isConnected = connected;

    if (this.onConnectionChange) {
      this.onConnectionChange(connected);
    }
  }

  /**
   * Stop listening for audio
   */
  public stop(): void {
    // Close WebSocket connection
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }

    // Clear any pending reconnect timeout
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }

    // Clear fallback interval if active
    this.clearFallbackInterval();

    // Reset state
    this.setConnectionState(false);
    this.reconnectAttempts = 0;
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
   * Set callback for connection state changes
   */
  public setOnConnectionChange(callback: (connected: boolean) => void): void {
    this.onConnectionChange = callback;
  }

  /**
   * Update configuration
   */
  public updateConfig(config: Partial<AudioListenerConfig>): void {
    const oldWebsocketUrl = this.config.websocketUrl;
    this.config = { ...this.config, ...config };

    // Restart connection if WebSocket URL changed and we're connected
    if (this.websocket && oldWebsocketUrl !== this.config.websocketUrl) {
      this.stop();
      this.start();
    }
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

  /**
   * Check if currently connected to WebSocket server
   */
  public isWebSocketConnected(): boolean {
    return this.isConnected;
  }
}

// Export a singleton instance for easy import
export const audioListener = new AudioListenerService();

// Default export for the hook
export default useAudioListener;
