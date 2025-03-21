import React, { useEffect, useRef, useState } from 'react';

interface WaveformVisualizerProps {
  isListening: boolean;
}

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({ isListening }) => {
  const waveformRef = useRef<HTMLDivElement>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  
  // Simulate audio input levels with a more natural pattern
  useEffect(() => {
    if (!isListening) return;
    
    // Simulate audio input with a more natural pattern
    let lastValue = 0.5;
    const audioSimInterval = setInterval(() => {
      // Use a combination of the previous value and random noise for more natural movement
      // This creates a smoother transition between values (like real audio)
      const noise = Math.random() * 0.3 - 0.15; // Random value between -0.15 and 0.15
      lastValue = Math.max(0.1, Math.min(1, lastValue + noise)); // Keep between 0.1 and 1
      
      // Occasionally add "speech peaks" for more realistic visualization
      if (Math.random() < 0.1) { // 10% chance of a peak
        lastValue = Math.min(1, lastValue + Math.random() * 0.4);
      }
      
      setAudioLevel(lastValue);
    }, 50); // Update every 50ms for smooth animation
    
    return () => clearInterval(audioSimInterval);
  }, [isListening]);
  
  useEffect(() => {
    if (!waveformRef.current) return;
    
    const container = waveformRef.current;
    container.innerHTML = '';
    
    // Create bars for visualization with improved aesthetics
    const barCount = 64; // More bars for smoother visualization
    const bars: HTMLDivElement[] = [];
    
    // Create a container for the reflection effect
    const visualizerContainer = document.createElement('div');
    visualizerContainer.className = 'visualizer-container';
    container.appendChild(visualizerContainer);
    
    // Create the actual bars
    const barsContainer = document.createElement('div');
    barsContainer.className = 'bars-container';
    visualizerContainer.appendChild(barsContainer);
    
    // Create the reflection container
    const reflectionContainer = document.createElement('div');
    reflectionContainer.className = 'reflection-container';
    visualizerContainer.appendChild(reflectionContainer);
    
    // Create bars with improved aesthetics
    for (let i = 0; i < barCount; i++) {
      // Main bar
      const bar = document.createElement('div');
      bar.className = 'waveform-bar';
      
      // Create a more interesting color pattern based on position
      // Center bars are more cyan, outer bars more purple/pink
      const centerDistance = Math.abs(i - barCount / 2) / (barCount / 2); // 0 at center, 1 at edges
      const hue = 180 - centerDistance * 60; // 180 is cyan, 120 is more blue-green
      const saturation = 80 + centerDistance * 20; // Higher saturation at edges
      const lightness = 60 - centerDistance * 10; // Brighter in center
      
      bar.style.backgroundColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
      
      // Set initial height with a pleasing curve (higher in middle)
      const positionFactor = 1 - Math.pow(2 * (i / barCount - 0.5), 2); // Parabolic curve, 1 in middle, 0 at edges
      const initialHeight = isListening
        ? (5 + positionFactor * 20 + Math.random() * 10) // Base height + position curve + randomness
        : (3 + positionFactor * 4); // Small curve when not listening
      
      bar.style.height = `${initialHeight}px`;
      
      // Add subtle transparency
      bar.style.opacity = `${0.7 + positionFactor * 0.3}`;
      
      barsContainer.appendChild(bar);
      bars.push(bar);
      
      // Reflection bar (mirror of the main bar)
      const reflectionBar = document.createElement('div');
      reflectionBar.className = 'waveform-bar reflection';
      reflectionBar.style.backgroundColor = bar.style.backgroundColor;
      reflectionBar.style.height = `${initialHeight * 0.4}px`; // Reflection is shorter
      reflectionBar.style.opacity = `${0.3}`; // Reflection is more transparent
      
      reflectionContainer.appendChild(reflectionBar);
    }
    
    // Animate bars with improved physics
    let animationFrame: number;
    let velocities = bars.map(() => 0); // Initial velocities for smoother animation
    
    const animate = () => {
      if (isListening) {
        // Create a "sound wave" pattern that moves from center to edges
        const centerIndex = bars.length / 2;
        const time = Date.now() / 1000; // Current time in seconds for wave animation
        
        bars.forEach((bar, i) => {
          // Calculate target height based on position and audio level
          const positionFactor = 1 - Math.pow(2 * (i / bars.length - 0.5), 2); // Parabolic curve
          
          // Add wave pattern
          const distFromCenter = Math.abs(i - centerIndex);
          const wavePhase = time * 3 - distFromCenter * 0.2; // Wave moves outward from center
          const waveFactor = Math.sin(wavePhase) * 0.3 + 0.7; // Wave oscillates between 0.4 and 1.0
          
          // Calculate target height with multiple factors
          const targetHeight = 5 + (audioLevel * 50 * positionFactor * waveFactor);
          
          // Apply physics for smoother animation (spring physics)
          const currentHeight = parseFloat(bar.style.height);
          const spring = 0.2; // Spring constant (higher = faster reaction)
          const damping = 0.7; // Damping factor (higher = less oscillation)
          
          // Calculate acceleration using spring physics formula
          const acceleration = spring * (targetHeight - currentHeight) - damping * velocities[i];
          velocities[i] += acceleration;
          
          // Update height based on velocity
          const newHeight = currentHeight + velocities[i];
          bar.style.height = `${newHeight}px`;
          
          // Update reflection (mirror of the main bar)
          const reflectionBar = reflectionContainer.children[i] as HTMLDivElement;
          reflectionBar.style.height = `${newHeight * 0.4}px`;
          
          // Subtle color shifts based on height
          const intensity = newHeight / 60; // Normalize height to 0-1 range
          const distanceFromCenter = Math.abs(i - centerIndex) / centerIndex; // Normalized distance from center
          const hue = 180 - distanceFromCenter * 60 - intensity * 20; // Shift hue based on intensity
          const saturation = 80 + distanceFromCenter * 20 + intensity * 10;
          const lightness = 60 - distanceFromCenter * 10 + intensity * 5;
          
          bar.style.backgroundColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
          reflectionBar.style.backgroundColor = bar.style.backgroundColor;
        });
      } else {
        // Animate to idle state with smooth transitions
        bars.forEach((bar, i) => {
          // Calculate target idle height (small curve)
          const positionFactor = 1 - Math.pow(2 * (i / bars.length - 0.5), 2);
          const targetHeight = 3 + positionFactor * 4;
          
          // Apply physics for smooth transition
          const currentHeight = parseFloat(bar.style.height);
          const spring = 0.1; // Slower spring for smoother idle transition
          const damping = 0.9; // Higher damping for less oscillation
          
          const acceleration = spring * (targetHeight - currentHeight) - damping * velocities[i];
          velocities[i] += acceleration;
          
          // Update height based on velocity
          const newHeight = currentHeight + velocities[i];
          bar.style.height = `${newHeight}px`;
          
          // Update reflection
          const reflectionBar = reflectionContainer.children[i] as HTMLDivElement;
          reflectionBar.style.height = `${newHeight * 0.4}px`;
          
          // Reset color to default
          const centerDistance = Math.abs(i - bars.length / 2) / (bars.length / 2);
          const hue = 180 - centerDistance * 60;
          const saturation = 80 + centerDistance * 20;
          const lightness = 60 - centerDistance * 10;
          
          bar.style.backgroundColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
          reflectionBar.style.backgroundColor = bar.style.backgroundColor;
        });
      }
      
      animationFrame = requestAnimationFrame(animate);
    };
    
    animate();
    
    // Clean up animation on unmount
    return () => {
      cancelAnimationFrame(animationFrame);
    };
  }, [isListening]);
  
  return (
    <div
      ref={waveformRef}
      className="h-32 rounded bg-transparent flex items-center justify-center"
      aria-label="Audio waveform visualization"
    >
      <style>
        {`
        .visualizer-container {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 0 10px;
        }
        
        .bars-container {
          display: flex;
          align-items: flex-end;
          justify-content: center;
          height: 50%;
          width: 100%;
          gap: 2px;
        }
        
        .reflection-container {
          display: flex;
          align-items: flex-start;
          justify-content: center;
          height: 50%;
          width: 100%;
          gap: 2px;
          transform: scaleY(-1);
          opacity: 0.3;
          filter: blur(1px);
        }
        
        .waveform-bar {
          flex: 1;
          max-width: 4px;
          min-height: 3px;
          border-radius: 2px;
          transition: background-color 0.2s ease;
        }
        
        .waveform-bar.reflection {
          opacity: 0.5;
        }
        `}
      </style>
    </div>
  );
};

export default WaveformVisualizer;