#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Download Silero VAD model for Genie Whisper.
This script downloads the Silero VAD model from Hugging Face.
"""

import os
import urllib.request
from pathlib import Path

def get_models_dir():
    """Get the path to the models directory."""
    # Get the project root directory (parent of the scripts directory)
    project_root = Path(__file__).resolve().parent.parent
    
    # Create models directory if it doesn't exist
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Create VAD directory
    vad_dir = models_dir / "vad"
    vad_dir.mkdir(exist_ok=True)
    
    return vad_dir

def download_silero_vad():
    """Download the Silero VAD model from Hugging Face."""
    try:
        print("Downloading Silero VAD model...")
        
        # Get the VAD directory
        vad_dir = get_models_dir()
        
        # The Hugging Face URL for the Silero VAD model
        model_url = "https://huggingface.co/snakers4/silero-vad/resolve/main/silero_vad.onnx"
        model_path = vad_dir / "silero_vad.onnx"
        
        # Download the model
        print(f"Downloading from {model_url}...")
        
        # Set up headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        req = urllib.request.Request(model_url, headers=headers)
        with urllib.request.urlopen(req) as response, open(model_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        
        print(f"Silero VAD model downloaded successfully to {model_path}")
        return True
        
    except Exception as e:
        print(f"Error downloading Silero VAD model: {e}")
        
        # Try alternative URL if the first one fails
        try:
            print("Trying alternative download source...")
            alt_model_url = "https://huggingface.co/alphacep/vosk-models/resolve/main/vad/silero_vad.onnx"
            print(f"Downloading from {alt_model_url}...")
            
            req = urllib.request.Request(alt_model_url, headers=headers)
            with urllib.request.urlopen(req) as response, open(vad_dir / "silero_vad.onnx", 'wb') as out_file:
                data = response.read()
                out_file.write(data)
                
            print(f"Silero VAD model downloaded successfully from alternative source")
            return True
        except Exception as e2:
            print(f"Error downloading from alternative source: {e2}")
            
            # Try one more source
            try:
                print("Trying third download source...")
                third_model_url = "https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx"
                print(f"Downloading from {third_model_url}...")
                
                req = urllib.request.Request(third_model_url, headers=headers)
                with urllib.request.urlopen(req) as response, open(vad_dir / "silero_vad.onnx", 'wb') as out_file:
                    data = response.read()
                    out_file.write(data)
                    
                print(f"Silero VAD model downloaded successfully from third source")
                return True
            except Exception as e3:
                print(f"Error downloading from third source: {e3}")
                return False

if __name__ == "__main__":
    success = download_silero_vad()
    if success:
        print("VAD model download completed successfully.")
    else:
        print("Failed to download VAD model.")