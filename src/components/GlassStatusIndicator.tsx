// Genie Whisper - Glass Status Indicator Component
// A futuristic glassmorphism status indicator

import React from 'react';

/**
 * Props for the GlassStatusIndicator component
 */
interface GlassStatusIndicatorProps {
  /** Whether the system is currently listening */
  listening: boolean;
  /** Optional CSS class name */
  className?: string;
  /** Optional style overrides */
  style?: React.CSSProperties;
}

/**
 * GlassStatusIndicator Component
 * 
 * A futuristic glassmorphism status indicator that shows
 * whether the system is listening or waiting.
 */
const GlassStatusIndicator: React.FC<GlassStatusIndicatorProps> = ({
  listening,
  className = '',
  style = {}
}) => {
  // Container styles with glassmorphism effect
  const containerStyle: React.CSSProperties = {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    borderRadius: '12px',
    padding: '0.75rem 2rem',
    fontSize: '1.25rem',
    fontWeight: 500,
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 4px 30px rgba(0, 0, 0, 0.1)',
    transition: 'all 0.3s ease',
    textAlign: 'center',
    ...style
  };

  return (
    <div className={className} style={containerStyle}>
      {listening ? 'Listening...' : 'Waiting...'}
    </div>
  );
};

export default React.memo(GlassStatusIndicator);
