# Genie Whisper Environment Setup Script
# This script sets up a virtual environment and installs the required dependencies
# with robust error handling, dependency verification, and automatic recovery

# Stop on error
$ErrorActionPreference = "Stop"

# Configuration
$maxRetries = 3
$timeoutBase = 120
$logFile = "setup_env.log"

# Initialize log file
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$timestamp] Genie Whisper Environment Setup Started" | Out-File -FilePath $logFile

function Write-Log {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
    "[$timestamp] $Message" | Out-File -FilePath $logFile -Append
}

function Test-CommandExists {
    param (
        [string]$Command
    )
    
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    return $exists
}

function Invoke-WithRetry {
    param (
        [scriptblock]$ScriptBlock,
        [string]$OperationName,
        [int]$MaxRetries = $maxRetries,
        [int]$RetryDelaySeconds = 5
    )
    
    $retryCount = 0
    $success = $false
    $result = $null
    
    while (-not $success -and $retryCount -lt $MaxRetries) {
        try {
            if ($retryCount -gt 0) {
                Write-Log "Retry $retryCount/$MaxRetries for $OperationName..." "Yellow"
                Start-Sleep -Seconds $RetryDelaySeconds
                # Increase delay for subsequent retries
                $RetryDelaySeconds = [Math]::Min($RetryDelaySeconds * 2, 60)
            }
            
            $result = & $ScriptBlock
            $success = $true
        }
        catch {
            $retryCount++
            $errorMessage = $_.Exception.Message
            Write-Log "Error in $OperationName (Attempt $retryCount/$MaxRetries): $errorMessage" "Red"
            
            if ($retryCount -ge $MaxRetries) {
                Write-Log "Maximum retry attempts reached for $OperationName. Giving up." "Red"
                throw $_
            }
        }
    }
    
    return $result
}

Write-Log "Setting up Genie Whisper development environment..." "Cyan"

# Check if Python is installed and verify version
function Test-PythonVersion {
    try {
        $pythonVersionOutput = Invoke-WithRetry -ScriptBlock { python --version 2>&1 } -OperationName "Python version check"
        
        # Extract version number
        if ($pythonVersionOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
                Write-Log "Python version $major.$minor is not supported. Please install Python 3.9 or later." "Red"
                return $false
            }
            
            Write-Log "Found Python: $pythonVersionOutput" "Green"
            return $true
        } else {
            Write-Log "Unable to determine Python version from output: $pythonVersionOutput" "Red"
            return $false
        }
    } catch {
        Write-Log "Python not found or error checking version: $_" "Red"
        return $false
    }
}

if (-not (Test-PythonVersion)) {
    Write-Log "Python 3.9 or later is required. Please install a compatible version and try again." "Red"
    exit 1
}

# Function to create and verify virtual environment
function Initialize-VirtualEnvironment {
    $venvPath = ".venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    # Check if virtual environment exists
    if (-not (Test-Path $venvPath)) {
        Write-Log "Creating virtual environment..." "Yellow"
        
        try {
            # Try to create virtual environment with retry
            Invoke-WithRetry -ScriptBlock {
                python -m venv $venvPath
                if (-not $?) { throw "Virtual environment creation failed" }
            } -OperationName "Virtual environment creation"
            
            Write-Log "Virtual environment created successfully." "Green"
        } catch {
            # If creation fails, try to clean up and retry once more
            Write-Log "Error creating virtual environment. Attempting to clean up and retry..." "Yellow"
            
            if (Test-Path $venvPath) {
                Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
            }
            
            try {
                python -m venv $venvPath
                if (-not $?) {
                    Write-Log "Failed to create virtual environment after cleanup. Error: $_" "Red"
                    return $false
                }
                Write-Log "Virtual environment created successfully after cleanup." "Green"
            } catch {
                Write-Log "Failed to create virtual environment after cleanup. Error: $_" "Red"
                return $false
            }
        }
    } else {
        Write-Log "Virtual environment already exists." "Green"
        
        # Verify the virtual environment is valid
        if (-not (Test-Path $activateScript)) {
            Write-Log "Virtual environment exists but appears to be corrupted (missing activate script)." "Yellow"
            Write-Log "Attempting to recreate virtual environment..." "Yellow"
            
            # Remove corrupted venv and recreate
            Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
            
            try {
                python -m venv $venvPath
                if (-not $?) {
                    Write-Log "Failed to recreate virtual environment. Error: $_" "Red"
                    return $false
                }
                Write-Log "Virtual environment recreated successfully." "Green"
            } catch {
                Write-Log "Failed to recreate virtual environment. Error: $_" "Red"
                return $false
            }
        }
    }
    
    # Activate virtual environment
    Write-Log "Activating virtual environment..." "Yellow"
    try {
        & $activateScript
        
        # Verify activation
        $venvPython = Get-Command python -ErrorAction SilentlyContinue
        if ($venvPython -and $venvPython.Source -like "*$venvPath*") {
            Write-Log "Virtual environment activated successfully." "Green"
            return $true
        } else {
            Write-Log "Virtual environment activation verification failed." "Red"
            return $false
        }
    } catch {
        Write-Log "Failed to activate virtual environment: $_" "Red"
        return $false
    }
}

