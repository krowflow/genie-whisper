#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for IDE integration.
This script tests the IDE integration functionality.
"""

import argparse
import logging
import os
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
try:
    from python.ide_integration import inject_text
except ImportError as e:
    logger.error(f"Failed to import local modules: {e}")
    sys.exit(1)

def test_ide_integration(text, ide=None, delay=3):
    """Test IDE integration.
    
    Args:
        text: Text to inject
        ide: IDE to inject into (None for auto-detection)
        delay: Delay in seconds before injecting text
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Testing IDE integration for {ide or 'auto-detected IDE'}...")
        logger.info(f"Text to inject: '{text}'")
        logger.info(f"Waiting {delay} seconds before injecting text...")
        
        # Wait for user to focus on the target application
        time.sleep(delay)
        
        # Inject text
        result = inject_text(text, ide)
        
        logger.info(f"Text injection {'successful' if result else 'failed'}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing IDE integration: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test IDE integration")
    
    parser.add_argument(
        "--text",
        type=str,
        default="Hello from Genie Whisper!",
        help="Text to inject"
    )
    
    parser.add_argument(
        "--ide",
        type=str,
        default=None,
        choices=["vscode", "cursor", "roocode", "openai", None],
        help="IDE to inject into (None for auto-detection)"
    )
    
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Delay in seconds before injecting text"
    )
    
    args = parser.parse_args()
    
    # Test IDE integration
    success = test_ide_integration(args.text, args.ide, args.delay)
    
    if success:
        logger.info("IDE integration test successful")
    else:
        logger.error("IDE integration test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()