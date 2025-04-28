import sounddevice as sd
import numpy as np
import asyncio
import websockets
import json
import threading
import time
from typing import Optional, Dict, Any

class AudioCapture:
    """
    AudioCapture class for handling microphone input with gain boosting and limiting.
    Supports low-output microphones like the Shure SM7B through adjustable gain boost.
    """
    def __init__(self, sample_rate=16000, channels=1, gain_boost=1.0, websocket_port=6789):
        """
        Initialize the AudioCapture with configurable parameters.

        Args:
            sample_rate (int): Audio sample rate in Hz, default is 16000
            channels (int): Number of audio channels, default is 1 (mono)
            gain_boost (float): Gain multiplier for boosting low-output microphones,
                               default is 1.0 (no boost)
            websocket_port (int): Port for WebSocket server to stream audio levels, default is 6789
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.gain_boost = gain_boost  # Default: no boost (1.0)
        self.stream = None

        # WebSocket server settings
        self.websocket_port = websocket_port
        self.websocket_server = None
        self.websocket_thread = None
        self.websocket_clients = set()
        self.running = False

        # Log initialization
        print(f"AudioCapture initialized with sample_rate={sample_rate}, "
              f"channels={channels}, gain_boost={gain_boost}, websocket_port={websocket_port}")

    def start_stream(self):
        """Start the audio input stream and WebSocket server."""
        self.running = True

        # Start WebSocket server in a separate thread
        self._start_websocket_server()

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                callback=self.audio_callback
            )
            self.stream.start()
            print(f"Audio stream started with gain_boost={self.gain_boost}")
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.running = False
            self._stop_websocket_server()

    def _start_websocket_server(self):
        """Start the WebSocket server in a separate thread."""
        try:
            # Define the WebSocket server handler
            async def websocket_handler(websocket, path):
                """Handle WebSocket connections."""
                try:
                    # Register client
                    self.websocket_clients.add(websocket)
                    print(f"WebSocket client connected: {websocket.remote_address}")

                    # Keep connection open until client disconnects
                    try:
                        await websocket.wait_closed()
                    finally:
                        self.websocket_clients.remove(websocket)
                        print(f"WebSocket client disconnected: {websocket.remote_address}")
                except Exception as e:
                    print(f"WebSocket handler error: {e}")

            # Define the server start function
            async def start_server():
                """Start the WebSocket server."""
                self.websocket_server = await websockets.serve(
                    websocket_handler,
                    "localhost",
                    self.websocket_port
                )
                print(f"WebSocket server started on port {self.websocket_port}")

                # Keep the server running
                while self.running:
                    await asyncio.sleep(1)

                # Close the server when running is False
                if self.websocket_server:
                    self.websocket_server.close()
                    await self.websocket_server.wait_closed()
                    print("WebSocket server closed")

            # Run the server in a separate thread
            def run_websocket_server():
                """Run the WebSocket server in the current thread."""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(start_server())
                except Exception as e:
                    print(f"WebSocket server error: {e}")
                finally:
                    loop.close()

            # Start the WebSocket server thread
            self.websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
            self.websocket_thread.start()

            # Give the server a moment to start
            time.sleep(0.5)

        except Exception as e:
            print(f"Error starting WebSocket server: {e}")

    def audio_callback(self, indata, frames, time, status):
        """
        Process incoming audio data and broadcast loudness over WebSocket.

        Args:
            indata: Input audio data as numpy array
            frames: Number of frames
            time: Timestamp
            status: Status of the stream
        """
        if status:
            print(f"Audio callback status: {status}")

        # Make a copy of the input data to avoid modifying the original
        processed_audio = indata.copy()

        # Apply gain boost if needed (gain_boost > 1.0)
        if self.gain_boost != 1.0:
            # Multiply audio samples by the gain factor
            processed_audio = processed_audio * self.gain_boost

            # Apply limiter to prevent digital clipping after boosting
            # Clip to 16-bit PCM range [-32768, 32767]
            processed_audio = np.clip(processed_audio, -32768, 32767).astype(np.int16)

        # Calculate audio loudness (mean absolute value)
        # Convert to float32 for calculation to avoid integer overflow
        audio_float = processed_audio.astype(np.float32)
        loudness = float(np.mean(np.abs(audio_float)))

        # Normalize loudness to a 0-1000 scale for easier consumption by clients
        # 16-bit audio has values from -32768 to 32767
        normalized_loudness = min(1000, (loudness / 32768) * 1000)

        # Broadcast loudness over WebSocket
        self._broadcast_loudness(normalized_loudness)

        # Here you would pass processed_audio to VAD or further processing
        # For example: self.audio_queue.put(processed_audio)

    def _broadcast_loudness(self, loudness):
        """
        Broadcast the audio loudness to all connected WebSocket clients.

        Args:
            loudness (float): The normalized loudness level (0-1000)
        """
        if not self.websocket_clients:
            return  # No clients connected

        # Create message with loudness and timestamp
        message = json.dumps({
            "loudness": loudness,
            "timestamp": time.time()
        })

        # Broadcast to all clients
        for client in list(self.websocket_clients):
            try:
                # Create a task to send the message (non-blocking)
                asyncio.run_coroutine_threadsafe(
                    client.send(message),
                    asyncio.get_event_loop()
                )
            except Exception as e:
                # Client might be disconnected, remove it
                try:
                    self.websocket_clients.remove(client)
                except:
                    pass

    def stop_stream(self):
        """Stop and close the audio stream and WebSocket server."""
        # Stop the audio stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("Audio stream stopped")

        # Stop the WebSocket server
        self._stop_websocket_server()

    def _stop_websocket_server(self):
        """Stop the WebSocket server."""
        self.running = False

        # Wait for the WebSocket thread to finish
        if self.websocket_thread and self.websocket_thread.is_alive():
            try:
                self.websocket_thread.join(timeout=2.0)
                print("WebSocket server thread stopped")
            except Exception as e:
                print(f"Error stopping WebSocket thread: {e}")

        self.websocket_thread = None
        self.websocket_server = None

    def set_gain_boost(self, gain_value):
        """
        Set a new gain boost value.

        Args:
            gain_value (float): New gain multiplier (1.0 = no boost, 2.0 = double volume, etc.)
        """
        if gain_value < 0:
            print(f"Warning: Negative gain ({gain_value}) not allowed. Setting to 0.")
            gain_value = 0

        self.gain_boost = gain_value
        print(f"Gain boost set to {self.gain_boost}")
