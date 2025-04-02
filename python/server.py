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
import json
import hashlib
import pickle
from datetime import datetime
from collections import OrderedDict
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import auto recovery module for automatic dependency verification and fixing
try:
    from auto_recovery import auto_verify_dependencies
    
    # Automatically verify and fix dependencies without user intervention
    logger.info("Starting automatic dependency verification and recovery...")
    dependency_check_result = auto_verify_dependencies()
    
    if dependency_check_result:
        logger.info("Automatic dependency verification and recovery completed successfully")
    else:
        logger.warning("Automatic dependency recovery completed with some issues")
        logger.warning("The application will continue with available dependencies")
        logger.warning("Some features may not work correctly")
except ImportError:
    logger.warning("Auto recovery module not found, falling back to basic dependency verification")
    
    # Define a fallback verify_dependencies function
    def verify_dependencies():
        """Verify that all required dependencies are installed and working correctly.
        
        Returns:
            bool: True if all dependencies are installed and working, False otherwise.
        """
        logger.info("Verifying dependencies...")
        missing_packages = []
        
        # Core dependencies
        core_packages = ["numpy", "sounddevice", "faster_whisper"]
        for package in core_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing core dependencies: {', '.join(missing_packages)}")
            logger.error("The application will continue with available dependencies")
            return False
        
        # PyTorch and torchaudio
        try:
            import torch
            import torchaudio
            logger.info(f"PyTorch version: {torch.__version__}")
            logger.info(f"torchaudio version: {torchaudio.__version__}")
            
            # Test basic functionality
            sample_rate = 16000
            waveform = torch.zeros([1, sample_rate])
            logger.info("PyTorch and torchaudio are working correctly")
            
            # Check CUDA availability
            if torch.cuda.is_available():
                logger.info(f"CUDA is available: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA version: {torch.version.cuda}")
            else:
                logger.info("CUDA is not available, using CPU")
        except ImportError as e:
            logger.error(f"PyTorch or torchaudio not installed: {e}")
            logger.error("The application will continue with available dependencies")
            return False
        except Exception as e:
            logger.error(f"Error testing PyTorch/torchaudio: {e}")
            logger.error("PyTorch or torchaudio may not be functioning correctly")
            return False
        
        # Import local modules
        local_modules = {
            "vad": "create_vad",
            "wake_word": "create_wake_word_detector",
            "ide_integration": "inject_text"
        }
        
        missing_local_modules = []
        for module, function in local_modules.items():
            try:
                module_obj = __import__(module)
                if not hasattr(module_obj, function):
                    missing_local_modules.append(f"{module}.{function}")
            except ImportError:
                missing_local_modules.append(module)
        
        if missing_local_modules:
            logger.error(f"Missing local modules or functions: {', '.join(missing_local_modules)}")
            logger.error("Make sure vad.py, wake_word.py, and ide_integration.py are in the same directory")
            # Continue without these modules, they will be handled gracefully
        
        logger.info("All core dependencies verified successfully")
        return True
    
    # Verify dependencies
    dependency_check_result = verify_dependencies()
    if not dependency_check_result:
        logger.error("Dependency verification failed. Some features may not work correctly.")
        # Continue with available dependencies, will handle gracefully

# Import required packages
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# Import local modules
try:
    from vad import create_vad
    from wake_word import create_wake_word_detector
    from ide_integration import inject_text
except ImportError as e:
    logger.error(f"Failed to import local modules: {e}")
    logger.error("Make sure vad.py, wake_word.py, and ide_integration.py are in the same directory")
    # Continue without these modules, they will be handled gracefully


