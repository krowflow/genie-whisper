# Genie Whisper Test Scripts

This directory contains test scripts for verifying the functionality of various components of the Genie Whisper application.

## Overview

These test scripts are designed to verify that the core components of Genie Whisper are working correctly, including:

- Whisper transcription model
- Voice Activity Detection (VAD)
- IDE integration

## Test Scripts

### `test_whisper.py`

Tests the Whisper transcription model to ensure it can be loaded and used for transcription. This script:

- Loads the Whisper model with optimized settings
- Detects if CUDA is available and configures the model accordingly
- Performs a simple transcription test
- Reports performance metrics

### `test_vad.py`

Tests the Voice Activity Detection (VAD) functionality to ensure it can detect speech in audio. This script:

- Tests the WebRTC VAD implementation
- Tests a wrapper class that provides enhanced functionality
- Verifies speech detection in silence and noise
- Tests audio filtering to keep only speech segments

### `test_ide_integration.py`

Tests the IDE integration functionality to ensure text can be injected into IDEs. This script:

- Tests clipboard functionality
- Tests text injection into IDEs
- Simulates keyboard shortcuts for paste operations

## Dependency Installation

To resolve dependency installation issues, we've taken the following approach:

1. Created a dedicated virtual environment for the project:
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Split dependencies into smaller, more manageable groups:
   - `requirements-minimal.txt`: Core dependencies (numpy, scipy, sounddevice, pyaudio)
   - `requirements-whisper.txt`: Whisper and related dependencies

3. Installed dependencies with extended timeout to handle large packages:
   ```
   pip install --timeout 120 -r requirements-minimal.txt
   pip install --timeout 120 -r requirements-whisper.txt
   ```

4. Used CPU-only versions of PyTorch when GPU versions caused timeout issues:
   ```
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

## Running the Tests

To run the tests, activate the virtual environment and execute the test scripts:

```
.\.venv\Scripts\Activate.ps1
python test_whisper.py
python test_vad.py
python test_ide_integration.py
```

## Troubleshooting

If you encounter issues with the tests:

1. Ensure the virtual environment is activated
2. Verify all dependencies are installed
3. Check the console output for specific error messages
4. For GPU-related issues, try using CPU-only versions of the dependencies

## Next Steps

After verifying that all components are working correctly, the next steps are:

1. Implement advanced Genie animations with lip-sync
2. Optimize performance for real-time transcription
3. Add more visual feedback for user actions
4. Implement proper error handling and recovery
5. Create comprehensive test suite