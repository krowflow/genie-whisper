import React, { useState, useEffect } from 'react';
import WaveformVisualizer from './WaveformVisualizer';
import GenieAvatar from './GenieAvatar';
import TranscriptionPreview from './TranscriptionPreview';
import SettingsPanel from './SettingsPanel';

interface Settings {
  hotkey: string;
  wakeWord: string;
  alwaysOnTop: boolean;
  startMinimized: boolean;
  startWithSystem: boolean;
  theme: 'dark' | 'light' | 'system';
  modelSize: 'tiny' | 'base' | 'small' | 'medium' | 'large';
  sensitivity: number;
  useVAD: boolean;
  offlineMode: boolean;
}

const defaultSettings: Settings = {
  hotkey: 'CommandOrControl+Shift+Space',
  wakeWord: 'Hey Genie',
  alwaysOnTop: true,
  startMinimized: false,
  startWithSystem: true,
  theme: 'dark',
  modelSize: 'base',
  sensitivity: 0.5,
  useVAD: true,
  offlineMode: true,
};

const App: React.FC = () => {
  const [isListening, setIsListening] = useState<boolean>(false);
  const [transcription, setTranscription] = useState<string>('');
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showTranscription, setShowTranscription] = useState<boolean>(false);
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [status, setStatus] = useState<string>('Ready');

  useEffect(() => {
    // Load settings from Electron store
    if (window.api) {
      const storedSettings = window.api.sendSync('get-settings');
      if (storedSettings) {
        setSettings(storedSettings);
      }
    }

    // Set up event listeners for messages from main process
    if (window.api) {
      window.api.receive('start-listening', () => {
        startListening();
      });

      window.api.receive('stop-listening', () => {
        stopListening();
      });

      window.api.receive('show-settings', () => {
        setShowSettings(true);
      });

      window.api.receive('python-message', handlePythonMessage);
    }

    // Clean up event listeners
    return () => {
      // Cleanup would go here if needed
    };
  }, []);

  const handlePythonMessage = (message: any) => {
    try {
      const data = JSON.parse(message);
      
      if (data.type === 'transcription') {
        setTranscription(data.text);
        if (data.text && !showTranscription) {
          setShowTranscription(true);
        }
      } else if (data.type === 'error') {
        handleError(data.error);
      } else if (data.type === 'status') {
        setStatus(data.status);
      }
    } catch (error) {
      console.error('Error parsing Python message:', error);
    }
  };

  const handleError = (error: string) => {
    console.error('Error:', error);
    setStatus(`Error: ${error}`);
    
    // Reset after a delay
    setTimeout(() => {
      setStatus('Ready');
    }, 5000);
  };

  const startListening = () => {
    setIsListening(true);
    setStatus('Listening...');
    
    // Send message to main process
    if (window.api) {
      window.api.send('start-listening');
    }
  };

  const stopListening = () => {
    setIsListening(false);
    setStatus('Ready');
    
    // Send message to main process
    if (window.api) {
      window.api.send('stop-listening');
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const saveSettings = (newSettings: Settings) => {
    setSettings(newSettings);
    
    // Send to main process
    if (window.api) {
      window.api.send('update-settings', newSettings);
    }
    
    setShowSettings(false);
    setStatus('Settings saved');
    
    setTimeout(() => {
      setStatus('Ready');
    }, 2000);
  };

  const minimizeWindow = () => {
    if (window.api) {
      window.api.send('minimize-window');
    }
  };

  const closeWindow = () => {
    if (window.api) {
      window.api.send('close-window');
    }
  };

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
    <div className="h-screen flex flex-col bg-indigo-950">
      {/* Draggable title bar */}
      <div className="bg-indigo-950 p-2 flex justify-between items-center draggable">
        <div className="flex items-center">
          <h1 className="text-sm font-medium text-gray-400">Genie Whisper</h1>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => setShowSettings(true)}
            className="text-gray-400 hover:text-cyan-400"
            title="Settings"
            aria-label="Settings"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
              <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"/>
            </svg>
          </button>
          <button 
            onClick={minimizeWindow}
            className="text-gray-400 hover:text-cyan-400"
            title="Minimize"
            aria-label="Minimize"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M14 8a1 1 0 0 1-1 1H3a1 1 0 0 1 0-2h10a1 1 0 0 1 1 1z"/>
            </svg>
          </button>
          <button 
            onClick={closeWindow}
            className="text-gray-400 hover:text-red-500"
            title="Close"
            aria-label="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
            </svg>
          </button>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-grow flex flex-col p-4">
        {/* App Title */}
        <div className="text-center mb-4">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 text-transparent bg-clip-text">
            Genie Whisper
          </h1>
          <p className="text-xs text-gray-400">Your Voice-to-Text Assistant</p>
        </div>
        
        {/* Transcription preview (only shown when there's transcription) */}
        {showTranscription && transcription && (
          <div className="w-full mb-4">
            <TranscriptionPreview text={transcription} isListening={isListening} />
          </div>
        )}
        
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
        
        {/* Status text (small and subtle) */}
        <div className="text-center text-xs text-gray-500 mt-4">
          <p>{status}</p>
        </div>
      </div>
      
      {/* Settings panel */}
      {showSettings && (
        <SettingsPanel 
          settings={settings} 
          onSave={saveSettings} 
          onClose={() => setShowSettings(false)} 
        />
      )}
    </div>
  );
};

export default App;