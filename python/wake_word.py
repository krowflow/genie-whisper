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
            
            # Preprocess audio to improve quality
            audio = self._preprocess_audio(audio)
            
            # Transcribe audio with improved parameters
            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=5,  # Increased beam size for better accuracy
                vad_filter=True
            )
            
            # Combine segments
            text = " ".join(segment.text for segment in segments).lower()
            
            # Check for exact match first (fastest path)
            if self.wake_word in text:
                logger.info(f"Wake word 'Hey Genie' detected: '{text}'")
                return True
                
            # If no exact match, check for similar phrases
            similarity = self._calculate_similarity(text)
            
            # Detect based on similarity threshold
            detected = similarity >= self.threshold
            
            if detected:
                logger.info(f"Wake word 'Hey Genie' detected with similarity {similarity:.2f}: '{text}'")
            elif similarity > 0.5:  # Log near misses for debugging
                logger.debug(f"Wake word near miss: '{text}' (similarity: {similarity:.2f})")
            
            return detected
            
        except Exception as e:
            logger.error(f"Error detecting wake word: {e}")
            return False
    
    def _preprocess_audio(self, audio: np.ndarray) -> np.ndarray:
        """Preprocess audio to improve quality for wake word detection.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Preprocessed audio
        """
        try:
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # Apply simple noise reduction
            try:
                from scipy import signal
                
                # Design a high-pass filter (remove frequencies below 80Hz)
                b, a = signal.butter(4, 80/(self.sample_rate/2), 'highpass')
                
                # Apply the filter
                audio = signal.filtfilt(b, a, audio)
                
            except ImportError:
                # If scipy is not available, skip this step
                pass
            
            return audio
            
        except Exception as e:
            logger.warning(f"Error preprocessing audio: {e}")
            return audio
    
    def _calculate_similarity(self, text: str) -> float:
        """Calculate similarity between transcribed text and wake word.
        
        Args:
            text: Transcribed text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Common variations of "Hey Genie"
        variations = [
            "hey genie", "hay genie", "hey jeanie", "hey gini",
            "hey genius", "hey jenny", "hey gini", "hey gene",
            "hey jeannie", "hey jeannie", "hey genie", "hey gini"
        ]
        
        # Check for common variations
        for variation in variations:
            if variation in text:
                # Calculate similarity based on how close the variation is to "hey genie"
                return max(0.8, 1.0 - (len(variation) - len("hey genie")) / len("hey genie"))
        
        # If no variation found, check for partial matches
        words = text.split()
        
        # Look for "hey" followed by something similar to "genie"
        for i in range(len(words) - 1):
            if self._is_similar("hey", words[i], 0.7) and self._is_similar("genie", words[i+1], 0.6):
                return 0.7
        
        # Look for individual words
        hey_similarity = max([self._is_similar("hey", word, 0.7) for word in words], default=0)
        genie_similarity = max([self._is_similar("genie", word, 0.6) for word in words], default=0)
        
        # Combined similarity score
        return (hey_similarity + genie_similarity) / 2
    
    def _is_similar(self, target: str, word: str, threshold: float) -> float:
        """Check if a word is similar to a target word.
        
        Args:
            target: Target word
            word: Word to compare
            threshold: Similarity threshold
            
        Returns:
            Similarity score if above threshold, otherwise 0
        """
        # Exact match
        if target == word:
            return 1.0
            
        # Empty strings
        if not target or not word:
            return 0.0
            
        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(target, word)
        max_len = max(len(target), len(word))
        similarity = 1.0 - (distance / max_len)
        
        return similarity if similarity >= threshold else 0.0
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Levenshtein distance
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
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
        
        # Create sliding windows for better detection
        window_duration = 2.0  # 2-second windows
        window_step = 0.5      # 0.5-second step
        window_size = int(self.sample_rate * window_duration)
        step_size = int(self.sample_rate * window_step)
        
        # Store recent audio for sliding window analysis
        recent_audio = []
        total_samples = 0
        
        # Track consecutive detections for confidence
        consecutive_detections = 0
        required_detections = 2  # Require multiple detections for confirmation
        
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
                        
                        # Add audio to buffer and recent audio
                        audio_flat = audio.squeeze()
                        self.add_audio(audio_flat)
                        
                        # Add to recent audio for sliding window
                        recent_audio.append(audio_flat)
                        total_samples += len(audio_flat)
                        
                        # Keep only enough audio for analysis
                        while total_samples > window_size * 2:
                            removed = recent_audio.pop(0)
                            total_samples -= len(removed)
                        
                        # Process when queue is empty (batch processing)
                        if audio_queue.qsize() == 0 and total_samples >= window_size:
                            # Create concatenated audio for sliding window
                            all_audio = np.concatenate(recent_audio)
                            
                            # Create sliding windows
                            detected = False
                            for start in range(0, max(1, len(all_audio) - window_size), step_size):
                                window = all_audio[start:start + window_size]
                                
                                # Skip windows that are too short
                                if len(window) < window_size * 0.75:
                                    continue
                                
                                # Check for wake word in this window
                                if self.detect_wake_word(window):
                                    detected = True
                                    consecutive_detections += 1
                                    logger.debug(f"Potential wake word detected (confidence: {consecutive_detections}/{required_detections})")
                                    break
                            
                            # If no detection in any window, decrease confidence
                            if not detected:
                                consecutive_detections = max(0, consecutive_detections - 0.5)
                            
                            # If we have enough consecutive detections
                            if consecutive_detections >= required_detections:
                                logger.info(f"Wake word 'Hey Genie' confirmed with {consecutive_detections} consecutive detections")
                                
                                # Call callback with the full buffer for context
                                if self.callback:
                                    self.callback(self.audio_buffer)
                                
                                # Reset buffer, recent audio, and detection counter
                                self.reset_buffer()
                                recent_audio.clear()
                                total_samples = 0
                                consecutive_detections = 0
                    
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
                # Try to use built-in keywords that sound similar to "Hey Genie"
                try:
                    # First try with "Genie" if available
                    self.porcupine = pvporcupine.create(
                        access_key=self.access_key,
                        keywords=["genie"],
                        sensitivities=[self.sensitivity]
                    )
                    logger.info("Using 'Genie' as wake word")
                except:
                    try:
                        # Try with "Jarvis" as it has similar phonetics
                        self.porcupine = pvporcupine.create(
                            access_key=self.access_key,
                            keywords=["jarvis"],
                            sensitivities=[self.sensitivity]
                        )
                        logger.info("Using 'Jarvis' as wake word (fallback for 'Hey Genie')")
                    except:
                        # Try "Computer" as final fallback
                        self.porcupine = pvporcupine.create(
                            access_key=self.access_key,
                            keywords=["computer"],
                            sensitivities=[self.sensitivity]
                        )
                        logger.info("Using 'Computer' as wake word (fallback for 'Hey Genie')")
            
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
                        # Get the keyword that was detected
                        keyword = "Hey Genie"
                        if self.porcupine.keywords and result < len(self.porcupine.keywords):
                            keyword = self.porcupine.keywords[result]
                        
                        logger.info(f"Wake word detected: '{keyword}' (using as 'Hey Genie')")
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
        
        # Track consecutive detections for confidence
        consecutive_detections = 0
        required_detections = 2  # Require multiple detections for confirmation
        detection_window_ms = 1000  # Time window for consecutive detections (ms)
        last_detection_time = 0
        
        # Callback for audio stream
        def audio_callback(indata, frames, time, status):
            nonlocal consecutive_detections, last_detection_time
            
            if status:
                logger.warning(f"Audio callback status: {status}")
            
            try:
                # Convert audio to int16
                audio_int16 = (indata.squeeze() * 32767).astype(np.int16)
                
                # Process audio
                result = self.porcupine.process(audio_int16)
                
                # Check result
                if result >= 0:
                    # Get current time
                    current_time = int(time.time() * 1000)
                    
                    # Check if this is within the detection window
                    if current_time - last_detection_time < detection_window_ms:
                        consecutive_detections += 1
                    else:
                        consecutive_detections = 1
                    
                    # Update last detection time
                    last_detection_time = current_time
                    
                    # Log potential detection
                    logger.debug(f"Potential wake word detected (confidence: {consecutive_detections}/{required_detections})")
                    
                    # If we have enough consecutive detections
                    if consecutive_detections >= required_detections and self.callback:
                        # Get the keyword that was detected
                        keyword = "Hey Genie"
                        if self.porcupine.keywords and result < len(self.porcupine.keywords):
                            keyword = self.porcupine.keywords[result]
                            
                        logger.info(f"Wake word '{keyword}' confirmed with {consecutive_detections} consecutive detections")
                        
                        # Call callback
                        self.callback()
                        
                        # Reset consecutive detections
                        consecutive_detections = 0
                    
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
                    
                    # Reset consecutive detections if too much time has passed
                    current_time = int(time.time() * 1000)
                    if current_time - last_detection_time > detection_window_ms * 2 and consecutive_detections > 0:
                        consecutive_detections = 0
                
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