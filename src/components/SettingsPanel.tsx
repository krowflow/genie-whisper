import React, { useState, useEffect } from 'react';

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

interface SettingsPanelProps {
  settings: Settings;
  onSave: (settings: Settings) => void;
  onClose: () => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ settings, onSave, onClose }) => {
  const [localSettings, setLocalSettings] = useState<Settings>({ ...settings });
  const [sensitivityValue, setSensitivityValue] = useState<string>(settings.sensitivity.toString());
  
  // Update local settings when props change
  useEffect(() => {
    setLocalSettings({ ...settings });
    setSensitivityValue(settings.sensitivity.toString());
  }, [settings]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setLocalSettings(prev => ({ ...prev, [name]: checked }));
    } else if (name === 'sensitivity') {
      const numValue = parseFloat(value);
      setSensitivityValue(value);
      setLocalSettings(prev => ({ ...prev, [name]: numValue }));
    } else {
      setLocalSettings(prev => ({ ...prev, [name]: value }));
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(localSettings);
  };
  
  const handleReset = () => {
    setLocalSettings({ ...settings });
    setSensitivityValue(settings.sensitivity.toString());
  };
  
  return (
    <div className="absolute inset-0 bg-indigo-900 bg-opacity-95 p-4 flex flex-col z-50 animate-fadeIn">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-medium text-white">Settings</h2>
        <button 
          onClick={onClose}
          className="text-gray-400 hover:text-white"
          title="Close Settings"
          aria-label="Close Settings"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
          </svg>
        </button>
      </div>
      
      <div className="flex-grow overflow-y-auto">
        <form id="settings-form" onSubmit={handleSubmit}>
          {/* General Settings */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-cyan-300 mb-3 border-b border-indigo-700 pb-1">
              General Settings
            </h3>
            
            <div className="mb-3">
              <label className="flex items-center text-white">
                <input 
                  type="checkbox" 
                  name="alwaysOnTop" 
                  checked={localSettings.alwaysOnTop}
                  onChange={handleChange}
                  className="mr-2 bg-indigo-700 border-indigo-600 text-cyan-400 focus:ring-cyan-400"
                />
                Always on top
              </label>
            </div>
            
            <div className="mb-3">
              <label className="flex items-center text-white">
                <input 
                  type="checkbox" 
                  name="startMinimized" 
                  checked={localSettings.startMinimized}
                  onChange={handleChange}
                  className="mr-2 bg-indigo-700 border-indigo-600 text-cyan-400 focus:ring-cyan-400"
                />
                Start minimized
              </label>
            </div>
            
            <div className="mb-3">
              <label className="flex items-center text-white">
                <input 
                  type="checkbox" 
                  name="startWithSystem" 
                  checked={localSettings.startWithSystem}
                  onChange={handleChange}
                  className="mr-2 bg-indigo-700 border-indigo-600 text-cyan-400 focus:ring-cyan-400"
                />
                Start with system
              </label>
            </div>
            
            <div className="mb-3">
              <label htmlFor="theme" className="block mb-1 text-sm text-white">Theme</label>
              <select 
                name="theme" 
                id="theme" 
                value={localSettings.theme}
                onChange={handleChange}
                className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                aria-label="Select theme"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="system">System</option>
              </select>
            </div>
          </div>
          
          {/* Transcription Settings */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-cyan-300 mb-3 border-b border-indigo-700 pb-1">
              Transcription Settings
            </h3>
            
            <div className="mb-3">
              <label htmlFor="modelSize" className="block mb-1 text-sm text-white">Model Size</label>
              <select 
                name="modelSize" 
                id="modelSize" 
                value={localSettings.modelSize}
                onChange={handleChange}
                className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                aria-label="Select model size"
              >
                <option value="tiny">Tiny (Fast, Less Accurate)</option>
                <option value="base">Base (Balanced)</option>
                <option value="small">Small (More Accurate)</option>
                <option value="medium">Medium (Most Accurate, Slower)</option>
              </select>
            </div>
            
            <div className="mb-3">
              <label htmlFor="sensitivity" className="block mb-1 text-sm text-white">
                Sensitivity: <span className="text-cyan-400">{sensitivityValue}</span>
              </label>
              <input 
                type="range" 
                name="sensitivity" 
                id="sensitivity" 
                min="0" 
                max="1" 
                step="0.1" 
                value={sensitivityValue}
                onChange={handleChange}
                className="w-full"
                aria-label="Adjust sensitivity"
              />
            </div>
            
            <div className="mb-3">
              <label className="flex items-center text-white">
                <input 
                  type="checkbox" 
                  name="useVAD" 
                  id="useVAD" 
                  checked={localSettings.useVAD}
                  onChange={handleChange}
                  className="mr-2 bg-indigo-700 border-indigo-600 text-cyan-400 focus:ring-cyan-400"
                />
                Use Voice Activity Detection
              </label>
            </div>
            
            <div className="mb-3">
              <label className="flex items-center text-white">
                <input 
                  type="checkbox" 
                  name="offlineMode" 
                  id="offlineMode" 
                  checked={localSettings.offlineMode}
                  onChange={handleChange}
                  className="mr-2 bg-indigo-700 border-indigo-600 text-cyan-400 focus:ring-cyan-400"
                />
                Offline Mode
              </label>
            </div>
          </div>
          
          {/* Activation Settings */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-cyan-300 mb-3 border-b border-indigo-700 pb-1">
              Activation Settings
            </h3>
            
            <div className="mb-3">
              <label htmlFor="hotkey" className="block mb-1 text-sm text-white">Hotkey</label>
              <input 
                type="text" 
                name="hotkey" 
                id="hotkey" 
                placeholder="Ctrl+Shift+Space" 
                value={localSettings.hotkey}
                onChange={handleChange}
                className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
              />
            </div>
            
            <div className="mb-3">
              <label htmlFor="wakeWord" className="block mb-1 text-sm text-white">Wake Word</label>
              <input 
                type="text" 
                name="wakeWord" 
                id="wakeWord" 
                placeholder="Hey Genie" 
                value={localSettings.wakeWord}
                onChange={handleChange}
                className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
              />
            </div>
          </div>
        </form>
      </div>
      
      <div className="flex justify-end space-x-2 mt-4">
        <button 
          type="button"
          onClick={handleReset}
          className="bg-indigo-700 hover:bg-indigo-600 text-white font-medium py-1 px-3 rounded"
        >
          Reset
        </button>
        <button 
          type="submit"
          onClick={handleSubmit}
          className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-1 px-3 rounded"
        >
          Save
        </button>
      </div>
      
      <style>
        {`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.3s ease;
        }
        
        /* Custom styling for range input */
        input[type="range"] {
          -webkit-appearance: none;
          height: 8px;
          background: #4338ca;
          border-radius: 4px;
          outline: none;
        }
        
        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #22d3ee;
          cursor: pointer;
          transition: background 0.2s ease;
        }
        
        input[type="range"]::-webkit-slider-thumb:hover {
          background: #06b6d4;
        }
        
        /* Custom styling for checkbox */
        input[type="checkbox"] {
          -webkit-appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 4px;
          background: #4338ca;
          border: 1px solid #4f46e5;
          position: relative;
          cursor: pointer;
        }
        
        input[type="checkbox"]:checked {
          background: #22d3ee;
          border-color: #22d3ee;
        }
        
        input[type="checkbox"]:checked::after {
          content: '';
          position: absolute;
          width: 4px;
          height: 8px;
          border: solid white;
          border-width: 0 2px 2px 0;
          top: 2px;
          left: 6px;
          transform: rotate(45deg);
        }
        `}
      </style>
    </div>
  );
};

export default SettingsPanel;