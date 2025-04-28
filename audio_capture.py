import sounddevice as sd
import numpy as np

class AudioCapture:
    """
    AudioCapture class for handling microphone input with gain boosting and limiting.
    Supports low-output microphones like the Shure SM7B through adjustable gain boost.
    """
    def __init__(self, sample_rate=16000, channels=1, gain_boost=1.0):
        """
        Initialize the AudioCapture with configurable parameters.
        
        Args:
            sample_rate (int): Audio sample rate in Hz, default is 16000
            channels (int): Number of audio channels, default is 1 (mono)
            gain_boost (float): Gain multiplier for boosting low-output microphones,
                               default is 1.0 (no boost)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.gain_boost = gain_boost  # Default: no boost (1.0)
        self.stream = None
        
        # Log initialization
        print(f"AudioCapture initialized with sample_rate={sample_rate}, "
              f"channels={channels}, gain_boost={gain_boost}")

    def start_stream(self):
        """Start the audio input stream."""
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                callback=self.audio_callback
            )
            self.stream.start()
            print(f"Audio stream started with gain_boost={self.gain_boost}")
        except Exception as e:
            print(f"Error starting audio stream: {e}")

    def audio_callback(self, indata, frames, time, status):
        """
        Process incoming audio data.
        
        Args:
            indata: Input audio data as numpy array
            frames: Number of frames
            time: Timestamp
            status: Status of the stream
        """
        if status:
            print(f"Audio callback status: {status}")
        
        # Make a copy of the input data to avoid modifying the original
        processed_audio = indata.copy()
        
        # Apply gain boost if needed (gain_boost > 1.0)
        if self.gain_boost != 1.0:
            # Multiply audio samples by the gain factor
            processed_audio = processed_audio * self.gain_boost
            
            # Apply limiter to prevent digital clipping after boosting
            # Clip to 16-bit PCM range [-32768, 32767]
            processed_audio = np.clip(processed_audio, -32768, 32767).astype(np.int16)
        
        # Here you would pass processed_audio to VAD or further processing
        # For example: self.audio_queue.put(processed_audio)

    def stop_stream(self):
        """Stop and close the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("Audio stream stopped")
    
    def set_gain_boost(self, gain_value):
        """
        Set a new gain boost value.
        
        Args:
            gain_value (float): New gain multiplier (1.0 = no boost, 2.0 = double volume, etc.)
        """
        if gain_value < 0:
            print(f"Warning: Negative gain ({gain_value}) not allowed. Setting to 0.")
            gain_value = 0
        
        self.gain_boost = gain_value
        print(f"Gain boost set to {self.gain_boost}")
