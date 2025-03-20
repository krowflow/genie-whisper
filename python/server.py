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
from typing import Dict, List, Optional, Union

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
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 4000, device_id: Optional[int] = None):
        """Initialize the audio processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
            device_id: Audio device ID (None for default)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device_id = device_id
        self.audio_buffer = []
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
        self.audio_buffer = []
        
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
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return the recorded audio.
        
        Returns:
            Numpy array of audio samples
        """
        if not self.is_recording:
            logger.warning("Not recording")
            return np.array([])
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
            self.recording_thread = None
        
        # Combine all audio chunks
        if not self.audio_buffer:
            return np.array([])
        
        audio = np.concatenate(self.audio_buffer)
        self.audio_buffer = []
        
        return audio
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Add audio chunk to buffer
        self.audio_buffer.append(indata.copy())
        
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
    
    def set_device(self, device_id: int) -> bool:
        """Set the audio device.
        
        Args:
            device_id: Audio device ID
            
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
            logger.info(f"Audio device set to: {devices[device_id]['name']} (ID: {device_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting audio device: {e}")
            return False


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
        
        # Cache for repeated phrases to avoid redundant processing
        self.transcription_cache = {}
        self.cache_hits = 0
        
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
        """Transcribe audio using Whisper with optimized parameters.
        
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
            # Check cache for similar audio (simple hash-based caching)
            audio_hash = hash(audio.tobytes())
            if audio_hash in self.transcription_cache:
                self.cache_hits += 1
                logger.info(f"Using cached transcription (hits: {self.cache_hits})")
                return self.transcription_cache[audio_hash]
            
            logger.info("Transcribing audio...")
            start_time = time.time()
            
            # Optimize transcription parameters based on device
            beam_size = 3 if self.device == "cuda" else 1  # Smaller beam size for faster processing
            
            # Transcribe audio with optimized parameters
            segments, info = self.model.transcribe(
                audio,
                language=language,
                beam_size=beam_size,
                vad_filter=True,
                vad_parameters={"threshold": 0.5},  # Optimize VAD for speed
                condition_on_previous_text=False,   # Faster processing
                compression_ratio_threshold=2.4,    # Optimize for speed
                log_prob_threshold=-1.0,            # Optimize for speed
                no_speech_threshold=0.6             # Optimize for speed
            )
            
            # Combine segments
            text = " ".join(segment.text for segment in segments)
            
            # Update performance metrics
            end_time = time.time()
            transcription_time = end_time - start_time
            self.total_transcription_time += transcription_time
            self.transcription_count += 1
            avg_time = self.total_transcription_time / self.transcription_count
            
            # Cache the result
            self.transcription_cache[audio_hash] = text
            
            # Limit cache size to prevent memory issues
            if len(self.transcription_cache) > 100:
                # Remove oldest entries
                for _ in range(10):
                    self.transcription_cache.pop(next(iter(self.transcription_cache)))
            
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
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "avg_transcription_time": self.total_transcription_time / max(1, self.transcription_count),
            "transcription_count": self.transcription_count,
            "cache_hits": self.cache_hits,
            "cache_size": len(self.transcription_cache)
        }


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
        
        # Initialize components
        self.audio_processor = AudioProcessor(device_id=self.device_id)
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
        """Continuously transcribe audio while listening with optimized performance."""
        # Adaptive sleep time based on device
        sleep_time = 0.5 if self.device == "cuda" else 1.0
        
        # Minimum audio length for transcription (to avoid processing very short segments)
        min_audio_length = 0.5 * self.audio_processor.sample_rate
        
        # Last transcription time for adaptive processing
        last_transcription_time = time.time()
        
        # Performance tracking
        transcription_times = []
        
        while self.is_listening:
            start_time = time.time()
            
            # Get current audio buffer (copy)
            if not self.audio_processor.audio_buffer:
                time.sleep(sleep_time)
                continue
                
            audio = np.concatenate(self.audio_processor.audio_buffer)
            
            # Skip if audio is too short
            if len(audio) < min_audio_length:
                time.sleep(sleep_time)
                continue
            
            # Filter audio with VAD if enabled
            if self.use_vad:
                # Use enhanced VAD filtering
                filtered_audio = self.audio_processor.filter_audio(audio)
                
                # Check if we have any speech after filtering
                if len(filtered_audio) > 0:
                    audio = filtered_audio
                else:
                    # No speech detected, skip transcription
                    logger.debug("No speech detected in current buffer, skipping transcription")
                    time.sleep(sleep_time)
                    continue
            
            # Transcribe audio
            text = self.transcriber.transcribe(audio)
            
            # Track transcription time
            transcription_time = time.time() - start_time
            transcription_times.append(transcription_time)
            
            # Keep only the last 10 times for adaptive sleep
            if len(transcription_times) > 10:
                transcription_times.pop(0)
            
            # Calculate average transcription time
            avg_time = sum(transcription_times) / len(transcription_times)
            
            # Adjust sleep time based on transcription performance
            if avg_time < 0.5:
                # Fast transcription, can process more frequently
                sleep_time = max(0.2, sleep_time * 0.9)
            else:
                # Slow transcription, reduce frequency
                sleep_time = min(1.5, sleep_time * 1.1)
            
            # Send transcription result
            if text:
                self._send_message({
                    "type": "transcription",
                    "text": text,
                    "final": False,
                    "performance": {
                        "transcription_time": transcription_time,
                        "avg_time": avg_time
                    }
                })
                
                # Log performance
                logger.debug(f"Transcription time: {transcription_time:.2f}s, avg: {avg_time:.2f}s, sleep: {sleep_time:.2f}s")
            
            # Adaptive sleep based on performance
            time.sleep(sleep_time)
    
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
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Start the server
    server = GenieWhisperServer(args)
    server.start()