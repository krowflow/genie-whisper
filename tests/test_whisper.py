#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Whisper model loading and basic transcription.
This script verifies that the Whisper model can be loaded and used for transcription.
"""

import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_whisper_loading():
    """Test loading the Whisper model."""
    try:
        logger.info("Testing Whisper model loading...")
        
        # Import faster_whisper
        from faster_whisper import WhisperModel
        
        # Get models directory
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            logger.info(f"Created models directory: {models_dir}")
        
        # Try to detect if CUDA is available
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                device = "cuda"
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"CUDA is available. Using GPU: {gpu_name} with {gpu_memory:.2f} GB memory")
                compute_type = "float16"  # Use float16 for CUDA
            else:
                device = "cpu"
                logger.info("CUDA is not available. Using CPU.")
                compute_type = "int8"  # Use int8 for CPU
        except ImportError:
            device = "cpu"
            compute_type = "int8"
            logger.info("PyTorch not available. Using CPU.")
        
        # Load the model
        logger.info(f"Loading Whisper model: base on {device} with {compute_type}")
        start_time = time.time()
        
        model = WhisperModel(
            model_size_or_path="base",
            device=device,
            compute_type=compute_type,
            download_root=models_dir,
            cpu_threads=4,
            num_workers=1
        )
        
        end_time = time.time()
        logger.info(f"Model loaded successfully in {end_time - start_time:.2f} seconds")
        
        # Test transcription with a simple audio sample
        logger.info("Testing transcription with a simple audio sample...")
        
        # Create a simple test audio (silence)
        import numpy as np
        sample_rate = 16000
        duration = 2  # seconds
        audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        # Transcribe
        start_time = time.time()
        segments, info = model.transcribe(audio, language="en")
        segments = list(segments)  # Convert generator to list
        end_time = time.time()
        
        logger.info(f"Transcription completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Detected language: {info.language} with probability {info.language_probability:.2f}")
        logger.info(f"Number of segments: {len(segments)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Whisper model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_whisper_loading()
    if success:
        logger.info("Whisper test completed successfully!")
        sys.exit(0)
    else:
        logger.error("Whisper test failed!")
        sys.exit(1)