class AudioProcessor:
    """Handles audio capture and processing."""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 4000, device_id: Optional[int] = None, gain: float = 1.0):
        """Initialize the audio processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
            device_id: Audio device ID (None for default)
            gain: Audio gain multiplier (default: 1.0)
        """
        self.sample_rate = sample_rate
        self.gain = gain
        self.chunk_size = chunk_size
        self.device_id = device_id
        self.audio_queue = queue.Queue() # Use a queue for real-time chunk processing
        self.is_recording = False
        self.recording_thread = None
        
        # Initialize VADs
        self.silero_vad = None
        self.webrtc_vad = None
        self.vad = None
        
        # Try to initialize Silero VAD
        try:
            self.silero_vad = create_vad("silero", threshold=0.5)
            logger.info("Silero VAD initialized")
        except Exception as e:
            logger.error(f"Error initializing Silero VAD: {e}")
        
        # Try to initialize WebRTC VAD
        try:
            self.webrtc_vad = create_vad("webrtc", aggressiveness=3)
            logger.info("WebRTC VAD initialized")
        except Exception as e:
            logger.error(f"Error initializing WebRTC VAD: {e}")
        
        # Set primary VAD (prefer Silero, fallback to WebRTC)
        if self.silero_vad:
            self.vad = self.silero_vad
            logger.info("Using Silero VAD as primary")
        elif self.webrtc_vad:
            self.vad = self.webrtc_vad
            logger.info("Using WebRTC VAD as primary")
        else:
            logger.warning("No VAD available, speech filtering disabled")
        
    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        self.is_recording = True
        self.audio_queue = queue.Queue() # Clear queue on start
        
        def record_audio():
            """Record audio in a separate thread."""
            logger.info("Starting audio recording")
            
            try:
                with sd.InputStream(
                    samplerate=self.sample_rate,
                    device=self.device_id,
                    channels=1,
                    dtype='float32',
                    callback=self._audio_callback
                ):
                    logger.info(f"Audio stream started with device ID: {self.device_id}")
                    
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
    
    def stop_recording(self) -> None:
        """Stop recording audio."""
        if not self.is_recording:
            logger.warning("Not recording")
            return np.array([])
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
            self.recording_thread = None
        
        # No need to return audio, chunks are processed via queue
        logger.info("Audio recording stopped.")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Apply gain to the audio data
        amplified_data = indata.copy() * self.gain
        
        # Put audio chunk into the queue for processing
        self.audio_queue.put(amplified_data)
        
        # Enhanced speech detection using both VADs if available
        if self.silero_vad and self.webrtc_vad:
            # Check if the chunk contains speech using both VADs
            silero_speech = self.silero_vad.is_speech(indata.squeeze())
            webrtc_speech = self.webrtc_vad.is_speech(indata.squeeze())
            
            # Consider it speech if either VAD detects speech
            is_speech = silero_speech or webrtc_speech
            
            # Log speech detection (debug only)
            if is_speech:
                logger.debug(f"Speech detected in audio chunk (Silero: {silero_speech}, WebRTC: {webrtc_speech})")
        
        # Process audio with single VAD if only one is available
        elif self.vad:
            # Check if the chunk contains speech
            is_speech = self.vad.is_speech(indata.squeeze())
            
            # Log speech detection (debug only)
            if is_speech:
                logger.debug("Speech detected in audio chunk")
    
    def filter_audio(self, audio: np.ndarray) -> np.ndarray:
        """Filter audio using VAD to keep only speech segments.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Filtered audio with only speech segments
        """
        # Enhanced filtering using both VADs if available
        if self.silero_vad and self.webrtc_vad:
            logger.info("Applying enhanced VAD filtering with both Silero and WebRTC")
            
            # Get speech segments from both VADs
            silero_segments = self.silero_vad.get_speech_segments(audio)
            webrtc_segments = self.webrtc_vad.get_speech_segments(audio)
            
            # Merge segments
            all_segments = silero_segments + webrtc_segments
            
            # Sort segments by start time
            all_segments.sort(key=lambda x: x[0])
            
            # Merge overlapping segments
            merged_segments = []
            if all_segments:
                current_start, current_end = all_segments[0]
                
                for start, end in all_segments[1:]:
                    if start <= current_end:
                        # Segments overlap, merge them
                        current_end = max(current_end, end)
                    else:
                        # Add current segment
                        merged_segments.append((current_start, current_end))
                        
                        # Start new segment
                        current_start, current_end = start, end
                
                # Add the last segment
                merged_segments.append((current_start, current_end))
            
            # Concatenate speech segments
            if merged_segments:
                filtered_audio = np.concatenate([audio[start:end] for start, end in merged_segments])
                return filtered_audio
            else:
                logger.info("No speech detected by enhanced VAD")
                return np.array([])
        
        # Use single VAD if only one is available
        elif self.vad:
            logger.info(f"Applying VAD filtering with {type(self.vad).__name__}")
            return self.vad.filter_audio(audio)
        else:
            return audio
    
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
                        'default': device.get('default_input', False),
                        'sample_rates': device.get('default_samplerate', 44100)
                    })
                    
                    # Log device info for debugging
                    logger.info(f"Found audio device: {device['name']} (ID: {i}, Channels: {device['max_input_channels']})")
                    
                    # Check if this is a Focusrite device
                    if 'focusrite' in device['name'].lower() or 'clarett' in device['name'].lower():
                        logger.info(f"Detected Focusrite audio interface: {device['name']}")
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
        
        return devices
    
    def set_device(self, device_id: int, gain: Optional[float] = None) -> bool:
        """Set the audio device.
        
        Args:
            device_id: Audio device ID
            gain: Optional new gain value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if device exists
            devices = sd.query_devices()
            if device_id >= len(devices):
                logger.error(f"Invalid device ID: {device_id}")
                return False
            
            # Set device
            self.device_id = device_id
            
            # Update gain if provided
            if gain is not None:
                self.gain = gain
                logger.info(f"Audio gain set to: {self.gain}")
            
            logger.info(f"Audio device set to: {devices[device_id]['name']} (ID: {device_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting audio device: {e}")
            return False

    def get_audio_chunk(self, timeout=0.1) -> Optional[np.ndarray]:
        """Retrieves an audio chunk from the queue.

        Args:
            timeout (float): Maximum time to wait for an item in seconds.

        Returns:
            np.ndarray or None: An audio chunk as a NumPy array, or None if the queue is empty.
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_running(self) -> bool:
        """Returns True if audio capture is currently active."""
        return self.is_recording


