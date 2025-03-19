#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wake Word Detection module for Genie Whisper.
This module provides wake word detection functionality.
"""

import logging
import os
import sys
import time
import numpy as np
import threading
import queue
from typing import Optional, Callable, List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class WhisperWakeWordDetector:
    """Wake word detection using Whisper for transcription."""
    
    def __init__(
        self,
        wake_word: str = "Hey Genie",
        threshold: float = 0.7,
        sample_rate: int = 16000,
        buffer_duration: float = 3.0
    ):
        """Initialize the wake word detector.
        
        Args:
            wake_word: Wake word or phrase to detect
            threshold: Confidence threshold (0.0-1.0)
            sample_rate: Audio sample rate in Hz
            buffer_duration: Audio buffer duration in seconds
        """
        self.wake_word = wake_word.lower()
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration
        self.buffer_size = int(sample_rate * buffer_duration)
        
        self.audio_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.buffer_index = 0
        
        self.is_listening = False
        self.callback = None
        self.listening_thread = None
        
        # Import Whisper here to avoid circular imports
        try:
            from faster_whisper import WhisperModel
            
            # Check if models directory exists
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Load a small model for wake word detection
            self.model = WhisperModel(
                model_size_or_path="tiny",
                device="cpu",
                compute_type="int8",
                download_root=models_dir
            )
            
            logger.info("Whisper wake word detector initialized")
            
        except ImportError:
            logger.error("Failed to import faster_whisper. Wake word detection will not work.")
            self.model = None
    
    def add_audio(self, audio: np.ndarray) -> None:
        """Add audio to the buffer.
        
        Args:
            audio: Numpy array of audio samples
        """
        # Calculate how much audio to add
        audio_length = len(audio)
        space_left = self.buffer_size - self.buffer_index
        
        if audio_length <= space_left:
            # Add all audio to buffer
            self.audio_buffer[self.buffer_index:self.buffer_index + audio_length] = audio
            self.buffer_index += audio_length
        else:
            # Add as much as possible
            self.audio_buffer[self.buffer_index:] = audio[:space_left]
            
            # Wrap around to beginning of buffer
            remaining = audio_length - space_left
            self.audio_buffer[:remaining] = audio[space_left:]
            self.buffer_index = remaining
    
    def reset_buffer(self) -> None:
        """Reset the audio buffer."""
        self.audio_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.buffer_index = 0
    
    def detect_wake_word(self, audio: Optional[np.ndarray] = None) -> bool:
        """Detect wake word in audio.
        
        Args:
            audio: Numpy array of audio samples (uses buffer if None)
            
        Returns:
            True if wake word is detected, False otherwise
        """
        if self.model is None:
            logger.error("Whisper model not loaded")
            return False
        
        try:
            # Use provided audio or buffer
            if audio is None:
                audio = self.audio_buffer
            
            # Transcribe audio
            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=1,
                vad_filter=True
            )
            
            # Combine segments
            text = " ".join(segment.text for segment in segments).lower()
            
            # Check if wake word is in transcription
            detected = self.wake_word in text
            
            if detected:
                logger.info(f"Wake word detected: '{text}'")
            
            return detected
            
        except Exception as e:
            logger.error(f"Error detecting wake word: {e}")
            return False
    
    def start_listening(self, callback: Callable[[np.ndarray], None]) -> None:
        """Start listening for wake word.
        
        Args:
            callback: Function to call when wake word is detected
        """
        if self.is_listening:
            logger.warning("Already listening for wake word")
            return
        
        self.is_listening = True
        self.callback = callback
        
        # Reset buffer
        self.reset_buffer()
        
        # Start listening thread
        self.listening_thread = threading.Thread(target=self._listening_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        logger.info("Started listening for wake word")
    
    def stop_listening(self) -> None:
        """Stop listening for wake word."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        # Wait for thread to finish
        if self.listening_thread:
            self.listening_thread.join(timeout=1.0)
            self.listening_thread = None
        
        logger.info("Stopped listening for wake word")
    
    def _listening_loop(self) -> None:
        """Continuously listen for wake word."""
        import sounddevice as sd
        
        # Create a queue for audio data
        audio_queue = queue.Queue()
        
        # Callback for audio stream
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            
            # Add audio to queue
            audio_queue.put(indata.copy())
        
        # Start audio stream
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=audio_callback
            ):
                logger.info("Wake word audio stream started")
                
                # Process audio in chunks
                while self.is_listening:
                    try:
                        # Get audio from queue with timeout
                        audio = audio_queue.get(timeout=0.5)
                        
                        # Add audio to buffer
                        self.add_audio(audio.squeeze())
                        
                        # Check for wake word every 0.5 seconds
                        if audio_queue.qsize() == 0:
                            if self.detect_wake_word():
                                # Wake word detected, call callback
                                if self.callback:
                                    self.callback(self.audio_buffer)
                                
                                # Reset buffer
                                self.reset_buffer()
                    
                    except queue.Empty:
                        # No audio available, continue
                        pass
                    
                    except Exception as e:
                        logger.error(f"Error in wake word listening loop: {e}")
                
                logger.info("Wake word audio stream stopped")
                
        except Exception as e:
            logger.error(f"Error starting wake word audio stream: {e}")
            self.is_listening = False


