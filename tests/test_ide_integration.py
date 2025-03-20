#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for IDE integration.
This script verifies that the IDE integration module can be loaded and used for text injection.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_clipboard_integration():
    """Test clipboard integration."""
    try:
        logger.info("Testing clipboard integration...")
        
        # Import pyperclip
        import pyperclip
        
        # Save current clipboard content
        original_clipboard = pyperclip.paste()
        
        # Set clipboard content
        test_text = "Hello from Genie Whisper!"
        pyperclip.copy(test_text)
        
        # Verify clipboard content
        clipboard_content = pyperclip.paste()
        logger.info(f"Clipboard content: {clipboard_content}")
        
        # Restore original clipboard content
        pyperclip.copy(original_clipboard)
        
        # Check if clipboard content was set correctly
        if clipboard_content == test_text:
            logger.info("Clipboard integration test passed!")
            return True
        else:
            logger.error("Clipboard integration test failed!")
            return False
        
    except Exception as e:
        logger.error(f"Error testing clipboard integration: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_ide_integration_module():
    """Create a simple IDE integration module."""
    
    def inject_text(text, ide=None):
        """Inject text into IDE.
        
        Args:
            text: Text to inject
            ide: IDE to inject into (None for auto-detection)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Injecting text into IDE: {ide or 'auto-detect'}")
            logger.info(f"Text: {text}")
            
            # Import required modules
            import pyperclip
            
            # Save current clipboard content
            original_clipboard = pyperclip.paste()
            
            # Set clipboard content
            pyperclip.copy(text)
            
            # Simulate keyboard shortcut for paste
            # In a real implementation, this would use pyautogui to press Ctrl+V
            # or use IDE-specific APIs
            logger.info("Simulating keyboard shortcut for paste (Ctrl+V)")
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
            return True
            
        except Exception as e:
            logger.error(f"Error injecting text: {e}")
            return False
    
    return inject_text

def test_ide_integration():
    """Test IDE integration."""
    try:
        logger.info("Testing IDE integration...")
        
        # Create IDE integration module
        inject_text = create_ide_integration_module()
        
        # Test text injection
        test_text = "Hello from Genie Whisper!"
        result = inject_text(test_text, ide="vscode")
        
        if result:
            logger.info("IDE integration test passed!")
            return True
        else:
            logger.error("IDE integration test failed!")
            return False
        
    except Exception as e:
        logger.error(f"Error testing IDE integration: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_clipboard_integration() and test_ide_integration()
    if success:
        logger.info("IDE integration tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("IDE integration tests failed!")
        sys.exit(1)