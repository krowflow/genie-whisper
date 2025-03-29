# Active Context: Genie Whisper

## Current Work Focus

We are pivoting the Genie Whisper project to become a **full Jarvis-like voice assistant** that works globally across all applications on the PC. The primary focus is on:

1. **Getting Basic Genie Whisper Working**
   - Fixing the core audio pipeline
   - Resolving Silero VAD model download issues (using WebRTC VAD as fallback)
   - Implementing working audio capture from microphone
   - Connecting to Whisper for transcription
   - Creating a minimal viable product with system tray and global hotkey
   - Adding text-to-speech capabilities for two-way voice interaction

2. **Expanding to Jarvis-Like Functionality**
   - Implementing command recognition system
   - Adding global system integration
   - Creating enhanced IDE integration for AI agent communication
   - Implementing local knowledge base
   - Building automation features

3. **Ensuring Cross-Platform Compatibility**
   - Supporting Windows, macOS, and Linux
   - Implementing platform-specific integrations
   - Ensuring consistent experience across environments
   - Optimizing for different hardware configurations

4. **Optimizing Performance and Usability**
   - Minimizing latency in the transcription pipeline
   - Reducing resource usage
   - Improving accuracy of speech recognition
   - Enhancing user interface and experience

## Technology Stack Decision

After researching available technologies, we've decided to focus on currently available, proven technologies rather than speculating about future developments. Our core stack includes:

1. **Speech Recognition**: OpenAI Whisper (local implementation)
2. **Text-to-Speech**: 
   - Primary option: Mozilla TTS (free, local, good documentation)
   - Alternative option: Spark-TTS (higher quality, voice cloning, but more resource-intensive)
3. **Voice Activity Detection**: Hybrid approach with WebRTC VAD and Silero VAD
4. **Wake Word Detection**: Picovoice Porcupine (free tier)
5. **System Integration**: Electron with Node.js
6. **Local Knowledge**: SQLite with FTS5
7. **AI Integration**: Direct API integration with Roo Code and other assistants

This stack provides a solid foundation for a completely local, free, and powerful voice assistant.

## Recent Changes

| Date | Change | Details |
|------|--------|---------|
| 2025-03-19 | Project Initialization | Created initial project structure and documentation |
| 2025-03-19 | Memory Bank Setup | Established core Memory Bank files |
| 2025-03-19 | Project Guide | Created comprehensive Genie Whisper Guide |
| 2025-03-19 | UI Implementation | Implemented core UI with Genie avatar, waveform visualization, and microphone button |
| 2025-03-19 | Backend Implementation | Created Python backend with Whisper, VAD, wake word detection, and IDE integration |
| 2025-03-19 | Audio Device Support | Added support for professional audio interfaces like Focusrite Clarett 4 Pre |
| 2025-03-19 | GPU Acceleration | Implemented GPU acceleration for Whisper transcription on NVIDIA GPUs |
| 2025-03-19 | Test Scripts | Added test scripts for audio capture and IDE integration |
| 2025-03-19 | Git Repository | Set up Git repository with proper branching strategy |
| 2025-03-19 | Tabbed Interface | Implemented tabbed interface with Main, Settings, Devices, and Help tabs |
| 2025-03-19 | UI Enhancements | Added scrollable tabs, keyboard shortcuts, and improved button functionality |
| 2025-03-19 | Genie Image Update | Updated Genie image with transparent background and improved animations |
| 2025-03-19 | Tray Icon Fix | Fixed tray icon path in main.js to use the correct Genie image |
| 2025-03-20 | Audio Device Configuration | Configured Focusrite Clarett 4 Pre as default audio device |
| 2025-03-20 | Transcription Preview Fix | Fixed transcription preview display in the UI |
| 2025-03-20 | Enhanced VAD Implementation | Implemented hybrid VAD approach using both Silero and WebRTC for better noise filtering |
| 2025-03-20 | Improved Wake Word Detection | Enhanced wake word detection with similarity matching and consecutive detection confirmation |
| 2025-03-20 | PyTorch Audio Installation Fix | Created documentation and scripts for resolving PyTorch audio installation issues while maintaining correct branch |
| 2025-03-20 | Dependency Management Best Practices | Created comprehensive documentation on best practices for integrating dependency management into the application |
| 2025-03-20 | PyTorch CUDA Installation | Successfully installed PyTorch with CUDA support for the RTX 4090, fixed NumPy compatibility issues, and resolved f-string syntax errors in IDE integration |
| 2025-03-20 | Enhanced Setup Script | Improved setup_env.ps1 with robust error handling, dependency verification, automatic recovery, and custom PyTorch installation script support |
| 2025-03-20 | Integrated Dependency Management | Implemented comprehensive dependency management system with automatic recovery for seamless user experience |
| 2025-03-20 | Enhanced UI Experience | Improved animations and visual feedback for Genie avatar, waveform visualization, and transcription preview |
| 2025-03-22 | Enhanced IDE Integration | Added support for more IDEs (Notepad++, Visual Studio, Eclipse) and implemented text formatting for different languages |
| 2025-03-29 | Silero VAD Model Issue | Identified issue with Silero VAD model download (404 and 401 errors), created alternative download script and documented the issue |
| 2025-03-29 | Jarvis-Like Assistant Plan | Created comprehensive plan to transform Genie Whisper into a full Jarvis-like voice assistant with global system integration |
| 2025-03-29 | Tech Stack Research | Documented current available technologies for implementing a Jarvis-like assistant |
| 2025-03-29 | TTS Integration Analysis | Analyzed Mozilla TTS and Spark-TTS options for voice output capabilities |

