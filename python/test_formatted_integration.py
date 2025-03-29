#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for formatted IDE integration.
This script demonstrates the IDE integration with text formatting.
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
    from python.text_formatter import detect_language, format_text
except ImportError as e:
    logger.error(f"Failed to import local modules: {e}")
    sys.exit(1)

def test_formatted_integration():
    """Test IDE integration with text formatting for different languages."""
    
    # Python function example
    python_example = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
"""
    
    # JavaScript function example
    javascript_example = """
function calculateTotal(items) {
    let total = 0;
    for (let i = 0; i < items.length; i++) {
        total += items[i];
    }
    return total;
}
"""
    
    # Java method example
    java_example = """
public int calculateTotal(List<Integer> items) {
    int total = 0;
    for (Integer item : items) {
        total += item;
    }
    return total;
}
"""
    
    # C# method example
    csharp_example = """
public int CalculateTotal(List<int> items)
{
    int total = 0;
    foreach (int item in items)
    {
        total += item;
    }
    return total;
}
"""
    
    # HTML example
    html_example = """
<div class="container">
<h1>Hello World</h1>
<p>This is a paragraph.</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ul>
</div>
"""
    
    # SQL example
    sql_example = """
select id, name, price from products where category = 'electronics' order by price desc limit 10
"""
    
    # Examples with their languages and contexts
    examples = [
        {"text": python_example, "language": "python", "context": "function", "name": "Python Function"},
        {"text": javascript_example, "language": "javascript", "context": "function", "name": "JavaScript Function"},
        {"text": java_example, "language": "java", "context": "method", "name": "Java Method"},
        {"text": csharp_example, "language": "csharp", "context": "method", "name": "C# Method"},
        {"text": html_example, "language": "html", "context": None, "name": "HTML"},
        {"text": sql_example, "language": "sql", "context": None, "name": "SQL"}
    ]
    
    # Test each example
    for example in examples:
        logger.info(f"\n\n=== Testing {example['name']} ===")
        
        # Show original text
        logger.info(f"Original text:\n{example['text']}")
        
        # Format text
        formatted_text = format_text(example['text'], example['language'], example['context'])
        
        # Show formatted text
        logger.info(f"Formatted text:\n{formatted_text}")
        
        # Ask user if they want to inject this example
        response = input(f"\nInject {example['name']} example? (y/n): ")
        
        if response.lower() == 'y':
            logger.info(f"Injecting {example['name']} example...")
            logger.info("Please focus on the target application within 3 seconds...")
            
            # Wait for user to focus on the target application
            time.sleep(3)
            
            # Inject formatted text
            result = inject_text(example['text'], None, example['language'], example['context'])
            
            logger.info(f"Text injection {'successful' if result else 'failed'}")
        else:
            logger.info(f"Skipping {example['name']} example")
    
    logger.info("\n=== Testing Complete ===")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test formatted IDE integration")
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in automatic mode without prompting"
    )
    
    args = parser.parse_args()
    
    # Test formatted IDE integration
    test_formatted_integration()

if __name__ == "__main__":
    main()