class TranscriptionCache:
    """Enhanced caching system for transcriptions with smarter phrase matching and optimization."""
    
    def __init__(self, max_size: int = 200, similarity_threshold: float = 0.85, 
                 persistent_path: Optional[str] = None):
        """Initialize the transcription cache with smart features.
        
        Args:
            max_size: Maximum number of entries in the cache
            similarity_threshold: Threshold for text similarity matching (0.0-1.0)
            persistent_path: File path for persistent cache storage (None for in-memory only)
        """
        # Main cache using OrderedDict to track usage order
        self.cache = OrderedDict()
        
        # Phrase-based cache for common phrases
        self.phrase_cache = {}
        
        # Audio fingerprint cache for similar audio
        self.audio_fingerprint_cache = {}
        
        # Keep track of common phrases for optimization
        self.phrase_frequency = {}
        
        # Configuration
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.persistent_path = persistent_path
        
        # Statistics
        self.cache_hits = 0
        self.phrase_hits = 0
        self.similarity_hits = 0
        self.audio_hits = 0
        self.total_lookups = 0
        self.hit_ratio = 0.0
        
        # Load persistent cache if available
        if persistent_path and os.path.exists(persistent_path):
            self._load_persistent_cache()
            
        # Create context-based common phrases
        self._initialize_common_phrases()
    
    def _initialize_common_phrases(self):
        """Initialize cache with common programming and voice command phrases."""
        common_phrases = [
            # Common programming phrases
            "import numpy as np",
            "import torch",
            "import tensorflow as tf",
            "def __init__(self):",
            "return result",
            "if __name__ == '__main__':",
            # Common voice commands
            "new function",
            "new class",
            "create variable",
            "add comment",
            "delete line",
            "save file",
            "run program",
            "stop program",
            "import library"
        ]
        
        for phrase in common_phrases:
            # Add to phrase cache with empty audio fingerprint
            phrase_hash = self._hash_text(phrase)
            self.phrase_cache[phrase_hash] = phrase
            self.phrase_frequency[phrase_hash] = 1
    
    def _hash_text(self, text: str) -> str:
        """Create a hash from text for efficient lookup.
        
        Args:
            text: Text to hash
            
        Returns:
            Hash string
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _hash_audio(self, audio: np.ndarray) -> str:
        """Create a hash from audio data for efficient lookup.
        
        Args:
            audio: Audio data
            
        Returns:
            Hash string
        """
        # Use downsample to create a more general fingerprint
        # This allows similar audio inputs to match
        if len(audio) > 1600:  # Ensure audio is long enough
            downsampled = audio[::10]  # Take every 10th sample
            # Round values to reduce precision for better matching
            rounded = np.round(downsampled * 10) / 10
            return hashlib.md5(rounded.tobytes()).hexdigest()
        return hashlib.md5(audio.tobytes()).hexdigest()
    
    def _compute_audio_fingerprint(self, audio: np.ndarray) -> Dict[str, float]:
        """Compute audio fingerprint features for similarity detection.
        
        Args:
            audio: Audio data
            
        Returns:
            Dictionary of audio features
        """
        if len(audio) == 0:
            return {}
            
        # Extract basic audio features
        features = {
            'length': len(audio),
            'mean': float(np.mean(audio)),
            'std': float(np.std(audio)),
            'max': float(np.max(audio)),
            'min': float(np.min(audio)),
            'energy': float(np.sum(audio**2)),
            # More advanced features could be added here
        }
        
        # Add spectral features if audio is long enough
        if len(audio) > 1600:
            # Compute frequency features
            try:
                from scipy import signal
                frequencies, power = signal.periodogram(audio, fs=16000)
                features['peak_freq'] = float(frequencies[np.argmax(power)])
                features['spectral_centroid'] = float(np.sum(frequencies * power) / np.sum(power) if np.sum(power) > 0 else 0)
            except ImportError:
                # Skip spectral features if scipy not available
                pass
                
        return features
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Use SequenceMatcher for better string comparison
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _calculate_audio_similarity(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Calculate similarity between two audio fingerprints.
        
        Args:
            features1: First audio features
            features2: Second audio features
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not features1 or not features2:
            return 0.0
            
        # Calculate similarity based on features
        try:
            length_similarity = min(features1['length'], features2['length']) / max(features1['length'], features2['length'])
            mean_similarity = 1.0 - min(1.0, abs(features1['mean'] - features2['mean']) / max(0.01, max(abs(features1['mean']), abs(features2['mean']))))
            std_similarity = 1.0 - min(1.0, abs(features1['std'] - features2['std']) / max(0.01, max(features1['std'], features2['std'])))
            energy_similarity = min(features1['energy'], features2['energy']) / max(0.01, max(features1['energy'], features2['energy']))
            
            # Weighted combination
            similarity = (length_similarity * 0.1 + 
                         mean_similarity * 0.3 + 
                         std_similarity * 0.3 + 
                         energy_similarity * 0.3)
                         
            # Include spectral features if available
            if 'peak_freq' in features1 and 'peak_freq' in features2:
                peak_freq_similarity = 1.0 - min(1.0, abs(features1['peak_freq'] - features2['peak_freq']) / max(1.0, max(features1['peak_freq'], features2['peak_freq'])))
                similarity = similarity * 0.8 + peak_freq_similarity * 0.2
                
            return min(1.0, max(0.0, similarity))
        except (KeyError, ZeroDivisionError):
            return 0.0
    
    def _load_persistent_cache(self):
        """Load cache from disk."""
        try:
            with open(self.persistent_path, 'rb') as f:
                data = pickle.load(f)
                self.cache = data.get('cache', OrderedDict())
                self.phrase_cache = data.get('phrase_cache', {})
                self.audio_fingerprint_cache = data.get('audio_fingerprint_cache', {})
                self.phrase_frequency = data.get('phrase_frequency', {})
                self.cache_hits = data.get('cache_hits', 0)
                self.phrase_hits = data.get('phrase_hits', 0)
                self.similarity_hits = data.get('similarity_hits', 0)
                self.audio_hits = data.get('audio_hits', 0)
                self.total_lookups = data.get('total_lookups', 0)
                logger.info(f"Loaded cache with {len(self.cache)} entries from {self.persistent_path}")
        except Exception as e:
            logger.error(f"Error loading cache from {self.persistent_path}: {e}")
            # Reset caches
            self.cache = OrderedDict()
            self.phrase_cache = {}
            self.audio_fingerprint_cache = {}
    
    def _save_persistent_cache(self):
        """Save cache to disk."""
        if not self.persistent_path:
            return
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.persistent_path), exist_ok=True)
            
            # Prepare data to save
            data = {
                'cache': self.cache,
                'phrase_cache': self.phrase_cache,
                'audio_fingerprint_cache': self.audio_fingerprint_cache,
                'phrase_frequency': self.phrase_frequency,
                'cache_hits': self.cache_hits,
                'phrase_hits': self.phrase_hits,
                'similarity_hits': self.similarity_hits,
                'audio_hits': self.audio_hits,
                'total_lookups': self.total_lookups,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.persistent_path, 'wb') as f:
                pickle.dump(data, f)
                
            logger.info(f"Saved cache with {len(self.cache)} entries to {self.persistent_path}")
            
        except Exception as e:
            logger.error(f"Error saving cache to {self.persistent_path}: {e}")
    
    def get(self, audio: np.ndarray) -> Optional[str]:
        """Get transcription from cache with smart matching.
        
        Args:
            audio: Audio array
            
        Returns:
            Cached transcription or None if not found
        """
        self.total_lookups += 1
        
        # Try exact audio match first (fastest)
        audio_hash = hashlib.md5(audio.tobytes()).hexdigest()
        if audio_hash in self.cache:
            self.cache_hits += 1
            self.hit_ratio = (self.cache_hits + self.phrase_hits + self.similarity_hits + self.audio_hits) / self.total_lookups
            
            # Move to end of OrderedDict to mark as recently used
            text = self.cache[audio_hash]
            self.cache.move_to_end(audio_hash)
            
            logger.info(f"Exact cache hit (total hits: {self.cache_hits}, ratio: {self.hit_ratio:.2f})")
            return text
        
        # Compute audio fingerprint for similarity matching
        audio_fingerprint = self._compute_audio_fingerprint(audio)
        
        # Try similarity-based matching
        for stored_hash, features in self.audio_fingerprint_cache.items():
            similarity = self._calculate_audio_similarity(audio_fingerprint, features)
            
            if similarity >= self.similarity_threshold:
                self.audio_hits += 1
                self.hit_ratio = (self.cache_hits + self.phrase_hits + self.similarity_hits + self.audio_hits) / self.total_lookups
                
                logger.info(f"Audio similarity cache hit (similarity: {similarity:.2f}, hits: {self.audio_hits}, ratio: {self.hit_ratio:.2f})")
                return self.cache[stored_hash]
        
        return None
    
    def get_by_text(self, text: str) -> Optional[str]:
        """Get most similar text from cache.
        
        Args:
            text: Query text
            
        Returns:
            Most similar cached text or None if no match
        """
        # Try phrase cache first (exact matches of common phrases)
        text_hash = self._hash_text(text)
        if text_hash in self.phrase_cache:
            self.phrase_hits += 1
            logger.info(f"Phrase cache hit (hits: {self.phrase_hits})")
            return self.phrase_cache[text_hash]
        
        # Try similarity-based text matching
        if self.cache:
            best_match = None
            best_similarity = 0.0
            
            for audio_hash, cached_text in self.cache.items():
                similarity = self._calculate_text_similarity(text, cached_text)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = cached_text
            
            if best_match:
                self.similarity_hits += 1
                logger.info(f"Text similarity cache hit (similarity: {best_similarity:.2f}, hits: {self.similarity_hits})")
                return best_match
        
        return None
    
    def set(self, audio: np.ndarray, text: str) -> None:
        """Add or update a cache entry.
        
        Args:
            audio: Audio array
            text: Transcribed text
        """
        # Store in main cache
        audio_hash = hashlib.md5(audio.tobytes()).hexdigest()
        self.cache[audio_hash] = text
        
        # Store audio fingerprint
        self.audio_fingerprint_cache[audio_hash] = self._compute_audio_fingerprint(audio)
        
        # Update phrase frequency
        text_hash = self._hash_text(text)
        self.phrase_frequency[text_hash] = self.phrase_frequency.get(text_hash, 0) + 1
        
        # Store common phrases in phrase cache
        if self.phrase_frequency[text_hash] >= 3:
            self.phrase_cache[text_hash] = text
        
        # Limit cache size
        self._enforce_size_limit()
        
        # Periodically save to disk if persistent
        if self.persistent_path and self.total_lookups % 50 == 0:
            self._save_persistent_cache()
    
    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit by removing least recently used items."""
        # Check main cache
        while len(self.cache) > self.max_size:
            # Remove oldest item (first item in OrderedDict)
            audio_hash, _ = self.cache.popitem(last=False)
            
            # Also remove from fingerprint cache
            if audio_hash in self.audio_fingerprint_cache:
                del self.audio_fingerprint_cache[audio_hash]
                
        # Limit phrase cache to most frequent items
        if len(self.phrase_cache) > self.max_size / 2:
            # Sort phrases by frequency
            sorted_phrases = sorted(self.phrase_frequency.items(), key=lambda x: x[1], reverse=True)
            
            # Keep only the top half
            keep_phrases = set(item[0] for item in sorted_phrases[:int(self.max_size / 2)])
            
            # Filter phrase cache
            self.phrase_cache = {k: v for k, v in self.phrase_cache.items() if k in keep_phrases}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        return {
            'size': len(self.cache),
            'phrase_cache_size': len(self.phrase_cache),
            'fingerprint_cache_size': len(self.audio_fingerprint_cache),
            'cache_hits': self.cache_hits,
            'phrase_hits': self.phrase_hits,
            'similarity_hits': self.similarity_hits,
            'audio_hits': self.audio_hits,
            'total_lookups': self.total_lookups,
            'hit_ratio': self.hit_ratio,
            'common_phrases': len(self.phrase_frequency),
            'persistent': bool(self.persistent_path)
        }
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.audio_fingerprint_cache.clear()
        # Keep phrase cache for common phrases
        self.total_lookups = 0
        self.cache_hits = 0
        self.phrase_hits = 0
        self.similarity_hits = 0
        self.audio_hits = 0
        self.hit_ratio = 0.0


