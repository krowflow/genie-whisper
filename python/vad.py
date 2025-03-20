#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Activity Detection (VAD) module for Genie Whisper.
This module provides VAD functionality using Silero VAD.
"""

import logging
import os
import sys
import torch
import numpy as np
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class SileroVAD:
    """Voice Activity Detection using Silero VAD."""
    
    def __init__(
        self,
        threshold: float = 0.5,
        sample_rate: int = 16000,
        use_onnx: bool = False
    ):
        """Initialize the VAD.
        
        Args:
            threshold: VAD threshold (0.0-1.0)
            sample_rate: Audio sample rate in Hz
            use_onnx: Whether to use ONNX model
        """
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.use_onnx = use_onnx
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Silero VAD model."""
        logger.info("Loading Silero VAD model")
        
        try:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Download or load the model
            if self.use_onnx:
                # ONNX model path
                onnx_model_path = os.path.join(models_dir, "silero_vad.onnx")
                
                # Check if model exists, download if not
                if not os.path.exists(onnx_model_path):
                    logger.info("Downloading Silero VAD ONNX model")
                    torch.hub.download_url_to_file(
                        'https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx',
                        onnx_model_path
                    )
                
                # Load ONNX model
                import onnxruntime
                self.model = onnxruntime.InferenceSession(onnx_model_path)
                logger.info("Silero VAD ONNX model loaded")
            else:
                # PyTorch model
                self.model, utils = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    onnx=False,
                    verbose=False
                )
                
                # Move model to device
                self.model = self.model.to(self.device)
                
                # Get utils
                self.get_speech_timestamps = utils[0]
                self.save_audio = utils[1]
                self.read_audio = utils[2]
                self.VADIterator = utils[3]
                self.collect_chunks = utils[4]
                
                logger.info(f"Silero VAD PyTorch model loaded on {self.device}")
        
        except Exception as e:
            logger.error(f"Error loading Silero VAD model: {e}")
            self.model = None
    
    def is_speech(self, audio: np.ndarray) -> bool:
        """Check if audio contains speech.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            True if speech is detected, False otherwise
        """
        if self.model is None:
            logger.error("VAD model not loaded")
            return True  # Default to assuming speech if model not loaded
        
        try:
            # Convert numpy array to torch tensor
            if not isinstance(audio, torch.Tensor):
                audio_tensor = torch.from_numpy(audio.squeeze()).float()
            else:
                audio_tensor = audio
            
            # Move tensor to device
            audio_tensor = audio_tensor.to(self.device)
            
            # Get speech probability
            with torch.no_grad():
                speech_prob = self.model(audio_tensor, self.sample_rate).item()
            
            # Check if probability exceeds threshold
            is_speech = speech_prob >= self.threshold
            
            return is_speech
            
        except Exception as e:
            logger.error(f"Error detecting speech: {e}")
            return True  # Default to assuming speech on error
    
    def get_speech_segments(self, audio: np.ndarray) -> List[Tuple[int, int]]:
        """Get speech segments from audio.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            List of (start, end) tuples in samples
        """
        if self.model is None:
            logger.error("VAD model not loaded")
            return [(0, len(audio))]  # Default to full audio if model not loaded
        
        try:
            # Convert numpy array to torch tensor
            if not isinstance(audio, torch.Tensor):
                audio_tensor = torch.from_numpy(audio.squeeze()).float()
            else:
                audio_tensor = audio
            
            # Move tensor to device
            audio_tensor = audio_tensor.to(self.device)
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                threshold=self.threshold,
                sampling_rate=self.sample_rate
            )
            
            # Convert timestamps to (start, end) tuples
            segments = [(ts['start'], ts['end']) for ts in speech_timestamps]
            
            return segments
            
        except Exception as e:
            logger.error(f"Error getting speech segments: {e}")
            return [(0, len(audio))]  # Default to full audio on error
    
    def filter_audio(self, audio: np.ndarray) -> np.ndarray:
        """Filter audio to keep only speech segments.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Filtered audio with only speech segments
        """
        if self.model is None:
            logger.error("VAD model not loaded")
            return audio  # Return original audio if model not loaded
        
        try:
            # Convert numpy array to torch tensor
            if not isinstance(audio, torch.Tensor):
                audio_tensor = torch.from_numpy(audio.squeeze()).float()
            else:
                audio_tensor = audio
            
            # Move tensor to device
            audio_tensor = audio_tensor.to(self.device)
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                threshold=self.threshold,
                sampling_rate=self.sample_rate
            )
            
            # Collect speech chunks
            speech_audio = self.collect_chunks(speech_timestamps, audio_tensor)
            
            # Convert back to numpy array
            speech_audio_np = speech_audio.cpu().numpy()
            
            return speech_audio_np
            
        except Exception as e:
            logger.error(f"Error filtering audio: {e}")
            return audio  # Return original audio on error


