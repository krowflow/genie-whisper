@echo off
echo ===== PyTorch Audio Fix for Genie Whisper =====
echo.

REM Uninstall existing PyTorch installations
echo Uninstalling existing PyTorch installations...
pip uninstall -y torch torchvision torchaudio
echo.

REM Check for CUDA availability
echo Checking for CUDA availability...
nvidia-smi > nul 2>&1
if %errorlevel% equ 0 (
    echo CUDA GPU detected. Attempting CUDA installation...
    
    REM Try CUDA 12.1
    echo Trying PyTorch with CUDA 12.1...
    pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu121
    
    REM Verify installation
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" > cuda_check.txt
    findstr /C:"CUDA available: True" cuda_check.txt > nul
    if %errorlevel% equ 0 (
        echo Successfully installed PyTorch with CUDA 12.1
        goto verify_installation
    )
    
    REM Try CUDA 11.8
    echo CUDA 12.1 failed. Trying PyTorch with CUDA 11.8...
    pip uninstall -y torch torchaudio
    pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
    
    REM Verify installation
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" > cuda_check.txt
    findstr /C:"CUDA available: True" cuda_check.txt > nul
    if %errorlevel% equ 0 (
        echo Successfully installed PyTorch with CUDA 11.8
        goto verify_installation
    )
    
    REM Try CUDA 11.7
    echo CUDA 11.8 failed. Trying PyTorch with CUDA 11.7...
    pip uninstall -y torch torchaudio
    pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117
    
    REM Verify installation
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" > cuda_check.txt
    findstr /C:"CUDA available: True" cuda_check.txt > nul
    if %errorlevel% equ 0 (
        echo Successfully installed PyTorch with CUDA 11.7
        goto verify_installation
    )
    
    REM Try CUDA 11.6
    echo CUDA 11.7 failed. Trying PyTorch with CUDA 11.6...
    pip uninstall -y torch torchaudio
    pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu116
    
    REM Verify installation
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" > cuda_check.txt
    findstr /C:"CUDA available: True" cuda_check.txt > nul
    if %errorlevel% equ 0 (
        echo Successfully installed PyTorch with CUDA 11.6
        goto verify_installation
    )
    
    REM All CUDA versions failed, fall back to CPU
    echo All CUDA versions failed. Falling back to CPU version...
) else (
    echo No CUDA GPU detected. Installing CPU version...
)

REM Install CPU version
echo Installing PyTorch CPU version...
pip uninstall -y torch torchaudio
pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

:verify_installation
REM Clean up temporary file
if exist cuda_check.txt del cuda_check.txt

REM Verify the installation works correctly
echo.
echo Verifying PyTorch and torchaudio installation...
python -c "import torch, torchaudio; print(f'PyTorch {torch.__version__}, torchaudio {torchaudio.__version__}, CUDA available: {torch.cuda.is_available()}')"

echo.
echo ===== Installation Complete =====
echo.
echo Next steps:
echo 1. Test the Whisper pipeline: python tests/test_whisper.py
echo 2. Test the VAD: python tests/test_vad.py
echo 3. Test IDE integration: python tests/test_ide_integration.py
echo.

pause