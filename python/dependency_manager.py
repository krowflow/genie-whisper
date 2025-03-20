#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Manager for Genie Whisper

This module provides functionality to verify and manage dependencies for the Genie Whisper application.
It checks for required dependencies at startup and provides clear feedback to the user if any
dependencies are missing or incompatible. It also provides functions to automatically recover from
common dependency issues.

Author: Genie Whisper Team
Date: March 20, 2025
"""

import os
import sys
import importlib
import subprocess
import logging
import json
from typing import Dict, List, Tuple, Optional, Any, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("genie_whisper_deps.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DependencyManager")

# Define required dependencies with version constraints
REQUIRED_DEPENDENCIES = {
    "torch": {"min_version": "2.0.0", "recommended_version": "2.2.0", "critical": True},
    "torchaudio": {"min_version": "2.0.0", "recommended_version": "2.2.0", "critical": True},
    "numpy": {"min_version": "1.20.0", "max_version": "1.26.4", "critical": True},
    "whisper": {"min_version": "1.0.0", "critical": True},
    "silero": {"min_version": "0.4.1", "critical": False},
    "webrtcvad": {"min_version": "2.0.10", "critical": False},
}

# Define system requirements
SYSTEM_REQUIREMENTS = {
    "python": {"min_version": "3.9.0", "recommended_version": "3.10.0"},
    "cuda": {"min_version": "11.6", "recommended_version": "12.1", "required": False},
}


class DependencyManager:
    """
    A class to manage dependencies for the Genie Whisper application.
    
    This class provides methods to verify dependencies, check system requirements,
    and recover from common dependency issues.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the DependencyManager.
        
        Args:
            config_path: Path to a JSON configuration file with custom dependency requirements.
                         If None, the default requirements will be used.
        """
        self.required_dependencies = REQUIRED_DEPENDENCIES.copy()
        self.system_requirements = SYSTEM_REQUIREMENTS.copy()
        
        # Load custom configuration if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Update dependencies from config
                if 'dependencies' in config:
                    for dep, settings in config['dependencies'].items():
                        if dep in self.required_dependencies:
                            self.required_dependencies[dep].update(settings)
                        else:
                            self.required_dependencies[dep] = settings
                
                # Update system requirements from config
                if 'system_requirements' in config:
                    for req, settings in config['system_requirements'].items():
                        if req in self.system_requirements:
                            self.system_requirements[req].update(settings)
                        else:
                            self.system_requirements[req] = settings
                
                logger.info(f"Loaded custom dependency configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {e}")
    
    def check_python_version(self) -> bool:
        """
        Check if the current Python version meets the requirements.
        
        Returns:
            bool: True if the Python version is compatible, False otherwise.
        """
        python_req = self.system_requirements.get("python", {})
        min_version = python_req.get("min_version", "3.9.0")
        
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        logger.info(f"Checking Python version: {current_version}")
        
        if self._compare_versions(current_version, min_version) < 0:
            logger.error(f"Python version {current_version} is below the minimum required version {min_version}")
            return False
        
        return True
    
    def check_cuda_availability(self) -> Tuple[bool, Optional[str]]:
        """
        Check if CUDA is available and get the CUDA version.
        
        Returns:
            Tuple[bool, Optional[str]]: A tuple containing a boolean indicating if CUDA is available
                                       and the CUDA version string if available, None otherwise.
        """
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                cuda_version = torch.version.cuda
                logger.info(f"CUDA is available: version {cuda_version}")
                
                # Check if CUDA version meets minimum requirements
                cuda_req = self.system_requirements.get("cuda", {})
                min_version = cuda_req.get("min_version", "0.0.0")
                
                if self._compare_versions(cuda_version, min_version) < 0:
                    logger.warning(f"CUDA version {cuda_version} is below the minimum recommended version {min_version}")
                
                return True, cuda_version
            else:
                logger.info("CUDA is not available")
                return False, None
        except ImportError:
            logger.warning("Could not check CUDA availability: PyTorch not installed")
            return False, None
        except Exception as e:
            logger.error(f"Error checking CUDA availability: {e}")
            return False, None
    
    def verify_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Verify that all required dependencies are installed and meet version requirements.
        
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary with dependency status information.
        """
        results = {}
        all_critical_deps_ok = True
        
        for dep_name, dep_info in self.required_dependencies.items():
            min_version = dep_info.get("min_version", "0.0.0")
            max_version = dep_info.get("max_version", None)
            recommended_version = dep_info.get("recommended_version", None)
            critical = dep_info.get("critical", False)
            
            result = {
                "installed": False,
                "version": None,
                "compatible": False,
                "critical": critical,
                "message": ""
            }
            
            try:
                # Try to import the module
                module = importlib.import_module(dep_name)
                result["installed"] = True
                
                # Get the version
                try:
                    version = getattr(module, "__version__", "unknown")
                    result["version"] = version
                    
                    # Check version compatibility
                    if version != "unknown":
                        min_compatible = self._compare_versions(version, min_version) >= 0
                        max_compatible = True if max_version is None else self._compare_versions(version, max_version) <= 0
                        
                        result["compatible"] = min_compatible and max_compatible
                        
                        if not min_compatible:
                            result["message"] = f"Version {version} is below the minimum required version {min_version}"
                        elif not max_compatible:
                            result["message"] = f"Version {version} is above the maximum supported version {max_version}"
                        else:
                            if recommended_version and self._compare_versions(version, recommended_version) < 0:
                                result["message"] = f"Version {version} is below the recommended version {recommended_version}"
                            else:
                                result["message"] = "Compatible version installed"
                    else:
                        result["compatible"] = True  # Assume compatible if version is unknown
                        result["message"] = "Version unknown, assuming compatible"
                except Exception as e:
                    result["message"] = f"Error getting version: {e}"
            except ImportError:
                result["message"] = f"Module {dep_name} is not installed"
            except Exception as e:
                result["message"] = f"Error importing module {dep_name}: {e}"
            
            # Update critical dependencies status
            if critical and not (result["installed"] and result["compatible"]):
                all_critical_deps_ok = False
            
            results[dep_name] = result
            
            # Log the result
            if result["installed"] and result["compatible"]:
                logger.info(f"Dependency {dep_name} {result['version']} is compatible")
            else:
                log_func = logger.error if critical else logger.warning
                log_func(f"Dependency {dep_name}: {result['message']}")
        
        # Add overall status
        results["_status"] = {
            "all_critical_deps_ok": all_critical_deps_ok,
            "timestamp": import_time.time()
        }
        
        return results
    
    def fix_dependency(self, dep_name: str) -> bool:
        """
        Attempt to fix a dependency issue.
        
        Args:
            dep_name: The name of the dependency to fix.
            
        Returns:
            bool: True if the fix was successful, False otherwise.
        """
        if dep_name not in self.required_dependencies:
            logger.error(f"Unknown dependency: {dep_name}")
            return False
        
        dep_info = self.required_dependencies[dep_name]
        recommended_version = dep_info.get("recommended_version", None)
        
        if not recommended_version:
            logger.error(f"No recommended version specified for {dep_name}")
            return False
        
        logger.info(f"Attempting to fix {dep_name} by installing version {recommended_version}")
        
        try:
            # Use pip to install the recommended version
            cmd = [sys.executable, "-m", "pip", "install", f"{dep_name}=={recommended_version}"]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully installed {dep_name} {recommended_version}")
                return True
            else:
                logger.error(f"Failed to install {dep_name}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error fixing dependency {dep_name}: {e}")
            return False
    
    def fix_numpy_compatibility(self) -> bool:
        """
        Fix NumPy compatibility issues with PyTorch.
        
        Returns:
            bool: True if the fix was successful, False otherwise.
        """
        try:
            import numpy
            numpy_version = numpy.__version__
            
            # Check if NumPy version is too high for PyTorch
            if numpy_version.startswith("2."):
                logger.warning(f"NumPy version {numpy_version} may be incompatible with PyTorch")
                
                # Downgrade to a compatible version
                compatible_version = "1.26.4"
                logger.info(f"Downgrading NumPy to {compatible_version}")
                
                cmd = [sys.executable, "-m", "pip", "install", f"numpy=={compatible_version}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Successfully downgraded NumPy to {compatible_version}")
                    return True
                else:
                    logger.error(f"Failed to downgrade NumPy: {result.stderr}")
                    return False
            
            return True  # No fix needed
        except ImportError:
            logger.warning("NumPy not installed, cannot fix compatibility")
            return False
        except Exception as e:
            logger.error(f"Error fixing NumPy compatibility: {e}")
            return False
    
    def fix_torchaudio_issues(self) -> bool:
        """
        Fix common torchaudio issues.
        
        Returns:
            bool: True if the fix was successful, False otherwise.
        """
        try:
            # Check if PyTorch is installed
            import torch
            
            # Get CUDA information
            cuda_available, cuda_version = self.check_cuda_availability()
            
            # Get torchaudio info from requirements
            torchaudio_info = self.required_dependencies.get("torchaudio", {})
            recommended_version = torchaudio_info.get("recommended_version", "2.2.0")
            
            # Uninstall current torchaudio
            logger.info("Uninstalling current torchaudio")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torchaudio"], 
                          capture_output=True, text=True)
            
            # Install the appropriate version
            if cuda_available:
                # Extract CUDA version for PyTorch index URL
                if cuda_version.startswith("11"):
                    cuda_tag = "cu118"  # Use CUDA 11.8 for CUDA 11.x
                elif cuda_version.startswith("12"):
                    cuda_tag = "cu121"  # Use CUDA 12.1 for CUDA 12.x
                else:
                    cuda_tag = "cu118"  # Default to CUDA 11.8
                
                logger.info(f"Installing torchaudio {recommended_version} with CUDA support ({cuda_tag})")
                cmd = [
                    sys.executable, "-m", "pip", "install", 
                    f"torchaudio=={recommended_version}", 
                    "--index-url", f"https://download.pytorch.org/whl/{cuda_tag}"
                ]
            else:
                logger.info(f"Installing torchaudio {recommended_version} CPU version")
                cmd = [
                    sys.executable, "-m", "pip", "install", 
                    f"torchaudio=={recommended_version}", 
                    "--index-url", "https://download.pytorch.org/whl/cpu"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully installed torchaudio {recommended_version}")
                return True
            else:
                logger.error(f"Failed to install torchaudio: {result.stderr}")
                return False
        except ImportError:
            logger.error("PyTorch not installed, cannot fix torchaudio")
            return False
        except Exception as e:
            logger.error(f"Error fixing torchaudio issues: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of the system's dependency status.
        
        Returns:
            Dict[str, Any]: A dictionary containing the dependency report.
        """
        report = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_compatible": self.check_python_version(),
            "cuda": {},
            "dependencies": {},
            "timestamp": import_time.time(),
            "platform": sys.platform
        }
        
        # Check CUDA
        cuda_available, cuda_version = self.check_cuda_availability()
        report["cuda"] = {
            "available": cuda_available,
            "version": cuda_version
        }
        
        # Check dependencies
        report["dependencies"] = self.verify_dependencies()
        
        return report
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            int: -1 if version1 < version2, 0 if version1 == version2, 1 if version1 > version2
        """
        def normalize(v):
            return [int(x) for x in v.split(".")]
        
        v1_parts = normalize(version1)
        v2_parts = normalize(version2)
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
        
        return 0


# Fix import error in the code above
import time as import_time


def verify_dependencies(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify that all required dependencies are installed and meet version requirements.
    
    This is a convenience function that creates a DependencyManager instance and calls
    its verify_dependencies method.
    
    Args:
        config_path: Path to a JSON configuration file with custom dependency requirements.
                     If None, the default requirements will be used.
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary with dependency status information.
    """
    manager = DependencyManager(config_path)
    return manager.verify_dependencies()


def check_and_fix_dependencies(config_path: Optional[str] = None, 
                              auto_fix: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """
    Check dependencies and optionally fix issues.
    
    Args:
        config_path: Path to a JSON configuration file with custom dependency requirements.
        auto_fix: Whether to automatically fix dependency issues.
        
    Returns:
        Tuple[bool, Dict[str, Any]]: A tuple containing a boolean indicating if all critical
                                    dependencies are OK and a dictionary with the dependency report.
    """
    manager = DependencyManager(config_path)
    
    # Check Python version
    python_ok = manager.check_python_version()
    if not python_ok:
        logger.error("Python version check failed. Please install a compatible Python version.")
        return False, {"python_compatible": False}
    
    # Verify dependencies
    results = manager.verify_dependencies()
    all_critical_deps_ok = results.get("_status", {}).get("all_critical_deps_ok", False)
    
    # Fix issues if requested
    if auto_fix and not all_critical_deps_ok:
        logger.info("Attempting to fix dependency issues...")
        
        # Fix NumPy compatibility issues
        if "numpy" in results and not results["numpy"]["compatible"]:
            manager.fix_numpy_compatibility()
        
        # Fix torchaudio issues
        if "torchaudio" in results and not results["torchaudio"]["compatible"]:
            manager.fix_torchaudio_issues()
        
        # Fix other critical dependencies
        for dep_name, dep_info in results.items():
            if dep_name != "_status" and dep_info.get("critical", False) and not dep_info["compatible"]:
                manager.fix_dependency(dep_name)
        
        # Verify again after fixes
        results = manager.verify_dependencies()
        all_critical_deps_ok = results.get("_status", {}).get("all_critical_deps_ok", False)
    
    # Generate full report
    report = manager.generate_report()
    
    return all_critical_deps_ok, report


if __name__ == "__main__":
    """
    Command-line interface for dependency verification.
    
    Usage:
        python dependency_manager.py [--config CONFIG_PATH] [--fix] [--report]
    
    Options:
        --config CONFIG_PATH  Path to a JSON configuration file with custom dependency requirements.
        --fix                 Automatically fix dependency issues.
        --report              Generate a detailed report.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify and manage dependencies for Genie Whisper")
    parser.add_argument("--config", help="Path to a JSON configuration file")
    parser.add_argument("--fix", action="store_true", help="Automatically fix dependency issues")
    parser.add_argument("--report", action="store_true", help="Generate a detailed report")
    
    args = parser.parse_args()
    
    if args.report:
        manager = DependencyManager(args.config)
        report = manager.generate_report()
        print(json.dumps(report, indent=2))
    else:
        all_ok, report = check_and_fix_dependencies(args.config, args.fix)
        
        if all_ok:
            print("All critical dependencies are satisfied.")
            sys.exit(0)
        else:
            print("Some critical dependencies are missing or incompatible.")
            if args.fix:
                print("Attempted to fix issues, but some problems remain.")
            else:
                print("Run with --fix to attempt automatic fixes.")
            sys.exit(1)