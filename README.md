# Genie Whisper

A real-time voice-to-text transcription tool designed to work offline and online, integrating seamlessly with Cursor, VS Code, Roo Code, and Cline Dev.

![Genie Whisper](images/genie_without_background.png)

## Features

- **Real-Time Speech-to-Text**: Converts voice input into text using OpenAI Whisper
- **Offline & Online Mode**: Runs locally, with optional cloud-based fallback
- **Global UI Overlay**: Toggleable UI overlay that works across PC, Cursor, VS Code IDEs
- **Intelligent Speech Filtering**: Uses Voice Activity Detection (VAD) to ignore background noise
- **Live Waveform Visualization**: Displays real-time waveform during speech
- **Animated Genie Avatar**: A dynamic avatar that "speaks" transcribed text
- **Hotkey & Wake Word Activation**: Allows push-to-talk, wake-word mode, or always-on transcription
- **Direct IDE Integration**: Seamlessly injects text into Cursor, VS Code, Roo Code, and OpenAI chat UI
- **Minimal Latency**: Optimized for fast transcription with lightweight models
- **System Tray & Toggle Control**: UI settings panel to enable/disable transcription and configure settings

## Installation

### Prerequisites

- Node.js (for Electron)
- Python 3.9+ (for Whisper backend)
- FFmpeg (for audio processing)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/krowflow/genie-whisper.git
   cd genie-whisper
   ```

2. Set up the environment and install dependencies:

   **Windows**:
   ```powershell
   .\setup_env.ps1
   ```

   **Linux/macOS**:
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

   This will:
   - Create a virtual environment
   - Install all required dependencies
   - Run tests to verify the installation

   **Manual Setup**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r tests/requirements-minimal.txt
   pip install -r tests/requirements-whisper.txt
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
   
   # Install Node.js dependencies
   npm install
   ```

3. Download models:
   ```bash
   npm run download-models
   ```

## Usage

### Starting the Application

```bash
npm start
```

This will launch the Electron application and start the Python backend.

### Development Mode

```bash
npm run dev
```

This will start the application in development mode with hot reloading.

### Keyboard Shortcuts

- **CommandOrControl+Shift+Space**: Start/stop listening (default, can be customized)

### Activation Methods

- **Push-to-Talk**: Hold the hotkey while speaking, release to finalize
- **Wake Word**: Say "Hey Genie" to start listening, automatic stop on silence
- **Toggle Mode**: Activate for continuous transcription until manually stopped

### Settings

- **Model Size**: Choose between tiny, base, small, medium, or large Whisper models
- **Sensitivity**: Adjust the sensitivity of the Voice Activity Detection
- **Activation Mode**: Select between push-to-talk, wake word, or always-on
- **IDE Integration**: Choose which IDE to inject text into
- **Theme**: Select between dark and light themes
- **Always on Top**: Keep the window on top of other windows
- **Start Minimized**: Start the application minimized to the system tray
- **Start with System**: Start the application when the system starts

## Testing

The project includes comprehensive test scripts to verify the functionality of various components:

### Running Tests

Make sure your virtual environment is activated, then run:

```bash
# Test Whisper transcription
python tests/test_whisper.py

# Test Voice Activity Detection
python tests/test_vad.py

# Test IDE integration
python tests/test_ide_integration.py
```

### Test Scripts

- **test_whisper.py**: Tests the Whisper transcription model loading and basic transcription
- **test_vad.py**: Tests the Voice Activity Detection functionality
- **test_ide_integration.py**: Tests the clipboard and IDE integration functionality

These tests help ensure that all components are working correctly and can be used to troubleshoot issues.

## Building

### Package the Application

```bash
npm run package
```

### Create Installers

```bash
npm run make
```

## Project Structure

- `/electron`: Electron main process code
- `/src`: Frontend React components and logic
- `/python`: Python backend for Whisper and audio processing
- `/models`: Pre-downloaded Whisper models
- `/scripts`: Build and utility scripts
- `/docs`: Project documentation
- `/memory-bank`: Roo Code memory bank files
- `/tests`: Test scripts and testing utilities

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) for the optimized Whisper implementation
- [Silero VAD](https://github.com/snakers4/silero-vad) for Voice Activity Detection
- [Electron](https://www.electronjs.org/) for the desktop application framework
- [React](https://reactjs.org/) for the UI components