class WhisperTranscriber:
    """Handles transcription using Whisper with optimized GPU acceleration."""
    
    # Model size options
    MODEL_SIZES = ["tiny", "base", "small", "medium", "large"]
    
    def __init__(self, model_size: str = "base", device: str = "auto", compute_type: str = "auto"):
        """Initialize the transcriber with optimized settings.
        
        Args:
            model_size: Whisper model size
            device: Device to run the model on ("cpu", "cuda", or "auto")
            compute_type: Compute type ("int8", "float16", "float32", or "auto")
        """
        if model_size not in self.MODEL_SIZES:
            logger.warning(f"Invalid model size: {model_size}. Using 'base' instead.")
            model_size = "base"
        
        self.model_size = model_size
        
        # Determine device with better GPU detection
        if device == "auto":
            try:
                import torch
                if torch.cuda.is_available():
                    # Check GPU memory
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    logger.info(f"Detected GPU with {gpu_memory:.2f} GB memory")
                    
                    # Use CUDA if enough memory is available
                    if gpu_memory >= 2.0 or self.model_size in ["tiny", "base"]:
                        self.device = "cuda"
                        logger.info(f"Using GPU for {self.model_size} model")
                    else:
                        self.device = "cpu"
                        logger.info(f"GPU memory may be insufficient for {self.model_size} model, using CPU")
                else:
                    self.device = "cpu"
                    logger.info("No GPU detected, using CPU")
            except ImportError:
                self.device = "cpu"
                logger.info("PyTorch not available, using CPU")
        else:
            self.device = device
        
        # Optimize compute type based on device and available memory
        if compute_type == "auto":
            if self.device == "cuda":
                try:
                    import torch
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    
                    # Use float16 for better performance on most GPUs
                    if gpu_memory >= 4.0 or self.model_size in ["tiny", "base", "small"]:
                        self.compute_type = "float16"  # Faster on GPU
                    else:
                        # For very limited memory, use int8
                        self.compute_type = "int8"
                except:
                    self.compute_type = "float16"  # Default for GPU
            else:
                self.compute_type = "int8"  # Better for CPU
        else:
            self.compute_type = compute_type
        
        self.model = None
        
        # Initialize enhanced transcription cache with persistent storage
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        cache_file = os.path.join(cache_dir, f"transcription_cache_{model_size}.pkl")
        self.cache = TranscriptionCache(
            max_size=500,  # Larger cache size for better performance
            similarity_threshold=0.85,
            persistent_path=cache_file
        )
        logger.info(f"Initialized enhanced transcription cache with persistent storage at {cache_file}")
        
        # Performance metrics
        self.total_transcription_time = 0
        self.transcription_count = 0
        
        # Load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model with optimized settings."""
        logger.info(f"Loading Whisper model: {self.model_size} on {self.device} with {self.compute_type}")
        
        try:
            # Check if models directory exists
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Load the model with optimized settings
            self.model = WhisperModel(
                model_size_or_path=self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=models_dir,
                cpu_threads=8,  # Optimize CPU threading
                num_workers=2   # Optimize data loading
            )
            
            # Optimize CUDA settings if using GPU
            if self.device == "cuda":
                try:
                    import torch
                    # Set CUDA optimization flags
                    torch.backends.cudnn.benchmark = True
                    torch.backends.cudnn.deterministic = False
                    
                    # Log GPU info
                    logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
                    logger.info(f"CUDA version: {torch.version.cuda}")
                    logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
                except:
                    logger.warning("Failed to set CUDA optimization flags")
            
            logger.info("Model loaded successfully with optimized settings")
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio using Whisper with optimized parameters and enhanced caching.
        
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
            # Check enhanced cache system for similar audio
            cached_text = self.cache.get(audio)
            if cached_text:
                # Use text formatter to clean up cached text if needed
                try:
                    from text_formatter import format_text, detect_language
                    detected_lang = detect_language(cached_text)
                    if detected_lang != "plain":
                        cached_text = format_text(cached_text, detected_lang)
                except ImportError:
                    pass
                
                logger.info(f"Using enhanced cached transcription")
                return cached_text
            
            logger.info("Transcribing audio...")
            start_time = time.time()
            
            # Optimize transcription parameters based on device and model size
            # Adjust beam size based on GPU memory and model size
            if self.device == "cuda":
                try:
                    import torch
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    
                    # RTX 4090 optimization
                    is_rtx_4090 = "4090" in torch.cuda.get_device_name(0)
                    
                    if is_rtx_4090:
                        logger.info("Optimizing for RTX 4090 GPU")
                        # RTX 4090 has enough memory for larger beam sizes with all models
                        if self.model_size in ["large"]:
                            beam_size = 5  # Maximum quality for large model
                        else:
                            beam_size = 8  # Larger beam size for smaller models
                    elif gpu_memory > 10:  # More than 10GB VRAM
                        beam_size = 5 if self.model_size in ["tiny", "base", "small"] else 3
                    elif gpu_memory > 6:   # 6-10GB VRAM
                        beam_size = 3
                    else:                  # <6GB VRAM
                        beam_size = 2
                except Exception:
                    # Default if we can't determine
                    beam_size = 3
            else:
                # CPU processing - use smaller beam for faster results
                beam_size = 1
            
            logger.debug(f"Using beam size: {beam_size} for model: {self.model_size} on {self.device}")
            
            # Dynamic VAD parameters based on audio characteristics
            audio_power = np.mean(np.abs(audio))
            is_quiet_audio = audio_power < 0.01
            vad_threshold = 0.3 if is_quiet_audio else 0.5  # Lower threshold for quiet audio
            
            # Check for wake word to use as initial prompt for better context
            initial_prompt = None
            try:
                # Try to get the most similar text from cache for context
                similar_text = self.cache.get_by_text("")  # This will return the most common phrase
                if similar_text:
                    # Use the similar text as initial prompt if it might be related
                    initial_prompt = similar_text
                    logger.debug(f"Using context from cache as initial prompt: {initial_prompt}")
            except Exception as e:
                logger.debug(f"Error getting initial prompt: {e}")
            
            # Optimized parameters for RTX 4090 and other GPUs
            segments, info = self.model.transcribe(
                audio,
                language=language,
                beam_size=beam_size,
                vad_filter=True,
                vad_parameters={"threshold": vad_threshold},  # Dynamic threshold
                condition_on_previous_text=True if initial_prompt else False,  # Use context if available
                compression_ratio_threshold=2.4,        # Optimize for speed
                log_prob_threshold=-1.0,                # Optimize for speed
                no_speech_threshold=0.6,                # Optimize for speed
                initial_prompt=initial_prompt,          # Use context from cache if available
                word_timestamps=False                   # Disable word timestamps for speed
            )
            
            # Combine segments
            text = " ".join(segment.text for segment in segments)
            
            # Update performance metrics
            end_time = time.time()
            transcription_time = end_time - start_time
            self.total_transcription_time += transcription_time
            self.transcription_count += 1
            avg_time = self.total_transcription_time / self.transcription_count
            
            # Use text formatter to format the text based on content
            try:
                from text_formatter import format_text, detect_language
                detected_lang = detect_language(text)
                if detected_lang != "plain":
                    text = format_text(text, detected_lang)
                    logger.debug(f"Formatted transcription as {detected_lang}")
            except ImportError:
                pass
            
            # Store in enhanced cache
            self.cache.set(audio, text)
            
            logger.info(f"Transcription complete: {text}")
            logger.info(f"Transcription time: {transcription_time:.2f}s (avg: {avg_time:.2f}s)")
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics for the transcriber.
        
        Returns:
            Dictionary with performance statistics
        """
        # Get basic stats
        stats = {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "avg_transcription_time": self.total_transcription_time / max(1, self.transcription_count),
            "transcription_count": self.transcription_count,
        }
        
        # Add enhanced cache stats
        cache_stats = self.cache.get_stats()
        stats.update({
            "cache_hits_total": cache_stats["cache_hits"] + cache_stats["phrase_hits"] + 
                               cache_stats["similarity_hits"] + cache_stats["audio_hits"],
            "cache_hit_ratio": cache_stats["hit_ratio"],
            "cache_size": cache_stats["size"],
            "cache_exact_hits": cache_stats["cache_hits"],
            "cache_phrase_hits": cache_stats["phrase_hits"],
            "cache_similarity_hits": cache_stats["similarity_hits"],
            "cache_audio_hits": cache_stats["audio_hits"],
            "phrase_cache_size": cache_stats["phrase_cache_size"],
            "cache_lookups": cache_stats["total_lookups"],
            "cache_persistent": cache_stats["persistent"]
        })
        
        return stats


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
        self.wake_word = args.wake_word
        self.activation_mode = args.activation_mode
        self.ide = args.ide
        self.device_id = args.device_id
        self.compute_type = args.compute_type
        
        # Determine device for Whisper
        if args.gpu and self._is_gpu_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        
        # Initialize audio processor with default device first and increased gain
        self.audio_processor = AudioProcessor(device_id=self.device_id, gain=5.0)  # Increase gain by 5x
        
        # Then find and set Focusrite device if available
        focusrite_id = self._find_focusrite_device()
        if focusrite_id is not None:
            logger.info(f"Using Focusrite audio interface (ID: {focusrite_id})")
            self.device_id = focusrite_id
            # Update the audio processor with the Focusrite device and increased gain
            self.audio_processor.set_device(focusrite_id, gain=5.0)  # Increase gain by 5x
        else:
            logger.warning("Focusrite audio interface not found, using specified device ID")
        self.transcriber = WhisperTranscriber(
            model_size=self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )
        
        # Initialize wake word detector if needed
        if self.activation_mode == "wake_word":
            try:
                self.wake_word_detector = create_wake_word_detector(
                    "whisper",
                    wake_word=self.wake_word,
                    threshold=self.sensitivity
                )
                logger.info(f"Wake word detector initialized with wake word: {self.wake_word}")
            except Exception as e:
                logger.error(f"Error initializing wake word detector: {e}")
                self.wake_word_detector = None
                self.activation_mode = "manual"  # Fallback to manual mode
        else:
            self.wake_word_detector = None
        
        # State
        self.is_listening = False
        self.wake_word_active = False

        # Real-time processing state variables
        self.silence_threshold_ms = getattr(args, 'silence_threshold_ms', 1000) # Default 1 second
        self.wake_word_timeout_ms = getattr(args, 'wake_word_timeout_ms', 5000) # Default 5 seconds
        self.reset_wake_word_after_silence = getattr(args, 'reset_wake_word', True) # Default True

        self.speech_active = False
        self.accumulated_audio = []
        self.last_speech_time = 0
        self.wake_word_detected = False # Will be True only if wake word mode is active and word is heard
        self.speech_started_time = 0 # To track timeout after wake word
    def _find_focusrite_device(self) -> Optional[int]:
        """Find the Focusrite audio interface device ID.
        
        Returns:
            Device ID if found, None otherwise
        """
        devices = self.audio_processor.get_audio_devices()
        
        # Look for Focusrite or Clarett in device names
        for device in devices:
            if 'focusrite' in device['name'].lower() or 'clarett' in device['name'].lower():
                logger.info(f"Found Focusrite device: {device['name']} (ID: {device['id']})")
                return device['id']
        
        return None
    
    def _is_gpu_available(self) -> bool:
        """Check if GPU is available.
        
        Returns:
            True if GPU is available, False otherwise
        """
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def start(self) -> None:
        """Start the server."""
        logger.info("Starting Genie Whisper server")
        
        # Log system info
        self._log_system_info()
        
        # Send initial status
        self._send_message({
            "type": "status",
            "status": "Server started"
        })
        
        # Start wake word detection if needed
        if self.activation_mode == "wake_word" and self.wake_word_detector:
            self._start_wake_word_detection()
        
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
    
    def _log_system_info(self) -> None:
        """Log system information."""
        logger.info("System Information:")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Operating system: {os.name} - {sys.platform}")
        
        # Log CPU info
        try:
            import psutil
            logger.info(f"CPU: {psutil.cpu_count(logical=False)} cores, {psutil.cpu_count()} threads")
            logger.info(f"Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
        except ImportError:
            logger.info("psutil not available, skipping CPU/memory info")
        
        # Log GPU info
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA version: {torch.version.cuda}")
                logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
            else:
                logger.info("No GPU available")
        except ImportError:
            logger.info("PyTorch not available, skipping GPU info")
        
        # Log audio devices
        logger.info("Audio devices:")
        for device in self.audio_processor.get_audio_devices():
            logger.info(f"  {device['name']} (ID: {device['id']}, Channels: {device['channels']})")
    
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
        elif cmd_type == "set_device":
            self._set_audio_device(command.get("device_id"))
        elif cmd_type == "update_settings":
            self._update_settings(command.get("settings", {}))
        elif cmd_type == "inject_text":
            self._inject_text(command.get("text", ""), command.get("ide"))
        elif cmd_type == "get_performance":
            self._get_performance_stats()
        else:
            logger.warning(f"Unknown command: {cmd_type}")
    
    def _get_performance_stats(self) -> None:
        """Get performance statistics."""
        # Get transcriber performance stats
        stats = self.transcriber.get_performance_stats()
        
        # Add GPU information if available
        try:
            import torch
            if torch.cuda.is_available():
                stats["gpu_name"] = torch.cuda.get_device_name(0)
                stats["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                stats["gpu_memory_allocated"] = torch.cuda.memory_allocated(0) / (1024**3)
                stats["gpu_memory_reserved"] = torch.cuda.memory_reserved(0) / (1024**3)
        except:
            pass
        
        # Send performance stats to frontend
        self._send_message({
            "type": "performance_stats",
            "stats": stats
        })
    
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
        
        # Filter audio with VAD if enabled
        if self.use_vad:
            filtered_audio = self.audio_processor.filter_audio(audio)
            
            # Check if we have any speech after filtering
            if len(filtered_audio) > 0:
                audio = filtered_audio
                logger.info("Speech detected in final audio")
            else:
                logger.info("No speech detected in final audio")
                self._send_message({
                    "type": "status",
                    "status": "No speech detected"
                })
                return
        
        # Transcribe final audio
        if len(audio) > 0:
            text = self.transcriber.transcribe(audio)
            
            if text:
                self._send_message({
                    "type": "transcription",
                    "text": text,
                    "final": True
                })
                
                # Inject text into IDE if specified
                if self.ide:
                    self._inject_text(text, self.ide)
    
    def _transcription_loop(self) -> None:
        """Continuously processes audio chunks for transcription with silence detection."""
        logger.info("Starting real-time transcription loop...")

        # Reset state variables at the start of the loop
        self.speech_active = False
        self.accumulated_audio = []
        self.last_speech_time = time.time() # Initialize last speech time
        # Reset wake word detected state based on activation mode
        self.wake_word_detected = self.activation_mode != "wake_word"
        self.speech_started_time = 0

        if self.activation_mode == "wake_word":
             self._send_message({"type": "status", "data": "listening_for_wake_word"})
        else:
             self._send_message({"type": "status", "data": "listening_continuously"})


        while self.is_listening:
            # Get audio chunk from the queue
            current_chunk = self.audio_processor.get_audio_chunk(timeout=0.1) # Short timeout

            if current_chunk is not None:
                # --- Wake Word Detection ---
                if self.activation_mode == "wake_word" and not self.wake_word_detected:
                    if self.wake_word_detector and self.wake_word_detector.detect(current_chunk):
                        logger.info("Wake word detected!")
                        self.wake_word_detected = True
                        self.speech_started_time = time.time() # Start speech timer on wake word
                        self.accumulated_audio = [] # Reset buffer on wake word
                        self.speech_active = False # Reset speech active flag
                        self.last_speech_time = time.time() # Reset silence timer
                        self._send_message({"type": "status", "data": "wake_word_detected"})
                        # Skip processing this chunk as it was the wake word
                        continue
                    else:
                        # If in wake word mode but not detected, discard chunk and continue waiting
                        continue # Go to next loop iteration to get next chunk

                # --- VAD and Speech Accumulation ---
                is_speech = False
                if self.use_vad and self.audio_processor.vad:
                    try:
                        # Assuming VAD works on chunks directly
                        is_speech = self.audio_processor.vad.is_speech(current_chunk.squeeze())
                    except Exception as e:
                        logger.error(f"Error during VAD processing in loop: {e}")
                else:
                    # If VAD is disabled, treat every chunk as speech
                    is_speech = True

                if is_speech:
                    if not self.speech_active:
                        logger.debug("Speech started.")
                        self.speech_active = True
                        # Optionally capture timestamp of speech start
                        # self.speech_started_time = time.time() # Reset this? Or keep from wake word?
                    self.accumulated_audio.append(current_chunk)
                    self.last_speech_time = time.time()
                elif self.speech_active:
                    # Speech was active, now silence or VAD says no speech
                    self.accumulated_audio.append(current_chunk) # Include potentially trailing silence chunk
                    silence_duration = time.time() - self.last_speech_time
                    logger.debug(f"Silence detected. Duration: {silence_duration:.2f}s")

                    # Check if silence duration exceeds threshold
                    if silence_duration > self.silence_threshold_ms / 1000.0:
                        logger.info(f"Significant silence ({silence_duration:.2f}s) detected after speech. Processing accumulated audio.")
                        self._process_accumulated_audio() # Process the audio
                        # State reset happens within _process_accumulated_audio

            # --- Timeout Checks ---
            else: # current_chunk is None (queue was empty)
                # Check if speech was active but we haven't received data or speech for a while
                if self.speech_active and (time.time() - self.last_speech_time > self.silence_threshold_ms / 1000.0):
                    logger.info(f"Processing accumulated audio due to timeout after speech ({time.time() - self.last_speech_time:.2f}s).")
                    self._process_accumulated_audio() # Process the audio

                # Check for timeout after wake word detection if no speech started
                if self.activation_mode == "wake_word" and self.wake_word_detected and not self.speech_active and \
                   (time.time() - self.speech_started_time > self.wake_word_timeout_ms / 1000.0):
                    logger.info("Timeout waiting for speech after wake word.")
                    self.wake_word_detected = False # Reset wake word
                    self._send_message({"type": "status", "data": "listening_for_wake_word"}) # Inform frontend

            # Small sleep to prevent high CPU usage when queue is empty frequently
            time.sleep(0.01)

        logger.info("Transcription loop finished.")
        # Process any remaining audio when listening stops
        if self.accumulated_audio:
             logger.info("Processing remaining accumulated audio after loop exit.")
             self._process_accumulated_audio()


    def _process_accumulated_audio(self):
        """Helper function to process accumulated audio, transcribe, and reset state."""
        if not self.accumulated_audio:
            logger.debug("No accumulated audio to process.")
            # Reset state even if buffer is empty after silence trigger
            self.speech_active = False
            if self.activation_mode == "wake_word" and self.reset_wake_word_after_silence:
                self.wake_word_detected = False
                self._send_message({"type": "status", "data": "listening_for_wake_word"})
            return

        try:
            # Combine accumulated chunks
            audio_to_process = np.concatenate(self.accumulated_audio)
            audio_duration = len(audio_to_process) / self.audio_processor.sample_rate
            logger.info(f"Processing {audio_duration:.2f}s of accumulated audio...")

            # --- Transcription ---
            start_transcribe_time = time.time()
            # Optional: Filter the combined audio again if needed
            # filtered_audio = self.audio_processor.filter_audio(audio_to_process)
            # transcription = self.transcriber.transcribe(filtered_audio)
            transcription = self.transcriber.transcribe(audio_to_process)
            end_transcribe_time = time.time()
            logger.info(f"Transcription: '{transcription}' (took {end_transcribe_time - start_transcribe_time:.2f}s)")

            if transcription.strip():
                # Send transcription to frontend/IDE
                self._send_message({"type": "transcription", "data": transcription, "final": True}) # Mark as final
                self._inject_text(transcription) # Inject into IDE

                # Add to cache
                self.cache.set(audio_to_process, transcription) # Use the cache object from __init__

        except Exception as e:
            logger.error(f"Error during transcription processing: {e}")
        finally:
            # --- Reset State ---
            self.accumulated_audio = []
            self.speech_active = False
            # Reset wake word detection if necessary
            if self.activation_mode == "wake_word" and self.reset_wake_word_after_silence:
                logger.info("Resetting wake word detection after processing.")
                self.wake_word_detected = False
                self._send_message({"type": "status", "data": "listening_for_wake_word"})
    
    def _start_wake_word_detection(self) -> None:
        """Start wake word detection."""
        if not self.wake_word_detector:
            logger.error("Wake word detector not initialized")
            return
        
        if self.wake_word_active:
            logger.warning("Wake word detection already active")
            return
        
        self.wake_word_active = True
        
        # Define callback for wake word detection
        def wake_word_callback(audio):
            logger.info("Wake word detected")
            
            # Send message to frontend
            self._send_message({
                "type": "wake_word_detected",
                "wake_word": self.wake_word
            })
            
            # Start listening
            self._start_listening()
        
        # Start wake word detection
        self.wake_word_detector.start_listening(wake_word_callback)
        
        logger.info("Wake word detection started")
    
    def _stop_wake_word_detection(self) -> None:
        """Stop wake word detection."""
        if not self.wake_word_detector or not self.wake_word_active:
            return
        
        self.wake_word_active = False
        self.wake_word_detector.stop_listening()
        
        logger.info("Wake word detection stopped")
    
    def _get_audio_devices(self) -> None:
        """Get available audio devices."""
        devices = self.audio_processor.get_audio_devices()
        
        self._send_message({
            "type": "devices",
            "devices": devices
        })
    
    def _set_audio_device(self, device_id: Optional[int]) -> None:
        """Set the audio device.
        
        Args:
            device_id: Audio device ID
        """
        if device_id is None:
            logger.warning("No device ID provided")
            return
        
        success = self.audio_processor.set_device(device_id)
        
        self._send_message({
            "type": "device_set",
            "success": success,
            "device_id": device_id
        })
    
    def _update_settings(self, settings: Dict) -> None:
        """Update server settings."""
        # Update model size if changed
        if "modelSize" in settings and settings["modelSize"] != self.model_size:
            self.model_size = settings["modelSize"]
            self.transcriber = WhisperTranscriber(
                model_size=self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
        
        # Update other settings
        if "sensitivity" in settings:
            self.sensitivity = float(settings["sensitivity"])
        
        if "useVAD" in settings:
            self.use_vad = settings["useVAD"]
        
        if "offlineMode" in settings:
            self.offline_mode = settings["offlineMode"]
        
        if "wakeWord" in settings and settings["wakeWord"] != self.wake_word:
            self.wake_word = settings["wakeWord"]
            
            # Restart wake word detection if active
            if self.wake_word_active:
                self._stop_wake_word_detection()
                
                # Recreate wake word detector
                self.wake_word_detector = create_wake_word_detector(
                    "whisper",
                    wake_word=self.wake_word,
                    threshold=self.sensitivity
                )
                
                self._start_wake_word_detection()
        
        if "activationMode" in settings and settings["activationMode"] != self.activation_mode:
            self.activation_mode = settings["activationMode"]
            
            # Start or stop wake word detection based on mode
            if self.activation_mode == "wake_word":
                if not self.wake_word_active and self.wake_word_detector:
                    self._start_wake_word_detection()
            else:
                if self.wake_word_active:
                    self._stop_wake_word_detection()
        
        if "ide" in settings:
            self.ide = settings["ide"]
        
        if "deviceId" in settings and settings["deviceId"] != self.device_id:
            self._set_audio_device(settings["deviceId"])
        
        self._send_message({
            "type": "status",
            "status": "Settings updated"
        })
    
    def _inject_text(self, text: str, ide: Optional[str] = None) -> None:
        """Inject text into IDE.
        
        Args:
            text: Text to inject
            ide: IDE to inject into (None for auto-detection)
        """
        try:
            # Use IDE integration module
            result = inject_text(text, ide or self.ide)
            
            self._send_message({
                "type": "text_injected",
                "success": result
            })
            
        except Exception as e:
            logger.error(f"Error injecting text: {e}")
            
            self._send_message({
                "type": "text_injected",
                "success": False,
                "error": str(e)
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
        
        # Stop wake word detection if active
        if self.wake_word_active:
            self._stop_wake_word_detection()


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
    
    parser.add_argument(
        "--wake-word",
        type=str,
        default="Hey Genie",
        help="Wake word for activation"
    )
    
    parser.add_argument(
        "--activation-mode",
        type=str,
        default="manual",
        choices=["manual", "wake_word", "always_on"],
        help="Activation mode"
    )
    
    parser.add_argument(
        "--ide",
        type=str,
        default=None,
        help="IDE to inject text into (vscode, cursor, roocode, openai, or none for auto-detection)"
    )
    
    parser.add_argument(
        "--device-id",
        type=int,
        default=None,
        help="Audio device ID (None for default)"
    )
    
    parser.add_argument(
        "--gpu",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Use GPU for transcription if available"
    )
    
    parser.add_argument(
        "--compute-type",
        type=str,
        default="auto",
        choices=["auto", "int8", "float16", "float32"],
        help="Compute type for Whisper model"
    )

    parser.add_argument(
        "--silence-threshold-ms",
        type=int,
        default=1000,
        help="Duration of silence in milliseconds after speech to trigger transcription"
    )

    parser.add_argument(
        "--wake-word-timeout-ms",
        type=int,
        default=5000,
        help="Duration in milliseconds to wait for speech after wake word detection before resetting"
    )

    parser.add_argument(
        "--reset-wake-word",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Reset wake word detection after processing transcription following silence"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Start the server
    server = GenieWhisperServer(args)
    server.start()