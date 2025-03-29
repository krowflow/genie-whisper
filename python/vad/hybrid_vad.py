#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hybrid Voice Activity Detection (VAD) module for Genie Whisper.

This module implements a hybrid approach using both Silero VAD and WebRTC VAD.
If Silero VAD is unavailable, it falls back to using only WebRTC VAD.
"""

import os
import logging
import numpy as np
import torch
import webrtcvad
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hybrid_vad")

class HybridVAD:
    """
    Hybrid Voice Activity Detection using both Silero VAD and WebRTC VAD.
    Falls back to WebRTC VAD if Silero is unavailable.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        silero_threshold: float = 0.5,
        webrtc_aggressiveness: int = 2,
        use_silero: bool = True,
        models_dir: Optional[str] = None,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 500,
        window_size_samples: int = 512,
        speech_pad_ms: int = 30
    ):
        """
        Initialize the Hybrid VAD.
        
        Args:
            sample_rate: Audio sample rate (must be 16000 for WebRTC VAD)
            silero_threshold: Threshold for Silero VAD (0.0 to 1.0)
            webrtc_aggressiveness: Aggressiveness for WebRTC VAD (0 to 3)
            use_silero: Whether to attempt to use Silero VAD
            models_dir: Directory containing the Silero VAD model
            min_speech_duration_ms: Minimum speech segment duration in ms
            min_silence_duration_ms: Minimum silence segment duration in ms
            window_size_samples: Window size for Silero VAD
            speech_pad_ms: Padding to add to speech segments in ms
        """
        self.sample_rate = sample_rate
        self.silero_threshold = silero_threshold
        self.webrtc_aggressiveness = webrtc_aggressiveness
        self.use_silero = use_silero
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.window_size_samples = window_size_samples
        self.speech_pad_ms = speech_pad_ms
        
        # Initialize WebRTC VAD
        self.webrtc_vad = webrtcvad.Vad(self.webrtc_aggressiveness)
        
        # Initialize Silero VAD if requested
        self.silero_vad = None
        self.silero_available = False
        
        if self.use_silero:
            try:
                # Get models directory
                if models_dir is None:
                    # Get the project root directory
                    project_root = Path(__file__).resolve().parent.parent.parent
                    models_dir = project_root / "models"
                else:
                    models_dir = Path(models_dir)
                
                # Check if Silero VAD model exists
                vad_dir = models_dir / "vad"
                model_path = vad_dir / "silero_vad.onnx"
                
                if model_path.exists():
                    # Load Silero VAD model
                    logger.info(f"Loading Silero VAD model from {model_path}")
                    self.silero_vad = torch.jit.load(str(model_path))
                    self.silero_available = True
                    logger.info("Silero VAD model loaded successfully")
                else:
                    # Try to load from torch hub
                    try:
                        logger.info("Silero VAD model not found locally, trying to load from torch hub")
                        self.silero_vad, _ = torch.hub.load(
                            repo_or_dir='snakers4/silero-vad',
                            model='silero_vad',
                            force_reload=False,
                            onnx=False,
                            verbose=False
                        )
                        self.silero_available = True
                        logger.info("Silero VAD model loaded from torch hub")
                    except Exception as e:
                        logger.warning(f"Failed to load Silero VAD model from torch hub: {e}")
                        logger.warning("Falling back to WebRTC VAD only")
                        self.silero_available = False
            except Exception as e:
                logger.warning(f"Failed to initialize Silero VAD: {e}")
                logger.warning("Falling back to WebRTC VAD only")
                self.silero_available = False
        
        # Log initialization status
        if self.silero_available:
            logger.info("Hybrid VAD initialized with Silero and WebRTC")
        else:
            logger.info("Hybrid VAD initialized with WebRTC only (Silero unavailable)")
    
    def detect_speech(self, audio_data: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect speech segments in audio data.
        
        Args:
            audio_data: Audio data as numpy array (16-bit PCM, 16kHz)
            
        Returns:
            List of speech segments with start and end times in seconds
        """
        # Ensure audio data is in the correct format
        if audio_data.dtype != np.int16:
            audio_data = (audio_data * 32767).astype(np.int16)
        
        # Detect speech using both VADs if Silero is available
        if self.silero_available:
            return self._hybrid_detection(audio_data)
        else:
            return self._webrtc_detection(audio_data)
    
    def _hybrid_detection(self, audio_data: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect speech using both Silero and WebRTC VAD.
        
        Args:
            audio_data: Audio data as numpy array (16-bit PCM, 16kHz)
            
        Returns:
            List of speech segments with start and end times in seconds
        """
        # Get speech segments from both VADs
        silero_segments = self._silero_detection(audio_data)
        webrtc_segments = self._webrtc_detection(audio_data)
        
        # Merge segments
        merged_segments = self._merge_segments(silero_segments, webrtc_segments)
        
        return merged_segments
    
    def _silero_detection(self, audio_data: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect speech using Silero VAD.
        
        Args:
            audio_data: Audio data as numpy array (16-bit PCM, 16kHz)
            
        Returns:
            List of speech segments with start and end times in seconds
        """
        try:
            # Convert to float32 and normalize
            float_audio = audio_data.astype(np.float32) / 32767.0
            
            # Convert to tensor
            tensor_audio = torch.from_numpy(float_audio)
            
            # Get speech timestamps
            speech_timestamps = self.silero_vad(
                tensor_audio,
                self.sample_rate,
                threshold=self.silero_threshold,
                min_speech_duration_ms=self.min_speech_duration_ms,
                min_silence_duration_ms=self.min_silence_duration_ms,
                window_size_samples=self.window_size_samples,
                speech_pad_ms=self.speech_pad_ms
            )
            
            # Convert to seconds
            segments = []
            for segment in speech_timestamps:
                start_sample = segment['start']
                end_sample = segment['end']
                start_time = start_sample / self.sample_rate
                end_time = end_sample / self.sample_rate
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'source': 'silero'
                })
            
            return segments
        except Exception as e:
            logger.warning(f"Silero VAD detection failed: {e}")
            return []
    
    def _webrtc_detection(self, audio_data: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect speech using WebRTC VAD.
        
        Args:
            audio_data: Audio data as numpy array (16-bit PCM, 16kHz)
            
        Returns:
            List of speech segments with start and end times in seconds
        """
        # WebRTC VAD requires 10, 20, or 30 ms frames
        frame_duration_ms = 30
        frame_size = int(self.sample_rate * frame_duration_ms / 1000)
        
        # Split audio into frames
        num_frames = len(audio_data) // frame_size
        frames = [audio_data[i * frame_size:(i + 1) * frame_size] for i in range(num_frames)]
        
        # Process each frame
        is_speech = []
        for frame in frames:
            try:
                is_speech.append(self.webrtc_vad.is_speech(frame.tobytes(), self.sample_rate))
            except Exception as e:
                logger.warning(f"WebRTC VAD frame processing error: {e}")
                is_speech.append(False)
        
        # Find speech segments
        segments = []
        in_speech = False
        start_frame = 0
        
        for i, speech in enumerate(is_speech):
            if speech and not in_speech:
                # Speech start
                in_speech = True
                start_frame = i
            elif not speech and in_speech:
                # Speech end
                in_speech = False
                # Convert to seconds
                start_time = start_frame * frame_duration_ms / 1000
                end_time = i * frame_duration_ms / 1000
                
                # Only add if duration is above threshold
                if (end_time - start_time) * 1000 >= self.min_speech_duration_ms:
                    segments.append({
                        'start': start_time,
                        'end': end_time,
                        'source': 'webrtc'
                    })
        
        # Handle case where audio ends during speech
        if in_speech:
            start_time = start_frame * frame_duration_ms / 1000
            end_time = len(is_speech) * frame_duration_ms / 1000
            
            # Only add if duration is above threshold
            if (end_time - start_time) * 1000 >= self.min_speech_duration_ms:
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'source': 'webrtc'
                })
        
        return segments
    
    def _merge_segments(self, silero_segments: List[Dict[str, Any]], webrtc_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge speech segments from both VADs.
        
        Args:
            silero_segments: Speech segments from Silero VAD
            webrtc_segments: Speech segments from WebRTC VAD
            
        Returns:
            Merged speech segments
        """
        # Combine all segments
        all_segments = silero_segments + webrtc_segments
        
        # Sort by start time
        all_segments.sort(key=lambda x: x['start'])
        
        # Merge overlapping segments
        merged_segments = []
        if not all_segments:
            return merged_segments
        
        current_segment = all_segments[0].copy()
        
        for segment in all_segments[1:]:
            # If current segment overlaps with next segment
            if segment['start'] <= current_segment['end']:
                # Extend current segment
                current_segment['end'] = max(current_segment['end'], segment['end'])
                # Update source
                if current_segment['source'] != segment['source']:
                    current_segment['source'] = 'hybrid'
            else:
                # No overlap, add current segment and start a new one
                merged_segments.append(current_segment)
                current_segment = segment.copy()
        
        # Add the last segment
        merged_segments.append(current_segment)
        
        return merged_segments

# Example usage
if __name__ == "__main__":
    # Create a hybrid VAD
    vad = HybridVAD()
    
    # Generate some test audio (1 second of silence, 1 second of "speech", 1 second of silence)
    silence = np.zeros(16000, dtype=np.int16)
    speech = np.random.randint(-32768, 32767, 16000, dtype=np.int16)
    audio = np.concatenate([silence, speech, silence])
    
    # Detect speech
    segments = vad.detect_speech(audio)
    
    # Print results
    print(f"Detected {len(segments)} speech segments:")
    for i, segment in enumerate(segments):
        print(f"Segment {i+1}: {segment['start']:.2f}s to {segment['end']:.2f}s (source: {segment['source']})")