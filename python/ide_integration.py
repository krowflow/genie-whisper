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

# Import text formatter
try:
    from python.text_formatter import format_text, detect_language
except ImportError:
    try:
        from text_formatter import format_text, detect_language
    except ImportError:
        # Define fallback functions if text_formatter is not available
        def format_text(text: str, language: str = "plain", context: Optional[str] = None) -> str:
            return text
        
        def detect_language(text: str) -> str:
            return "plain"

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


class JetBrainsIntegration(IDEIntegration):
    """JetBrains IDEs integration (IntelliJ, PyCharm, WebStorm, etc.)."""
    
    def __init__(self):
        """Initialize the JetBrains integration."""
        super().__init__()
        self.jetbrains_ides = [
            "IntelliJ", "PyCharm", "WebStorm", "PhpStorm",
            "Rider", "CLion", "GoLand", "RubyMine", "DataGrip"
        ]
    
    def inject_text(self, text: str) -> bool:
        """Inject text into JetBrains IDEs.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if any JetBrains IDE is active
        window_title = self._get_active_window_title()
        
        for ide in self.jetbrains_ides:
            if ide in window_title:
                # JetBrains IDE is active, use clipboard method
                logger.info(f"Detected JetBrains IDE: {ide}")
                return self._simulate_clipboard(text)
        
        return False


class SublimeTextIntegration(IDEIntegration):
    """Sublime Text integration."""
    
    def __init__(self):
        """Initialize the Sublime Text integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Sublime Text.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Sublime Text is active
        window_title = self._get_active_window_title()
        
        if "Sublime Text" in window_title:
            # Sublime Text is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class AtomIntegration(IDEIntegration):
    """Atom integration."""
    
    def __init__(self):
        """Initialize the Atom integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Atom.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Atom is active
        window_title = self._get_active_window_title()
        
        if "Atom" in window_title:
            # Atom is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class NotepadPlusPlusIntegration(IDEIntegration):
    """Notepad++ integration."""
    
    def __init__(self):
        """Initialize the Notepad++ integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Notepad++.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Notepad++ is active
        window_title = self._get_active_window_title()
        
        if "Notepad++" in window_title:
            # Notepad++ is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class VisualStudioIntegration(IDEIntegration):
    """Visual Studio integration (not VS Code)."""
    
    def __init__(self):
        """Initialize the Visual Studio integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Visual Studio.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Visual Studio is active
        window_title = self._get_active_window_title()
        
        # Check for Visual Studio but not VS Code
        if "Visual Studio" in window_title and "Code" not in window_title:
            # Visual Studio is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class EclipseIntegration(IDEIntegration):
    """Eclipse integration."""
    
    def __init__(self):
        """Initialize the Eclipse integration."""
        super().__init__()
    
    def inject_text(self, text: str) -> bool:
        """Inject text into Eclipse.
        
        Args:
            text: Text to inject
            
        Returns:
            True if successful, False otherwise
        """
        # Check if Eclipse is active
        window_title = self._get_active_window_title()
        
        if "Eclipse" in window_title:
            # Eclipse is active, use clipboard method
            return self._simulate_clipboard(text)
        
        return False


class IDEIntegrationManager:
    """Manager for IDE integrations."""
    
    def __init__(self):
        """Initialize the IDE integration manager."""
        self.integrations = {
            "vscode": VSCodeIntegration(),
            "cursor": CursorIntegration(),
            "roocode": RooCodeIntegration(),
            "openai": OpenAIChatIntegration(),
            "jetbrains": JetBrainsIntegration(),
            "sublime": SublimeTextIntegration(),
            "atom": AtomIntegration(),
            "notepadplusplus": NotepadPlusPlusIntegration(),
            "visualstudio": VisualStudioIntegration(),
            "eclipse": EclipseIntegration(),
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


def inject_text(text: str, ide: Optional[str] = None, language: Optional[str] = None, context: Optional[str] = None) -> bool:
    """Inject text into the active IDE with optional formatting.
    
    Args:
        text: Text to inject
        ide: IDE to inject into (None for auto-detection)
        language: Programming language for formatting (None for auto-detection)
        context: Additional context for formatting (e.g., "function", "method", etc.)
        
    Returns:
        True if successful, False otherwise
    """
    # Format text if language is specified or can be detected
    if language is None:
        # Try to detect language
        language = detect_language(text)
    
    # Format text based on language and context
    formatted_text = format_text(text, language, context)
    
    # Inject formatted text
    return ide_manager.inject_text(formatted_text, ide)


if __name__ == "__main__":
    # Test IDE integration
    text = "Hello from Genie Whisper!"
    
    print(f"Injecting text: {text}")
    result = inject_text(text)
    
    print(f"Result: {result}")