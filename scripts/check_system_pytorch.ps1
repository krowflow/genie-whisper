# PowerShell script to check PyTorch in system Python
# This script will temporarily deactivate the virtual environment

# Save the current directory
$currentDir = Get-Location

# Create a temporary script
$tempScript = @"
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")
except ImportError:
    print("PyTorch not installed")
"@

$tempFile = Join-Path $env:TEMP "check_pytorch_temp.py"
Set-Content -Path $tempFile -Value $tempScript

# Run the script with system Python
Write-Host "Checking PyTorch in system Python..."
& "C:\Users\kuzzn\anaconda3\python.exe" $tempFile

# Clean up
Remove-Item $tempFile