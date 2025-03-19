# Project Brief: Genie Whisper

## Project Overview
Genie Whisper is a **real-time voice-to-text transcription tool** designed to work **offline and online**, integrating seamlessly with **Cursor, VS Code, Roo Code, and Cline Dev**. This tool enables users to **speak prompts** instead of typing, using **OpenAI Whisper** for transcription with **intelligent speech filtering**, a **futuristic UI**, and **global overlay support**.

## Core Requirements

### Primary Objectives
- Create a seamless voice-to-text experience for developers
- Minimize latency (<1 second) for real-time transcription
- Support both offline (local) and online (cloud) transcription
- Integrate directly with popular coding environments
- Filter out background noise and unintended speech
- Provide an intuitive, non-intrusive user interface

### Key Features
1. **Real-Time Speech-to-Text**: Converts voice input into text using OpenAI Whisper (optimized via Whisper.cpp or Faster-Whisper)
2. **Offline & Online Mode**: Runs locally, with optional cloud-based fallback if needed
3. **Global UI Overlay**: Toggleable UI overlay that works across PC, Cursor, VS Code IDEs
4. **Intelligent Speech Filtering**: Uses Voice Activity Detection (VAD) to ignore background noise and random conversations
5. **Live Waveform Visualization**: Displays real-time waveform during speech
6. **Animated Genie Avatar**: A dynamic avatar that "speaks" transcribed text
7. **Hotkey & Wake Word Activation**: Allows push-to-talk, wake-word mode ("Hey Genie"), or always-on transcription
8. **Direct IDE Integration**: Seamlessly injects text into Cursor, VS Code, Roo Code, and OpenAI chat UI
9. **Minimal Latency**: Optimized for fast transcription (<1 sec lag) with lightweight models
10. **System Tray & Toggle Control**: UI settings panel to enable/disable transcription, set wake-word, and configure sensitivity

## Project Scope

### In Scope
- Electron-based desktop application with global overlay capabilities
- Python backend for Whisper integration and audio processing
- Real-time transcription with minimal latency
- Voice activity detection and noise filtering
- Direct integration with Cursor, VS Code, Roo Code, and OpenAI chat
- System tray controls and settings management
- Animated Genie avatar and waveform visualization
- Hotkey and wake-word activation options

### Out of Scope (Future Considerations)
- Mobile application versions
- Browser extension versions (initial focus is desktop)
- Custom fine-tuned Whisper models (will use existing models initially)
- Text-to-speech response capabilities (one-way transcription only in initial version)
- Multi-user collaboration features

## Success Criteria
- Transcription latency under 1 second
- Accurate transcription in typical development environments
- Successful noise filtering and speech detection
- Seamless integration with target IDEs
- Intuitive UI that doesn't interfere with development workflow
- Ability to function offline with comparable performance to online mode

## Timeline
The project will be developed in three phases:
1. **Phase 1**: Core Implementation (4 weeks)
2. **Phase 2**: UI/UX Enhancements (3 weeks)
3. **Phase 3**: Production Features (3 weeks)

Total estimated timeline: 10 weeks

## Stakeholders
- Developers using Cursor, VS Code, Roo Code, and Cline Dev
- Project development team
- OpenAI (Whisper technology provider)