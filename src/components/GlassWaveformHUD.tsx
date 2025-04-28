// Genie Whisper - Glass Waveform HUD Component
// A futuristic glassmorphism waveform visualization component

import React, { useMemo } from 'react';

/**
 * Props for the GlassWaveformHUD component
 */
interface GlassWaveformHUDProps {
  /** Current audio level (0-1000) */
  audioLevel: number;
  /** Whether the system is currently listening */
  listening: boolean;
  /** Optional CSS class name */
  className?: string;
  /** Optional style overrides */
  style?: React.CSSProperties;
}

/**
 * GlassWaveformHUD Component
 * 
 * A futuristic glassmorphism waveform visualization component that
 * reacts to real-time audio input.
 */
const GlassWaveformHUD: React.FC<GlassWaveformHUDProps> = ({
  audioLevel,
  listening,
  className = '',
  style = {}
}) => {
  // Calculate waveform amplitude based on audio level
  const waveformAmplitude = useMemo(() => {
    // Map audioLevel (0-1000) to amplitude percentage (0-100%)
    return Math.min(100, (audioLevel / 1000) * 100);
  }, [audioLevel]);

  // Container styles with glassmorphism effect
  const containerStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100%',
    borderRadius: '16px',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 4px 30px rgba(0, 0, 0, 0.1)',
    padding: '1rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    ...style
  };

  // Waveform container styles
  const waveformStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    height: '100%',
    gap: '4px'
  };

  // Generate waveform bars
  const renderWaveformBars = () => {
    const bars = [];
    const barCount = 30; // Number of bars in the waveform
    
    for (let i = 0; i < barCount; i++) {
      // Create a pattern where bars are taller in the middle
      const positionFactor = 1 - Math.abs((i - barCount / 2) / (barCount / 2));
      
      // Calculate height based on position and audio level
      const heightPercentage = Math.max(
        10, // Minimum height percentage
        positionFactor * waveformAmplitude
      );
      
      // Alternate bar heights for more interesting visual
      const heightVariation = i % 2 === 0 ? 1 : 0.7;
      const height = `${heightPercentage * heightVariation}%`;
      
      // Calculate color based on whether we're listening
      const hue = listening ? 190 : 210; // Blue when listening, slightly different blue when not
      const saturation = listening ? '100%' : '70%';
      const lightness = listening ? '50%' : '40%';
      const opacity = listening ? 0.9 : 0.6;
      
      bars.push(
        <div
          key={i}
          style={{
            width: '6px',
            height,
            backgroundColor: `hsla(${hue}, ${saturation}, ${lightness}, ${opacity})`,
            borderRadius: '2px',
            transition: 'height 0.1s ease-out, background-color 0.3s ease',
          }}
        />
      );
    }
    
    return bars;
  };

  return (
    <div className={className} style={containerStyle}>
      <div style={waveformStyle}>
        {renderWaveformBars()}
      </div>
    </div>
  );
};

export default React.memo(GlassWaveformHUD);