# Initialize and activate virtual environment
if (-not (Initialize-VirtualEnvironment)) {
    Write-Log "Failed to initialize virtual environment. Setup cannot continue." "Red"
    exit 1
}

# Function to upgrade pip with retry
function Update-Pip {
    Write-Log "Upgrading pip..." "Yellow"
    
    try {
        Invoke-WithRetry -ScriptBlock {
            python -m pip install --upgrade pip
            if (-not $?) { throw "Pip upgrade failed" }
        } -OperationName "Pip upgrade"
        
        Write-Log "Pip upgraded successfully." "Green"
        return $true
    } catch {
        Write-Log "Failed to upgrade pip after multiple attempts: $_" "Red"
        
        # Try alternative method if standard method fails
        try {
            Write-Log "Trying alternative pip upgrade method..." "Yellow"
            python -m ensurepip --upgrade
            python -m pip install --upgrade pip
            
            if ($?) {
                Write-Log "Pip upgraded successfully using alternative method." "Green"
                return $true
            } else {
                Write-Log "Alternative pip upgrade method also failed." "Red"
                return $false
            }
        } catch {
            Write-Log "Alternative pip upgrade method failed: $_" "Red"
            return $false
        }
    }
}

# Function to install dependencies with retry
function Install-Dependencies {
    param (
        [string]$RequirementsFile,
        [string]$Description = "dependencies",
        [int]$Timeout = $timeoutBase
    )
    
    Write-Log "Installing $Description..." "Yellow"
    
    # Check if requirements file exists
    if (-not (Test-Path $RequirementsFile)) {
        Write-Log "Requirements file not found: $RequirementsFile" "Red"
        return $false
    }
    
    try {
        Invoke-WithRetry -ScriptBlock {
            pip install --timeout $Timeout -r $RequirementsFile
            if (-not $?) { throw "Dependency installation failed" }
        } -OperationName "$Description installation"
        
        Write-Log "$Description installed successfully." "Green"
        return $true
    } catch {
        Write-Log "Failed to install $Description after multiple attempts: $_" "Red"
        
        # Try alternative installation method with --no-cache-dir
        try {
            Write-Log "Trying alternative installation method with --no-cache-dir..." "Yellow"
            pip install --no-cache-dir --timeout $Timeout -r $RequirementsFile
            
            if ($?) {
                Write-Log "$Description installed successfully using alternative method." "Green"
                return $true
            } else {
                Write-Log "Alternative installation method also failed." "Red"
                return $false
            }
        } catch {
            Write-Log "Alternative installation method failed: $_" "Red"
            return $false
        }
    }
}

# Upgrade pip
if (-not (Update-Pip)) {
    Write-Log "Failed to upgrade pip. Continuing with existing version, but this may cause issues." "Yellow"
}

# Install core dependencies
if (-not (Install-Dependencies -RequirementsFile "tests/requirements-minimal.txt" -Description "core dependencies")) {
    Write-Log "Failed to install core dependencies. Setup cannot continue." "Red"
    exit 1
}

