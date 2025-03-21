import React, { useEffect, useRef, useState } from 'react';

interface GenieAvatarProps {
  isListening: boolean;
}

const GenieAvatar: React.FC<GenieAvatarProps> = ({ isListening }) => {
  const avatarRef = useRef<HTMLDivElement>(null);
  const [pulseIntensity, setPulseIntensity] = useState(0);
  
  // Enhanced animation effects
  useEffect(() => {
    if (!avatarRef.current) return;
    
    // Pulse effect when listening
    let pulseInterval: number;
    if (isListening) {
      pulseInterval = window.setInterval(() => {
        setPulseIntensity((prev) => (prev + 1) % 100);
      }, 50);
    }
    
    return () => {
      if (pulseInterval) clearInterval(pulseInterval);
    };
  }, [isListening]);
  
  // Calculate dynamic glow based on pulse intensity
  const getGlowIntensity = () => {
    if (!isListening) return 0;
    // Convert pulse to a sine wave for smooth pulsing
    return 0.5 + Math.sin(pulseIntensity / 15) * 0.2;
  };
  
  return (
    <div id="genie-avatar" className="flex justify-center mb-4">
      <div
        ref={avatarRef}
        className={`w-32 h-32 rounded-full bg-indigo-900 flex items-center justify-center transition-all duration-300 ${
          isListening ? 'shadow-lg' : ''
        }`}
        style={{
          boxShadow: isListening
            ? `0 0 ${15 + pulseIntensity % 10}px ${5 + pulseIntensity % 5}px rgba(6, 182, 212, ${getGlowIntensity()})`
            : 'none'
        }}
      >
        {/* Enhanced glow effect container with dynamic intensity */}
        <div className={`absolute w-full h-full rounded-full ${
          isListening ? 'opacity-70' : 'opacity-0'
        } transition-opacity duration-500`}
        style={{
          background: `radial-gradient(circle, rgba(6, 182, 212, ${getGlowIntensity()}) 0%, rgba(6, 182, 212, 0) 70%)`,
          transform: isListening ? `scale(${1 + Math.sin(pulseIntensity / 20) * 0.05})` : 'scale(1)'
        }}></div>
        
        {/* Genie Image */}
        <div className="relative w-24 h-24 flex items-center justify-center">
          {/* Genie image with enhanced animations */}
          <div className="w-full h-full z-10 flex items-center justify-center">
            <img
              src="../images/Genie.png"
              alt="Genie"
              className={`w-20 h-20 object-contain transition-all duration-300 ${
                isListening ? 'opacity-90 scale-110' : 'opacity-70'
              }`}
              style={{
                animation: isListening ? 'float 3s ease-in-out infinite' : 'none',
                filter: `drop-shadow(0 0 ${5 + pulseIntensity % 5}px rgba(6, 182, 212, ${getGlowIntensity() + 0.2}))`,
                transform: isListening
                  ? `rotate(${Math.sin(pulseIntensity / 50) * 3}deg)`
                  : 'rotate(0deg)'
              }}
            />
          </div>
          
          {/* Enhanced smoke/mist effect when listening */}
          {isListening && (
            <div className="absolute inset-0 z-0 overflow-hidden">
              {/* More smoke particles for a richer effect */}
              <div className="smoke-1"></div>
              <div className="smoke-2"></div>
              <div className="smoke-3"></div>
              <div className="smoke-4"></div>
              <div className="smoke-5"></div>
              <div className="smoke-6"></div>
              <div className="smoke-7"></div>
              <div className="smoke-8"></div>
              
              {/* Magical sparkle effects */}
              <div className="sparkle-1"></div>
              <div className="sparkle-2"></div>
              <div className="sparkle-3"></div>
            </div>
          )}
        </div>
        
        {/* Microphone icon when not listening - with subtle hover effect */}
        {!isListening && (
          <div className="absolute inset-0 flex items-center justify-center mic-icon-container">
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="text-cyan-400 mic-icon"
            >
              <path
                d="M12 15.5C14.21 15.5 16 13.71 16 11.5V6C16 3.79 14.21 2 12 2C9.79 2 8 3.79 8 6V11.5C8 13.71 9.79 15.5 12 15.5Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M4.34998 9.64999V11.35C4.34998 15.57 7.77998 19 12 19C16.22 19 19.65 15.57 19.65 11.35V9.64999"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M12 19V22"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )}
      </div>
      
      {/* Enhanced CSS for smoke animations and other effects */}
      <style>
        {`
        /* Enhanced floating animation */
        @keyframes float {
          0% { transform: translateY(0px) rotate(0deg); }
          25% { transform: translateY(-3px) rotate(1deg); }
          50% { transform: translateY(-5px) rotate(0deg); }
          75% { transform: translateY(-2px) rotate(-1deg); }
          100% { transform: translateY(0px) rotate(0deg); }
        }
        
        /* Enhanced smoke animations with more variety */
        @keyframes smoke-1 {
          0% { transform: translateY(10px) scale(0.5); opacity: 0; }
          25% { opacity: 0.5; }
          50% { transform: translateY(-15px) translateX(5px) scale(0.8); opacity: 0.8; }
          100% { transform: translateY(-30px) translateX(-5px) scale(1.2); opacity: 0; }
        }
        
        @keyframes smoke-2 {
          0% { transform: translateY(5px) scale(0.5); opacity: 0; }
          25% { opacity: 0.7; }
          50% { transform: translateY(-20px) translateX(-7px) scale(0.9); opacity: 0.6; }
          100% { transform: translateY(-40px) translateX(5px) scale(1.3); opacity: 0; }
        }
        
        @keyframes smoke-3 {
          0% { transform: translateY(10px) scale(0.5); opacity: 0; }
          25% { opacity: 0.3; }
          50% { transform: translateY(-15px) translateX(10px) scale(1); opacity: 0.5; }
          100% { transform: translateY(-35px) translateX(-10px) scale(1.5); opacity: 0; }
        }
        
        @keyframes smoke-4 {
          0% { transform: translateY(8px) scale(0.4); opacity: 0; }
          20% { opacity: 0.4; }
          60% { transform: translateY(-25px) translateX(-12px) scale(1.1); opacity: 0.6; }
          100% { transform: translateY(-45px) translateX(8px) scale(1.4); opacity: 0; }
        }
        
        @keyframes smoke-5 {
          0% { transform: translateY(12px) scale(0.3); opacity: 0; }
          30% { opacity: 0.3; }
          55% { transform: translateY(-18px) translateX(15px) scale(0.9); opacity: 0.4; }
          100% { transform: translateY(-38px) translateX(-15px) scale(1.6); opacity: 0; }
        }
        
        @keyframes smoke-6 {
          0% { transform: translateY(7px) translateX(-5px) scale(0.4); opacity: 0; }
          20% { opacity: 0.2; }
          70% { transform: translateY(-22px) translateX(8px) scale(1.2); opacity: 0.5; }
          100% { transform: translateY(-42px) translateX(-3px) scale(1.5); opacity: 0; }
        }
        
        @keyframes smoke-7 {
          0% { transform: translateY(9px) translateX(5px) scale(0.3); opacity: 0; }
          15% { opacity: 0.3; }
          65% { transform: translateY(-28px) translateX(-10px) scale(1.0); opacity: 0.4; }
          100% { transform: translateY(-48px) translateX(12px) scale(1.7); opacity: 0; }
        }
        
        @keyframes smoke-8 {
          0% { transform: translateY(11px) translateX(-8px) scale(0.5); opacity: 0; }
          25% { opacity: 0.4; }
          60% { transform: translateY(-20px) translateX(13px) scale(0.8); opacity: 0.7; }
          100% { transform: translateY(-40px) translateX(-7px) scale(1.3); opacity: 0; }
        }
        
        /* Sparkle animations */
        @keyframes sparkle {
          0% { transform: scale(0); opacity: 0; }
          20% { transform: scale(1); opacity: 1; }
          80% { transform: scale(1); opacity: 1; }
          100% { transform: scale(0); opacity: 0; }
        }
        
        /* Base smoke style with enhanced blur and colors */
        .smoke-1, .smoke-2, .smoke-3, .smoke-4, .smoke-5, .smoke-6, .smoke-7, .smoke-8 {
          position: absolute;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          bottom: 0;
          filter: blur(7px);
        }
        
        /* Different colors for smoke particles */
        .smoke-1, .smoke-5 {
          background-color: rgba(6, 182, 212, 0.3); /* Cyan */
        }
        
        .smoke-2, .smoke-6 {
          background-color: rgba(139, 92, 246, 0.3); /* Purple */
        }
        
        .smoke-3, .smoke-7 {
          background-color: rgba(14, 165, 233, 0.3); /* Sky blue */
        }
        
        .smoke-4, .smoke-8 {
          background-color: rgba(232, 121, 249, 0.3); /* Pink */
        }
        
        /* Positioning and animations for each smoke particle */
        .smoke-1 {
          left: 30%;
          animation: smoke-1 3s infinite;
        }
        
        .smoke-2 {
          left: 50%;
          animation: smoke-2 4s infinite 1s;
        }
        
        .smoke-3 {
          left: 60%;
          animation: smoke-3 3.5s infinite 0.5s;
        }
        
        .smoke-4 {
          left: 40%;
          animation: smoke-4 4.5s infinite 0.7s;
        }
        
        .smoke-5 {
          left: 25%;
          animation: smoke-5 3.8s infinite 1.2s;
        }
        
        .smoke-6 {
          left: 55%;
          animation: smoke-6 4.2s infinite 0.3s;
        }
        
        .smoke-7 {
          left: 35%;
          animation: smoke-7 3.7s infinite 1.5s;
        }
        
        .smoke-8 {
          left: 65%;
          animation: smoke-8 4.7s infinite 0.8s;
        }
        
        /* Sparkle styles */
        .sparkle-1, .sparkle-2, .sparkle-3 {
          position: absolute;
          width: 6px;
          height: 6px;
          background-color: white;
          border-radius: 50%;
          filter: blur(1px);
          box-shadow: 0 0 5px 2px rgba(255, 255, 255, 0.8);
        }
        
        .sparkle-1 {
          top: 30%;
          left: 40%;
          animation: sparkle 2s infinite 0.5s;
        }
        
        .sparkle-2 {
          top: 50%;
          left: 60%;
          animation: sparkle 2.5s infinite 1.2s;
        }
        
        .sparkle-3 {
          top: 20%;
          left: 50%;
          animation: sparkle 1.8s infinite 0.8s;
        }
        
        /* Microphone icon hover effect */
        .mic-icon-container {
          transition: all 0.3s ease;
        }
        
        .mic-icon-container:hover .mic-icon {
          transform: scale(1.1);
          filter: drop-shadow(0 0 5px rgba(6, 182, 212, 0.8));
        }
        
        .mic-icon {
          transition: all 0.3s ease;
        }
        `}
      </style>
    </div>
  );
};

export default GenieAvatar;