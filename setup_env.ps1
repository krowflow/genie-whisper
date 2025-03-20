# Genie Whisper Environment Setup Script
# This script sets up a virtual environment and installs the required dependencies

# Stop on error
$ErrorActionPreference = "Stop"

Write-Host "Setting up Genie Whisper development environment..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.9 or later." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if (-not $?) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if (-not $?) {
    Write-Host "Failed to upgrade pip." -ForegroundColor Red
    exit 1
}

# Install core dependencies
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
pip install --timeout 120 -r tests/requirements-minimal.txt
if (-not $?) {
    Write-Host "Failed to install core dependencies." -ForegroundColor Red
    exit 1
}

# Ask user if they want to install GPU or CPU version of PyTorch
$gpuSupport = Read-Host "Do you want to install PyTorch with GPU support? (y/n)"
if ($gpuSupport -eq "y" -or $gpuSupport -eq "Y") {
    Write-Host "Installing PyTorch with GPU support..." -ForegroundColor Yellow
    pip install --timeout 300 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    if (-not $?) {
        Write-Host "Failed to install PyTorch with GPU support. Falling back to CPU version..." -ForegroundColor Yellow
        pip install --timeout 120 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    }
} else {
    Write-Host "Installing PyTorch CPU version..." -ForegroundColor Yellow
    pip install --timeout 120 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
}

# Install Whisper dependencies
Write-Host "Installing Whisper dependencies..." -ForegroundColor Yellow
pip install --timeout 120 -r tests/requirements-whisper.txt
if (-not $?) {
    Write-Host "Failed to install Whisper dependencies." -ForegroundColor Red
    exit 1
}

# Run tests to verify installation
Write-Host "Running tests to verify installation..." -ForegroundColor Yellow

Write-Host "Testing Whisper..." -ForegroundColor Cyan
python tests/test_whisper.py
if (-not $?) {
    Write-Host "Whisper test failed." -ForegroundColor Red
} else {
    Write-Host "Whisper test passed!" -ForegroundColor Green
}

Write-Host "Testing VAD..." -ForegroundColor Cyan
python tests/test_vad.py
if (-not $?) {
    Write-Host "VAD test failed." -ForegroundColor Red
} else {
    Write-Host "VAD test passed!" -ForegroundColor Green
}

Write-Host "Testing IDE integration..." -ForegroundColor Cyan
python tests/test_ide_integration.py
if (-not $?) {
    Write-Host "IDE integration test failed." -ForegroundColor Red
} else {
    Write-Host "IDE integration test passed!" -ForegroundColor Green
}

Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment in the future, run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan