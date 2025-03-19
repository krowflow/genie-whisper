import React, { useEffect, useRef } from 'react';

interface WaveformVisualizerProps {
  isListening: boolean;
}

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({ isListening }) => {
  const waveformRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!waveformRef.current) return;
    
    const container = waveformRef.current;
    container.innerHTML = '';
    
    // Create bars for visualization
    const barCount = 32; // Number of bars
    const bars: HTMLDivElement[] = [];
    
    for (let i = 0; i < barCount; i++) {
      const bar = document.createElement('div');
      bar.className = 'waveform-bar';
      
      // Randomly assign cyan or pink color (with more cyan than pink)
      const isCyan = Math.random() > 0.2; // 80% chance of cyan
      bar.classList.add(isCyan ? 'bg-cyan-400' : 'bg-pink-400');
      
      // Set initial height
      const initialHeight = isListening 
        ? Math.random() * 40 + 5 // Random height when listening
        : 5; // Minimal height when not listening
      
      bar.style.height = `${initialHeight}px`;
      
      container.appendChild(bar);
      bars.push(bar);
    }
    
    // Animate bars if listening
    let animationFrame: number;
    
    const animate = () => {
      if (isListening) {
        bars.forEach(bar => {
          // Generate random heights for active visualization
          const height = Math.random() * 40 + 5; // Between 5px and 45px
          bar.style.height = `${height}px`;
          
          // Occasionally change color for some visual interest
          if (Math.random() < 0.05) { // 5% chance to change color
            const isCyan = bar.classList.contains('bg-cyan-400');
            if (isCyan) {
              bar.classList.remove('bg-cyan-400');
              bar.classList.add('bg-pink-400');
            } else {
              bar.classList.remove('bg-pink-400');
              bar.classList.add('bg-cyan-400');
            }
          }
        });
      } else {
        // Set all bars to minimal height when not listening
        bars.forEach(bar => {
          bar.style.height = '5px';
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
      className="h-24 rounded bg-transparent flex items-center justify-center space-x-1"
      aria-label="Audio waveform visualization"
    ></div>
  );
};

export default WaveformVisualizer;