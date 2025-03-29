#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Text Formatter module for Genie Whisper.
This module provides functionality to format text for different languages and contexts.
"""

import logging
import sys
import re
from typing import Optional, Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class TextFormatter:
    """Text formatter for different languages and contexts."""
    
    def __init__(self):
        """Initialize the text formatter."""
        # Language-specific formatters
        self.formatters = {
            "python": self._format_python,
            "javascript": self._format_javascript,
            "typescript": self._format_typescript,
            "java": self._format_java,
            "csharp": self._format_csharp,
            "cpp": self._format_cpp,
            "go": self._format_go,
            "rust": self._format_rust,
            "markdown": self._format_markdown,
            "html": self._format_html,
            "css": self._format_css,
            "sql": self._format_sql,
            "shell": self._format_shell,
            "plain": self._format_plain
        }
    
    def format_text(self, text: str, language: str = "plain", context: Optional[str] = None) -> str:
        """Format text for the specified language and context.
        
        Args:
            text: Text to format
            language: Programming language or format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Convert language to lowercase
        language = language.lower()
        
        # Use the appropriate formatter
        if language in self.formatters:
            logger.info(f"Formatting text for {language}")
            return self.formatters[language](text, context)
        else:
            logger.warning(f"No formatter available for {language}, using plain text")
            return self._format_plain(text, context)
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language
        """
        # Simple language detection based on keywords and syntax
        if re.search(r'def\s+\w+\s*\(.*\):', text):
            return "python"
        elif re.search(r'function\s+\w+\s*\(.*\)', text):
            return "javascript"
        elif re.search(r'class\s+\w+\s*\{', text) and re.search(r':\s*\w+', text):
            return "typescript"
        elif re.search(r'public\s+class\s+\w+', text):
            return "java"
        elif re.search(r'public\s+static\s+void\s+Main', text):
            return "csharp"
        elif re.search(r'#include\s+<\w+>', text):
            return "cpp"
        elif re.search(r'func\s+\w+\s*\(.*\)', text):
            return "go"
        elif re.search(r'fn\s+\w+\s*\(.*\)', text):
            return "rust"
        elif re.search(r'^#\s+', text, re.MULTILINE):
            return "markdown"
        elif re.search(r'<\w+>.*</\w+>', text):
            return "html"
        elif re.search(r'\{\s*\w+\s*:\s*\w+', text):
            return "css"
        elif re.search(r'SELECT\s+.*\s+FROM\s+', text, re.IGNORECASE):
            return "sql"
        elif re.search(r'^#!\s*/bin/(bash|sh)', text):
            return "shell"
        else:
            return "plain"
    
    def _format_python(self, text: str, context: Optional[str] = None) -> str:
        """Format Python code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent
            if stripped.startswith(('return', 'break', 'continue', 'pass', 'raise', 'else:', 'elif', 'except:', 'finally:')):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('    ' * indent_level + stripped)
            
            # Check for indent
            if stripped.endswith((':',)) and not stripped.startswith(('import', 'from')):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        # Add docstrings if it's a function or class
        if context == "function" and "def " in formatted_text and '"""' not in formatted_text:
            # Extract function name and parameters
            match = re.search(r'def\s+(\w+)\s*\((.*?)\)', formatted_text)
            if match:
                func_name = match.group(1)
                params = match.group(2).split(',')
                
                # Create docstring
                docstring = f'    """{func_name} function.\n    \n'
                
                for param in params:
                    param = param.strip()
                    if param and param != 'self':
                        docstring += f'    Args:\n        {param}: Description\n    \n'
                
                docstring += '    Returns:\n        Description\n    """\n'
                
                # Insert docstring after function definition
                formatted_text = re.sub(r'(def\s+\w+\s*\(.*?\):)', r'\1\n' + docstring, formatted_text)
        
        return formatted_text
    
    def _format_javascript(self, text: str, context: Optional[str] = None) -> str:
        """Format JavaScript code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('  ' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        # Add JSDoc comments if it's a function
        if context == "function" and "function " in formatted_text and '/**' not in formatted_text:
            # Extract function name and parameters
            match = re.search(r'function\s+(\w+)\s*\((.*?)\)', formatted_text)
            if match:
                func_name = match.group(1)
                params = match.group(2).split(',')
                
                # Create JSDoc comment
                jsdoc = f'/**\n * {func_name} function.\n *\n'
                
                for param in params:
                    param = param.strip()
                    if param:
                        jsdoc += f' * @param {{{param.split("=")[0].strip()}}} {param} - Description\n'
                
                jsdoc += ' * @returns {any} Description\n */\n'
                
                # Insert JSDoc comment before function definition
                formatted_text = re.sub(r'(function\s+\w+\s*\(.*?\))', jsdoc + r'\1', formatted_text)
        
        return formatted_text
    
    def _format_typescript(self, text: str, context: Optional[str] = None) -> str:
        """Format TypeScript code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Similar to JavaScript but with type annotations
        formatted_text = self._format_javascript(text, context)
        
        # Add type annotations if not present
        if ":" not in formatted_text and "function " in formatted_text:
            # Add return type
            formatted_text = re.sub(r'(function\s+\w+\s*\(.*?\))', r'\1: any', formatted_text)
            
            # Add parameter types
            formatted_text = re.sub(r'(\(\s*)(\w+)(\s*[,)])', r'\1\2: any\3', formatted_text)
        
        return formatted_text
    
    def _format_java(self, text: str, context: Optional[str] = None) -> str:
        """Format Java code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('    ' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        # Add Javadoc comments if it's a method
        if context == "method" and "public " in formatted_text and '/**' not in formatted_text:
            # Extract method name and parameters
            match = re.search(r'(public|private|protected)\s+\w+\s+(\w+)\s*\((.*?)\)', formatted_text)
            if match:
                method_name = match.group(2)
                params = match.group(3).split(',')
                
                # Create Javadoc comment
                javadoc = f'/**\n * {method_name} method.\n *\n'
                
                for param in params:
                    param = param.strip()
                    if param:
                        param_parts = param.split()
                        if len(param_parts) >= 2:
                            javadoc += f' * @param {param_parts[-1]} Description\n'
                
                javadoc += ' * @return Description\n */\n'
                
                # Insert Javadoc comment before method definition
                formatted_text = re.sub(r'(public|private|protected)', javadoc + r'\1', formatted_text, count=1)
        
        return formatted_text
    
    def _format_csharp(self, text: str, context: Optional[str] = None) -> str:
        """Format C# code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('    ' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        # Add XML comments if it's a method
        if context == "method" and "public " in formatted_text and '///' not in formatted_text:
            # Extract method name and parameters
            match = re.search(r'(public|private|protected)\s+\w+\s+(\w+)\s*\((.*?)\)', formatted_text)
            if match:
                method_name = match.group(2)
                params = match.group(3).split(',')
                
                # Create XML comment
                xml_comment = f'/// <summary>\n/// {method_name} method.\n/// </summary>\n'
                
                for param in params:
                    param = param.strip()
                    if param:
                        param_parts = param.split()
                        if len(param_parts) >= 2:
                            xml_comment += f'/// <param name="{param_parts[-1]}">Description</param>\n'
                
                xml_comment += '/// <returns>Description</returns>\n'
                
                # Insert XML comment before method definition
                formatted_text = re.sub(r'(public|private|protected)', xml_comment + r'\1', formatted_text, count=1)
        
        return formatted_text
    
    def _format_cpp(self, text: str, context: Optional[str] = None) -> str:
        """Format C++ code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('    ' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        return formatted_text
    
    def _format_go(self, text: str, context: Optional[str] = None) -> str:
        """Format Go code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('\t' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        return formatted_text
    
    def _format_rust(self, text: str, context: Optional[str] = None) -> str:
        """Format Rust code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('    ' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        return formatted_text
    
    def _format_markdown(self, text: str, context: Optional[str] = None) -> str:
        """Format Markdown text.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Ensure proper spacing for headers
        formatted_text = re.sub(r'^(#+)([^ ])', r'\1 \2', text, flags=re.MULTILINE)
        
        # Ensure proper spacing for lists
        formatted_text = re.sub(r'^(-|\*|\+)([^ ])', r'\1 \2', formatted_text, flags=re.MULTILINE)
        
        # Ensure proper spacing for numbered lists
        formatted_text = re.sub(r'^(\d+\.)([^ ])', r'\1 \2', formatted_text, flags=re.MULTILINE)
        
        return formatted_text
    
    def _format_html(self, text: str, context: Optional[str] = None) -> str:
        """Format HTML code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing tag)
            if re.search(r'^</\w+', stripped):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('  ' * indent_level + stripped)
            
            # Check for indent (opening tag with no closing tag on same line)
            if re.search(r'^<\w+[^>]*>$', stripped) and not re.search(r'/>$', stripped) and not re.search(r'^<(img|br|hr|input|link|meta)', stripped):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        return formatted_text
    
    def _format_css(self, text: str, context: Optional[str] = None) -> str:
        """Format CSS code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add proper indentation
        lines = text.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            # Adjust indent level based on line content
            stripped = line.strip()
            
            # Check for dedent (closing brace)
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indented_lines.append('  ' * indent_level + stripped)
            
            # Check for indent (opening brace)
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines
        formatted_text = '\n'.join(indented_lines)
        
        return formatted_text
    
    def _format_sql(self, text: str, context: Optional[str] = None) -> str:
        """Format SQL code.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Uppercase SQL keywords
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
            'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'INSERT', 'UPDATE',
            'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE', 'VIEW', 'INDEX', 'TRIGGER',
            'PROCEDURE', 'FUNCTION', 'AS', 'ON', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN',
            'LIKE', 'IS NULL', 'IS NOT NULL', 'ASC', 'DESC'
        ]
        
        formatted_text = text
        for keyword in keywords:
            formatted_text = re.sub(r'\b' + keyword + r'\b', keyword, formatted_text, flags=re.IGNORECASE)
        
        return formatted_text
    
    def _format_shell(self, text: str, context: Optional[str] = None) -> str:
        """Format shell script.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Add shebang if not present
        if not text.startswith('#!'):
            text = '#!/bin/bash\n\n' + text
        
        # Add comments for functions
        if context == "function" and "function " in text and not re.search(r'#.*function', text):
            # Extract function name
            match = re.search(r'function\s+(\w+)', text)
            if match:
                func_name = match.group(1)
                
                # Create comment
                comment = f'# {func_name} function\n# \n# Args:\n#   $1: Description\n# \n# Returns:\n#   Description\n'
                
                # Insert comment before function definition
                text = re.sub(r'(function\s+\w+)', comment + r'\1', text)
        
        return text
    
    def _format_plain(self, text: str, context: Optional[str] = None) -> str:
        """Format plain text.
        
        Args:
            text: Text to format
            context: Additional context for formatting
            
        Returns:
            Formatted text
        """
        # Just return the text as is
        return text


# Create a singleton instance
text_formatter = TextFormatter()


def format_text(text: str, language: str = "plain", context: Optional[str] = None) -> str:
    """Format text for the specified language and context.
    
    Args:
        text: Text to format
        language: Programming language or format
        context: Additional context for formatting
        
    Returns:
        Formatted text
    """
    return text_formatter.format_text(text, language, context)


def detect_language(text: str) -> str:
    """Detect the language of the text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Detected language
    """
    return text_formatter.detect_language(text)


if __name__ == "__main__":
    # Test text formatter
    test_text = "def hello(name):\nprint(f'Hello, {name}!')"
    
    print(f"Original text:\n{test_text}\n")
    
    formatted_text = format_text(test_text, "python", "function")
    print(f"Formatted text:\n{formatted_text}")