## Next Steps

### Immediate Tasks (Next 1-2 Weeks)
1. **Fix Core Audio Pipeline** (Current Focus)
   - Resolve Silero VAD model download issues (use WebRTC VAD as fallback) ✅
   - Implement working audio capture from microphone
   - Connect to Whisper for transcription
   - Create basic preview display
   - Implement text output to active application

2. **Add Text-to-Speech Capabilities**
   - Integrate Mozilla TTS as primary TTS engine
   - Create voice selection system
   - Implement speech output pipeline
   - Test voice quality and latency
   - Add response generation system
   - Design pluggable architecture to support future Spark-TTS integration

3. **Create Minimal Viable Product**
   - Implement system tray application
   - Add global hotkey activation
   - Create floating UI with microphone button
   - Implement basic settings (microphone selection, model selection)
   - Add clipboard integration for universal compatibility

4. **Test Basic Functionality**
   - Test with different microphones
   - Test in different applications
   - Measure transcription accuracy
   - Optimize for latency
   - Fix critical bugs

### Short-Term Goals (Next 3-4 Weeks)

1. **Implement Command Recognition System**
   - Create command parsing from transcribed text
   - Build command registry system
   - Add built-in commands for system control
   - Implement context-aware command execution
   - Add custom command creation

2. **Begin AI Agent Integration**
   - Research Roo Code API integration
   - Create proof-of-concept for voice commands to AI
   - Implement basic context passing
   - Test with simple AI interactions
   - Add voice responses from AI agents

3. **Add Global System Integration**
   - Implement application launching
   - Add file and folder operations
   - Create system settings control
   - Implement media playback control
   - Add window management functions

4. **Create Desktop Hub Implementation**
   - Create central configuration system
   - Implement system status monitoring
   - Add notification center integration
   - Create cross-application context awareness
   - Implement device discovery for future expansion

## Active Decisions and Considerations

### Technical Decisions Under Consideration

1. **Whisper Model Selection**
   - **Current Decision**: Start with base model, allow user selection
   - **Considerations**: Performance vs. accuracy, disk space, memory usage
   - **Status**: Implemented model selection, need to test performance with RTX 4090

2. **VAD Implementation**
   - **Current Decision**: Using hybrid approach with both Silero VAD and WebRTC VAD for enhanced noise filtering
   - **Considerations**: Accuracy, performance, resource usage
   - **Status**: Implemented enhanced hybrid approach, merging speech segments from both VADs for better accuracy
   - **New Issue**: Silero VAD model download failing with 404/401 errors, need to find alternative source or implement fallback

3. **Wake Word Detection**
   - **Current Decision**: Using enhanced Whisper for wake word detection with similarity matching, with improved Porcupine as fallback
   - **Considerations**: Accuracy, latency, resource usage
   - **Status**: Enhanced implementation with similarity matching and consecutive detection confirmation

4. **IDE Integration**
   - **Current Decision**: Using clipboard-based approach with fallback, added support for more IDEs and text formatting
   - **Considerations**: Compatibility, reliability, security
   - **Status**: Enhanced implementation with support for multiple IDEs and text formatting for different languages

5. **Audio Device Selection**
   - **Current Decision**: Added support for selecting specific audio devices, configured Focusrite Clarett 4 Pre as default
   - **Considerations**: Compatibility with professional audio interfaces
   - **Status**: Implemented device selection, configured Focusrite as default, tested with success

6. **GPU Acceleration**
   - **Current Decision**: Added support for GPU acceleration with compute type selection
   - **Considerations**: Performance improvement, compatibility with different GPUs
   - **Status**: Implemented GPU support, successfully tested with RTX 4090

7. **Dependency Management**
   - **Current Decision**: Implemented comprehensive dependency management system with automatic recovery
   - **Considerations**: Reliability, cross-platform compatibility, ease of use, user experience
   - **Status**: Implemented dependency_manager.py and auto_recovery.py modules, integrated into server.py for seamless user experience

8. **UI Animation and Feedback**
   - **Current Decision**: Enhanced animations for Genie avatar, waveform visualization, and transcription preview
   - **Considerations**: Performance, visual appeal, user experience
   - **Status**: Implemented advanced animations with dynamic effects and improved visual feedback

9. **Text-to-Speech Engine** (Updated)
   - **Current Decision**: Primary implementation with Mozilla TTS, design for future Spark-TTS integration
   - **Considerations**: 
     - Mozilla TTS: Good quality, better documentation, lower resources, limited languages
     - Spark-TTS: Excellent quality, voice cloning, higher resources, limited to English/Chinese
   - **Status**: Analyzed options, created integration plan with pluggable architecture

