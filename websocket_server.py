#!/usr/bin/env python3
"""
Genie Whisper WebSocket Server for Real-time Audio Loudness

This server captures microphone audio, calculates loudness values,
and broadcasts them to connected WebSocket clients in real-time.

Usage:
    python websocket_server.py

Requirements:
    pip install websockets sounddevice numpy
"""

import asyncio
import json
import logging
import signal
import sys
import time
from typing import Dict, List, Set, Any

import numpy as np
import sounddevice as sd
import websockets
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("websocket_server")

# Audio configuration
SAMPLE_RATE = 16000  # Hz
CHANNELS = 1  # Mono
DTYPE = 'float32'
BLOCK_DURATION = 0.03  # seconds (30ms blocks)
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION)

# WebSocket configuration
WS_HOST = "localhost"
WS_PORT = 8000

# Global state
connected_clients: Set[WebSocketServerProtocol] = set()
audio_queue: asyncio.Queue = asyncio.Queue()
running = True


class AudioProcessor:
    """Handles audio processing and loudness calculation."""
    
    def __init__(self):
        self.stream = None
        self.calibration_factor = 2.0  # Adjust this to normalize loudness
        self.silence_threshold = 0.01  # Threshold below which audio is considered silence
        
    def start_stream(self):
        """Start the audio input stream."""
        try:
            self.stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                blocksize=BLOCK_SIZE,
                callback=self.audio_callback
            )
            self.stream.start()
            logger.info(f"Audio stream started: {SAMPLE_RATE}Hz, {CHANNELS} channel(s)")
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
            raise
    
    def stop_stream(self):
        """Stop the audio input stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            logger.info("Audio stream stopped")
    
    def audio_callback(self, indata, frames, time_info, status):
        """Process incoming audio data and put loudness in queue."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Calculate loudness (root mean square of the audio chunk)
        loudness = self.calculate_loudness(indata)
        
        # Put loudness in queue for broadcasting
        try:
            audio_queue.put_nowait({
                "type": "loudness",
                "value": loudness,
                "timestamp": time.time()
            })
        except asyncio.QueueFull:
            # If queue is full, we're processing too slowly - log and continue
            logger.warning("Audio queue full, dropping frame")
    
    def calculate_loudness(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate normalized loudness from audio chunk.
        
        Returns:
            float: Loudness value between 0.0 and 1.0
        """
        # Calculate RMS (root mean square)
        rms = np.sqrt(np.mean(np.square(audio_chunk)))
        
        # Apply calibration to normalize
        normalized = min(1.0, rms * self.calibration_factor)
        
        # Apply silence threshold
        if normalized < self.silence_threshold:
            return 0.0
            
        return float(normalized)


async def broadcast_loudness():
    """Continuously broadcast loudness values to all connected clients."""
    while running:
        try:
            # Get loudness data from queue
            data = await audio_queue.get()
            
            # Prepare message
            message = json.dumps(data)
            
            # Broadcast to all connected clients
            if connected_clients:
                # Create tasks for each client to avoid blocking
                await asyncio.gather(
                    *[
                        asyncio.create_task(send_to_client(client, message))
                        for client in connected_clients
                    ],
                    return_exceptions=True
                )
            
            # Mark task as done
            audio_queue.task_done()
            
        except Exception as e:
            logger.error(f"Error in broadcast_loudness: {e}")
            await asyncio.sleep(0.1)  # Prevent tight loop on error


async def send_to_client(client: WebSocketServerProtocol, message: str):
    """Send message to a client, handling disconnections gracefully."""
    try:
        await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        # Client disconnected - will be removed in handler
        pass
    except Exception as e:
        logger.error(f"Error sending to client: {e}")
        # Remove problematic client
        if client in connected_clients:
            connected_clients.remove(client)


async def handle_client(websocket: WebSocketServerProtocol, path: str):
    """Handle a WebSocket client connection."""
    client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    
    try:
        # Register new client
        connected_clients.add(websocket)
        logger.info(f"New WebSocket client connected: {client_info}")
        
        # Keep connection open until client disconnects
        try:
            await websocket.wait_closed()
        finally:
            # Client disconnected
            if websocket in connected_clients:
                connected_clients.remove(websocket)
            logger.info(f"Client disconnected: {client_info}")
    
    except Exception as e:
        logger.error(f"Error handling client {client_info}: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)


async def main():
    """Main entry point for the WebSocket server."""
    global running
    
    # Initialize audio processor
    audio_processor = AudioProcessor()
    
    try:
        # Start audio stream
        audio_processor.start_stream()
        
        # Start WebSocket server
        async with websockets.serve(
            handle_client, WS_HOST, WS_PORT
        ):
            logger.info(f"WebSocket server started at ws://{WS_HOST}:{WS_PORT}")
            
            # Start broadcasting task
            broadcast_task = asyncio.create_task(broadcast_loudness())
            
            # Keep server running until interrupted
            while running:
                await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Clean shutdown
        running = False
        
        # Stop audio stream
        audio_processor.stop_stream()
        
        # Wait for broadcast task to complete
        if 'broadcast_task' in locals():
            broadcast_task.cancel()
            try:
                await broadcast_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Server shutdown complete")


def handle_shutdown(sig, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info(f"Received signal {sig}, shutting down...")
    running = False


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server terminated by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
