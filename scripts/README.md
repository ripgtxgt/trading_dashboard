# Trading Dashboard Scripts

## 核心文件

### 交易系统
- `start_trading_system.py` - 主交易系统启动脚本
- `live_strategy_engine_rolling.py` - 10U战神滚仓策略引擎
- `rolling_manager.py` - 滚仓管理器
- `kucoin_trader.py` - KuCoin交易接口
- `kucoin_api.py` - KuCoin API封装

### 风险管理
- `risk_manager.py` - 风险管理模块
- `auto_pause_manager.py` - 自动暂停管理
- `dynamic_position_manager.py` - 动态仓位管理
- `volatility_monitor.py` - 波动率监控

### 数据库
- `db_sync.py` - 数据库同步模块
- `db_integration.py` - 数据库集成

### 通知系统
- `telegram_bot.py` - Telegram Bot控制器
- `telegram_notifier.py` - Telegram通知发送器
- `websocket_pusher.py` - WebSocket推送服务

### 报告
- `daily_report.py` - 每日报告生成器

### 配置
- `live_trading_config.py` - 实盘交易配置
- `config_loader.py` - 配置加载器

## 使用方法

### 启动交易系统
```bash
python start_trading_system.py
```

### 启动Telegram Bot
```bash
python telegram_bot.py
```

### 生成每日报告
```bash
python daily_report.py
```

### 启动WebSocket推送
```bash
python websocket_pusher.py
```

## 注意事项

1. 所有脚本需要在项目根目录下运行
2. 确保已安装所有依赖：`pip install -r requirements.txt`
3. 配置文件位于 `.env` 文件中
4. 数据库配置在 `config/database.json` 中
