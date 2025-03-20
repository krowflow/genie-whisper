# PowerShell script to download PyTorch CUDA wheel files from multiple sources
# This script tries multiple download methods and sources

# Configuration
$PYTORCH_VERSION = "2.2.1"
$CUDA_VERSION = "121"  # Using CUDA 12.1 packages (closest to 12.7)
$PYTHON_VERSION = "311"  # Python 3.11

# Create a directory for downloads
$downloadDir = ".\pytorch_wheels"
if (-not (Test-Path $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
}

# URLs for PyTorch wheels - Primary source
$TORCH_URL_PRIMARY = "https://download.pytorch.org/whl/cu$CUDA_VERSION/torch-$PYTORCH_VERSION%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"
$TORCHVISION_URL_PRIMARY = "https://download.pytorch.org/whl/cu$CUDA_VERSION/torchvision-0.17.1%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"
$TORCHAUDIO_URL_PRIMARY = "https://download.pytorch.org/whl/cu$CUDA_VERSION/torchaudio-2.2.1%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"

# Alternative URLs - Mirror sites (these are examples, may need to be updated)
$TORCH_URL_ALT1 = "https://files.pythonhosted.org/packages/whl/torch/torch-$PYTORCH_VERSION%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"
$TORCH_URL_ALT2 = "https://anaconda.org/pytorch/pytorch/download/torch-$PYTORCH_VERSION%2Bcu$CUDA_VERSION-cp$PYTHON_VERSION-cp$PYTHON_VERSION-win_amd64.whl"

# File paths
$torchPath = Join-Path $downloadDir "torch.whl"
$torchvisionPath = Join-Path $downloadDir "torchvision.whl"
$torchaudioPath = Join-Path $downloadDir "torchaudio.whl"

# Function to download a file using multiple methods
function Download-FileMultiMethod {
    param (
        [string]$Url,
        [string]$OutputPath,
        [array]$AlternativeUrls = @()
    )
    
    Write-Host "Attempting to download $Url to $OutputPath..."
    
    # Try WebClient first
    try {
        Write-Host "Trying WebClient download method..." -ForegroundColor Yellow
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
        Write-Host "WebClient download failed: $_" -ForegroundColor Red
    }
    
    # Try Invoke-WebRequest
    try {
        Write-Host "Trying Invoke-WebRequest download method..." -ForegroundColor Yellow
        $ProgressPreference = 'SilentlyContinue'  # Hide progress bar for faster downloads
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath -UseBasicParsing -ErrorAction Stop
        Write-Host "Successfully downloaded to $OutputPath using Invoke-WebRequest" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Invoke-WebRequest download failed: $_" -ForegroundColor Red
    }
    
    # Try BITS
    try {
        Write-Host "Trying BITS download method..." -ForegroundColor Yellow
        Start-BitsTransfer -Source $Url -Destination $OutputPath -DisplayName "PyTorch Download" -Priority High -ErrorAction Stop
        Write-Host "Successfully downloaded to $OutputPath using BITS" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "BITS download failed: $_" -ForegroundColor Red
    }
    
    # Try alternative URLs if provided
    foreach ($altUrl in $AlternativeUrls) {
        Write-Host "Trying alternative URL: $altUrl" -ForegroundColor Yellow
        
        # Try WebClient with alternative URL
        try {
            $webClient = New-Object System.Net.WebClient
            $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
            $webClient.DownloadFile($altUrl, $OutputPath)
            Write-Host "Successfully downloaded from alternative URL to $OutputPath" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "Alternative URL download failed: $_" -ForegroundColor Red
        }
    }
    
    # Try using curl as a last resort
    try {
        Write-Host "Trying curl download method..." -ForegroundColor Yellow
        $curlCommand = "curl -L -o `"$OutputPath`" `"$Url`""
        Invoke-Expression $curlCommand
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $OutputPath) -and (Get-Item $OutputPath).Length -gt 0) {
            Write-Host "Successfully downloaded to $OutputPath using curl" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "curl download failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "curl download failed: $_" -ForegroundColor Red
    }
    
    # Try using aria2 if available
    try {
        $aria2Exists = Get-Command aria2c -ErrorAction SilentlyContinue
        if ($aria2Exists) {
            Write-Host "Trying aria2 download method..." -ForegroundColor Yellow
            $aria2Command = "aria2c -x 16 -s 16 -k 1M -o `"$OutputPath`" `"$Url`""
            Invoke-Expression $aria2Command
            
            if ($LASTEXITCODE -eq 0 -and (Test-Path $OutputPath) -and (Get-Item $OutputPath).Length -gt 0) {
                Write-Host "Successfully downloaded to $OutputPath using aria2" -ForegroundColor Green
                return $true
            }
            else {
                Write-Host "aria2 download failed" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "aria2 download failed: $_" -ForegroundColor Red
    }
    
    # All methods failed
    Write-Host "All download methods failed for $Url" -ForegroundColor Red
    return $false
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

# Function to try installing PyTorch using pip directly
function Install-PyTorchPip {
    Write-Host "Trying to install PyTorch directly using pip..." -ForegroundColor Yellow
    
    # Try different pip install commands
    $commands = @(
        "pip install torch==2.2.1+cu121 torchvision==0.17.1+cu121 torchaudio==2.2.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121",
        "pip install torch==2.2.0+cu121 torchvision==0.17.0+cu121 torchaudio==2.2.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121",
        "pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121",
        "pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118"
    )
    
    foreach ($cmd in $commands) {
        Write-Host "Executing: $cmd" -ForegroundColor Yellow
        Invoke-Expression $cmd
        
        # Check if installation was successful
        try {
            $checkCmd = "python -c `"import torch; print(torch.__version__); print(torch.cuda.is_available())`""
            $result = Invoke-Expression $checkCmd
            
            if ($LASTEXITCODE -eq 0 -and $result -match "True") {
                Write-Host "PyTorch with CUDA support installed successfully!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "Installation check failed: $_" -ForegroundColor Red
        }
        
        Write-Host "This installation attempt failed, trying next method..." -ForegroundColor Yellow
    }
    
    return $false
}

# Function to try installing PyTorch using conda
function Install-PyTorchConda {
    Write-Host "Trying to install PyTorch using conda..." -ForegroundColor Yellow
    
    # Check if conda is available
    try {
        $condaExists = Get-Command conda -ErrorAction SilentlyContinue
        if (-not $condaExists) {
            Write-Host "Conda not found, skipping conda installation method" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "Conda not found, skipping conda installation method" -ForegroundColor Yellow
        return $false
    }
    
    # Try different conda install commands
    $commands = @(
        "conda install -y pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia",
        "conda install -y pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia",
        "conda install -y pytorch torchvision torchaudio cudatoolkit=11.8 -c pytorch -c nvidia"
    )
    
    foreach ($cmd in $commands) {
        Write-Host "Executing: $cmd" -ForegroundColor Yellow
        Invoke-Expression $cmd
        
        # Check if installation was successful
        try {
            $checkCmd = "python -c `"import torch; print(torch.__version__); print(torch.cuda.is_available())`""
            $result = Invoke-Expression $checkCmd
            
            if ($LASTEXITCODE -eq 0 -and $result -match "True") {
                Write-Host "PyTorch with CUDA support installed successfully using conda!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "Installation check failed: $_" -ForegroundColor Red
        }
        
        Write-Host "This installation attempt failed, trying next method..." -ForegroundColor Yellow
    }
    
    return $false
}

# Main script

Write-Host "=" * 80
Write-Host "PyTorch CUDA Multi-Method Download Script for RTX 4090"
Write-Host "=" * 80

# Uninstall existing PyTorch installations
Write-Host "Removing existing PyTorch installations..." -ForegroundColor Yellow
python -m pip uninstall -y torch torchvision torchaudio

# Try installing directly with pip first (fastest if it works)
if (Install-PyTorchPip) {
    Write-Host "PyTorch installed successfully using pip!" -ForegroundColor Green
    if (Verify-PyTorch) {
        Write-Host "=" * 80
        Write-Host "PyTorch installation completed successfully!" -ForegroundColor Green
        Write-Host "=" * 80
        exit 0
    }
}

# Try installing with conda if pip failed
if (Install-PyTorchConda) {
    Write-Host "PyTorch installed successfully using conda!" -ForegroundColor Green
    if (Verify-PyTorch) {
        Write-Host "=" * 80
        Write-Host "PyTorch installation completed successfully!" -ForegroundColor Green
        Write-Host "=" * 80
        exit 0
    }
}

# If direct installation methods failed, try downloading wheels manually
Write-Host "Direct installation methods failed, trying manual wheel downloads..." -ForegroundColor Yellow

# Download torch
if (-not (Download-FileMultiMethod -Url $TORCH_URL_PRIMARY -OutputPath $torchPath -AlternativeUrls @($TORCH_URL_ALT1, $TORCH_URL_ALT2))) {
    Write-Host "Failed to download PyTorch. Aborting." -ForegroundColor Red
    exit 1
}

# Download torchvision
if (-not (Download-FileMultiMethod -Url $TORCHVISION_URL_PRIMARY -OutputPath $torchvisionPath)) {
    Write-Host "Failed to download torchvision. Aborting." -ForegroundColor Red
    exit 1
}

# Download torchaudio
if (-not (Download-FileMultiMethod -Url $TORCHAUDIO_URL_PRIMARY -OutputPath $torchaudioPath)) {
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