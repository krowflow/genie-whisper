import React, { useState, useEffect } from 'react';

interface AudioDevice {
  id: number;
  name: string;
  channels: number;
  default: boolean;
  sample_rates?: number;
}

interface DevicesTabProps {
  selectedDeviceId?: number;
  onDeviceSelect: (deviceId: number) => void;
}

const DevicesTab: React.FC<DevicesTabProps> = ({ selectedDeviceId, onDeviceSelect }) => {
  const [audioDevices, setAudioDevices] = useState<AudioDevice[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // Load audio devices
  useEffect(() => {
    const loadAudioDevices = async () => {
      setIsLoading(true);
      
      try {
        // Request devices from backend
        if (window.api) {
          window.api.send('get-devices');
          
          // Set up listener for devices
          const handleDevices = (message: string) => {
            try {
              const data = JSON.parse(message);
              
              if (data.type === 'devices') {
                setAudioDevices(data.devices || []);
                setIsLoading(false);
              }
            } catch (error) {
              console.error('Error parsing devices message:', error);
              setIsLoading(false);
            }
          };
          
          // Add listener
          window.api.receive('python-message', handleDevices);
        }
      } catch (error) {
        console.error('Error loading audio devices:', error);
        setIsLoading(false);
      }
    };
    
    loadAudioDevices();
  }, []);
  
  return (
    <div className="flex-grow p-4">
      <h2 className="text-lg font-medium text-white mb-4">Audio Devices</h2>
      
      {isLoading ? (
        <p className="text-gray-400">Loading audio devices...</p>
      ) : (
        <div className="space-y-4">
          <div className="mb-4">
            <label htmlFor="deviceId" className="block mb-2 text-sm text-white">Select Audio Input Device</label>
            <select 
              id="deviceId" 
              value={selectedDeviceId !== undefined ? selectedDeviceId.toString() : ''}
              onChange={(e) => onDeviceSelect(parseInt(e.target.value, 10))}
              className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
            >
              <option value="">Default Device</option>
              {audioDevices.map(device => (
                <option key={device.id} value={device.id.toString()}>
                  {device.name} {device.default ? '(Default)' : ''}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mt-6">
            <h3 className="text-sm font-medium text-cyan-300 mb-2">Device Information</h3>
            <div className="bg-indigo-900 bg-opacity-50 rounded p-3">
              {audioDevices.length > 0 ? (
                <ul className="space-y-2">
                  {audioDevices.map(device => (
                    <li key={device.id} className={`p-2 rounded ${selectedDeviceId === device.id ? 'bg-indigo-700' : ''}`}>
                      <div className="font-medium text-white">{device.name}</div>
                      <div className="text-sm text-gray-400">ID: {device.id}</div>
                      <div className="text-sm text-gray-400">Channels: {device.channels}</div>
                      {device.default && <div className="text-xs text-cyan-400 mt-1">Default Device</div>}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">No audio devices found</p>
              )}
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="text-sm font-medium text-cyan-300 mb-2">Audio Settings</h3>
            <div className="space-y-3">
              <div>
                <label htmlFor="sampleRate" className="block mb-1 text-sm text-white">Sample Rate</label>
                <select 
                  id="sampleRate" 
                  className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                >
                  <option value="16000">16,000 Hz (Recommended for Whisper)</option>
                  <option value="44100">44,100 Hz (CD Quality)</option>
                  <option value="48000">48,000 Hz (Professional Audio)</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="bufferSize" className="block mb-1 text-sm text-white">Buffer Size</label>
                <select 
                  id="bufferSize" 
                  className="w-full bg-indigo-800 text-white rounded p-2 border border-indigo-600 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                >
                  <option value="256">256 (Lowest Latency, Higher CPU)</option>
                  <option value="512">512 (Balanced)</option>
                  <option value="1024">1024 (Higher Latency, Lower CPU)</option>
                  <option value="2048">2048 (Highest Latency, Lowest CPU)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DevicesTab;