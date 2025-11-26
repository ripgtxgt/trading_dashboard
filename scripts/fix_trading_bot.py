#!/usr/bin/env python3
"""
Fix Trading Bot - Add .env loading and encoding fix
"""

import os
import sys

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    # 设置环境变量强制使用UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 读取原始文件
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经添加了dotenv
if 'load_dotenv' in content:
    print("✓ .env loading already added")
    sys.exit(0)

# 在import部分之后添加dotenv加载
import_section_end = content.find('from live_strategy_engine_rolling')

if import_section_end == -1:
    print("✗ Could not find import section")
    sys.exit(1)

# 构建新的导入部分
new_imports = '''
# Load environment variables from .env file
from dotenv import load_dotenv
import codecs

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Load .env file from project root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)
print(f"Loaded environment variables from: {env_path}")

'''

# 在sys.path.insert之后插入新代码
insert_pos = content.find('sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
if insert_pos == -1:
    print("✗ Could not find insertion point")
    sys.exit(1)

# 找到这一行的结束位置
insert_pos = content.find('\n', insert_pos) + 1

# 插入新代码
new_content = content[:insert_pos] + new_imports + content[insert_pos:]

# 备份原文件
backup_path = script_path + '.backup'
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Backup created: {backup_path}")

# 写入修改后的文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f"✓ Fixed: {script_path}")

print("\n" + "="*60)
print("Trading Bot Fix Applied Successfully!")
print("="*60)
print("\nChanges made:")
print("1. Added python-dotenv to load .env file")
print("2. Added UTF-8 encoding fix for Windows")
print("3. Environment variables will now be loaded automatically")
print("\nNext steps:")
print("1. Restart trading-bot: pm2 restart trading-bot")
print("2. Check logs: pm2 logs trading-bot")
