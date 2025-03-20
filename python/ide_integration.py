#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IDE Integration module for Genie Whisper.
This module provides functionality to inject text into different IDEs.
"""

import logging
import os
import sys
import time
import platform
import subprocess
from typing import Optional, Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class IDEIntegration:
    """Base class for IDE integration."""
    
    def __init__(self):
        """Initialize the IDE integration."""
        self.os_name = platform.system()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into the active IDE.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement inject_text")
    
    def _get_active_window_title(self) -> str:
        """Get the title of the active window.
        
        Returns:
            Window title or empty string if not available
        """
        try:
            if self.os_name == "Windows":
                # Windows implementation
                import win32gui
                
                window = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(window)
                
                return title
            
            elif self.os_name == "Darwin":
                # macOS implementation
                script = """
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    set windowTitle to ""
                    
                    tell process frontApp
                        if exists (1st window whose value of attribute "AXMain" is true) then
                            set windowTitle to name of 1st window whose value of attribute "AXMain" is true
                        end if
                    end tell
                    
                    return {frontApp, windowTitle}
                end tell
                """
                
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    parts = output.split(", ")
                    
                    if len(parts) >= 2:
                        return parts[1]
                
                return ""
            
            elif self.os_name == "Linux":
                # Linux implementation
                try:
                    # Try xdotool
                    result = subprocess.run(
                        ["xdotool", "getactivewindow", "getwindowname"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        return result.stdout.strip()
                    
                except FileNotFoundError:
                    # Try wmctrl
                    try:
                        result = subprocess.run(
                            ["wmctrl", "-a", ":ACTIVE:"],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            return result.stdout.strip()
                    
                    except FileNotFoundError:
                        logger.warning("Neither xdotool nor wmctrl found on Linux")
                
                return ""
            
            else:
                logger.warning(f"Unsupported OS: {self.os_name}")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting active window title: {e}")
            return ""
    
    def _simulate_keystrokes(self, text: str) -> bool:
        """Simulate keystrokes to type text.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.os_name == "Windows":
                # Windows implementation
                import win32com.client
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys(text)
                
                return True
            
            elif self.os_name == "Darwin":
                # macOS implementation
                # Use string concatenation instead of f-string to avoid backslash issues
                escaped_text = text.replace('"', '\\"')
                script = """
                tell application "System Events"
                    keystroke \"""" + escaped_text + """\"
                end tell
                """
                
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True
                )
                
                return result.returncode == 0
            
            elif self.os_name == "Linux":
                # Linux implementation
                try:
                    # Try xdotool
                    result = subprocess.run(
                        ["xdotool", "type", text],
                        capture_output=True,
                        text=True
                    )
                    
                    return result.returncode == 0
                    
                except FileNotFoundError:
                    logger.warning("xdotool not found on Linux")
                    return False
            
            else:
                logger.warning(f"Unsupported OS: {self.os_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error simulating keystrokes: {e}")
            return False
    
    def _simulate_clipboard(self, text: str) -> bool:
        """Simulate clipboard paste to insert text.
        
        Args:
            text: Text to paste
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Store original clipboard content
            import pyperclip
            original_clipboard = pyperclip.paste()
            
            # Copy text to clipboard
            pyperclip.copy(text)
            
            # Simulate paste keystroke
            if self.os_name == "Windows":
                import win32com.client
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys("^v")  # Ctrl+V
                
            elif self.os_name == "Darwin":
                script = """
                tell application "System Events"
                    keystroke "v" using command down
                end tell
                """
                
                subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True
                )
                
            elif self.os_name == "Linux":
                try:
                    subprocess.run(
                        ["xdotool", "key", "ctrl+v"],
                        capture_output=True,
                        text=True
                    )
                except FileNotFoundError:
                    logger.warning("xdotool not found on Linux")
                    return False
            
            # Wait a bit before restoring clipboard
            time.sleep(0.5)
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
            return True
            
        except Exception as e:
            logger.error(f"Error simulating clipboard paste: {e}")
            return False


class VSCodeIntegration(IDEIntegration):
    """VS Code integration."""
    
    def __init__(self):
        """Initialize the VS Code integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into VS Code.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if VS Code is active
        window_title = self._get_active_window_title()
        
        if "Visual Studio Code" in window_title or "VS Code" in window_title:
            # VS Code is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class CursorIntegration(IDEIntegration):
    """Cursor integration."""
    
    def __init__(self):
        """Initialize the Cursor integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Cursor.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Cursor is active
        window_title = self._get_active_window_title()
        
        if "Cursor" in window_title:
            # Cursor is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class RooCodeIntegration(IDEIntegration):
    """Roo Code integration."""
    
    def __init__(self):
        """Initialize the Roo Code integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Roo Code.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Roo Code is active
        window_title = self._get_active_window_title()
        
        if "Roo Code" in window_title:
            # Roo Code is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class OpenAIChatIntegration(IDEIntegration):
    """OpenAI Chat integration."""
    
    def __init__(self):
        """Initialize the OpenAI Chat integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into OpenAI Chat.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if OpenAI Chat is active
        window_title = self._get_active_window_title()
        
        if "ChatGPT" in window_title or "OpenAI" in window_title:
            # OpenAI Chat is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class FallbackIntegration(IDEIntegration):
    """Fallback integration using clipboard."""
    
    def __init__(self):
        """Initialize the fallback integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text using clipboard.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Use clipboard method as fallback
        return self._simulate_clipboard(text)


class IDEIntegrationManager:
    """Manager for IDE integrations."""
    
    def __init__(self):
        """Initialize the IDE integration manager."""
        self.integrations = {
            "vscode": VSCodeIntegration(),
            "cursor": CursorIntegration(),
            "roocode": RooCodeIntegration(),
            "openai": OpenAIChatIntegration(),
            "fallback": FallbackIntegration()
        }
    
    def inject_text(self, text: str, ide: Optional[str] = None) -> bool:
        """Inject text into the specified IDE or detect automatically.
        
        Args:
            text: Text to inject
            ide: IDE to inject into (None for auto-detection)
            
        Returns:
            True if successful, False otherwise
        """
        if ide and ide.lower() in self.integrations:
            # Use specified IDE
            return self.integrations[ide.lower()].inject_text(text)
        
        # Auto-detect IDE
        for name, integration in self.integrations.items():
            if name != "fallback":
                if integration.inject_text(text):
                    logger.info(f"Text injected into {name}")
                    return True
        
        # Use fallback
        logger.info("Using fallback integration")
        return self.integrations["fallback"].inject_text(text)


# Create a singleton instance
ide_manager = IDEIntegrationManager()


def inject_text(text: str, ide: Optional[str] = None) -> bool:
    """Inject text into the active IDE.
    
    Args:
        text: Text to inject
        ide: IDE to inject into (None for auto-detection)
        
    Returns:
        True if successful, False otherwise
    """
    return ide_manager.inject_text(text, ide)


if __name__ == "__main__":
    # Test IDE integration
    text = "Hello from Genie Whisper!"
    
    print(f"Injecting text: {text}")
    result = inject_text(text)
    
    print(f"Result: {result}")