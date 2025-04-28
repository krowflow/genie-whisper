// Genie Whisper - Main Home Page
// A futuristic UI with glassmorphism effects and real-time audio visualization

import React, { useMemo } from 'react';
import { useAudioListener } from '../listeners/AudioListener';
import GenieAvatar from '../components/GenieAvatar';
import GlassWaveformHUD from '../components/GlassWaveformHUD';
import GlassStatusIndicator from '../components/GlassStatusIndicator';

// Define the interface for the component's props
interface GenieHomeProps {
  // Add any props if needed in the future
}

/**
 * GenieHome Component
 *
 * The main page for the Genie Whisper application featuring:
 * - Genie avatar with reactive glow based on audio input
 * - Animated waveform HUD that reacts to microphone input
 * - Listening status indicator
 * - Glassmorphism UI elements
 */
const GenieHome: React.FC<GenieHomeProps> = () => {
  // Connect to the WebSocket server for real-time audio loudness
  const { listening, audioLevel, connected } = useAudioListener({
    websocketUrl: 'ws://localhost:8000',
    threshold: 300,  // Threshold for determining when user is speaking
    decayRate: 0.2   // Smooth transitions between audio levels
  });

  // Memoize styles to prevent unnecessary re-renders
  const styles = useMemo(() => ({
    // Main container
    container: {
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      background: 'linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(23,37,84,0.8) 100%)',
      fontFamily: '"Inter", "Roboto", sans-serif',
      color: 'white',
      position: 'relative' as const,
      overflow: 'hidden',
    },

    // Waveform container
    waveformContainer: {
      width: '400px',
      height: '100px',
      marginBottom: '2rem',
    },

    // Connection status indicator
    connectionStatus: {
      position: 'absolute' as const,
      top: '1rem',
      right: '1rem',
      padding: '0.5rem 1rem',
      borderRadius: '8px',
      fontSize: '0.875rem',
      background: connected ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
      color: connected ? 'rgb(16, 185, 129)' : 'rgb(239, 68, 68)',
      border: `1px solid ${connected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
      backdropFilter: 'blur(10px)',
    },
  }), [connected]);

  return (
    <div style={styles.container}>
      {/* Connection status indicator */}
      <div style={styles.connectionStatus}>
        {connected ? 'Connected' : 'Disconnected'}
      </div>

      {/* Genie avatar with dynamic glow */}
      <GenieAvatar
        isListening={listening}
      />

      {/* Waveform HUD with real-time audio visualization */}
      <div style={styles.waveformContainer}>
        <GlassWaveformHUD
          audioLevel={audioLevel}
          listening={listening}
        />
      </div>

      {/* Listening status indicator */}
      <GlassStatusIndicator listening={listening} />
    </div>
  );
};

export default GenieHome;
