#!/bin/bash
# Genie Whisper Environment Setup Script
# This script sets up a virtual environment and installs the required dependencies

# Stop on error
set -e

echo -e "\033[36mSetting up Genie Whisper development environment...\033[0m"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "\033[31mPython not found. Please install Python 3.9 or later.\033[0m"
    exit 1
fi

echo -e "\033[32mFound Python: $($PYTHON_CMD --version)\033[0m"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\033[33mCreating virtual environment...\033[0m"
    $PYTHON_CMD -m venv .venv
else
    echo -e "\033[32mVirtual environment already exists.\033[0m"
fi

# Activate virtual environment
echo -e "\033[33mActivating virtual environment...\033[0m"
source .venv/bin/activate

# Upgrade pip
echo -e "\033[33mUpgrading pip...\033[0m"
python -m pip install --upgrade pip

# Install core dependencies
echo -e "\033[33mInstalling core dependencies...\033[0m"
pip install --timeout 120 -r tests/requirements-minimal.txt

# Ask user if they want to install GPU or CPU version of PyTorch
read -p "Do you want to install PyTorch with GPU support? (y/n) " GPU_SUPPORT
if [[ $GPU_SUPPORT == "y" || $GPU_SUPPORT == "Y" ]]; then
    echo -e "\033[33mInstalling PyTorch with GPU support...\033[0m"
    pip install --timeout 300 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 || {
        echo -e "\033[33mFailed to install PyTorch with GPU support. Falling back to CPU version...\033[0m"
        pip install --timeout 120 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    }
else
    echo -e "\033[33mInstalling PyTorch CPU version...\033[0m"
    pip install --timeout 120 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install Whisper dependencies
echo -e "\033[33mInstalling Whisper dependencies...\033[0m"
pip install --timeout 120 -r tests/requirements-whisper.txt

# Run tests to verify installation
echo -e "\033[33mRunning tests to verify installation...\033[0m"

echo -e "\033[36mTesting Whisper...\033[0m"
python tests/test_whisper.py
if [ $? -ne 0 ]; then
    echo -e "\033[31mWhisper test failed.\033[0m"
else
    echo -e "\033[32mWhisper test passed!\033[0m"
fi

echo -e "\033[36mTesting VAD...\033[0m"
python tests/test_vad.py
if [ $? -ne 0 ]; then
    echo -e "\033[31mVAD test failed.\033[0m"
else
    echo -e "\033[32mVAD test passed!\033[0m"
fi

echo -e "\033[36mTesting IDE integration...\033[0m"
python tests/test_ide_integration.py
if [ $? -ne 0 ]; then
    echo -e "\033[31mIDE integration test failed.\033[0m"
else
    echo -e "\033[32mIDE integration test passed!\033[0m"
fi

echo -e "\033[32mEnvironment setup complete!\033[0m"
echo -e "\033[36mTo activate the virtual environment in the future, run: source .venv/bin/activate\033[0m"