// HUD Waveform Augment - Waveform HUD Component

import React from 'react';

/**
 * Props for the WaveformHUD component
 */
interface WaveformHUDProps {
  listening: boolean;
}

/**
 * WaveformHUD Component
 *
 * A simple HUD (Heads-Up Display) component for the waveform visualization.
 * Displays different text and background color based on listening state.
 *
 * @param listening - Boolean indicating whether the system is currently listening
 */
const WaveformHUD: React.FC<WaveformHUDProps> = ({ listening }) => {
  // Define styles based on listening state
  const hudStyle: React.CSSProperties = {
    padding: '10px',
    borderRadius: '4px',
    textAlign: 'center',
    fontWeight: 'bold',
    backgroundColor: listening ? '#4CAF50' : '#808080', // Green when listening, gray when not
    color: '#FFFFFF', // White text for better contrast
    transition: 'background-color 0.3s ease' // Smooth transition between states
  };

  return (
    <div style={hudStyle}>
      {listening ? 'Listening...' : 'Waveform HUD Active'}
    </div>
  );
};

export default WaveformHUD;
