// Main application script for Genie Whisper

// DOM Elements
const listenBtn = document.getElementById('listen-btn');
const settingsBtn = document.getElementById('settings-btn');
const minimizeBtn = document.getElementById('minimize-btn');
const closeBtn = document.getElementById('close-btn');
const settingsPanel = document.getElementById('settings-panel');
const closeSettingsBtn = document.getElementById('close-settings-btn');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const resetSettingsBtn = document.getElementById('reset-settings-btn');
const transcriptionPreview = document.getElementById('transcription-preview');
const statusElement = document.getElementById('status');
const sensitivityValue = document.getElementById('sensitivity-value');
const sensitivityRange = document.getElementById('sensitivity');
const settingsForm = document.getElementById('settings-form');

// State
let isListening = false;
let settings = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  // Load settings
  loadSettings();
  
  // Initialize UI
  initializeUI();
  
  // Set up event listeners
  setupEventListeners();
  
  // Initialize waveform visualization
  initializeWaveform();
});

// Load settings from Electron store
function loadSettings() {
  // Use IPC to get settings from main process
  if (window.api) {
    settings = window.api.sendSync('get-settings');
    updateSettingsForm(settings);
  } else {
    console.warn('Running outside of Electron environment');
    // Default settings for development
    settings = {
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
  }
}

// Update settings form with current values
function updateSettingsForm(settings) {
  // General settings
  document.getElementById('alwaysOnTop').checked = settings.alwaysOnTop;
  document.getElementById('startMinimized').checked = settings.startMinimized;
  document.getElementById('startWithSystem').checked = settings.startWithSystem;
  document.getElementById('theme').value = settings.theme;
  
  // Transcription settings
  document.getElementById('modelSize').value = settings.modelSize;
  document.getElementById('sensitivity').value = settings.sensitivity;
  document.getElementById('sensitivity-value').textContent = settings.sensitivity;
  document.getElementById('useVAD').checked = settings.useVAD;
  document.getElementById('offlineMode').checked = settings.offlineMode;
  
  // Activation settings
  document.getElementById('hotkey').value = settings.hotkey;
  document.getElementById('wakeWord').value = settings.wakeWord;
  
  // Apply theme
  applyTheme(settings.theme);
}

// Apply theme to the application
function applyTheme(theme) {
  if (theme === 'light') {
    document.body.classList.add('theme-light');
  } else {
    document.body.classList.remove('theme-light');
  }
}

// Initialize UI elements
function initializeUI() {
  // Apply theme
  applyTheme(settings.theme);
  
  // Update sensitivity value display
  sensitivityValue.textContent = settings.sensitivity;
}

// Set up event listeners
function setupEventListeners() {
  // Listen button
  listenBtn.addEventListener('click', toggleListening);
  
  // Settings button
  settingsBtn.addEventListener('click', () => {
    settingsPanel.classList.remove('hidden');
  });
  
  // Close settings button
  closeSettingsBtn.addEventListener('click', () => {
    settingsPanel.classList.add('hidden');
  });
  
  // Save settings button
  saveSettingsBtn.addEventListener('click', saveSettings);
  
  // Reset settings button
  resetSettingsBtn.addEventListener('click', resetSettings);
  
  // Minimize button
  if (minimizeBtn && window.api) {
    minimizeBtn.addEventListener('click', () => {
      window.api.send('minimize-window');
    });
  }
  
  // Close button
  if (closeBtn && window.api) {
    closeBtn.addEventListener('click', () => {
      window.api.send('close-window');
    });
  }
  
  // Sensitivity range input
  sensitivityRange.addEventListener('input', (e) => {
    sensitivityValue.textContent = e.target.value;
  });
  
  // Listen for messages from main process
  if (window.api) {
    window.api.receive('start-listening', () => {
      startListening();
    });
    
    window.api.receive('stop-listening', () => {
      stopListening();
    });
    
    window.api.receive('show-settings', () => {
      settingsPanel.classList.remove('hidden');
    });
    
    window.api.receive('python-message', handlePythonMessage);
  }
}

// Initialize waveform visualization
function initializeWaveform() {
  // This is a placeholder for the actual waveform visualization
  // In a real implementation, we would use Wavesurfer.js or a similar library
  console.log('Waveform visualization initialized');
}

// Toggle listening state
function toggleListening() {
  if (isListening) {
    stopListening();
  } else {
    startListening();
  }
}

// Start listening for voice input
function startListening() {
  isListening = true;
  listenBtn.classList.add('listening');
  listenBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="mr-2" viewBox="0 0 16 16">
      <path d="M5.164 14H10.836A1.5 1.5 0 0 0 12 12.5V3.5A1.5 1.5 0 0 0 10.5 2h-5A1.5 1.5 0 0 0 4 3.5v9a1.5 1.5 0 0 0 1.164 1.5z"/>
    </svg>
    Stop Listening
  `;
  document.body.classList.add('listening');
  statusElement.textContent = 'Listening...';
  
  // Send message to main process
  if (window.api) {
    window.api.send('start-listening');
  }
  
  // Clear transcription preview
  transcriptionPreview.innerHTML = '<p class="text-gray-400 italic">Listening for speech...</p>';
}

// Stop listening for voice input
function stopListening() {
  isListening = false;
  listenBtn.classList.remove('listening');
  listenBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="mr-2" viewBox="0 0 16 16">
      <path d="M8 1a5 5 0 0 0-5 5v1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a6 6 0 1 1 12 0v6a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h1V6a5 5 0 0 0-5-5z"/>
    </svg>
    Start Listening
  `;
  document.body.classList.remove('listening');
  statusElement.textContent = 'Ready';
  
  // Send message to main process
  if (window.api) {
    window.api.send('stop-listening');
  }
}

// Handle messages from Python backend
function handlePythonMessage(message) {
  try {
    const data = JSON.parse(message);
    
    if (data.type === 'transcription') {
      updateTranscription(data.text);
    } else if (data.type === 'error') {
      handleError(data.error);
    } else if (data.type === 'status') {
      updateStatus(data.status);
    }
  } catch (error) {
    console.error('Error parsing Python message:', error);
  }
}

// Update transcription preview
function updateTranscription(text) {
  if (text) {
    transcriptionPreview.innerHTML = `<p>${text}</p>`;
  } else {
    transcriptionPreview.innerHTML = '<p class="text-gray-400 italic">No speech detected...</p>';
  }
}

// Handle errors
function handleError(error) {
  console.error('Error:', error);
  statusElement.textContent = `Error: ${error}`;
  statusElement.style.color = 'var(--error-color)';
  
  // Reset after a delay
  setTimeout(() => {
    statusElement.style.color = '';
    statusElement.textContent = 'Ready';
  }, 5000);
}

// Update status display
function updateStatus(status) {
  statusElement.textContent = status;
}

// Save settings
function saveSettings() {
  // Get values from form
  const newSettings = {
    // General settings
    alwaysOnTop: document.getElementById('alwaysOnTop').checked,
    startMinimized: document.getElementById('startMinimized').checked,
    startWithSystem: document.getElementById('startWithSystem').checked,
    theme: document.getElementById('theme').value,
    
    // Transcription settings
    modelSize: document.getElementById('modelSize').value,
    sensitivity: parseFloat(document.getElementById('sensitivity').value),
    useVAD: document.getElementById('useVAD').checked,
    offlineMode: document.getElementById('offlineMode').checked,
    
    // Activation settings
    hotkey: document.getElementById('hotkey').value,
    wakeWord: document.getElementById('wakeWord').value,
  };
  
  // Update settings
  settings = newSettings;
  
  // Apply theme
  applyTheme(settings.theme);
  
  // Send to main process
  if (window.api) {
    window.api.send('update-settings', settings);
  }
  
  // Hide settings panel
  settingsPanel.classList.add('hidden');
  
  // Show success message
  statusElement.textContent = 'Settings saved';
  setTimeout(() => {
    statusElement.textContent = 'Ready';
  }, 2000);
}

// Reset settings to defaults
function resetSettings() {
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
  
  // Update settings
  settings = defaultSettings;
  
  // Update form
  updateSettingsForm(settings);
  
  // Show message
  statusElement.textContent = 'Settings reset to defaults';
  setTimeout(() => {
    statusElement.textContent = 'Ready';
  }, 2000);
}