class WebRTCVAD:
    """Voice Activity Detection using WebRTC VAD."""
    
    def __init__(
        self,
        aggressiveness: int = 3,
        sample_rate: int = 16000,
        frame_duration_ms: int = 30
    ):
        """Initialize the VAD.
        
        Args:
            aggressiveness: VAD aggressiveness (0-3)
            sample_rate: Audio sample rate in Hz
            frame_duration_ms: Frame duration in milliseconds
        """
        self.aggressiveness = aggressiveness
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.vad = None
        
        # Load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the WebRTC VAD model."""
        logger.info("Loading WebRTC VAD model")
        
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(self.aggressiveness)
            logger.info(f"WebRTC VAD model loaded with aggressiveness {self.aggressiveness}")
        except Exception as e:
            logger.error(f"Error loading WebRTC VAD model: {e}")
            self.vad = None
    
    def _frame_generator(self, audio: np.ndarray) -> List[bytes]:
        """Generate frames from audio.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            List of audio frames as bytes
        """
        # Calculate frame size
        frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
        # Convert audio to int16
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Generate frames
        frames = []
        for i in range(0, len(audio_int16), frame_size):
            frame = audio_int16[i:i+frame_size]
            
            # Ensure frame is the right size
            if len(frame) < frame_size:
                # Pad with zeros if needed
                frame = np.pad(frame, (0, frame_size - len(frame)))
            
            frames.append(frame.tobytes())
        
        return frames
    
    def is_speech(self, audio: np.ndarray) -> bool:
        """Check if audio contains speech.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            True if speech is detected, False otherwise
        """
        if self.vad is None:
            logger.error("VAD model not loaded")
            return True  # Default to assuming speech if model not loaded
        
        try:
            # Generate frames
            frames = self._frame_generator(audio)
            
            # Check each frame for speech
            speech_frames = 0
            for frame in frames:
                if self.vad.is_speech(frame, self.sample_rate):
                    speech_frames += 1
            
            # Consider it speech if at least 25% of frames contain speech
            is_speech = speech_frames >= len(frames) * 0.25
            
            return is_speech
            
        except Exception as e:
            logger.error(f"Error detecting speech: {e}")
            return True  # Default to assuming speech on error
    
    def get_speech_segments(self, audio: np.ndarray) -> List[Tuple[int, int]]:
        """Get speech segments from audio.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            List of (start, end) tuples in samples
        """
        if self.vad is None:
            logger.error("VAD model not loaded")
            return [(0, len(audio))]  # Default to full audio if model not loaded
        
        try:
            # Generate frames
            frames = self._frame_generator(audio)
            
            # Calculate frame size
            frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
            
            # Check each frame for speech
            segments = []
            start = None
            
            for i, frame in enumerate(frames):
                is_speech = self.vad.is_speech(frame, self.sample_rate)
                
                if is_speech and start is None:
                    # Start of speech segment
                    start = i * frame_size
                elif not is_speech and start is not None:
                    # End of speech segment
                    end = i * frame_size
                    segments.append((start, end))
                    start = None
            
            # Handle case where audio ends during speech
            if start is not None:
                segments.append((start, len(audio)))
            
            return segments
            
        except Exception as e:
            logger.error(f"Error getting speech segments: {e}")
            return [(0, len(audio))]  # Default to full audio on error
    
    def filter_audio(self, audio: np.ndarray) -> np.ndarray:
        """Filter audio to keep only speech segments.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Filtered audio with only speech segments
        """
        if self.vad is None:
            logger.error("VAD model not loaded")
            return audio  # Return original audio if model not loaded
        
        try:
            # Get speech segments
            segments = self.get_speech_segments(audio)
            
            # Concatenate speech segments
            speech_audio = np.concatenate([audio[start:end] for start, end in segments])
            
            return speech_audio
            
        except Exception as e:
            logger.error(f"Error filtering audio: {e}")
            return audio  # Return original audio on error


