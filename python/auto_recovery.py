#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Recovery Module for Genie Whisper

This module provides automatic dependency verification and recovery at application startup.
It handles dependency issues transparently without requiring user intervention.

Author: Genie Whisper Team
Date: March 20, 2025
"""

import os
import sys
import json
import logging
import subprocess
import importlib
import time
from typing import Dict, List, Tuple, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("genie_whisper_recovery.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutoRecovery")

class AutoRecovery:
    """
    Automatic dependency recovery system for Genie Whisper.
    
    This class provides methods to verify dependencies and automatically fix common issues
    without requiring user intervention.
    """
    
    def __init__(self, app_name: str = "Genie Whisper"):
        """
        Initialize the auto recovery system.
        
        Args:
            app_name: Name of the application
        """
        self.app_name = app_name
        self.recovery_log = []
        self.dependency_manager = None
        
        # Try to import dependency_manager
        try:
            # First try relative import
            from dependency_manager import DependencyManager, check_and_fix_dependencies
            self.dependency_manager = DependencyManager
            self.check_and_fix_dependencies = check_and_fix_dependencies
            logger.info("Successfully imported dependency_manager module")
        except ImportError:
            logger.warning("Could not import dependency_manager module, will use fallback methods")
            self.dependency_manager = None
    
    def log_recovery_action(self, action: str, success: bool, details: str = "") -> None:
        """
        Log a recovery action.
        
        Args:
            action: Description of the action
            success: Whether the action was successful
            details: Additional details
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.recovery_log.append({
            "timestamp": timestamp,
            "action": action,
            "success": success,
            "details": details
        })
        
        if success:
            logger.info(f"Recovery action '{action}' succeeded: {details}")
        else:
            logger.error(f"Recovery action '{action}' failed: {details}")
    
    def verify_and_fix_dependencies(self) -> bool:
        """
        Verify dependencies and automatically fix issues.
        
        Returns:
            bool: True if all critical dependencies are satisfied, False otherwise
        """
        logger.info("Starting automatic dependency verification and recovery")
        
        # Check if dependency_manager is available
        if self.dependency_manager:
            # Use enhanced dependency manager
            return self._verify_with_dependency_manager()
        else:
            # Use fallback method
            return self._verify_with_fallback()
    
    def _verify_with_dependency_manager(self) -> bool:
        """
        Verify dependencies using the dependency_manager module.
        
        Returns:
            bool: True if all critical dependencies are satisfied, False otherwise
        """
        logger.info("Using enhanced dependency manager for verification")
        
        # Check if dependency configuration file exists
        config_path = self._get_or_create_config()
        
        # Run dependency check with auto-fix enabled
        try:
            all_ok, report = self.check_and_fix_dependencies(config_path, auto_fix=True)
            
            # Log results
            if all_ok:
                self.log_recovery_action(
                    "Dependency verification", 
                    True, 
                    "All critical dependencies are satisfied"
                )
            else:
                self.log_recovery_action(
                    "Dependency verification", 
                    False, 
                    "Some critical dependencies could not be fixed automatically"
                )
                
                # Log details of failed dependencies
                if "dependencies" in report:
                    for dep_name, dep_info in report["dependencies"].items():
                        if dep_name != "_status" and not (dep_info.get("installed", False) and dep_info.get("compatible", False)):
                            self.log_recovery_action(
                                f"Fix {dep_name}", 
                                False, 
                                dep_info.get("message", "Unknown issue")
                            )
            
            return all_ok
            
        except Exception as e:
            self.log_recovery_action(
                "Dependency verification", 
                False, 
                f"Error during verification: {str(e)}"
            )
            return False
    
    def _verify_with_fallback(self) -> bool:
        """
        Verify dependencies using fallback methods when dependency_manager is not available.
        
        Returns:
            bool: True if all critical dependencies are satisfied, False otherwise
        """
        logger.info("Using fallback method for dependency verification")
        
        # Define critical dependencies
        critical_dependencies = {
            "torch": {"min_version": "2.0.0"},
            "torchaudio": {"min_version": "2.0.0"},
            "numpy": {"min_version": "1.20.0", "max_version": "1.26.4"},
            "faster_whisper": {"min_version": "0.5.0"},
            "sounddevice": {"min_version": "0.4.0"}
        }
        
        all_ok = True
        
        # Check each dependency
        for dep_name, dep_info in critical_dependencies.items():
            try:
                # Try to import the module
                module = importlib.import_module(dep_name)
                
                # Get the version
                version = getattr(module, "__version__", "unknown")
                
                # Check version compatibility
                if version != "unknown":
                    min_version = dep_info.get("min_version", "0.0.0")
                    max_version = dep_info.get("max_version", None)
                    
                    min_compatible = self._compare_versions(version, min_version) >= 0
                    max_compatible = True if max_version is None else self._compare_versions(version, max_version) <= 0
                    
                    if not min_compatible:
                        self.log_recovery_action(
                            f"Check {dep_name}", 
                            False, 
                            f"Version {version} is below the minimum required version {min_version}"
                        )
                        all_ok = False
                    elif not max_compatible:
                        self.log_recovery_action(
                            f"Check {dep_name}", 
                            False, 
                            f"Version {version} is above the maximum supported version {max_version}"
                        )
                        all_ok = False
                    else:
                        self.log_recovery_action(
                            f"Check {dep_name}", 
                            True, 
                            f"Version {version} is compatible"
                        )
                else:
                    self.log_recovery_action(
                        f"Check {dep_name}", 
                        True, 
                        "Version unknown, assuming compatible"
                    )
            except ImportError:
                self.log_recovery_action(
                    f"Check {dep_name}", 
                    False, 
                    f"Module {dep_name} is not installed"
                )
                all_ok = False
            except Exception as e:
                self.log_recovery_action(
                    f"Check {dep_name}", 
                    False, 
                    f"Error checking module {dep_name}: {str(e)}"
                )
                all_ok = False
        
        # Try to fix NumPy compatibility issues
        if not all_ok:
            try:
                import numpy
                numpy_version = numpy.__version__
                
                # Check if NumPy version is too high for PyTorch
                if numpy_version.startswith("2."):
                    self.log_recovery_action(
                        "Fix NumPy compatibility", 
                        True, 
                        f"Detected NumPy {numpy_version}, attempting to downgrade to 1.26.4"
                    )
                    
                    # Downgrade to a compatible version
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "numpy==1.26.4"],
                        check=True,
                        capture_output=True
                    )
                    
                    self.log_recovery_action(
                        "Fix NumPy compatibility", 
                        True, 
                        "Successfully downgraded NumPy to 1.26.4"
                    )
            except Exception as e:
                self.log_recovery_action(
                    "Fix NumPy compatibility", 
                    False, 
                    f"Error fixing NumPy compatibility: {str(e)}"
                )
        
        return all_ok
    
    def _get_or_create_config(self) -> str:
        """
        Get the path to the dependency configuration file, creating it if it doesn't exist.
        
        Returns:
            str: Path to the configuration file
        """
        # Check if config file exists
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependency_config.json")
        
        if not os.path.exists(config_path):
            logger.info(f"Creating default dependency configuration at {config_path}")
            
            # Create default configuration
            default_config = {
                "dependencies": {
                    "torch": {"min_version": "2.0.0", "recommended_version": "2.2.0", "critical": True},
                    "torchaudio": {"min_version": "2.0.0", "recommended_version": "2.2.0", "critical": True},
                    "numpy": {"min_version": "1.20.0", "max_version": "1.26.4", "critical": True},
                    "faster_whisper": {"min_version": "0.5.0", "critical": True},
                    "sounddevice": {"min_version": "0.4.0", "critical": True}
                },
                "system_requirements": {
                    "python": {"min_version": "3.9.0", "recommended_version": "3.10.0"},
                    "cuda": {"min_version": "11.6", "recommended_version": "12.1", "required": False}
                }
            }
            
            try:
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                self.log_recovery_action(
                    "Create default config", 
                    True, 
                    f"Created at {config_path}"
                )
            except Exception as e:
                self.log_recovery_action(
                    "Create default config", 
                    False, 
                    f"Error: {str(e)}"
                )
                # Use a fallback path in the temp directory
                import tempfile
                config_path = os.path.join(tempfile.gettempdir(), "genie_whisper_dependency_config.json")
                try:
                    with open(config_path, 'w') as f:
                        json.dump(default_config, f, indent=2)
                    self.log_recovery_action(
                        "Create fallback config", 
                        True, 
                        f"Created at {config_path}"
                    )
                except Exception as e:
                    self.log_recovery_action(
                        "Create fallback config", 
                        False, 
                        f"Error: {str(e)}"
                    )
        
        return config_path
    
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
    
    def get_recovery_log(self) -> List[Dict[str, Any]]:
        """
        Get the recovery log.
        
        Returns:
            List[Dict[str, Any]]: List of recovery actions
        """
        return self.recovery_log
    
    def get_recovery_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the recovery process.
        
        Returns:
            Dict[str, Any]: Summary of the recovery process
        """
        total_actions = len(self.recovery_log)
        successful_actions = sum(1 for action in self.recovery_log if action["success"])
        failed_actions = total_actions - successful_actions
        
        return {
            "app_name": self.app_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "success_rate": successful_actions / max(1, total_actions) * 100,
            "recovery_log": self.recovery_log
        }


def auto_verify_dependencies() -> bool:
    """
    Automatically verify and fix dependencies.
    
    This function is designed to be called at application startup to ensure
    all dependencies are satisfied without requiring user intervention.
    
    Returns:
        bool: True if all critical dependencies are satisfied, False otherwise
    """
    recovery = AutoRecovery()
    return recovery.verify_and_fix_dependencies()


if __name__ == "__main__":
    """
    Command-line interface for testing the auto recovery system.
    """
    print("Genie Whisper Auto Recovery System")
    print("=================================")
    print("Testing automatic dependency verification and recovery...")
    
    recovery = AutoRecovery()
    result = recovery.verify_and_fix_dependencies()
    
    print("\nRecovery Summary:")
    print(f"Success: {'Yes' if result else 'No'}")
    
    summary = recovery.get_recovery_summary()
    print(f"Total actions: {summary['total_actions']}")
    print(f"Successful actions: {summary['successful_actions']}")
    print(f"Failed actions: {summary['failed_actions']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    print("\nRecovery Log:")
    for action in recovery.get_recovery_log():
        status = "✓" if action["success"] else "✗"
        print(f"[{action['timestamp']}] {status} {action['action']}: {action['details']}")
    
    sys.exit(0 if result else 1)