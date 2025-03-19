#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Download Whisper models for Genie Whisper.
This script downloads the specified Whisper models to the models directory.
"""

import argparse
import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the environment and check for required packages."""
    try:
        import faster_whisper
        print(f"faster-whisper version: {faster_whisper.__version__}")
    except ImportError:
        print("Error: faster-whisper package not found.")
        print("Please install it using: pip install faster-whisper")
        sys.exit(1)

def get_models_dir():
    """Get the path to the models directory."""
    # Get the project root directory (parent of the scripts directory)
    project_root = Path(__file__).resolve().parent.parent
    
    # Create models directory if it doesn't exist
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    return models_dir

def download_model(model_size, models_dir):
    """Download a Whisper model.
    
    Args:
        model_size: Size of the model to download
        models_dir: Directory to save the model
    """
    try:
        from faster_whisper import WhisperModel
        
        print(f"Downloading {model_size} model...")
        
        # Initialize the model, which will download it if not present
        model = WhisperModel(
            model_size_or_path=model_size,
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir)
        )
        
        print(f"{model_size} model downloaded successfully.")
        return True
        
    except Exception as e:
        print(f"Error downloading {model_size} model: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download Whisper models for Genie Whisper")
    
    parser.add_argument(
        "--models",
        type=str,
        default="tiny,base",
        help="Comma-separated list of models to download (tiny, base, small, medium, large)"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    # Get models directory
    models_dir = get_models_dir()
    print(f"Models will be downloaded to: {models_dir}")
    
    # Parse models to download
    model_sizes = [size.strip() for size in args.models.split(",")]
    valid_sizes = ["tiny", "base", "small", "medium", "large"]
    
    # Validate model sizes
    for size in model_sizes:
        if size not in valid_sizes:
            print(f"Warning: Invalid model size '{size}'. Valid sizes are: {', '.join(valid_sizes)}")
            model_sizes.remove(size)
    
    if not model_sizes:
        print("No valid model sizes specified.")
        sys.exit(1)
    
    # Download models
    success_count = 0
    for size in model_sizes:
        print(f"\nDownloading {size} model...")
        if download_model(size, models_dir):
            success_count += 1
    
    # Print summary
    print(f"\nDownloaded {success_count} of {len(model_sizes)} models.")
    
    if success_count == len(model_sizes):
        print("All models downloaded successfully!")
    else:
        print("Some models failed to download. Please check the error messages above.")

if __name__ == "__main__":
    main()