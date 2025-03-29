import React from 'react';
import GenieAvatar from './GenieAvatar';
import WaveformVisualizer from './WaveformVisualizer';
import TranscriptionPreview from './TranscriptionPreview';

interface MainTabProps {
  isListening: boolean;
  transcription: string;
  showTranscription: boolean;
  toggleListening: () => void;
}

const MainTab: React.FC<MainTabProps> = ({ 
  isListening, 
  transcription, 
  showTranscription,
  toggleListening 
}) => {
  // Microphone button component
  const MicrophoneButton = () => (
    <div 
      onClick={toggleListening}
      className="cursor-pointer flex items-center justify-center"
    >
      <div className={`w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center transition-all duration-300 ${
        isListening ? 'shadow-lg shadow-cyan-500/50' : ''
      }`}>
        <svg 
          width="32" 
          height="32" 
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
    </div>
  );

  return (
    <div className="flex-grow flex flex-col">
      {/* Transcription preview (always shown) */}
      <div className="w-full mb-4">
        <TranscriptionPreview text={transcription} isListening={isListening} />
      </div>
      
      {/* Main UI area with Genie on left, waveform in center, mic on right */}
      <div className="flex-grow flex flex-col justify-center">
        {/* Waveform with Genie and Mic on sides */}
        <div className="flex items-center justify-between w-full">
          {/* Genie Avatar on left */}
          <div className="w-1/4 flex justify-center" onClick={toggleListening}>
            <GenieAvatar isListening={isListening} />
          </div>
          
          {/* Waveform in center */}
          <div className="w-2/4">
            <WaveformVisualizer isListening={isListening} />
          </div>
          
          {/* Microphone button on right */}
          <div className="w-1/4 flex justify-center">
            <MicrophoneButton />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainTab;