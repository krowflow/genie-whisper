# Genie Whisper

A real-time voice-to-text transcription tool designed to work offline and online, integrating seamlessly with Cursor, VS Code, Roo Code, and Cline Dev.

![Genie Whisper](images/genie_without_background.png)

## Features

- **Real-Time Speech-to-Text**: Converts voice input into text using OpenAI Whisper
- **Offline & Online Mode**: Runs locally, with optional cloud-based fallback
- **Global UI Overlay**: Toggleable HUD that works across PC, Cursor, VS Code IDEs
- **Intelligent Speech Filtering**: Uses Voice Activity Detection (VAD) to ignore background noise
- **Live Waveform Visualization**: (Planned) Displays real-time waveform during speech
- **Animated Genie Avatar**: (Planned) Dynamic avatar that reacts during speech
- **Hotkey & Wake Word Activation**: Push-to-talk, wake-word mode, or always-on transcription
- **Direct IDE Integration**: (Planned) Inject text into Cursor, VS Code, Roo Code, and OpenAI chat
- **Minimal Latency**: Optimized for fast transcription with lightweight models
- **System Tray & Toggle Control**: Control transcription and settings easily

## Installation

### Prerequisites
- Node.js (v18+)
- Python 3.9+
- FFmpeg

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/krowflow/genie-whisper.git
   cd genie-whisper
   ```

2. Set up environment and install dependencies:

   **Windows**:
   ```powershell
   .\setup_env.ps1
   ```

   **Linux/macOS**:
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

   **Manual Setup**:
   ```bash
   python -m venv .venv
   # Activate virtual environment
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r tests/requirements-minimal.txt
   pip install -r tests/requirements-whisper.txt
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

   npm install
   ```

3. Download Whisper models:
   ```bash
   npm run download-models
   ```

## Usage

### Starting the Application
```bash
npm start
```

### Development Mode
```bash
npm run dev
```

### Keyboard Shortcuts
- **CommandOrControl+Shift+Space**: Start/Stop Listening (default)

### Activation Methods
- **Push-to-Talk**: Hold hotkey while speaking
- **Wake Word**: Say "Hey Genie" to start listening
- **Toggle Mode**: Continuous transcription until manually stopped

### Settings
- Model size selection (tiny, base, small, medium, large)
- Sensitivity adjustment
- Activation mode selection
- IDE integration target (future)
- Theme (light/dark)
- Always-on-top toggle
- Start minimized
- Auto-start with system

## Testing

### Running Tests

Ensure virtual environment is activated, then:
```bash
python tests/test_whisper.py
python tests/test_vad.py
python tests/test_ide_integration.py
```

### Test Scripts
- **test_whisper.py**: Whisper model testing
- **test_vad.py**: Voice activity detection testing
- **test_ide_integration.py**: IDE clipboard injection testing (future phase)

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

- `/electron`: Electron main process
- `/src`: React frontend components
- `/python`: Python backend for Whisper and audio processing
- `/models`: Whisper model files
- `/scripts`: Utility scripts
- `/docs`: Documentation
- `/memory-bank`: AI agent memory bank
- `/tests`: Test scripts

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

**This project is proprietary and privately owned by KrowFlow. All rights reserved. Unauthorized copying, distribution, modification, or use is strictly prohibited.**

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Electron](https://www.electronjs.org/)
- [React](https://reactjs.org/)
