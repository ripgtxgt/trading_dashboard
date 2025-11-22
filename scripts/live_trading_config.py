"""
实盘交易配置文件 - 10U战神滚仓策略
版本: 2.0 (实盘版)
请妥善保管此文件，不要泄露API密钥
"""

# KuCoin API 配置
KUCOIN_CONFIG = {
    'api_key': '6902f625f9a9a300014c3976',
    'api_secret': 'd71e4e3d-4369-4e77-94f8-fd456c5e0387',
    'api_passphrase': 'x5gU7dnL6bvrvbV!',
    'sandbox': False,  # 已确认使用实盘环境
    'leverage': 100,  # 杠杆倍数
}

# 交易配置
TRADING_CONFIG = {
    'symbol': 'BTC/USDT:USDT',  # 合约交易对（永续合约格式）
    'leverage': 100,  # 杠杆倍数
    'margin_mode': 'isolated',  # 保证金模式：isolated=逐仓（推荐）, cross=全仓
    'position_mode': 'one-way',  # 持仓模式：one-way=单向持仓, hedge=双向持仓
    'initial_capital': 10,  # 初始资金（USDT）
    'fee_rate': 0.0006,  # KuCoin合约手续费率（Taker费率）
}

# 策略参数（严格按照原策略）
STRATEGY_CONFIG = {
    # 基础配置
    'symbol': 'BTC/USDT:USDT',
    'leverage': 100,
    'timeframe': '1h',
    'kline_limit': 100,
    
    # 初始阶段（10U-80U）
    'stage1': {
        'capital_range': (10, 80),
        'position_ratio': 0.5,  # 半仓
        'stop_loss_pct': 0.20,  # 20%止损
        'take_profit_pct': 1.0,  # 100%止盈
    },
    # 第二阶段（80U-200U）
    'stage2': {
        'capital_range': (80, 200),
        'position_size': 10,  # 每次10U
        'stop_loss_pct': 0.15,
        'take_profit_pct': 0.5,
    },
    # 第三阶段（200U-1000U）
    'stage3': {
        'capital_range': (200, 1000),
        'position_size': 20,  # 每次20U
        'stop_loss_pct': 0.15,
        'take_profit_pct': 0.5,
    },
    # 第四阶段（1000U+）
    'stage4': {
        'capital_range': (1000, float('inf')),
        'position_size': 50,  # 每次50U
        'stop_loss_pct': 0.15,
        'take_profit_pct': 0.5,
    },
}

# 信号策略配置
SIGNAL_CONFIG = {
    'strategy_type': 'trend_follow',  # 趋势跟踪
    'short_ma_period': 5,  # 短期均线周期
    'long_ma_period': 20,  # 长期均线周期
    'timeframe': '1h',  # K线周期
}

# 安全配置
SAFETY_CONFIG = {
    'max_daily_loss': 100,  # 单日最大亏损（USDT）
    'max_daily_trades': 50,  # 单日最大交易次数
    'min_balance': 5,  # 最小账户余额（USDT），低于此值停止交易
    'emergency_stop_loss': 0.5,  # 紧急止损：账户总资金亏损50%时强制停止
    'enable_notifications': True,  # 是否启用通知（预留）
}

# 运行配置
RUN_CONFIG = {
    'check_interval': 60,  # 检查间隔（秒）
    'log_level': 'INFO',  # 日志级别：DEBUG, INFO, WARNING, ERROR
    'log_dir': 'logs',  # 日志目录（相对路径，跨平台兼容）
    'state_file': 'trading_state.json',  # 状态文件（相对路径，跨平台兼容）
    'enable_dashboard': False,  # 是否启用Dashboard（需要单独部署trading_dashboard项目）
    'enable_detailed_log': True,  # 是否启用详细日志
}
