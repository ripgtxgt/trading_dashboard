#!/usr/bin/env python3
"""
Safe encoding fix script - Only replaces string content, preserves code structure
"""
import os
import re

# Translation map for common Chinese characters
TRANSLATIONS = {
    # Keep the translations simple and safe
    '初始化': 'Initialize',
    '成功': 'Success',
    '失败': 'Failed',
    '错误': 'Error',
    '警告': 'Warning',
    '信息': 'Info',
    '开始': 'Start',
    '结束': 'End',
    '启动': 'Start',
    '停止': 'Stop',
    '运行': 'Running',
    '完成': 'Complete',
}

# Emoji replacements
EMOJI_MAP = {
    '[OK]': '[OK]',
    '[ERROR]': '[ERROR]',
    '[WARNING]': '[WARNING]',
    '[WARNING]': '[WARNING]',
    '[INFO]': '[INFO]',
    '[OK]': '[OK]',
    '[FAIL]': '[FAIL]',
    '[SUCCESS]': '[SUCCESS]',
    '[START]': '[START]',
}

def replace_in_string(text):
    """Replace non-ASCII characters in string content only"""
    # First replace emojis
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    
    # Then replace Chinese with English
    for chinese, english in TRANSLATIONS.items():
        text = text.replace(chinese, english)
    
    # Remove any remaining non-ASCII characters
    # Keep only printable ASCII (32-126) plus common whitespace
    result = []
    for char in text:
        if 32 <= ord(char) <= 126 or char in '\n\r\t':
            result.append(char)
        # If non-ASCII, just skip it (don't replace with space to avoid breaking code)
    
    return ''.join(result)

def fix_file_safe(filepath):
    """
    Safely fix a Python file by only modifying string literals
    Preserves all code structure, indentation, and syntax
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Strategy: Use regex to find string literals and replace content inside them
        # Match f-strings, regular strings, and docstrings
        
        def replace_string_content(match):
            """Replace content inside a matched string"""
            full_match = match.group(0)
            quote_char = match.group(1)  # Single or double quote
            string_content = match.group(2)
            
            # Only process if string contains non-ASCII
            if any(ord(c) > 127 for c in string_content):
                # Replace non-ASCII in the string content
                new_content = replace_in_string(string_content)
                return f'{quote_char}{new_content}{quote_char}'
            
            return full_match
        
        # Pattern to match string literals (both single and double quoted)
        # This pattern handles:
        # - Regular strings: "text" or 'text'
        # - f-strings: f"text" or f'text'
        # - Raw strings: r"text" or r'text'
        # But NOT docstrings (""" or ''')
        
        # Match single-line strings
        pattern = r'(["\'])([^\1\n]*?)\1'
        content = re.sub(pattern, replace_string_content, content)
        
        # Match f-strings
        f_pattern = r'f(["\'])([^\1\n]*?)\1'
        content = re.sub(f_pattern, lambda m: 'f' + replace_string_content(m), content)
        
        # Match r-strings
        r_pattern = r'r(["\'])([^\1\n]*?)\1'
        content = re.sub(r_pattern, lambda m: 'r' + replace_string_content(m), content)
        
        # Check if anything changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("SAFE ENCODING FIX - Preserves code structure")
    print("=" * 80)
    print()
    
    # Get all Python files
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'fix_encoding_safe.py']
    
    fixed_count = 0
    for filename in sorted(python_files):
        if fix_file_safe(filename):
            print(f"[FIXED] {filename}")
            fixed_count += 1
        else:
            print(f"[SKIP]  {filename}")
    
    print()
    print("=" * 80)
    print(f"Fixed {fixed_count} out of {len(python_files)} files")
    print("=" * 80)
    
    # Verify syntax
    print("\nVerifying Python syntax...")
    errors = []
    for filename in sorted(python_files):
        result = os.system(f'python3 -m py_compile {filename} 2>/dev/null')
        if result != 0:
            errors.append(filename)
    
    if errors:
        print(f"\n[WARNING] {len(errors)} files have syntax errors:")
        for f in errors:
            print(f"  - {f}")
    else:
        print("\n[SUCCESS] All files have valid Python syntax!")

if __name__ == '__main__':
    main()
