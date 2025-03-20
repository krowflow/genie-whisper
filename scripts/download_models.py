#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Download models for Genie Whisper.
This script downloads the specified Whisper models and VAD models to the models directory.
"""

import argparse
import os
import sys
import torch
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment and check for required packages."""
    missing_packages = []
    
    try:
        import faster_whisper
        print(f"faster-whisper version: {faster_whisper.__version__}")
    except ImportError:
        missing_packages.append("faster-whisper")
    
    try:
        import torch
        print(f"torch version: {torch.__version__}")
    except ImportError:
        missing_packages.append("torch")
    
    try:
        import torchaudio
        print(f"torchaudio version: {torchaudio.__version__}")
    except ImportError:
        missing_packages.append("torchaudio")
    
    if missing_packages:
        print(f"Error: The following packages are missing: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        sys.exit(1)

def get_models_dir():
    """Get the path to the models directory."""
    # Get the project root directory (parent of the scripts directory)
    project_root = Path(__file__).resolve().parent.parent
    
    # Create models directory if it doesn't exist
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    return models_dir

def download_whisper_model(model_size, models_dir):
    """Download a Whisper model.
    
    Args:
        model_size: Size of the model to download
        models_dir: Directory to save the model
    """
    try:
        from faster_whisper import WhisperModel
        
        print(f"Downloading Whisper {model_size} model...")
        
        # Initialize the model, which will download it if not present
        model = WhisperModel(
            model_size_or_path=model_size,
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir)
        )
        
        print(f"Whisper {model_size} model downloaded successfully.")
        return True
        
    except Exception as e:
        print(f"Error downloading Whisper {model_size} model: {e}")
        return False

def download_silero_vad_model(models_dir):
    """Download the Silero VAD model.
    
    Args:
        models_dir: Directory to save the model
    """
    try:
        print("Downloading Silero VAD model...")
        
        # Create VAD directory
        vad_dir = models_dir / "vad"
        vad_dir.mkdir(exist_ok=True)
        
        # Download the model
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False,
            verbose=False
        )
        
        # Save the model
        torch.save(model.state_dict(), vad_dir / "silero_vad.pt")
        
        # Download ONNX model
        onnx_model_url = 'https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx'
        torch.hub.download_url_to_file(onnx_model_url, vad_dir / "silero_vad.onnx")
        
        print("Silero VAD model downloaded successfully.")
        return True
        
    except Exception as e:
        print(f"Error downloading Silero VAD model: {e}")
        return False

def download_porcupine_model(models_dir, access_key=None):
    """Download the Porcupine wake word model.
    
    Args:
        models_dir: Directory to save the model
        access_key: Picovoice access key (optional)
    """
    try:
        # Skip if no access key
        if not access_key:
            print("Skipping Porcupine model download (no access key provided).")
            return False
        
        print("Downloading Porcupine wake word model...")
        
        # Create wake word directory
        ww_dir = models_dir / "wake_word"
        ww_dir.mkdir(exist_ok=True)
        
        # Import Porcupine
        import pvporcupine
        
        # Download the model
        handle = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis"]  # Use a built-in keyword
        )
        
        # Get model path
        model_path = handle.model_path
        
        # Copy model to our directory
        shutil.copy(model_path, ww_dir / "porcupine_model.pv")
        
        # Clean up
        handle.delete()
        
        print("Porcupine wake word model downloaded successfully.")
        return True
        
    except Exception as e:
        print(f"Error downloading Porcupine wake word model: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download models for Genie Whisper")
    
    parser.add_argument(
        "--whisper-models",
        type=str,
        default="tiny,base",
        help="Comma-separated list of Whisper models to download (tiny, base, small, medium, large)"
    )
    
    parser.add_argument(
        "--vad",
        action="store_true",
        default=True,
        help="Download Silero VAD model"
    )
    
    parser.add_argument(
        "--porcupine",
        action="store_true",
        default=False,
        help="Download Porcupine wake word model"
    )
    
    parser.add_argument(
        "--pv-access-key",
        type=str,
        default=None,
        help="Picovoice access key for Porcupine"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    # Get models directory
    models_dir = get_models_dir()
    print(f"Models will be downloaded to: {models_dir}")
    
    # Parse Whisper models to download
    whisper_models = [size.strip() for size in args.whisper_models.split(",")]
    valid_sizes = ["tiny", "base", "small", "medium", "large"]
    
    # Validate model sizes
    for size in whisper_models[:]:  # Create a copy to iterate over
        if size not in valid_sizes:
            print(f"Warning: Invalid model size '{size}'. Valid sizes are: {', '.join(valid_sizes)}")
            whisper_models.remove(size)
    
    if not whisper_models:
        print("No valid Whisper model sizes specified.")
        sys.exit(1)
    
    # Download Whisper models
    whisper_success_count = 0
    for size in whisper_models:
        print(f"\nDownloading Whisper {size} model...")
        if download_whisper_model(size, models_dir):
            whisper_success_count += 1
    
    # Download VAD model
    vad_success = False
    if args.vad:
        print("\nDownloading VAD model...")
        vad_success = download_silero_vad_model(models_dir)
    
    # Download Porcupine model
    porcupine_success = False
    if args.porcupine:
        print("\nDownloading Porcupine model...")
        porcupine_success = download_porcupine_model(models_dir, args.pv_access_key)
    
    # Print summary
    print("\n=== Download Summary ===")
    print(f"Whisper models: {whisper_success_count} of {len(whisper_models)} downloaded successfully")
    
    if args.vad:
        print(f"VAD model: {'Success' if vad_success else 'Failed'}")
    
    if args.porcupine:
        print(f"Porcupine model: {'Success' if porcupine_success else 'Failed'}")
    
    # Check overall success
    all_success = (whisper_success_count == len(whisper_models))
    if args.vad:
        all_success = all_success and vad_success
    if args.porcupine:
        all_success = all_success and porcupine_success
    
    if all_success:
        print("\nAll models downloaded successfully!")
    else:
        print("\nSome models failed to download. Please check the error messages above.")

if __name__ == "__main__":
    main()