10. **System Integration Framework** (New)
    - **Current Decision**: Using Electron with Node.js for cross-platform compatibility
    - **Considerations**: Performance, resource usage, development speed
    - **Status**: Planning phase, evaluating implementation approach

### Open Questions

1. **Performance Optimization**
   - How to best utilize the RTX 4090 for transcription?
   - What's the optimal buffer size for high-quality audio input?
   - How to balance transcription accuracy vs. speed?
   - How to manage resource sharing between STT and TTS on GPU?

2. **UI/UX Refinement**
   - What additional customization options would be useful for users?
   - How to further improve the visual experience?
   - What accessibility features should be added?

3. **Cross-Platform Compatibility**
   - How to ensure consistent behavior across different operating systems?
   - What platform-specific issues need to be addressed?
   - How to handle different audio APIs on different platforms?

4. **System Integration** (New)
   - What's the best approach for global system control?
   - How to handle security and permissions?
   - What level of system access is appropriate?

5. **AI Agent Communication** (New)
   - How to design an effective voice interface for AI agents?
   - What context information is most valuable to pass to AI?
   - How to format voice responses from AI agents?

6. **TTS Voice Selection** (New)
   - Which voices provide the best balance of quality and performance?
   - Should we allow users to create custom voices with Spark-TTS in the future?
   - How to handle multilingual support with limited language models?

### Current Challenges

1. **Transcription Latency**
   - Reducing the delay between speech and transcription
   - Optimizing the audio processing pipeline
   - Balancing accuracy and speed

2. **Wake Word Accuracy**
   - Improving the accuracy of wake word detection
   - Reducing false positives and negatives
   - Handling different accents and environments

3. **Resource Usage**
   - Minimizing CPU and memory usage
   - Optimizing for battery life on laptops
   - Ensuring smooth performance on lower-end systems
   - Balancing resources between STT and TTS components

4. **Audio Quality**
   - Ensuring optimal audio capture from professional microphones
   - Handling different audio interfaces and settings
   - Optimizing for different voice types and environments
   - Producing natural-sounding TTS output

5. **Dependency Management** (Completed)
   - ~~Resolving PyTorch audio installation issues~~ ✅
   - ~~Preventing branch switching problems during dependency installation~~ ✅
   - ~~Installing PyTorch with CUDA support for RTX 4090~~ ✅
   - ~~Enhancing setup scripts with robust error handling and recovery~~ ✅
   - ~~Maintaining consistent development environment across team members~~ ✅
   - ~~Implementing integrated dependency management based on best practices~~ ✅
   - ~~Ensuring robust error handling and recovery for dependency issues~~ ✅

6. **Silero VAD Model Availability** (New)
   - Silero VAD model download failing with 404/401 errors
   - Repository URLs have changed or access has been restricted
   - Need to find alternative sources or implement fallback mechanisms
   - Created alternative download script with multiple source attempts
   - May need to consider bundling the model with the application

7. **Text-to-Speech Integration** (New)
   - Selecting appropriate TTS engine
   - Ensuring natural-sounding voice output
   - Minimizing latency for conversational interaction
   - Handling different languages and accents
   - Managing voice resources efficiently
   - Creating pluggable architecture for future enhancements

## Development Environment Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Project Repository** | Active | GitHub repository set up with proper branching |
| **Frontend UI** | Implemented | Core components created and styled with enhanced animations |
| **Backend Integration** | Implemented | Python backend with Whisper, VAD, and IDE integration |
| **Audio Device Support** | Implemented | Added support for professional audio interfaces |
| **GPU Acceleration** | Implemented | Added support for NVIDIA GPUs, tested with RTX 4090 |
| **Dependency Management** | Completed | Implemented comprehensive system with automatic recovery |
| **UI Experience** | Enhanced | Improved animations and visual feedback for all components |
| **IDE Integration** | Enhanced | Added support for more IDEs and text formatting |
| **IDE Extensions** | Not Started | Will follow backend implementation |
| **Build Configuration** | In Progress | Basic Electron setup complete |
| **Text-to-Speech** | Researched | Analyzed Mozilla TTS and Spark-TTS options |
| **Global System Integration** | Not Started | Planned for short-term implementation |
| **AI Agent Communication** | Not Started | Planned for short-term implementation |
| **Local Knowledge Base** | Not Started | Planned for medium-term implementation |

## Team Focus

| Team Member | Current Focus | Next Up |
|-------------|--------------|---------|
| **Lead Developer** | Core Audio Pipeline | Text-to-Speech Integration |
| **Frontend Developer** | UI refinement | System Tray Application |
| **ML Engineer** | Whisper optimization | TTS Implementation |
| **DevOps** | Build configuration | Cross-platform support |

## Current Blockers

- Silero VAD model download failing with 404/401 errors (Workaround implemented: WebRTC VAD fallback)
- No working end-to-end functionality yet (Next focus: Create minimal viable product)
- Need to implement text-to-speech capabilities (Researched options: Mozilla TTS and Spark-TTS)
- Need to implement global system integration (Planned for short-term implementation)