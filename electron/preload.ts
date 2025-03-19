// Preload script for Electron
import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Send messages to main process
    send: (channel: string, data?: any) => {
      // Whitelist channels
      const validChannels = [
        'update-settings',
        'start-listening',
        'stop-listening',
        'quit-app',
        'minimize-window',
        'close-window'
      ];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, data);
      }
    },
    
    // Receive messages from main process
    receive: (channel: string, func: (...args: any[]) => void) => {
      const validChannels = [
        'python-message',
        'start-listening',
        'stop-listening',
        'show-settings'
      ];
      if (validChannels.includes(channel)) {
        // Deliberately strip event as it includes `sender` 
        ipcRenderer.on(channel, (event, ...args) => func(...args));
      }
    },
    
    // Synchronous messages
    sendSync: (channel: string) => {
      const validChannels = ['get-settings'];
      if (validChannels.includes(channel)) {
        return ipcRenderer.sendSync(channel);
      }
      return null;
    }
  }
);

// Expose process versions
contextBridge.exposeInMainWorld('versions', {
  node: () => process.versions.node,
  chrome: () => process.versions.chrome,
  electron: () => process.versions.electron,
});

// Define types for the exposed API
declare global {
  interface Window {
    api: {
      send: (channel: string, data?: any) => void;
      receive: (channel: string, func: (...args: any[]) => void) => void;
      sendSync: (channel: string) => any;
    };
    versions: {
      node: () => string;
      chrome: () => string;
      electron: () => string;
    };
  }
}