# GenieHome Integration Documentation

## Overview

This document describes the integration of the GenieHome component as the main UI for the Genie Whisper application. The GenieHome component provides a modern, glassmorphism-style interface with real-time audio visualization that reacts to microphone input.

## Components

### Main Components

1. **GenieHome**: The main page component that displays the Genie avatar, waveform visualization, and status indicators.
2. **AppContainer**: A container component that wraps GenieHome and adds the draggable header for window controls.
3. **DraggableHeader**: Provides window controls (minimize, close) and settings button.

### Supporting Components

1. **GlassWaveformHUD**: A glassmorphism-style waveform visualization that reacts to audio input.
2. **GlassStatusIndicator**: Shows the current listening status ("Listening..." or "Waiting...").
3. **GenieAvatar**: Displays the Genie character with animations that react to audio input.

## Audio Processing

The application uses a WebSocket connection to receive real-time audio loudness data from the Python backend:

1. **websocket_server.py**: Captures microphone audio, calculates loudness, and broadcasts it to connected clients.
2. **AudioListener.ts**: Connects to the WebSocket server and provides React hooks for components to access audio data.

## Integration Flow

1. The application starts with `index.tsx`, which renders the `AppContainer` component.
2. `AppContainer` renders the `DraggableHeader` and `GenieHome` components.
3. `GenieHome` connects to the WebSocket server using `useAudioListener` hook.
4. Real-time audio data flows from the WebSocket server to the UI components.

## File Structure

```
src/
├── components/
│   ├── DraggableHeader.tsx    # Window controls
│   ├── GenieAvatar.tsx        # Animated Genie character
│   ├── GlassWaveformHUD.tsx   # Audio visualization
│   └── GlassStatusIndicator.tsx # Status display
├── listeners/
│   └── AudioListener.ts       # WebSocket connection to audio server
├── pages/
│   └── GenieHome.tsx          # Main page component
├── styles/
│   └── main.css               # Global styles
├── AppContainer.tsx           # Main container component
└── index.tsx                  # Application entry point
```

## WebSocket Protocol

The WebSocket server sends JSON messages with the following format:

```json
{
  "type": "loudness",
  "value": 0.75,  // Normalized loudness value between 0.0 and 1.0
  "timestamp": 1620000000.123  // Unix timestamp
}
```

## Development

To start the development environment:

1. Run the WebSocket server: `python websocket_server.py`
2. Run the frontend development server: `npm run dev`

Alternatively, use the provided `start-dev.bat` script to start both servers simultaneously.

## Troubleshooting

- If the waveform doesn't react to audio, check that the WebSocket server is running on port 8000.
- If the Genie avatar doesn't appear, check that the image path is correct in `GenieAvatar.tsx`.
- If the WebSocket connection fails, the UI will fall back to simulated audio data.
