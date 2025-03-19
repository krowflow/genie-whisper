# Genie Whisper

A real-time voice-to-text transcription tool designed for developers, integrating seamlessly with Cursor, VS Code, Roo Code, and Cline Dev.

![Genie Whisper](images/genie_without_background.png)

## Features

- **Real-Time Speech-to-Text**: Convert voice input into text using OpenAI Whisper
- **Offline & Online Mode**: Run locally with optional cloud-based fallback
- **Global UI Overlay**: Toggleable UI overlay that works across multiple IDEs
- **Intelligent Speech Filtering**: Voice Activity Detection (VAD) to ignore background noise
- **Live Waveform Visualization**: Real-time audio visualization
- **Animated Genie Avatar**: Dynamic avatar that responds to your voice
- **Multiple Activation Methods**: Push-to-talk, wake word, or always-on transcription
- **Direct IDE Integration**: Seamless text injection into supported IDEs
- **Minimal Latency**: Fast transcription with lightweight models

## System Requirements

- **OS**: Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for application and models
- **Microphone**: Any system-compatible microphone

## Installation

### Prerequisites

- Node.js v18.0.0 or higher
- Python 3.9 or higher
- Git
- FFmpeg

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/user/genie-whisper
   cd genie-whisper
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Set up Python environment:
   ```
   # Create a virtual environment (recommended)
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

4. Download Whisper models:
   ```
   python scripts/download_models.py
   ```

5. Start the application:
   ```
   npm run dev
   ```

## Development

### Project Structure

- `/electron` - Electron main process code
- `/src` - Frontend React components and logic
- `/python` - Python backend for Whisper and audio processing
- `/models` - Pre-downloaded Whisper models
- `/extensions` - IDE extensions for VS Code, Cursor, etc.
- `/scripts` - Build and utility scripts
- `/docs` - Project documentation
- `/memory-bank` - Roo Code memory bank files

### Available Scripts

- `npm run dev` - Start the application in development mode
- `npm run lint` - Run ESLint to check code quality
- `npm run test` - Run Jest tests
- `npm run package` - Package the application
- `npm run make` - Make distributable packages

## IDE Integration

### VS Code

1. Install the Genie Whisper extension from the VS Code marketplace
2. Configure the extension settings
3. Use the provided commands or keyboard shortcuts to activate transcription

### Cursor, Roo Code, and Cline Dev

These IDEs are supported through the global overlay functionality. The application will automatically detect text fields and inject transcribed text at the cursor position.

## License

MIT

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Electron](https://www.electronjs.org/)
- [React](https://reactjs.org/)