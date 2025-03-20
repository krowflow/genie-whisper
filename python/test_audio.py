#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for audio capture and transcription.
This script tests the audio capture, VAD, and transcription functionality.
"""

import argparse
import json
import logging
import os
import sys
import time
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
try:
    from python.vad import create_vad
    from python.wake_word import create_wake_word_detector
except ImportError as e:
    logger.error(f"Failed to import local modules: {e}")
    sys.exit(1)

def test_audio_capture(duration=5, sample_rate=16000):
    """Test audio capture.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz
    
    Returns:
        Numpy array of audio samples
    """
    try:
        import sounddevice as sd
        
        logger.info(f"Recording for {duration} seconds...")
        
        # Record audio
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        
        logger.info(f"Recording complete. Audio shape: {audio.shape}")
        
        return audio.squeeze()
        
    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        return None

def test_vad(audio, vad_type="silero", threshold=0.5):
    """Test Voice Activity Detection.
    
    Args:
        audio: Numpy array of audio samples
        vad_type: Type of VAD to use
        threshold: VAD threshold
    
    Returns:
        Filtered audio
    """
    try:
        logger.info(f"Testing {vad_type} VAD with threshold {threshold}...")
        
        # Create VAD
        vad = create_vad(vad_type, threshold=threshold)
        
        if vad is None:
            logger.error(f"Failed to create {vad_type} VAD")
            return audio
        
        # Check if audio contains speech
        start_time = time.time()
        is_speech = vad.is_speech(audio)
        end_time = time.time()
        
        logger.info(f"Speech detected: {is_speech} (took {end_time - start_time:.3f} seconds)")
        
        # Get speech segments
        start_time = time.time()
        segments = vad.get_speech_segments(audio)
        end_time = time.time()
        
        logger.info(f"Speech segments: {segments} (took {end_time - start_time:.3f} seconds)")
        
        # Filter audio
        start_time = time.time()
        filtered_audio = vad.filter_audio(audio)
        end_time = time.time()
        
        logger.info(f"Filtered audio shape: {filtered_audio.shape} (took {end_time - start_time:.3f} seconds)")
        
        return filtered_audio
        
    except Exception as e:
        logger.error(f"Error testing VAD: {e}")
        return audio

def test_wake_word(audio, wake_word="Hey Genie", threshold=0.5):
    """Test wake word detection.
    
    Args:
        audio: Numpy array of audio samples
        wake_word: Wake word to detect
        threshold: Detection threshold
    
    Returns:
        True if wake word detected, False otherwise
    """
    try:
        logger.info(f"Testing wake word detection for '{wake_word}' with threshold {threshold}...")
        
        # Create wake word detector
        detector = create_wake_word_detector("whisper", wake_word=wake_word, threshold=threshold)
        
        if detector is None:
            logger.error("Failed to create wake word detector")
            return False
        
        # Detect wake word
        start_time = time.time()
        detected = detector.detect_wake_word(audio)
        end_time = time.time()
        
        logger.info(f"Wake word detected: {detected} (took {end_time - start_time:.3f} seconds)")
        
        return detected
        
    except Exception as e:
        logger.error(f"Error testing wake word detection: {e}")
        return False

def test_transcription(audio, model_size="tiny"):
    """Test transcription.
    
    Args:
        audio: Numpy array of audio samples
        model_size: Whisper model size
    
    Returns:
        Transcribed text
    """
    try:
        from faster_whisper import WhisperModel
        
        logger.info(f"Testing transcription with {model_size} model...")
        
        # Get models directory
        models_dir = Path(__file__).resolve().parent.parent / "models"
        
        # Create model
        start_time = time.time()
        model = WhisperModel(
            model_size_or_path=model_size,
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir)
        )
        end_time = time.time()
        
        logger.info(f"Model loaded in {end_time - start_time:.3f} seconds")
        
        # Transcribe audio
        start_time = time.time()
        segments, info = model.transcribe(audio, beam_size=5, vad_filter=True)
        
        # Combine segments
        text = " ".join(segment.text for segment in segments)
        end_time = time.time()
        
        logger.info(f"Transcription: '{text}' (took {end_time - start_time:.3f} seconds)")
        
        return text
        
    except Exception as e:
        logger.error(f"Error testing transcription: {e}")
        return ""

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test audio capture and transcription")
    
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Recording duration in seconds"
    )
    
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Sample rate in Hz"
    )
    
    parser.add_argument(
        "--vad-type",
        type=str,
        default="silero",
        choices=["silero", "webrtc"],
        help="Type of VAD to use"
    )
    
    parser.add_argument(
        "--vad-threshold",
        type=float,
        default=0.5,
        help="VAD threshold"
    )
    
    parser.add_argument(
        "--wake-word",
        type=str,
        default="Hey Genie",
        help="Wake word to detect"
    )
    
    parser.add_argument(
        "--model-size",
        type=str,
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size"
    )
    
    args = parser.parse_args()
    
    # Test audio capture
    audio = test_audio_capture(args.duration, args.sample_rate)
    
    if audio is None:
        logger.error("Audio capture failed")
        sys.exit(1)
    
    # Test VAD
    filtered_audio = test_vad(audio, args.vad_type, args.vad_threshold)
    
    # Test wake word detection
    test_wake_word(audio, args.wake_word, args.vad_threshold)
    
    # Test transcription
    test_transcription(filtered_audio, args.model_size)
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()