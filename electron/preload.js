// Preload script for Electron
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Send messages to main process
    send: (channel, data) => {
      // Whitelist channels
      const validChannels = [
        'update-settings',
        'start-listening',
        'stop-listening',
        'quit-app'
      ];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, data);
      }
    },
    
    // Receive messages from main process
    receive: (channel, func) => {
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
    sendSync: (channel) => {
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