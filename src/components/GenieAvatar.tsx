import React, { useEffect, useRef } from 'react';

interface GenieAvatarProps {
  isListening: boolean;
}

const GenieAvatar: React.FC<GenieAvatarProps> = ({ isListening }) => {
  const avatarRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // This is a placeholder for actual Genie animation
    // In a real implementation, we would use Lottie.js or Three.js for more advanced animations
    
    if (!avatarRef.current) return;
    
    // In a full implementation, we would load and play Lottie animations here
    // that would show the ethereal, smoky genie with glowing effects
    
  }, [isListening]);
  
  return (
    <div id="genie-avatar" className="flex justify-center mb-4">
      <div 
        ref={avatarRef}
        className={`w-32 h-32 rounded-full bg-indigo-900 flex items-center justify-center transition-all duration-300 ${
          isListening ? 'shadow-lg' : ''
        }`}
        style={{
          boxShadow: isListening ? '0 0 15px 5px rgba(6, 182, 212, 0.5)' : 'none'
        }}
      >
        {/* Glow effect container */}
        <div className={`absolute w-full h-full rounded-full ${
          isListening ? 'opacity-70' : 'opacity-0'
        } transition-opacity duration-500`}
        style={{
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, rgba(6, 182, 212, 0) 70%)'
        }}></div>
        
        {/* Genie smoke silhouette SVG */}
        <div className="relative w-24 h-24 flex items-center justify-center">
          <svg 
            viewBox="0 0 100 100" 
            className="w-full h-full z-10"
            style={{
              filter: `drop-shadow(0 0 5px rgba(6, 182, 212, ${isListening ? '0.8' : '0.4'}))`,
              transition: 'all 0.3s ease-in-out',
              transform: isListening ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            {/* Genie smoke silhouette */}
            <path
              d="M50,80 C60,80 65,75 65,65 C65,55 60,50 65,40 C70,30 65,20 55,15 C45,10 40,15 35,10 C30,5 20,10 15,20 C10,30 15,40 20,45 C25,50 30,55 25,65 C20,75 30,80 40,80 L50,80 Z"
              fill="url(#genieGradient)"
              opacity="0.9"
            />
            
            {/* Small wisp 1 */}
            <path
              d="M40,15 C45,10 50,15 45,20 C40,25 35,20 40,15 Z"
              fill="url(#genieGradient)"
              opacity="0.7"
            />
            
            {/* Small wisp 2 */}
            <path
              d="M60,25 C65,20 70,25 65,30 C60,35 55,30 60,25 Z"
              fill="url(#genieGradient)"
              opacity="0.7"
            />
            
            {/* Gradient definition */}
            <defs>
              <linearGradient id="genieGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#0ea5e9" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#2563eb" stopOpacity="0.4" />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Animated smoke/mist effect when listening */}
          {isListening && (
            <div className="absolute inset-0 z-0 overflow-hidden">
              <div className="smoke-1"></div>
              <div className="smoke-2"></div>
              <div className="smoke-3"></div>
            </div>
          )}
        </div>
        
        {/* Microphone icon when not listening */}
        {!isListening && (
          <div className="absolute inset-0 flex items-center justify-center">
            <svg 
              width="40" 
              height="40" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
              className="text-cyan-400"
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
      
      {/* Add CSS for smoke animations */}
      <style>
        {`
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
        
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-5px); }
          100% { transform: translateY(0px); }
        }
        
        .smoke-1, .smoke-2, .smoke-3 {
          position: absolute;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background-color: rgba(6, 182, 212, 0.3);
          bottom: 0;
          filter: blur(7px);
        }
        
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
        `}
      </style>
    </div>
  );
};

export default GenieAvatar;