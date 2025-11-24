#!/usr/bin/env python3
"""
Batch fix all Python scripts to remove non-ASCII characters
Replace Chinese and emoji with English equivalents
"""
import os
import re

# Common Chinese to English translations for trading context
TRANSLATIONS = {
    # Status messages
    '初始化': 'Initialize',
    '启动': 'Start',
    '停止': 'Stop',
    '暂停': 'Pause',
    '恢复': 'Resume',
    '运行': 'Running',
    '成功': 'Success',
    '失败': 'Failed',
    '错误': 'Error',
    '警告': 'Warning',
    '完成': 'Complete',
    '开始': 'Begin',
    '结束': 'End',
    
    # Trading terms
    '买入': 'Buy',
    '卖出': 'Sell',
    '开多': 'Long',
    '开空': 'Short',
    '平仓': 'Close position',
    '持仓': 'Position',
    '订单': 'Order',
    '交易': 'Trade',
    '余额': 'Balance',
    '盈亏': 'PnL',
    '收益': 'Profit',
    '亏损': 'Loss',
    '胜率': 'Win rate',
    '仓位': 'Position',
    '价格': 'Price',
    '数量': 'Amount',
    '手续费': 'Fee',
    
    # Risk management
    '风险': 'Risk',
    '波动': 'Volatility',
    '回撤': 'Drawdown',
    '止损': 'Stop loss',
    '止盈': 'Take profit',
    '最大': 'Max',
    '最小': 'Min',
    '当前': 'Current',
    '总计': 'Total',
    
    # Time
    '时间': 'Time',
    '日期': 'Date',
    '小时': 'hour',
    '分钟': 'minute',
    '秒': 'second',
    '等待': 'Wait',
    
    # Database
    '数据库': 'Database',
    '连接': 'Connection',
    '查询': 'Query',
    '更新': 'Update',
    '插入': 'Insert',
    '删除': 'Delete',
    
    # Notifications
    '通知': 'Notification',
    '发送': 'Send',
    '接收': 'Receive',
    '消息': 'Message',
    
    # Common phrases
    '检测到': 'Detected',
    '正在': 'Processing',
    '已': 'Already',
    '未': 'Not',
    '无': 'No',
    '有': 'Has',
    '获取': 'Get',
    '设置': 'Set',
    '配置': 'Config',
    '参数': 'Parameter',
    '信号': 'Signal',
    '策略': 'Strategy',
    '状态': 'Status',
    '信息': 'Info',
    '详情': 'Details',
    '记录': 'Record',
    '历史': 'History',
    '实时': 'Realtime',
    '监控': 'Monitor',
    '分析': 'Analysis',
    '计算': 'Calculate',
    '执行': 'Execute',
    '处理': 'Process',
    '加载': 'Load',
    '保存': 'Save',
    '退出': 'Exit',
    '重试': 'Retry',
    '取消': 'Cancel',
    '确认': 'Confirm',
    '请': 'Please',
    '的': '',
    '了': '',
    '中': 'in',
    '和': 'and',
    '或': 'or',
    '与': 'and',
    '为': 'as',
    '是': 'is',
    '不': 'not',
    '到': 'to',
    '从': 'from',
    '在': 'at',
    '于': 'at',
    '对': 'for',
    '将': 'will',
    '已经': 'already',
    '正在': 'processing',
    '即将': 'about to',
    '尝试': 'try',
    '重新': 're-',
    '自动': 'auto',
    '手动': 'manual',
    '必需': 'required',
    '可选': 'optional',
    '默认': 'default',
    '建议': 'suggest',
    '推荐': 'recommend',
    '说明': 'description',
    '原因': 'reason',
    '结果': 'result',
    '次数': 'count',
    '次': 'times',
    '个': '',
    '条': '',
    '笔': '',
    '周期': 'cycle',
    '达到': 'reach',
    '超过': 'exceed',
    '低于': 'below',
    '高于': 'above',
    '等于': 'equal',
    '大于': 'greater than',
    '小于': 'less than',
    '之间': 'between',
    '范围': 'range',
    '限制': 'limit',
    '触发': 'trigger',
    '激活': 'activate',
    '禁用': 'disable',
    '启用': 'enable',
    '关闭': 'close',
    '打开': 'open',
    '缺少': 'missing',
    '环境变量': 'env var',
    '以下': 'following',
    '收到': 'received',
    '停止信号': 'stop signal',
    '出错': 'error occurred',
    '连续': 'consecutive',
    '单日': 'daily',
    '累计': 'cumulative',
    '占比': 'ratio',
    '系数': 'multiplier',
    '基础': 'base',
    '安全': 'safe',
    '调整': 'adjust',
    '价值': 'value',
    '等级': 'level',
    '趋势': 'trend',
    '应': 'should',
    '评估': 'assessment',
    '服务器': 'server',
    '断开': 'disconnect',
    '推送': 'push',
    '账户': 'account',
    '最终': 'final',
    '收益率': 'return rate',
    '比率': 'ratio',
}

# Emoji replacements
EMOJI_MAP = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    '📍': '[INFO]',
    '✓': '[OK]',
    '✗': '[FAIL]',
    '🎉': '[SUCCESS]',
    '🚀': '[START]',
    '📊': '[DATA]',
    '💰': '[MONEY]',
    '⏰': '[TIME]',
    '🔔': '[ALERT]',
    '🛑': '[STOP]',
}

def replace_chinese_phrase(text):
    """Replace common Chinese phrases with English"""
    # Sort by length (longest first) to handle multi-character phrases
    for chinese, english in sorted(TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(chinese, english)
    return text

def replace_emojis(text):
    """Replace emojis with ASCII equivalents"""
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    return text

def clean_extra_spaces(text):
    """Clean up extra spaces after replacements"""
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Remove space before punctuation
    text = re.sub(r' ([,.:;!?)])', r'\1', text)
    # Remove space after opening bracket
    text = re.sub(r'(\() ', r'\1', text)
    return text

def fix_file(filepath):
    """Fix a single Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace emojis first
        content = replace_emojis(content)
        
        # Replace Chinese phrases
        content = replace_chinese_phrase(content)
        
        # Clean up extra spaces
        content = clean_extra_spaces(content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    print("=" * 80)
    print("BATCH FIXING ALL PYTHON SCRIPTS")
    print("=" * 80)
    print()
    
    # Get all Python files
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'fix_all_encoding.py']
    
    fixed_count = 0
    for filename in sorted(python_files):
        if fix_file(filename):
            print(f"[FIXED] {filename}")
            fixed_count += 1
        else:
            print(f"[SKIP]  {filename} (no changes)")
    
    print()
    print("=" * 80)
    print(f"COMPLETE: Fixed {fixed_count} out of {len(python_files)} files")
    print("=" * 80)

if __name__ == '__main__':
    main()