# Function to verify PyTorch installation with detailed output
function Test-PyTorch {
    param (
        [switch]$Detailed = $false
    )
    
    try {
        $verificationCode = @"
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
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
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"@
        
        # Write verification code to temporary file
        $tempFile = Join-Path $env:TEMP "verify_pytorch.py"
        Set-Content -Path $tempFile -Value $verificationCode
        
        # Run verification
        $output = python $tempFile
        
        # Clean up
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        
        # Check if verification was successful
        if ($output -match "Basic functionality test passed") {
            if ($Detailed) {
                foreach ($line in $output) {
                    Write-Log $line "Green"
                }
            } else {
                $cudaInfo = if ($output -match "CUDA available: True") { "with CUDA support" } else { "CPU version" }
                $versionInfo = ($output | Where-Object { $_ -match "PyTorch version:" }) -replace "PyTorch version: ", ""
                Write-Log "PyTorch $versionInfo $cudaInfo is working correctly." "Green"
            }
            return $true
        } else {
            if ($Detailed) {
                foreach ($line in $output) {
                    Write-Log $line "Yellow"
                }
            }
            Write-Log "PyTorch verification failed." "Red"
            return $false
        }
    } catch {
        Write-Log "Error testing PyTorch: $_" "Red"
        return $false
    }
}

# Function to check for custom PyTorch installation scripts
function Get-CustomPyTorchScript {
    $scriptPaths = @(
        "scripts/download_pytorch_multi.ps1",
        "scripts/download_pytorch_bits.ps1",
        "scripts/download_pytorch_cuda.ps1",
        "scripts/install_pytorch.py"
    )
    
    foreach ($scriptPath in $scriptPaths) {
        if (Test-Path $scriptPath) {
            return $scriptPath
        }
    }
    
    return $null
}

# Function to install PyTorch with specific CUDA version
function Install-PyTorch {
    param (
        [string]$CudaVersion,
        [switch]$UseCustomScript = $false
    )
    
    # Check if we should use a custom script
    $customScript = Get-CustomPyTorchScript
    
    if ($UseCustomScript -and $customScript) {
        Write-Log "Using custom PyTorch installation script: $customScript" "Cyan"
        
        try {
            if ($customScript -match "\.ps1$") {
                # PowerShell script
                Invoke-WithRetry -ScriptBlock {
                    & $customScript
                    if (-not $?) { throw "Custom PyTorch installation script failed" }
                } -OperationName "Custom PyTorch installation"
            } elseif ($customScript -match "\.py$") {
                # Python script
                Invoke-WithRetry -ScriptBlock {
                    python $customScript
                    if (-not $?) { throw "Custom PyTorch installation script failed" }
                } -OperationName "Custom PyTorch installation"
            } else {
                Write-Log "Unsupported script type: $customScript" "Red"
                return $false
            }
            
            # Verify installation
            return (Test-PyTorch)
        } catch {
            Write-Log "Custom PyTorch installation failed: $_" "Red"
            return $false
        }
    } else {
        # Standard installation
        try {
            if ($CudaVersion) {
                Write-Log "Installing PyTorch with CUDA $CudaVersion..." "Yellow"
                
                Invoke-WithRetry -ScriptBlock {
                    pip install --timeout 300 torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url "https://download.pytorch.org/whl/$CudaVersion"
                    if (-not $?) { throw "PyTorch installation failed" }
                } -OperationName "PyTorch CUDA installation"
            } else {
                Write-Log "Installing PyTorch CPU version..." "Yellow"
                
                Invoke-WithRetry -ScriptBlock {
                    pip install --timeout 120 torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu
                    if (-not $?) { throw "PyTorch installation failed" }
                } -OperationName "PyTorch CPU installation"
            }
            
            # Fix NumPy compatibility if needed
            $pythonOutput = python -c "import numpy; print(numpy.__version__)"
            if ($pythonOutput -match "^2\.") {
                Write-Log "Detected NumPy 2.x, downgrading to 1.26.4 for compatibility with PyTorch..." "Yellow"
                pip install numpy==1.26.4
            }
            
            # Verify installation
            return (Test-PyTorch)
        } catch {
            Write-Log "Standard PyTorch installation failed: $_" "Red"
            return $false
        }
    }
}

# Function to detect GPU and CUDA
function Test-CudaAvailability {
    Write-Log "Checking for CUDA availability..." "Yellow"
    
    # Check if NVIDIA GPU is present
    try {
        $gpuInfo = Invoke-WithRetry -ScriptBlock {
            nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader
        } -OperationName "NVIDIA GPU detection" -MaxRetries 1
        
        if ($gpuInfo) {
            Write-Log "NVIDIA GPU detected: $gpuInfo" "Green"
            return $true
        }
    } catch {
        Write-Log "NVIDIA GPU detection failed: $_" "Yellow"
    }
    
    # Alternative method to check for CUDA
    try {
        $cudaPath = [System.Environment]::GetEnvironmentVariable("CUDA_PATH", "Machine")
        if ($cudaPath -and (Test-Path $cudaPath)) {
            Write-Log "CUDA installation found at: $cudaPath" "Green"
            return $true
        }
    } catch {
        Write-Log "CUDA path check failed: $_" "Yellow"
    }
    
    Write-Log "No CUDA-capable GPU detected." "Yellow"
    return $false
}

# Check if PyTorch is already installed
$pytorchInstalled = Test-PyTorch
if ($pytorchInstalled) {
    Write-Log "PyTorch is already installed and working correctly." "Green"
    Write-Log "Running detailed verification..." "Yellow"
    Test-PyTorch -Detailed
} else {
    # Check if CUDA is available
    $cudaAvailable = Test-CudaAvailability
    
    # Ask user if they want to install GPU or CPU version of PyTorch
    if ($cudaAvailable) {
        $gpuSupport = Read-Host "Do you want to install PyTorch with GPU support? (y/n)"
    } else {
        $gpuSupport = "n"
    }
    
    # Check for custom installation scripts
    $customScript = Get-CustomPyTorchScript
    if ($customScript) {
        Write-Log "Custom PyTorch installation script found: $customScript" "Cyan"
        $useCustom = Read-Host "Do you want to use the custom installation script? (y/n)"
        
        if ($useCustom -eq "y" -or $useCustom -eq "Y") {
            $success = Install-PyTorch -UseCustomScript
            
            if ($success) {
                Write-Log "PyTorch installed successfully using custom script!" "Green"
                Test-PyTorch -Detailed
            } else {
                Write-Log "Custom script installation failed. Falling back to standard installation..." "Yellow"
                # Continue to standard installation
            }
        }
    }
    
    # If custom script wasn't used or failed, use standard installation
    if (-not $pytorchInstalled) {
        if ($gpuSupport -eq "y" -or $gpuSupport -eq "Y") {
            # Try different CUDA versions, starting with the most recent
            $cudaVersions = @("cu121", "cu118", "cu117", "cu116")
            $success = $false
            
            foreach ($cudaVersion in $cudaVersions) {
                Write-Log "Trying PyTorch with CUDA $cudaVersion..." "Yellow"
                $success = Install-PyTorch -CudaVersion $cudaVersion
                
                if ($success) {
                    Write-Log "Successfully installed PyTorch with CUDA $cudaVersion!" "Green"
                    break
                } else {
                    Write-Log "PyTorch installation with CUDA $cudaVersion failed. Trying another version..." "Yellow"
                    pip uninstall -y torch torchvision torchaudio
                }
            }
            
            if (-not $success) {
                Write-Log "Could not install PyTorch with GPU support. Falling back to CPU version..." "Yellow"
                $success = Install-PyTorch
                
                if (-not $success) {
                    Write-Log "Failed to install PyTorch CPU version. Please check your internet connection and try again." "Red"
                    exit 1
                }
            }
        } else {
            Write-Log "Installing PyTorch CPU version..." "Yellow"
            $success = Install-PyTorch
            
            if (-not $success) {
                Write-Log "Failed to install PyTorch CPU version. Please check your internet connection and try again." "Red"
                exit 1
            }
        }
    }
}