class PorcupineWakeWordDetector:
    """Wake word detection using Picovoice Porcupine."""
    
    def __init__(
        self,
        access_key: Optional[str] = None,
        keyword_path: Optional[str] = None,
        sensitivity: float = 0.5,
        sample_rate: int = 16000
    ):
        """Initialize the wake word detector.
        
        Args:
            access_key: Picovoice access key
            keyword_path: Path to keyword file (.ppn)
            sensitivity: Detection sensitivity (0.0-1.0)
            sample_rate: Audio sample rate in Hz
        """
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.sensitivity = sensitivity
        self.sample_rate = sample_rate
        
        self.porcupine = None
        self.is_listening = False
        self.callback = None
        self.listening_thread = None
        
        # Try to load Porcupine
        self._load_porcupine()
    
    def _load_porcupine(self) -> None:
        """Load Porcupine wake word engine."""
        try:
            import pvporcupine
            
            # Check if we have a keyword path or use built-in
            if self.keyword_path:
                # Custom keyword
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=[self.keyword_path],
                    sensitivities=[self.sensitivity]
                )
            else:
                # Use built-in "Hey Genie" or "Computer" as fallback
                try:
                    self.porcupine = pvporcupine.create(
                        access_key=self.access_key,
                        keywords=["jarvis"],
                        sensitivities=[self.sensitivity]
                    )
                except:
                    # Try "Computer" as fallback
                    self.porcupine = pvporcupine.create(
                        access_key=self.access_key,
                        keywords=["computer"],
                        sensitivities=[self.sensitivity]
                    )
            
            logger.info(f"Porcupine wake word detector initialized with sensitivity {self.sensitivity}")
            
        except ImportError:
            logger.error("Failed to import pvporcupine. Wake word detection will not work.")
            self.porcupine = None
        except Exception as e:
            logger.error(f"Error loading Porcupine: {e}")
            self.porcupine = None
    
    def detect_wake_word(self, audio: np.ndarray) -> bool:
        """Detect wake word in audio.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            True if wake word is detected, False otherwise
        """
        if self.porcupine is None:
            logger.error("Porcupine not loaded")
            return False
        
        try:
            # Convert audio to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Process audio in frames
            frame_length = self.porcupine.frame_length
            
            for i in range(0, len(audio_int16) - frame_length + 1, frame_length):
                frame = audio_int16[i:i+frame_length]
                
                # Ensure frame is the right size
                if len(frame) == frame_length:
                    # Process frame
                    result = self.porcupine.process(frame)
                    
                    # Check result
                    if result >= 0:
                        logger.info("Wake word detected")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting wake word: {e}")
            return False
    
    def start_listening(self, callback: Callable[[], None]) -> None:
        """Start listening for wake word.
        
        Args:
            callback: Function to call when wake word is detected
        """
        if self.porcupine is None:
            logger.error("Porcupine not loaded")
            return
        
        if self.is_listening:
            logger.warning("Already listening for wake word")
            return
        
        self.is_listening = True
        self.callback = callback
        
        # Start listening thread
        self.listening_thread = threading.Thread(target=self._listening_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        logger.info("Started listening for wake word")
    
    def stop_listening(self) -> None:
        """Stop listening for wake word."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        # Wait for thread to finish
        if self.listening_thread:
            self.listening_thread.join(timeout=1.0)
            self.listening_thread = None
        
        logger.info("Stopped listening for wake word")
    
    def _listening_loop(self) -> None:
        """Continuously listen for wake word."""
        import sounddevice as sd
        
        # Frame length required by Porcupine
        frame_length = self.porcupine.frame_length
        
        # Callback for audio stream
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            
            try:
                # Convert audio to int16
                audio_int16 = (indata.squeeze() * 32767).astype(np.int16)
                
                # Process audio
                result = self.porcupine.process(audio_int16)
                
                # Check result
                if result >= 0 and self.callback:
                    # Wake word detected, call callback
                    self.callback()
                    
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
        
        # Start audio stream
        try:
            with sd.InputStream(
                samplerate=self.porcupine.sample_rate,
                channels=1,
                dtype='float32',
                blocksize=frame_length,
                callback=audio_callback
            ):
                logger.info("Wake word audio stream started")
                
                # Keep stream open while listening
                while self.is_listening:
                    time.sleep(0.1)
                
                logger.info("Wake word audio stream stopped")
                
        except Exception as e:
            logger.error(f"Error starting wake word audio stream: {e}")
            self.is_listening = False
    
    def __del__(self):
        """Clean up resources."""
        if self.porcupine:
            self.porcupine.delete()


def create_wake_word_detector(detector_type: str = "whisper", **kwargs) -> Optional[object]:
    """Create a wake word detector instance.
    
    Args:
        detector_type: Type of detector to create ("whisper" or "porcupine")
        **kwargs: Additional arguments for the detector
        
    Returns:
        Wake word detector instance or None if creation fails
    """
    try:
        if detector_type.lower() == "whisper":
            return WhisperWakeWordDetector(**kwargs)
        elif detector_type.lower() == "porcupine":
            return PorcupineWakeWordDetector(**kwargs)
        else:
            logger.error(f"Unknown wake word detector type: {detector_type}")
            return None
    except Exception as e:
        logger.error(f"Error creating wake word detector: {e}")
        return None


if __name__ == "__main__":
    # Test wake word detection
    import sounddevice as sd
    
    # Create detector
    detector = create_wake_word_detector("whisper", wake_word="Hey Genie")
    
    # Callback function
    def wake_word_callback(audio):
        print("Wake word detected!")
    
    # Start listening
    detector.start_listening(wake_word_callback)
    
    # Keep listening for 30 seconds
    print("Listening for wake word for 30 seconds...")
    time.sleep(30)
    
    # Stop listening
    detector.stop_listening()