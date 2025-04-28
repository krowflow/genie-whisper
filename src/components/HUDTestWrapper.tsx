// HUD Waveform Augment - Test Wrapper Component

import React from 'react';
import WaveformHUD from './WaveformHUD';
import useAudioListener from '../listeners/AudioListener';

/**
 * HUDTestWrapper Component
 *
 * A test wrapper component for the WaveformHUD that uses the AudioListener
 * service to automatically detect audio input and update the HUD's state.
 */
const HUDTestWrapper: React.FC = () => {
  // Use the AudioListener hook to get real-time listening state
  const { listening, audioLevel } = useAudioListener({
    threshold: 500,      // Adjust threshold for sensitivity
    checkInterval: 100,  // Check every 100ms
    decayRate: 0.3       // Smooth transitions
  });

  // Container styles
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
    maxWidth: '500px',
    margin: '0 auto'
  };

  // Audio level indicator styles
  const levelIndicatorStyle: React.CSSProperties = {
    width: '100%',
    height: '20px',
    backgroundColor: '#e0e0e0',
    borderRadius: '10px',
    overflow: 'hidden',
    margin: '10px 0 20px 0'
  };

  // Audio level fill styles
  const levelFillStyle: React.CSSProperties = {
    height: '100%',
    width: `${Math.min(100, audioLevel / 10)}%`, // Convert 0-1000 to 0-100%
    backgroundColor: listening ? '#4CAF50' : '#3f51b5',
    transition: 'width 0.1s ease, background-color 0.3s ease'
  };

  return (
    <div style={containerStyle}>
      <h2>WaveformHUD Test</h2>

      {/* Display current state */}
      <p>Current State: {listening ? 'Listening' : 'Not Listening'}</p>
      <p>Audio Level: {audioLevel}</p>

      {/* Audio level visualization */}
      <div style={levelIndicatorStyle}>
        <div style={levelFillStyle}></div>
      </div>

      {/* WaveformHUD component with listening prop */}
      <div style={{ width: '100%' }}>
        <WaveformHUD listening={listening} />
      </div>
    </div>
  );

export default HUDTestWrapper;
