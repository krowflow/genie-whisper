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
  activationMode: 'manual', // 'manual', 'wake_word', or 'always_on'
  ide: '', // '', 'vscode', 'cursor', 'roocode', or 'openai'
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
  console.log("Tray creation skipped temporarily to avoid crash.");

  /*
  try {
    // Use path.resolve instead of path.join to handle spaces in paths correctly
    const iconPath = path.resolve(__dirname, '..', 'images', 'Genie.png');
    tray = new Tray(iconPath);

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
  } catch (error) {
    console.error('Failed to create tray icon:', error);
    // Create a fallback tray with a simple empty image
    const emptyImage = Buffer.alloc(16 * 16 * 4); // 16x16 transparent image
    tray = new Tray(emptyImage);
    tray.setToolTip('Genie Whisper (Icon Failed to Load)');
  }
  */
}

// Start the Python backend
function startPythonBackend() {
  const settings = store.get('settings');

  const options = {
    mode: 'text',
    pythonPath: 'python', // Adjust based on environment
    pythonOptions: ['-u'], // Unbuffered output
    scriptPath: path.join(__dirname, '../python'),
    args: [
      '--model-size', settings.modelSize || 'base',
      '--sensitivity', (settings.sensitivity || 0.5).toString(),
      '--vad', settings.useVAD ? 'true' : 'false',
      '--offline', settings.offlineMode ? 'true' : 'false',
      '--wake-word', settings.wakeWord || 'Hey Genie',
      '--activation-mode', settings.activationMode || 'manual',
    ],
  };

  // Add IDE parameter if specified
  if (settings.ide) {
    options.args.push('--ide', settings.ide);
  }

  // Use spawn instead of PythonShell for better control over stdout/stderr
  const { spawn } = require('child_process');

  // Build command and arguments
  const pythonPath = options.pythonPath || 'python';
  const pythonArgs = [...(options.pythonOptions || [])];
  const scriptPath = path.join(options.scriptPath, 'server.py');
  pythonArgs.push(scriptPath);
  pythonArgs.push(...options.args);

  // Spawn Python process
  const pythonSpawnProcess = spawn(pythonPath, pythonArgs, {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // Create a wrapper object to maintain compatibility with PythonShell API
  pythonProcess = {
    _process: pythonSpawnProcess,
    send: (message) => {
      if (pythonSpawnProcess.stdin) {
        pythonSpawnProcess.stdin.write(message + '\n');
      }
    },
    end: () => {
      pythonSpawnProcess.kill();
    }
  };

  // Handle stdout (clean JSON messages)
  pythonSpawnProcess.stdout.on('data', (data) => {
    const lines = data.toString().trim().split('\n').filter(Boolean);

    lines.forEach(line => {
      try {
        // Parse message as JSON
        const jsonData = JSON.parse(line);

        // Forward messages to renderer
        if (mainWindow) {
          mainWindow.webContents.send('python-message', line);

          // Handle specific message types
          if (jsonData.type === 'wake_word_detected') {
            // Show window when wake word is detected
            mainWindow.show();
          }
        }
      } catch (error) {
        // Log parsing errors without crashing
        console.error('Invalid JSON from Python stdout:', line);
      }
    });
  });

  // Handle stderr (logs and errors)
  pythonSpawnProcess.stderr.on('data', (data) => {
    // Log Python stderr output to console
    console.log('[Python stderr]', data.toString().trim());
  });

  // Handle process errors
  pythonSpawnProcess.on('error', (err) => {
    console.error('Python Process Error:', err);
    if (mainWindow) {
      mainWindow.webContents.send('python-error', err.toString());
    }
  });

  // Handle process exit
  pythonSpawnProcess.on('close', (code) => {
    console.log(`Python process closed with code ${code}`);
    pythonProcess = null;
  });
}

// Send command to Python backend
function sendToPython(command) {
  if (pythonProcess) {
    try {
      // Ensure command is properly JSON stringified
      const jsonCommand = JSON.stringify(command);
      pythonProcess.send(jsonCommand);
    } catch (error) {
      console.error('Error sending command to Python:', error);
    }
  } else {
    console.error('Python process not running');
  }
}

// Start listening for voice input
function startListening() {
  if (pythonProcess) {
    sendToPython({ type: 'start_listening' });
  }

  if (mainWindow) {
    mainWindow.webContents.send('start-listening');
  }
}

// Stop listening for voice input
function stopListening() {
  if (pythonProcess) {
    sendToPython({ type: 'stop_listening' });
  }

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

  // Update Python backend with new settings
  if (pythonProcess) {
    sendToPython({
      type: 'update_settings',
      settings: settings
    });
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

ipcMain.on('get-devices', () => {
  if (pythonProcess) {
    sendToPython({ type: 'get_devices' });
  }
});

ipcMain.on('inject-text', (event, text, ide) => {
  if (pythonProcess) {
    sendToPython({
      type: 'inject_text',
      text: text,
      ide: ide
    });
  }
});

ipcMain.on('minimize-window', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

ipcMain.on('close-window', () => {
  if (mainWindow) {
    mainWindow.hide();
  }
});

ipcMain.on('quit-app', () => {
  quitApp();
});