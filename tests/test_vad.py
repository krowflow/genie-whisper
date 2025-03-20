#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Voice Activity Detection (VAD).
This script verifies that the VAD modules can be loaded and used for speech detection.
"""

import os
import sys
import time
import logging
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_webrtc_vad():
    """Test WebRTC VAD."""
    try:
        logger.info("Testing WebRTC VAD...")
        
        # Import webrtcvad
        import webrtcvad
        
        # Create VAD
        vad = webrtcvad.Vad(3)  # Aggressiveness level 3 (highest)
        
        # Create a sample audio frame (30ms of silence at 16kHz)
        sample_rate = 16000
        frame_duration_ms = 30
        frame_size = int(sample_rate * frame_duration_ms / 1000)
        frame = b'\x00' * frame_size * 2  # 16-bit samples
        
        # Test VAD
        is_speech = vad.is_speech(frame, sample_rate)
        logger.info(f"WebRTC VAD detected speech: {is_speech}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing WebRTC VAD: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_vad_wrapper():
    """Create a simple VAD wrapper class."""
    
    class WebRtcVAD:
        """Wrapper for WebRTC VAD."""
        
        def __init__(self, aggressiveness=3):
            """Initialize WebRTC VAD.
            
            Args:
                aggressiveness: Aggressiveness level (0-3)
            """
            import webrtcvad
            self.vad = webrtcvad.Vad(aggressiveness)
            self.sample_rate = 16000
            self.frame_duration_ms = 30
            self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
            
        def is_speech(self, audio):
            """Check if audio contains speech.
            
            Args:
                audio: Audio samples (numpy array)
                
            Returns:
                True if speech is detected, False otherwise
            """
            # Convert float32 to int16
            if audio.dtype == np.float32:
                audio = (audio * 32767).astype(np.int16)
                
            # Ensure audio is int16
            if audio.dtype != np.int16:
                audio = audio.astype(np.int16)
                
            # Convert to bytes
            audio_bytes = audio.tobytes()
            
            # Split into frames
            frames = []
            for i in range(0, len(audio_bytes), self.frame_size * 2):
                frame = audio_bytes[i:i + self.frame_size * 2]
                if len(frame) == self.frame_size * 2:
                    frames.append(frame)
            
            # Check each frame
            speech_frames = 0
            for frame in frames:
                try:
                    if self.vad.is_speech(frame, self.sample_rate):
                        speech_frames += 1
                except Exception as e:
                    logger.warning(f"Error processing frame: {e}")
            
            # Return True if at least 10% of frames contain speech
            return speech_frames > len(frames) * 0.1
            
        def filter_audio(self, audio):
            """Filter audio to keep only speech segments.
            
            Args:
                audio: Audio samples (numpy array)
                
            Returns:
                Filtered audio with only speech segments
            """
            # Convert float32 to int16
            if audio.dtype == np.float32:
                audio = (audio * 32767).astype(np.int16)
                
            # Ensure audio is int16
            if audio.dtype != np.int16:
                audio = audio.astype(np.int16)
                
            # Convert to bytes
            audio_bytes = audio.tobytes()
            
            # Split into frames
            frames = []
            for i in range(0, len(audio_bytes), self.frame_size * 2):
                frame = audio_bytes[i:i + self.frame_size * 2]
                if len(frame) == self.frame_size * 2:
                    frames.append(frame)
            
            # Check each frame
            speech_frames = []
            for i, frame in enumerate(frames):
                try:
                    if self.vad.is_speech(frame, self.sample_rate):
                        speech_frames.append(i)
                except Exception as e:
                    logger.warning(f"Error processing frame: {e}")
            
            # If no speech frames, return empty array
            if not speech_frames:
                return np.array([])
            
            # Merge consecutive speech frames
            segments = []
            start = speech_frames[0]
            end = speech_frames[0]
            
            for i in range(1, len(speech_frames)):
                if speech_frames[i] == end + 1:
                    end = speech_frames[i]
                else:
                    segments.append((start, end + 1))
                    start = speech_frames[i]
                    end = speech_frames[i]
            
            segments.append((start, end + 1))
            
            # Convert segments to samples
            filtered_audio = []
            for start, end in segments:
                start_sample = start * self.frame_size
                end_sample = end * self.frame_size
                filtered_audio.append(audio[start_sample:end_sample])
            
            # Concatenate segments
            if filtered_audio:
                return np.concatenate(filtered_audio)
            else:
                return np.array([])
                
        def get_speech_segments(self, audio):
            """Get speech segments from audio.
            
            Args:
                audio: Audio samples (numpy array)
                
            Returns:
                List of (start, end) tuples for speech segments
            """
            # Convert float32 to int16
            if audio.dtype == np.float32:
                audio = (audio * 32767).astype(np.int16)
                
            # Ensure audio is int16
            if audio.dtype != np.int16:
                audio = audio.astype(np.int16)
                
            # Convert to bytes
            audio_bytes = audio.tobytes()
            
            # Split into frames
            frames = []
            for i in range(0, len(audio_bytes), self.frame_size * 2):
                frame = audio_bytes[i:i + self.frame_size * 2]
                if len(frame) == self.frame_size * 2:
                    frames.append(frame)
            
            # Check each frame
            speech_frames = []
            for i, frame in enumerate(frames):
                try:
                    if self.vad.is_speech(frame, self.sample_rate):
                        speech_frames.append(i)
                except Exception as e:
                    logger.warning(f"Error processing frame: {e}")
            
            # If no speech frames, return empty list
            if not speech_frames:
                return []
            
            # Merge consecutive speech frames
            segments = []
            start = speech_frames[0]
            end = speech_frames[0]
            
            for i in range(1, len(speech_frames)):
                if speech_frames[i] == end + 1:
                    end = speech_frames[i]
                else:
                    segments.append((start, end + 1))
                    start = speech_frames[i]
                    end = speech_frames[i]
            
            segments.append((start, end + 1))
            
            # Convert segments to samples
            result = []
            for start, end in segments:
                start_sample = start * self.frame_size
                end_sample = end * self.frame_size
                result.append((start_sample, end_sample))
            
            return result
    
    return WebRtcVAD

def test_vad_wrapper():
    """Test VAD wrapper."""
    try:
        logger.info("Testing VAD wrapper...")
        
        # Create VAD wrapper
        WebRtcVAD = create_vad_wrapper()
        vad = WebRtcVAD(aggressiveness=3)
        
        # Create a sample audio (silence)
        sample_rate = 16000
        duration = 2  # seconds
        audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        # Test is_speech
        is_speech = vad.is_speech(audio)
        logger.info(f"VAD wrapper detected speech: {is_speech}")
        
        # Test filter_audio
        filtered_audio = vad.filter_audio(audio)
        logger.info(f"Filtered audio length: {len(filtered_audio)}")
        
        # Test get_speech_segments
        segments = vad.get_speech_segments(audio)
        logger.info(f"Speech segments: {segments}")
        
        # Create a sample audio with "speech" (just noise for testing)
        audio = np.random.normal(0, 0.1, sample_rate * duration).astype(np.float32)
        
        # Test is_speech
        is_speech = vad.is_speech(audio)
        logger.info(f"VAD wrapper detected speech in noise: {is_speech}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing VAD wrapper: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_webrtc_vad() and test_vad_wrapper()
    if success:
        logger.info("VAD tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("VAD tests failed!")
        sys.exit(1)