# Python-Electron Communication in Genie Whisper

## Overview

This document describes the communication protocol between the Python backend and Electron frontend in the Genie Whisper application. The implementation ensures clean separation of data channels and robust error handling to prevent crashes.

## Communication Architecture

### Python Backend

The Python backend (`server.py`) communicates with the Electron frontend through standard I/O streams:

1. **stdout**: Used exclusively for sending structured JSON messages to Electron
2. **stderr**: Used for logging and error messages
3. **stdin**: Used to receive commands from Electron

### Electron Frontend

The Electron frontend (`main.js`) spawns the Python process and handles its output streams:

1. **stdout**: Parsed as JSON messages and forwarded to the renderer process
2. **stderr**: Logged to the console for debugging
3. **stdin**: Used to send commands to the Python process

## Implementation Details

### Python Backend

The Python backend follows these principles:

1. **Logging Configuration**:
   ```python
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s [%(levelname)s] %(message)s",
       handlers=[logging.StreamHandler(sys.stderr)]
   )
   ```

2. **Message Sending**:
   ```python
   def _send_message(self, message: Dict) -> None:
       """Send a message to the frontend."""
       try:
           print(json.dumps(message), flush=True)
       except Exception as e:
           logger.error(f"Error sending message: {e}")
   ```

### Electron Frontend

The Electron frontend uses a more robust approach to handle Python process I/O:

1. **Process Spawning**:
   ```javascript
   const pythonSpawnProcess = spawn(pythonPath, pythonArgs, {
     stdio: ['pipe', 'pipe', 'pipe']
   });
   ```

2. **stdout Handling**:
   ```javascript
   pythonSpawnProcess.stdout.on('data', (data) => {
     const lines = data.toString().trim().split('\n').filter(Boolean);
     
     lines.forEach(line => {
       try {
         // Parse message as JSON
         const jsonData = JSON.parse(line);
         
         // Forward messages to renderer
         if (mainWindow) {
           mainWindow.webContents.send('python-message', line);
         }
       } catch (error) {
         // Log parsing errors without crashing
         console.error('Invalid JSON from Python stdout:', line);
       }
     });
   });
   ```

3. **stderr Handling**:
   ```javascript
   pythonSpawnProcess.stderr.on('data', (data) => {
     // Log Python stderr output to console
     console.log('[Python stderr]', data.toString().trim());
   });
   ```

## Message Format

All messages between Python and Electron are JSON objects with a `type` field indicating the message type:

```json
{
  "type": "status",
  "status": "Listening"
}
```

Common message types include:
- `status`: Status updates from the Python backend
- `transcription`: Transcription results
- `text_injected`: Result of text injection into an IDE
- `wake_word_detected`: Notification that the wake word was detected

## Error Handling

The implementation includes robust error handling:

1. **Python Side**:
   - JSON encoding errors are caught and logged to stderr
   - Invalid commands are logged but don't crash the server

2. **Electron Side**:
   - JSON parsing errors are caught and logged without crashing
   - Process errors are handled gracefully
   - Multiple lines in a single data chunk are processed correctly

## Benefits of This Approach

1. **Stability**: The application doesn't crash on malformed JSON or unexpected output
2. **Debuggability**: Logs are clearly separated from data messages
3. **Robustness**: Handles multi-line output and partial JSON chunks
4. **Maintainability**: Clear separation of concerns between data and logs

## Troubleshooting

If communication issues occur:

1. Check the Electron console for stderr output from Python
2. Verify that Python is only sending valid JSON to stdout
3. Ensure the Python process is started with the `-u` flag for unbuffered output
4. Check that path handling is correct, especially for paths with spaces
