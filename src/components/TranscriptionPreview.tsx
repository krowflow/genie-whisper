import React, { useEffect, useRef, useState } from 'react';

interface TranscriptionPreviewProps {
  text: string;
  isListening: boolean;
}

const TranscriptionPreview: React.FC<TranscriptionPreviewProps> = ({ text, isListening }) => {
  const previewRef = useRef<HTMLDivElement>(null);
  const [fadeIn, setFadeIn] = useState(false);
  const [highlightedText, setHighlightedText] = useState('');
  
  // Auto-scroll to bottom when text changes
  useEffect(() => {
    if (previewRef.current) {
      previewRef.current.scrollTop = previewRef.current.scrollHeight;
    }
    
    // Add fade-in effect for new text
    if (text !== highlightedText) {
      setFadeIn(true);
      setHighlightedText(text);
      
      // Reset fade-in after animation completes
      const timer = setTimeout(() => {
        setFadeIn(false);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [text, highlightedText]);
  
  // Format text with smart highlighting for better readability
  const formatText = (inputText: string) => {
    if (!inputText) return null;
    
    // Split text into sentences for better highlighting
    const sentences = inputText.split(/(?<=[.!?])\s+/);
    
    return (
      <>
        {sentences.map((sentence, index) => (
          <span
            key={index}
            className={`sentence ${index === sentences.length - 1 && fadeIn ? 'highlight-new' : ''}`}
          >
            {sentence}
            {index < sentences.length - 1 ? ' ' : ''}
          </span>
        ))}
      </>
    );
  };
  
  // Determine status message based on listening state
  const getStatusMessage = () => {
    if (isListening) {
      return (
        <div className="status-listening">
          <span className="status-dot"></span>
          <span className="status-dot"></span>
          <span className="status-dot"></span>
          <span className="ml-2">Listening for speech...</span>
        </div>
      );
    } else {
      return "Transcription will appear here...";
    }
  };
  
  return (
    <div
      ref={previewRef}
      className={`transcription-preview bg-indigo-900 bg-opacity-50 rounded p-3 mb-4 h-32 overflow-y-auto transition-all duration-300 ${
        isListening ? 'border-l-4 border-cyan-400 shadow-glow' : ''
      }`}
      aria-live="polite"
      aria-label="Transcription preview"
    >
      {text ? (
        <p className="text-white transcription-text">
          {formatText(text)}
          
          {/* Typing cursor effect when listening */}
          {isListening && (
            <span className="typing-cursor">|</span>
          )}
        </p>
      ) : (
        <p className="text-gray-400 italic status-message">
          {getStatusMessage()}
        </p>
      )}
      
      <style>
        {`
        .transcription-preview {
          position: relative;
          backdrop-filter: blur(4px);
          transition: all 0.3s ease;
        }
        
        .shadow-glow {
          box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }
        
        .transcription-text {
          line-height: 1.5;
          transition: opacity 0.2s ease;
        }
        
        .highlight-new {
          animation: highlight-fade 2s ease;
        }
        
        @keyframes highlight-fade {
          0% { background-color: rgba(6, 182, 212, 0.3); }
          100% { background-color: transparent; }
        }
        
        .typing-cursor {
          display: inline-block;
          width: 2px;
          height: 1.2em;
          background-color: #22d3ee;
          margin-left: 2px;
          vertical-align: middle;
          animation: blink 1s step-end infinite;
        }
        
        @keyframes blink {
          from, to { opacity: 1; }
          50% { opacity: 0; }
        }
        
        .status-message {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
        }
        
        .status-listening {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .status-dot {
          display: inline-block;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background-color: #22d3ee;
          margin: 0 2px;
        }
        
        .status-dot:nth-child(1) {
          animation: pulse 1.5s infinite 0s;
        }
        
        .status-dot:nth-child(2) {
          animation: pulse 1.5s infinite 0.3s;
        }
        
        .status-dot:nth-child(3) {
          animation: pulse 1.5s infinite 0.6s;
        }
        
        @keyframes pulse {
          0% { transform: scale(0.8); opacity: 0.5; }
          50% { transform: scale(1.2); opacity: 1; }
          100% { transform: scale(0.8); opacity: 0.5; }
        }
        
        .sentence {
          transition: background-color 1s ease;
          border-radius: 2px;
          padding: 0 2px;
        }
        `}
      </style>
    </div>
  );
};

export default TranscriptionPreview;