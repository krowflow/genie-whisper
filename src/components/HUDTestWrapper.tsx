// HUD Waveform Augment - Test Wrapper Component

import React, { useState } from 'react';
import WaveformHUD from './WaveformHUD';

/**
 * HUDTestWrapper Component
 * 
 * A test wrapper component for the WaveformHUD that provides a button
 * to toggle the listening state, allowing for easy testing of the HUD's
 * different states.
 */
const HUDTestWrapper: React.FC = () => {
  // State to track listening status
  const [listening, setListening] = useState<boolean>(false);

  // Toggle function to switch listening state
  const toggleListening = () => {
    setListening(prevState => !prevState);
  };

  // Button styles
  const buttonStyle: React.CSSProperties = {
    padding: '8px 16px',
    margin: '20px 0',
    backgroundColor: '#3f51b5', // Indigo color
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
    transition: 'background-color 0.2s ease'
  };

  // Container styles
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
    maxWidth: '500px',
    margin: '0 auto'
  };

  return (
    <div style={containerStyle}>
      <h2>WaveformHUD Test</h2>
      
      {/* Display current state */}
      <p>Current State: {listening ? 'Listening' : 'Not Listening'}</p>
      
      {/* Button to toggle state */}
      <button 
        style={buttonStyle} 
        onClick={toggleListening}
      >
        Toggle Listening State
      </button>
      
      {/* WaveformHUD component with listening prop */}
      <div style={{ width: '100%', marginTop: '20px' }}>
        <WaveformHUD listening={listening} />
      </div>
    </div>
  );
};

export default HUDTestWrapper;
