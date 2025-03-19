import React, { useEffect, useRef } from 'react';

interface TranscriptionPreviewProps {
  text: string;
  isListening: boolean;
}

const TranscriptionPreview: React.FC<TranscriptionPreviewProps> = ({ text, isListening }) => {
  const previewRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when text changes
  useEffect(() => {
    if (previewRef.current) {
      previewRef.current.scrollTop = previewRef.current.scrollHeight;
    }
  }, [text]);
  
  return (
    <div 
      ref={previewRef}
      className={`bg-indigo-900 bg-opacity-50 rounded p-3 mb-4 h-32 overflow-y-auto transition-all duration-300 ${
        isListening ? 'border-l-4 border-cyan-400' : ''
      }`}
      aria-live="polite"
      aria-label="Transcription preview"
    >
      {text ? (
        <p className="text-white">{text}</p>
      ) : (
        <p className="text-gray-400 italic">
          {isListening ? 'Listening for speech...' : 'Transcription will appear here...'}
        </p>
      )}
      
      {/* Typing cursor effect when listening */}
      {isListening && text && (
        <span className="typing-cursor">|</span>
      )}
      
      <style>
        {`
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
        `}
      </style>
    </div>
  );
};

export default TranscriptionPreview;