"""
实盘TradeConfig文件 - 10U战神滚仓Strategy
版本: 2.0 (实盘版)
Please妥善保管此文件，not要泄露API密钥
"""

# KuCoin API Config
KUCOIN_CONFIG = {
 'api_key': '6902f625f9a9a300014c3976',
 'api_secret': 'd71e4e3d-4369-4e77-94f8-fd456c5e0387',
 'api_passphrase': 'x5gU7dnL6bvrvbV!',
 'sandbox': False, # AlreadyConfirm使用实盘环境
 'leverage': 100, # 杠杆倍数
}

# TradeConfig
TRADING_CONFIG = {
 'symbol': 'BTC/USDT:USDT', # 合约Tradefor（永续合约格式）
 'leverage': 100, # 杠杆倍数
 'margin_mode': 'isolated', # 保证金模式：isolated=逐仓（recommend）, cross=全仓
 'position_mode': 'one-way', # Position模式：one-way=单向Position, hedge=双向Position
 'initial_capital': 10, # 初始资金（USDT）
 'fee_rate': 0.0006, # KuCoin合约Fee率（Taker费率）
}

# StrategyParameter（严格按照原Strategy）
STRATEGY_CONFIG = {
 # baseConfig
 'symbol': 'BTC/USDT:USDT',
 'leverage': 100,
 'timeframe': '1h',
 'kline_limit': 100,
 
 # 初始阶段（10U-80U）
 'stage1': {
 'capital_range': (10, 80),
 'position_ratio': 0.5, # 半仓
 'stop_loss_pct': 0.20, # 20%Stop loss
 'take_profit_pct': 1.0, # 100%Take profit
 },
 # 第二阶段（80U-200U）
 'stage2': {
 'capital_range': (80, 200),
 'position_size': 10, # 每times10U
 'stop_loss_pct': 0.15,
 'take_profit_pct': 0.5,
 },
 # 第三阶段（200U-1000U）
 'stage3': {
 'capital_range': (200, 1000),
 'position_size': 20, # 每times20U
 'stop_loss_pct': 0.15,
 'take_profit_pct': 0.5,
 },
 # 第四阶段（1000U+）
 'stage4': {
 'capital_range': (1000, float('inf')),
 'position_size': 50, # 每times50U
 'stop_loss_pct': 0.15,
 'take_profit_pct': 0.5,
 },
}

# SignalStrategyConfig
SIGNAL_CONFIG = {
 'strategy_type': 'trend_follow', # trend跟踪
 'short_ma_period': 5, # 短期均线cycle
 'long_ma_period': 20, # 长期均线cycle
 'timeframe': '1h', # K线cycle
}

# safeConfig
SAFETY_CONFIG = {
 'max_daily_loss_pct': 0.05, # dailyMaxLoss比例（总金额5%）
 'max_daily_trades': 50, # dailyMaxTradecount
 'min_balance': 5, # MinaccountBalance（USDT），below此值StopTrade
 'emergency_stop_loss': 0.20, # 紧急Stop loss：单PositionLoss20%时强制Close position
 'enable_notifications': True, # is否enableTelegramNotification
}

# RunningConfig
RUN_CONFIG = {
 'check_interval': 60, # 检查间隔（second）
 'log_level': 'INFO', # 日志级别：DEBUG, INFO, WARNING, ERROR
 'log_dir': 'logs', # 日志目录（相for路径，跨平台兼容）
 'state_file': 'trading_state.json', # Status文件（相for路径，跨平台兼容）
 'enable_dashboard': False, # is否enableDashboard（需要单独部署trading_dashboard项目）
 'enable_detailed_log': True, # is否enable详细日志
}
