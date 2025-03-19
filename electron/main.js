const { app, BrowserWindow, Tray, Menu, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const Store = require('electron-store');

// Initialize store for settings
const store = new Store();

// Keep references to prevent garbage collection
let mainWindow = null;
let tray = null;
let pythonProcess = null;
let isQuitting = false;

// Default settings
const defaultSettings = {
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

// Ensure settings exist
if (!store.has('settings')) {
  store.set('settings', defaultSettings);
}

// Create the main window
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    show: !store.get('settings.startMinimized', false),
    frame: false,
    transparent: true,
    resizable: true,
    alwaysOnTop: store.get('settings.alwaysOnTop', true),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // Load the index.html file
  mainWindow.loadFile(path.join(__dirname, '../src/index.html'));

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // Hide window on close (don't quit)
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
    return true;
  });
}

// Create the system tray
function createTray() {
  tray = new Tray(path.join(__dirname, '../images/genie_without_background.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show Genie Whisper', click: () => mainWindow.show() },
    { type: 'separator' },
    { label: 'Start Listening', click: () => startListening() },
    { label: 'Stop Listening', click: () => stopListening() },
    { type: 'separator' },
    { label: 'Settings', click: () => showSettings() },
    { type: 'separator' },
    { label: 'Quit', click: () => quitApp() },
  ]);
  
  tray.setToolTip('Genie Whisper');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
    }
  });
}

// Start the Python backend
function startPythonBackend() {
  const options = {
    mode: 'text',
    pythonPath: 'python', // Adjust based on environment
    pythonOptions: ['-u'], // Unbuffered output
    scriptPath: path.join(__dirname, '../python'),
    args: [
      '--model-size', store.get('settings.modelSize', 'base'),
      '--sensitivity', store.get('settings.sensitivity', 0.5).toString(),
      '--vad', store.get('settings.useVAD', true) ? 'true' : 'false',
      '--offline', store.get('settings.offlineMode', true) ? 'true' : 'false',
    ],
  };

  pythonProcess = new PythonShell('server.py', options);
  
  pythonProcess.on('message', (message) => {
    // Forward messages to renderer
    if (mainWindow) {
      mainWindow.webContents.send('python-message', message);
    }
  });
  
  pythonProcess.on('error', (err) => {
    console.error('Python Error:', err);
  });
  
  pythonProcess.on('close', () => {
    console.log('Python process closed');
    pythonProcess = null;
  });
}

// Start listening for voice input
function startListening() {
  if (mainWindow) {
    mainWindow.webContents.send('start-listening');
  }
}

// Stop listening for voice input
function stopListening() {
  if (mainWindow) {
    mainWindow.webContents.send('stop-listening');
  }
}

// Show settings window
function showSettings() {
  if (mainWindow) {
    mainWindow.webContents.send('show-settings');
    mainWindow.show();
  }
}

// Quit the application
function quitApp() {
  isQuitting = true;
  
  // Clean up Python process
  if (pythonProcess) {
    pythonProcess.end();
  }
  
  app.quit();
}

// App ready event
app.whenReady().then(() => {
  createMainWindow();
  createTray();
  startPythonBackend();
  
  // Register global shortcut
  const hotkey = store.get('settings.hotkey', defaultSettings.hotkey);
  globalShortcut.register(hotkey, () => {
    startListening();
  });
  
  // macOS: Re-create window when dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    } else {
      mainWindow.show();
    }
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Clean up before quitting
app.on('will-quit', () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

// IPC handlers
ipcMain.on('update-settings', (event, settings) => {
  store.set('settings', settings);
  
  // Update hotkey if changed
  const currentHotkey = store.get('settings.hotkey');
  globalShortcut.unregisterAll();
  globalShortcut.register(currentHotkey, () => {
    startListening();
  });
  
  // Restart Python backend with new settings
  if (pythonProcess) {
    pythonProcess.end();
    startPythonBackend();
  }
});

ipcMain.on('get-settings', (event) => {
  event.returnValue = store.get('settings');
});

ipcMain.on('start-listening', () => {
  startListening();
});

ipcMain.on('stop-listening', () => {
  stopListening();
});

ipcMain.on('quit-app', () => {
  quitApp();
});