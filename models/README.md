# Whisper Models Directory

This directory contains the Whisper models used by Genie Whisper for speech-to-text transcription.

## Available Models

Genie Whisper supports the following Whisper models:

| Model | Size | Languages | Description |
|-------|------|-----------|-------------|
| `tiny` | ~75 MB | English-only | Fastest, lowest accuracy |
| `base` | ~142 MB | English-only | Fast, decent accuracy |
| `small` | ~466 MB | English-only | Balanced speed/accuracy |
| `medium` | ~1.5 GB | English-only | High accuracy, slower |
| `large` | ~3 GB | Multilingual | Highest accuracy, slowest |

## Downloading Models

Models are automatically downloaded when first used. However, you can pre-download them using the provided script:

```bash
# Download tiny and base models (default)
python scripts/download_models.py

# Download specific models
python scripts/download_models.py --models tiny,base,small

# Download all models
python scripts/download_models.py --models tiny,base,small,medium,large
```

## Model Selection

You can select which model to use in the application settings. The choice involves a trade-off between:

- **Speed**: Smaller models are faster but less accurate
- **Accuracy**: Larger models are more accurate but slower
- **Disk Space**: Larger models require more storage
- **Memory Usage**: Larger models use more RAM during transcription

For most users, the `base` model provides a good balance between speed and accuracy.

## Technical Details

Genie Whisper uses the Faster-Whisper implementation, which is an optimized version of OpenAI's Whisper model. The models are quantized to int8 precision to improve performance.

## Offline Usage

All models work completely offline once downloaded, ensuring your voice data never leaves your computer.