class HybridVAD:
    """Hybrid Voice Activity Detection using both Silero and WebRTC VAD."""
    
    def __init__(
        self,
        silero_threshold: float = 0.5,
        webrtc_aggressiveness: int = 3,
        sample_rate: int = 16000,
        frame_duration_ms: int = 30,
        smoothing_window: int = 3,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100
    ):
        """Initialize the Hybrid VAD.
        
        Args:
            silero_threshold: Silero VAD threshold (0.0-1.0)
            webrtc_aggressiveness: WebRTC VAD aggressiveness (0-3)
            sample_rate: Audio sample rate in Hz
            frame_duration_ms: Frame duration in milliseconds
            smoothing_window: Number of frames to use for smoothing
            min_speech_duration_ms: Minimum speech duration in milliseconds
            min_silence_duration_ms: Minimum silence duration in milliseconds
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.smoothing_window = smoothing_window
        self.min_speech_samples = int(min_speech_duration_ms * sample_rate / 1000)
        self.min_silence_samples = int(min_silence_duration_ms * sample_rate / 1000)
        
        # Create both VAD instances
        self.silero_vad = SileroVAD(threshold=silero_threshold, sample_rate=sample_rate)
        self.webrtc_vad = WebRTCVAD(aggressiveness=webrtc_aggressiveness,
                                    sample_rate=sample_rate,
                                    frame_duration_ms=frame_duration_ms)
        
        logger.info(f"Hybrid VAD initialized with Silero threshold {silero_threshold} and WebRTC aggressiveness {webrtc_aggressiveness}")
    
    def is_speech(self, audio: np.ndarray) -> bool:
        """Check if audio contains speech using both VADs.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            True if speech is detected, False otherwise
        """
        try:
            # Get speech probability from both VADs
            silero_speech = self.silero_vad.is_speech(audio)
            webrtc_speech = self.webrtc_vad.is_speech(audio)
            
            # Consider it speech if either VAD detects speech
            # This increases recall (fewer false negatives)
            is_speech = silero_speech or webrtc_speech
            
            return is_speech
            
        except Exception as e:
            logger.error(f"Error detecting speech in hybrid VAD: {e}")
            return True  # Default to assuming speech on error
    
    def get_speech_segments(self, audio: np.ndarray) -> List[Tuple[int, int]]:
        """Get speech segments from audio using both VADs.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            List of (start, end) tuples in samples
        """
        try:
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
                        # Check if segment is long enough
                        if current_end - current_start >= self.min_speech_samples:
                            merged_segments.append((current_start, current_end))
                        
                        # Start new segment
                        current_start, current_end = start, end
                
                # Add the last segment if it's long enough
                if current_end - current_start >= self.min_speech_samples:
                    merged_segments.append((current_start, current_end))
            
            # Merge segments that are close together
            smoothed_segments = []
            if merged_segments:
                current_start, current_end = merged_segments[0]
                
                for start, end in merged_segments[1:]:
                    if start - current_end <= self.min_silence_samples:
                        # Segments are close, merge them
                        current_end = end
                    else:
                        # Add current segment
                        smoothed_segments.append((current_start, current_end))
                        
                        # Start new segment
                        current_start, current_end = start, end
                
                # Add the last segment
                smoothed_segments.append((current_start, current_end))
            
            return smoothed_segments
            
        except Exception as e:
            logger.error(f"Error getting speech segments in hybrid VAD: {e}")
            return [(0, len(audio))]  # Default to full audio on error
    
    def filter_audio(self, audio: np.ndarray) -> np.ndarray:
        """Filter audio to keep only speech segments.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Filtered audio with only speech segments
        """
        try:
            # Apply noise reduction preprocessing
            audio = self._preprocess_audio(audio)
            
            # Get speech segments
            segments = self.get_speech_segments(audio)
            
            # Concatenate speech segments
            if segments:
                speech_audio = np.concatenate([audio[start:end] for start, end in segments])
                return speech_audio
            else:
                # No speech detected
                return np.array([])
            
        except Exception as e:
            logger.error(f"Error filtering audio in hybrid VAD: {e}")
            return audio  # Return original audio on error
    
    def _preprocess_audio(self, audio: np.ndarray) -> np.ndarray:
        """Preprocess audio to reduce noise.
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Preprocessed audio
        """
        try:
            # Simple noise reduction by removing low amplitude signals
            # Calculate noise floor as the 10th percentile of absolute amplitude
            if len(audio) > 0:
                noise_floor = np.percentile(np.abs(audio), 10)
                
                # Apply soft noise gate
                audio = np.where(np.abs(audio) < noise_floor * 2, audio * 0.1, audio)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            return audio  # Return original audio on error


def create_vad(vad_type: str = "silero", **kwargs) -> Optional[object]:
    """Create a VAD instance.
    
    Args:
        vad_type: Type of VAD to create ("silero", "webrtc", or "hybrid")
        **kwargs: Additional arguments for the VAD
        
    Returns:
        VAD instance or None if creation fails
    """
    try:
        if vad_type.lower() == "silero":
            return SileroVAD(**kwargs)
        elif vad_type.lower() == "webrtc":
            return WebRTCVAD(**kwargs)
        elif vad_type.lower() == "hybrid":
            return HybridVAD(**kwargs)
        else:
            logger.error(f"Unknown VAD type: {vad_type}")
            return None
    except Exception as e:
        logger.error(f"Error creating VAD: {e}")
        return None


if __name__ == "__main__":
    # Test VAD
    import sounddevice as sd
    import time
    
    # Create VAD
    vad = create_vad("silero", threshold=0.5)
    
    # Record audio
    duration = 5  # seconds
    sample_rate = 16000
    
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    # Check if speech
    start_time = time.time()
    is_speech = vad.is_speech(audio)
    end_time = time.time()
    
    print(f"Speech detected: {is_speech} (took {end_time - start_time:.3f} seconds)")
    
    # Get speech segments
    start_time = time.time()
    segments = vad.get_speech_segments(audio)
    end_time = time.time()
    
    print(f"Speech segments: {segments} (took {end_time - start_time:.3f} seconds)")
    
    # Filter audio
    start_time = time.time()
    filtered_audio = vad.filter_audio(audio)
    end_time = time.time()
    
    print(f"Filtered audio length: {len(filtered_audio)} (took {end_time - start_time:.3f} seconds)")