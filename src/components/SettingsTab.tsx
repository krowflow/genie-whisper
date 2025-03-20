import React from 'react';
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
  activationMode: 'manual' | 'wake_word' | 'always_on';
  ide: string;
  deviceId?: number;
  useGPU: boolean;
  computeType: 'auto' | 'int8' | 'float16' | 'float32';
}

interface SettingsTabProps {
  settings: Settings;
  onSave: (settings: Settings) => void;
}

const SettingsTab: React.FC<SettingsTabProps> = ({ settings, onSave }) => {
  return (
    <div className="flex-grow overflow-y-auto">
      <SettingsPanel 
        settings={settings} 
        onSave={onSave} 
        onClose={() => {}} // No need to close in tab mode
        embedded={true} // New prop to indicate embedded in tab
      />
    </div>
  );
};

export default SettingsTab;