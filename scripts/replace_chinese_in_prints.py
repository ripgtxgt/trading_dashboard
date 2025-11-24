#!/usr/bin/env python3
"""
Smart Chinese character replacement in print/logging statements only
Preserves code structure, comments, and docstrings
"""
import os
import re

# Comprehensive Chinese to English translation map
TRANSLATIONS = {
    # Common actions
    '初始化': 'Initialize',
    '启动': 'Start',
    '停止': 'Stop',
    '开始': 'Start',
    '结束': 'End',
    '完成': 'Complete',
    '成功': 'Success',
    '失败': 'Failed',
    '错误': 'Error',
    '警告': 'Warning',
    '信息': 'Info',
    
    # Trading terms
    '交易': 'Trade',
    '买入': 'Buy',
    '卖出': 'Sell',
    '开仓': 'Open position',
    '平仓': 'Close position',
    '持仓': 'Position',
    '订单': 'Order',
    '价格': 'Price',
    '数量': 'Amount',
    '余额': 'Balance',
    '资金': 'Capital',
    '利润': 'Profit',
    '亏损': 'Loss',
    '盈利': 'Profit',
    '止损': 'Stop loss',
    '止盈': 'Take profit',
    
    # System terms
    '数据库': 'Database',
    '连接': 'Connect',
    '配置': 'Config',
    '加载': 'Load',
    '保存': 'Save',
    '更新': 'Update',
    '查询': 'Query',
    '获取': 'Get',
    'Send': 'Send',
    '接收': 'Receive',
    '推送': 'Push',
    '通知': 'Notify',
    '消息': 'Message',
    
    # Status
    '运行': 'Running',
    '暂停': 'Paused',
    '等待': 'Waiting',
    '重试': 'Retry',
    '取消': 'Cancel',
    '确认': 'Confirm',
    
    # Risk management
    '风险': 'Risk',
    '检查': 'Check',
    '监控': 'Monitor',
    '评估': 'Assess',
    '控制': 'Control',
    '限制': 'Limit',
    '超出': 'Exceed',
    '达到': 'Reach',
    
    # Time
    '时间': 'Time',
    '日期': 'Date',
    '周期': 'Period',
    '间隔': 'Interval',
    
    # Common phrases
    '正在': 'In progress',
    '已经': 'Already',
    '未': 'Not',
    '无法': 'Cannot',
    '请': 'Please',
    '当前': 'Current',
    '最新': 'Latest',
    '历史': 'History',
    '总计': 'Total',
    '平均': 'Average',
}

def replace_chinese(text):
    """Replace Chinese characters with English"""
    # First try phrase replacements
    for chinese, english in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        text = text.replace(chinese, english)
    
    # Then remove any remaining Chinese characters
    result = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # Chinese character range
            continue  # Skip it
        result.append(char)
    
    return ''.join(result)

def process_file(filepath):
    """Process a single Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            # Check if this line contains print or logging
            if ('print(' in line or 'logging.' in line or 'logger.' in line):
                # Check if it has Chinese characters
                if any('\u4e00' <= c <= '\u9fff' for c in line):
                    # Replace Chinese in this line
                    new_line = replace_chinese(line)
                    new_lines.append(new_line)
                    modified = True
                else:
                    new_lines.append(line)
            else:
                # Keep other lines unchanged (including comments and docstrings)
                new_lines.append(line)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("SMART CHINESE REPLACEMENT - Print/Logging statements only")
    print("=" * 80)
    print()
    
    # Get all Python files
    python_files = sorted([f for f in os.listdir('.') 
                          if f.endswith('.py') and f != 'replace_chinese_in_prints.py'])
    
    fixed_count = 0
    for filename in python_files:
        if process_file(filename):
            print(f"[FIXED] {filename}")
            fixed_count += 1
        else:
            print(f"[SKIP]  {filename}")
    
    print()
    print("=" * 80)
    print(f"Modified {fixed_count} out of {len(python_files)} files")
    print("=" * 80)
    
    # Verify syntax
    print("\nVerifying Python syntax...")
    errors = []
    for filename in python_files:
        result = os.system(f'python3 -m py_compile {filename} 2>/dev/null')
        if result != 0:
            errors.append(filename)
    
    if errors:
        print(f"\n[ERROR] {len(errors)} files have syntax errors:")
        for f in errors:
            print(f"  - {f}")
        return 1
    else:
        print("\n[SUCCESS] All files have valid Python syntax!")
        return 0

if __name__ == '__main__':
    exit(main())