# Test torchaudio functionality
Write-Log "Testing torchaudio functionality..." "Yellow"
try {
    $torchaudioTest = Invoke-WithRetry -ScriptBlock {
        python -c "import torchaudio; import torch; sample_rate = 16000; waveform = torch.zeros([1, sample_rate]); print('torchaudio test successful')"
    } -OperationName "torchaudio test"
    
    Write-Log $torchaudioTest "Green"
} catch {
    Write-Log "Error testing torchaudio: $_" "Red"
    Write-Log "torchaudio may not be functioning correctly. Attempting to fix..." "Yellow"
    
    # Try to fix common torchaudio issues
    try {
        Write-Log "Reinstalling torchaudio..." "Yellow"
        pip uninstall -y torchaudio
        
        # Try to install torchaudio with the same CUDA version as PyTorch
        $pythonOutput = python -c "import torch; print(torch.__version__)"
        if ($pythonOutput -match "cu(\d+)") {
            $cudaVersion = "cu" + $Matches[1]
            Write-Log "Detected PyTorch with CUDA $cudaVersion, installing matching torchaudio..." "Yellow"
            pip install torchaudio==2.2.0 --index-url "https://download.pytorch.org/whl/$cudaVersion"
        } else {
            Write-Log "Installing CPU version of torchaudio..." "Yellow"
            pip install torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu
        }
        
        # Test again
        $torchaudioTest = python -c "import torchaudio; import torch; sample_rate = 16000; waveform = torch.zeros([1, sample_rate]); print('torchaudio test successful after fix')"
        Write-Log $torchaudioTest "Green"
    } catch {
        Write-Log "Failed to fix torchaudio issues: $_" "Red"
        Write-Log "Continuing with installation, but audio functionality may be limited." "Yellow"
    }
}

# Install Whisper dependencies
Write-Log "Installing Whisper dependencies..." "Yellow"
if (-not (Install-Dependencies -RequirementsFile "tests/requirements-whisper.txt" -Description "Whisper dependencies" -Timeout 300)) {
    Write-Log "Failed to install Whisper dependencies. Setup cannot continue." "Red"
    exit 1
}

# Function to run tests with retry and detailed error reporting
function Test-Component {
    param (
        [string]$TestName,
        [string]$TestScript,
        [switch]$Critical = $false
    )
    
    Write-Log "Testing $TestName..." "Cyan"
    
    try {
        $output = Invoke-WithRetry -ScriptBlock {
            $result = python $TestScript 2>&1
            if (-not $?) { throw "Test failed: $result" }
            return $result
        } -OperationName "$TestName test" -MaxRetries $(if ($Critical) { 3 } else { 1 })
        
        Write-Log "$TestName test passed!" "Green"
        return $true
    } catch {
        Write-Log "$TestName test failed: $_" "Red"
        
        # Check if test file exists
        if (-not (Test-Path $TestScript)) {
            Write-Log "Test script not found: $TestScript" "Red"
        }
        
        # Try to get more information about the failure
        try {
            $errorOutput = python $TestScript 2>&1
            Write-Log "Error details: $errorOutput" "Yellow"
        } catch {
            # Ignore errors in error reporting
        }
        
        if ($Critical) {
            Write-Log "Critical test failed. Setup cannot continue." "Red"
            return $false
        } else {
            Write-Log "Non-critical test failed. Continuing with setup." "Yellow"
            return $true
        }
    }
}

# Run tests to verify installation
Write-Log "Running tests to verify installation..." "Yellow"

$testResults = @(
    (Test-Component -TestName "Whisper" -TestScript "tests/test_whisper.py" -Critical),
    (Test-Component -TestName "VAD" -TestScript "tests/test_vad.py"),
    (Test-Component -TestName "IDE integration" -TestScript "tests/test_ide_integration.py")
)

if ($testResults -contains $false) {
    Write-Log "Some critical tests failed. Please check the logs and fix the issues before continuing." "Red"
    exit 1
}

# Generate summary report
$passedTests = ($testResults | Where-Object { $_ -eq $true }).Count
$totalTests = $testResults.Count
Write-Log "Test summary: $passedTests/$totalTests tests passed" "Cyan"

Write-Log "Environment setup complete!" "Green"
Write-Log "To activate the virtual environment in the future, run: .\.venv\Scripts\Activate.ps1" "Cyan"