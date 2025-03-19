# Technical Context: Genie Whisper

## Technologies Used

### Frontend Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Electron.js** | Cross-platform desktop application framework | ^28.0.0 |
| **React** | UI component library | ^18.2.0 |
| **TypeScript** | Type-safe JavaScript | ^5.2.0 |
| **Wavesurfer.js** | Audio waveform visualization | ^7.3.0 |
| **Lottie.js** | Vector animation rendering | ^5.12.0 |
| **Three.js** | 3D graphics for Genie avatar (optional) | ^0.158.0 |
| **Electron-Store** | Persistent settings storage | ^8.1.0 |
| **Tailwind CSS** | Utility-first CSS framework | ^3.3.0 |

### Backend Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Backend language | ^3.9.0 |
| **Whisper.cpp** | Optimized C++ port of OpenAI Whisper | Latest |
| **Faster-Whisper** | Optimized Whisper implementation | Latest |
| **PyAudio** | Audio I/O library | ^0.2.13 |
| **SoundDevice** | Audio I/O alternative | ^0.4.6 |
| **Silero VAD** | Voice activity detection | Latest |
| **WebRTC VAD** | Alternative voice activity detection | Latest |
| **NumPy** | Numerical processing | ^1.24.0 |
| **FFmpeg** | Audio processing | ^6.0 |

### Integration Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Socket.io** | Real-time communication | ^4.7.0 |
| **Python-Shell** | Node.js to Python communication | ^5.0.0 |
| **node-gyp** | Native addon build tool | ^10.0.0 |
| **Electron IPC** | Inter-process communication | Built-in |
| **VS Code API** | VS Code extension integration | Latest |

## Development Setup

### Prerequisites

#### System Requirements
- **OS**: Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **CPU**: 4+ cores recommended (for Whisper processing)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for application and models
- **Microphone**: Any system-compatible microphone

#### Required Software
- **Node.js**: v18.0.0 or higher
- **Python**: 3.9 or higher
- **Git**: For version control
- **FFmpeg**: For audio processing
- **Visual Studio Code**: For extension development (optional)
- **C++ Build Tools**: For native dependencies

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/user/genie-whisper
cd genie-whisper

# Install frontend dependencies
npm install

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download Whisper models
python scripts/download_models.py

# Start development servers
npm run dev
```

### Project Structure

```
genie-whisper/
├── electron/              # Electron main process
│   ├── main.ts            # Main entry point
│   ├── ipc.ts             # IPC handlers
│   └── tray.ts            # System tray implementation
├── src/                   # Frontend source code
│   ├── components/        # React components
│   ├── hooks/             # Custom React hooks
│   ├── styles/            # CSS/Tailwind styles
│   ├── utils/             # Utility functions
│   └── App.tsx            # Main React component
├── python/                # Python backend
│   ├── server.py          # Main Python entry point
│   ├── whisper_engine.py  # Whisper implementation
│   ├── vad.py             # Voice activity detection
│   └── audio_capture.py   # Audio input handling
├── models/                # Pre-downloaded Whisper models
├── extensions/            # IDE extensions
│   ├── vscode/            # VS Code extension
│   └── cursor/            # Cursor extension
├── scripts/               # Build and utility scripts
├── package.json           # Node.js dependencies
└── requirements.txt       # Python dependencies
```

## Technical Constraints

### Performance Constraints

| Constraint | Target | Notes |
|------------|--------|-------|
| **Transcription Latency** | <1000ms | Maximum acceptable delay from speech to text |
| **CPU Usage (Idle)** | <1% | When not actively transcribing |
| **CPU Usage (Active)** | <30% | During active transcription |
| **Memory Usage** | <500MB | Total application footprint |
| **Startup Time** | <3s | Time to ready state |

### Compatibility Constraints

| Environment | Minimum Version | Notes |
|-------------|-----------------|-------|
| **Windows** | Windows 10 1909+ | With working microphone |
| **macOS** | macOS 12+ | With microphone permissions |
| **Linux** | Ubuntu 20.04+ | With PulseAudio/PipeWire |
| **VS Code** | 1.60+ | For extension integration |
| **Cursor** | Latest | For integration |
| **Roo Code** | Latest | For integration |

### Network Constraints

| Scenario | Requirement | Notes |
|----------|-------------|-------|
| **Offline Mode** | No network required | Using local models |
| **Online Mode** | Internet connection | For cloud API fallback |
| **Updates** | Internet connection | For application updates |

## Dependencies

### External Dependencies

| Dependency | Purpose | License |
|------------|---------|---------|
| **OpenAI Whisper** | Speech recognition model | MIT |
| **FFmpeg** | Audio processing | LGPL 2.1 |
| **Electron** | Desktop application framework | MIT |
| **React** | UI library | MIT |
| **Python** | Backend language | PSF License |

### Third-Party Services

| Service | Purpose | Authentication |
|---------|---------|---------------|
| **OpenAI API** | Cloud fallback for Whisper | API Key (optional) |
| **GitHub** | Application updates | None |

### Internal Dependencies

| Component | Depends On | Notes |
|-----------|------------|-------|
| **UI Overlay** | Electron | For cross-application window |
| **Transcription** | Whisper models | Downloaded during setup |
| **Audio Capture** | System permissions | Requires microphone access |
| **IDE Integration** | IDE extensions | Optional components |

## Development Tools

### Build Tools

| Tool | Purpose | Configuration |
|------|---------|--------------|
| **Webpack** | Frontend bundling | webpack.config.js |
| **Electron Forge** | Application packaging | forge.config.js |
| **PyInstaller** | Python packaging | spec files |
| **ESLint** | JavaScript/TypeScript linting | .eslintrc |
| **Prettier** | Code formatting | .prettierrc |

### Testing Tools

| Tool | Purpose | Configuration |
|------|---------|--------------|
| **Jest** | Frontend unit testing | jest.config.js |
| **Pytest** | Python unit testing | pytest.ini |
| **Spectron** | Electron integration testing | test/spectron/ |
| **Cypress** | E2E testing | cypress.json |

### CI/CD Tools

| Tool | Purpose | Configuration |
|------|---------|--------------|
| **GitHub Actions** | CI/CD pipeline | .github/workflows/ |
| **Electron Builder** | Application distribution | electron-builder.yml |

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `NODE_ENV` | Development/production mode | `development` |
| `WHISPER_MODEL_PATH` | Path to Whisper models | `./models` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | None |
| `LOG_LEVEL` | Logging verbosity | `info` |
| `DISABLE_HARDWARE_ACCELERATION` | Disable GPU acceleration | `false` |

## Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `config.json` | Application settings | JSON |
| `models.json` | Whisper model configurations | JSON |
| `keybindings.json` | Custom hotkeys | JSON |
| `themes.json` | UI themes | JSON |

## Logging Strategy

| Log Type | Location | Retention |
|----------|----------|-----------|
| **Application Logs** | `%APPDATA%/genie-whisper/logs` | 7 days |
| **Error Reports** | `%APPDATA%/genie-whisper/crashes` | 30 days |
| **Usage Statistics** | Local only (privacy-focused) | 30 days |

## Security Considerations

| Aspect | Approach | Notes |
|--------|----------|-------|
| **Audio Data** | Processed locally | Never sent to cloud unless explicitly enabled |
| **API Keys** | Encrypted storage | For optional cloud services |
| **Application Updates** | Signed packages | Verify authenticity |
| **Dependencies** | Regular audits | Using npm audit and safety |