# PowerShell script to download PyTorch CUDA wheel files using BITS
# BITS provides reliable downloads with resume capability

# Configuration
$PYTORCH_VERSION = "2.2.1"
$CUDA_VERSION = "121"  # Using CUDA 12.1 packages (closest to 12.7)
$PYTHON_VERSION = "311"  # Python 3.11

# Create a directory for downloads
$downloadDir = ".\pytorch_wheels"
if (-not (Test-Path $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
}

# URLs for PyTorch wheels
$TORCH_URL = "https://download.pytorch.org/whl/cu$CUDA_VERSION/torch-$PYTORCH_VERSION%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"
$TORCHVISION_URL = "https://download.pytorch.org/whl/cu$CUDA_VERSION/torchvision-0.17.1%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"
$TORCHAUDIO_URL = "https://download.pytorch.org/whl/cu$CUDA_VERSION/torchaudio-2.2.1%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"

# File paths
$torchPath = Join-Path $downloadDir "torch.whl"
$torchvisionPath = Join-Path $downloadDir "torchvision.whl"
$torchaudioPath = Join-Path $downloadDir "torchaudio.whl"

# Function to download a file with BITS
function Download-FileBITS {
    param (
        [string]$Url,
        [string]$OutputPath
    )
    
    Write-Host "Downloading $Url to $OutputPath using BITS..."
    
    try {
        # Start BITS transfer with resume capability
        Start-BitsTransfer -Source $Url -Destination $OutputPath -DisplayName "PyTorch Download" -Priority High -RetryInterval 60 -RetryTimeout 3600 -ErrorAction Stop
        
        Write-Host "Successfully downloaded to $OutputPath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error downloading $Url using BITS: $_" -ForegroundColor Red
        Write-Host "Trying alternative download method..." -ForegroundColor Yellow
        
        try {
            # Fallback to WebClient with resume capability
            $webClient = New-Object System.Net.WebClient
            $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
            
            # Check if file exists and get size for resume
            if (Test-Path $OutputPath) {
                $existingFile = Get-Item $OutputPath
                $fileSize = $existingFile.Length
                
                if ($fileSize -gt 0) {
                    Write-Host "Resuming download from byte $fileSize" -ForegroundColor Yellow
                    $webClient.Headers.Add("Range", "bytes=$fileSize-")
                }
            }
            
            $webClient.DownloadFile($Url, $OutputPath)
            Write-Host "Successfully downloaded to $OutputPath using WebClient" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "Error with alternative download method: $_" -ForegroundColor Red
            return $false
        }
    }
}

# Function to install a wheel file
function Install-Wheel {
    param (
        [string]$WheelPath
    )
    
    Write-Host "Installing $WheelPath..." -ForegroundColor Yellow
    
    # Use pip to install the wheel file
    $result = python -m pip install $WheelPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install $WheelPath" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Successfully installed $WheelPath" -ForegroundColor Green
    return $true
}

# Function to verify PyTorch installation
function Verify-PyTorch {
    Write-Host "Verifying PyTorch installation..." -ForegroundColor Yellow
    
    # Try to import torch and check CUDA availability
    $verificationCode = @"
import torch
import torchvision
import torchaudio
print(f"PyTorch version: {torch.__version__}")
print(f"torchvision version: {torchvision.__version__}")
print(f"torchaudio version: {torchaudio.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    
# Test basic functionality
sample_rate = 16000
waveform = torch.zeros([1, sample_rate])
print("Basic functionality test passed")
"@
    
    # Write the verification code to a temporary file
    $verificationFile = Join-Path $downloadDir "verify_pytorch.py"
    Set-Content -Path $verificationFile -Value $verificationCode
    
    # Run the verification script
    python $verificationFile
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyTorch verification failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "PyTorch verification succeeded" -ForegroundColor Green
    return $true
}

# Main script

Write-Host "=" * 80
Write-Host "PyTorch CUDA Download Script for RTX 4090 (BITS Transfer)"
Write-Host "=" * 80

# Uninstall existing PyTorch installations
Write-Host "Removing existing PyTorch installations..." -ForegroundColor Yellow
python -m pip uninstall -y torch torchvision torchaudio

# Download PyTorch
Write-Host "Starting download of PyTorch packages..." -ForegroundColor Yellow
Write-Host "This may take some time, but BITS will handle resume if interrupted." -ForegroundColor Yellow

# Download torch
if (-not (Download-FileBITS -Url $TORCH_URL -OutputPath $torchPath)) {
    Write-Host "Failed to download PyTorch. Aborting." -ForegroundColor Red
    exit 1
}

# Download torchvision
if (-not (Download-FileBITS -Url $TORCHVISION_URL -OutputPath $torchvisionPath)) {
    Write-Host "Failed to download torchvision. Aborting." -ForegroundColor Red
    exit 1
}

# Download torchaudio
if (-not (Download-FileBITS -Url $TORCHAUDIO_URL -OutputPath $torchaudioPath)) {
    Write-Host "Failed to download torchaudio. Aborting." -ForegroundColor Red
    exit 1
}

# Install the wheels
Write-Host "Installing PyTorch packages..." -ForegroundColor Yellow

if (-not (Install-Wheel -WheelPath $torchPath)) {
    Write-Host "Failed to install PyTorch. Aborting." -ForegroundColor Red
    exit 1
}

if (-not (Install-Wheel -WheelPath $torchvisionPath)) {
    Write-Host "Failed to install torchvision. Aborting." -ForegroundColor Red
    exit 1
}

if (-not (Install-Wheel -WheelPath $torchaudioPath)) {
    Write-Host "Failed to install torchaudio. Aborting." -ForegroundColor Red
    exit 1
}

# Verify installation
if (Verify-PyTorch) {
    Write-Host "=" * 80
    Write-Host "PyTorch installation completed successfully!" -ForegroundColor Green
    Write-Host "=" * 80
} else {
    Write-Host "=" * 80
    Write-Host "PyTorch installation verification failed." -ForegroundColor Red
    Write-Host "=" * 80
    exit 1
}

Write-Host "Done!" -ForegroundColor Green