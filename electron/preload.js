// Preload script for Electron
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Send messages to main process
    send: (channel, ...args) => {
      // Whitelist channels
      const validChannels = [
        'update-settings',
        'start-listening',
        'stop-listening',
        'get-devices',
        'inject-text',
        'minimize-window',
        'close-window',
        'quit-app'
      ];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, ...args);
      }
    },
    
    // Receive messages from main process
    receive: (channel, func) => {
      const validChannels = [
        'python-message',
        'python-error',
        'start-listening',
        'stop-listening',
        'show-settings',
        'wake-word-detected'
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
    },
    
    // Remove listeners
    removeAllListeners: (channel) => {
      const validChannels = [
        'python-message',
        'python-error',
        'start-listening',
        'stop-listening',
        'show-settings',
        'wake-word-detected'
      ];
      if (validChannels.includes(channel)) {
        ipcRenderer.removeAllListeners(channel);
      }
    }
  }
);

// Expose process versions
contextBridge.exposeInMainWorld('versions', {
  node: () => process.versions.node,
  chrome: () => process.versions.chrome,
  electron: () => process.versions.electron,
});

// Expose platform information
contextBridge.exposeInMainWorld('platform', {
  os: process.platform,
  arch: process.arch,
  isWindows: process.platform === 'win32',
  isMac: process.platform === 'darwin',
  isLinux: process.platform === 'linux',
});