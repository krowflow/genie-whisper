#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Genie Whisper Python Backend Server
This script handles audio capture, processing, and transcription using Whisper.
"""

import argparse
import json
import logging
import os
import sys
import threading
import time
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Try to import required packages
try:
    import numpy as np
    import sounddevice as sd
    from faster_whisper import WhisperModel
except ImportError as e:
    logger.error(f"Failed to import required packages: {e}")
    logger.error("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)

class AudioProcessor:
    """Handles audio capture and processing."""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 4000):
        """Initialize the audio processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_buffer = []
        self.is_recording = False
        self.recording_thread = None
        
    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        self.is_recording = True
        self.audio_buffer = []
        
        def record_audio():
            """Record audio in a separate thread."""
            logger.info("Starting audio recording")
            
            try:
                with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32',
                    callback=self._audio_callback
                ):
                    logger.info("Audio stream started")
                    
                    # Keep the stream open while recording
                    while self.is_recording:
                        time.sleep(0.1)
                        
            except Exception as e:
                logger.error(f"Error recording audio: {e}")
                self.is_recording = False
                
            logger.info("Audio recording stopped")
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return the recorded audio.
        
        Returns:
            Numpy array of audio samples
        """
        if not self.is_recording:
            logger.warning("Not recording")
            return np.array([])
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
            self.recording_thread = None
        
        # Combine all audio chunks
        if not self.audio_buffer:
            return np.array([])
        
        audio = np.concatenate(self.audio_buffer)
        self.audio_buffer = []
        
        return audio
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Add audio chunk to buffer
        self.audio_buffer.append(indata.copy())
        
        # Process audio (VAD, etc.) could be added here
        
    def get_audio_devices(self) -> List[Dict[str, str]]:
        """Get a list of available audio input devices.
        
        Returns:
            List of dictionaries with device information
        """
        devices = []
        
        try:
            device_list = sd.query_devices()
            for i, device in enumerate(device_list):
                if device['max_input_channels'] > 0:
                    devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'default': device.get('default_input', False)
                    })
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
        
        return devices


class WhisperTranscriber:
    """Handles transcription using Whisper."""
    
    # Model size options
    MODEL_SIZES = ["tiny", "base", "small", "medium", "large"]
    
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """Initialize the transcriber.
        
        Args:
            model_size: Whisper model size
            device: Device to run the model on ("cpu" or "cuda")
        """
        if model_size not in self.MODEL_SIZES:
            logger.warning(f"Invalid model size: {model_size}. Using 'base' instead.")
            model_size = "base"
        
        self.model_size = model_size
        self.device = device
        self.model = None
        
        # Load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model."""
        logger.info(f"Loading Whisper model: {self.model_size}")
        
        try:
            # Check if models directory exists
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Load the model
            self.model = WhisperModel(
                model_size_or_path=self.model_size,
                device=self.device,
                compute_type="int8",  # Use int8 quantization for efficiency
                download_root=models_dir
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio using Whisper.
        
        Args:
            audio: Numpy array of audio samples
            language: Language code (optional)
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            logger.error("Model not loaded")
            return ""
        
        if len(audio) == 0:
            logger.warning("Empty audio")
            return ""
        
        try:
            logger.info("Transcribing audio...")
            
            # Transcribe audio
            segments, info = self.model.transcribe(
                audio,
                language=language,
                beam_size=5,
                vad_filter=True
            )
            
            # Combine segments
            text = " ".join(segment.text for segment in segments)
            
            logger.info(f"Transcription complete: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""


class GenieWhisperServer:
    """Main server class for Genie Whisper."""
    
    def __init__(self, args):
        """Initialize the server.
        
        Args:
            args: Command line arguments
        """
        self.model_size = args.model_size
        self.sensitivity = args.sensitivity
        self.use_vad = args.vad
        self.offline_mode = args.offline
        
        # Initialize components
        self.audio_processor = AudioProcessor()
        self.transcriber = WhisperTranscriber(model_size=self.model_size)
        
        # State
        self.is_listening = False
    
    def start(self) -> None:
        """Start the server."""
        logger.info("Starting Genie Whisper server")
        
        # Send initial status
        self._send_message({
            "type": "status",
            "status": "Server started"
        })
        
        # Main loop
        try:
            while True:
                # Read command from stdin
                command = self._read_command()
                
                if command:
                    self._handle_command(command)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self._cleanup()
    
    def _read_command(self) -> Optional[Dict]:
        """Read command from stdin."""
        try:
            if sys.stdin.isatty():
                # Interactive mode
                line = input()
            else:
                # Non-interactive mode (from Electron)
                line = sys.stdin.readline().strip()
                
            if not line:
                return None
                
            return json.loads(line)
            
        except EOFError:
            # End of input
            sys.exit(0)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
            return None
        except Exception as e:
            logger.error(f"Error reading command: {e}")
            return None
    
    def _handle_command(self, command: Dict) -> None:
        """Handle a command from the frontend."""
        cmd_type = command.get("type")
        
        if cmd_type == "start_listening":
            self._start_listening()
        elif cmd_type == "stop_listening":
            self._stop_listening()
        elif cmd_type == "get_devices":
            self._get_audio_devices()
        elif cmd_type == "update_settings":
            self._update_settings(command.get("settings", {}))
        else:
            logger.warning(f"Unknown command: {cmd_type}")
    
    def _start_listening(self) -> None:
        """Start listening for speech."""
        if self.is_listening:
            return
            
        self.is_listening = True
        self._send_message({
            "type": "status",
            "status": "Listening"
        })
        
        # Start recording
        self.audio_processor.start_recording()
        
        # Start transcription thread
        threading.Thread(target=self._transcription_loop, daemon=True).start()
    
    def _stop_listening(self) -> None:
        """Stop listening for speech."""
        if not self.is_listening:
            return
            
        self.is_listening = False
        self._send_message({
            "type": "status",
            "status": "Stopped listening"
        })
        
        # Stop recording and get final audio
        audio = self.audio_processor.stop_recording()
        
        # Transcribe final audio
        if len(audio) > 0:
            text = self.transcriber.transcribe(audio)
            
            if text:
                self._send_message({
                    "type": "transcription",
                    "text": text,
                    "final": True
                })
    
    def _transcription_loop(self) -> None:
        """Continuously transcribe audio while listening."""
        while self.is_listening:
            # Get current audio buffer (copy)
            audio = np.concatenate(self.audio_processor.audio_buffer) if self.audio_processor.audio_buffer else np.array([])
            
            # Transcribe if we have enough audio
            if len(audio) > 0:
                text = self.transcriber.transcribe(audio)
                
                if text:
                    self._send_message({
                        "type": "transcription",
                        "text": text,
                        "final": False
                    })
            
            # Sleep to avoid excessive CPU usage
            time.sleep(1.0)
    
    def _get_audio_devices(self) -> None:
        """Get available audio devices."""
        devices = self.audio_processor.get_audio_devices()
        
        self._send_message({
            "type": "devices",
            "devices": devices
        })
    
    def _update_settings(self, settings: Dict) -> None:
        """Update server settings."""
        # Update model size if changed
        if "modelSize" in settings and settings["modelSize"] != self.model_size:
            self.model_size = settings["modelSize"]
            self.transcriber = WhisperTranscriber(model_size=self.model_size)
        
        # Update other settings
        if "sensitivity" in settings:
            self.sensitivity = float(settings["sensitivity"])
        
        if "useVAD" in settings:
            self.use_vad = settings["useVAD"]
        
        if "offlineMode" in settings:
            self.offline_mode = settings["offlineMode"]
        
        self._send_message({
            "type": "status",
            "status": "Settings updated"
        })
    
    def _send_message(self, message: Dict) -> None:
        """Send a message to the frontend."""
        try:
            print(json.dumps(message), flush=True)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up")
        
        # Stop recording if active
        if self.is_listening:
            self.audio_processor.stop_recording()
            self.is_listening = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Genie Whisper Backend Server")
    
    parser.add_argument(
        "--model-size",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size"
    )
    
    parser.add_argument(
        "--sensitivity",
        type=float,
        default=0.5,
        help="Voice detection sensitivity (0.0-1.0)"
    )
    
    parser.add_argument(
        "--vad",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Use Voice Activity Detection"
    )
    
    parser.add_argument(
        "--offline",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Use offline mode"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Start the server
    server = GenieWhisperServer(args)
    server.start()