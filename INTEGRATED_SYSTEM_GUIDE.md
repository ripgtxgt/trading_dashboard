# 10U战神滚仓策略 - 完整集成系统使用指南

## 系统概述

本系统将原有的10U战神滚仓交易策略完整集成到Web Dashboard中，实现：

- ✅ **原有策略完整保留**：所有交易逻辑、滚仓管理、风控机制保持不变
- ✅ **数据库实时同步**：交易数据自动同步到MySQL，Web界面实时显示
- ✅ **Telegram实时通知**：开仓/平仓/风险警告自动推送到手机
- ✅ **Web可视化监控**：实时查看账户状态、交易历史、K线图表、风险指标

## 快速开始

### 1. 配置环境变量

```bash
# 必需配置
export DATABASE_URL="mysql://user:password@host:port/database"
export KUCOIN_API_KEY="your_api_key"
export KUCOIN_API_SECRET="your_api_secret"
export KUCOIN_API_PASSPHRASE="your_api_passphrase"

# 可选配置
export TELEGRAM_BOT_TOKEN="your_bot_token"      # Telegram通知
export TELEGRAM_CHAT_ID="your_chat_id"          # Telegram Chat ID
export KUCOIN_SANDBOX="false"                   # 是否使用沙盒环境
export INITIAL_CAPITAL="10.0"                   # 初始资金（USDT）
```

### 2. 启动交易系统

```bash
cd /home/ubuntu/trading_dashboard/scripts
python3 start_trading_system.py
```

### 3. 访问Web Dashboard

打开浏览器访问：`https://your-domain.manus.space`

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Dashboard (前端)                      │
│  - 实时账户状态显示                                          │
│  - K线图表和MA指标                                           │
│  - 交易历史和盈亏曲线                                        │
│  - 风险控制面板                                              │
│  - 参数调整和回测                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────┴──────────────────────────────────────┐
│                  Node.js Backend (后端)                      │
│  - tRPC API接口                                              │
│  - WebSocket实时推送                                         │
│  - 数据库查询和统计                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ MySQL
┌──────────────────────┴──────────────────────────────────────┐
│                    MySQL Database                            │
│  - 账户状态 (bot_state)                                      │
│  - 交易记录 (trades)                                         │
│  - 持仓信息 (positions)                                      │
│  - 余额快照 (balance_snapshots)                             │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Python Trading System (交易系统)                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  start_trading_system.py (主启动脚本)               │    │
│  │  - 初始化所有组件                                   │    │
│  │  - 协调数据流                                       │    │
│  └──────────┬──────────────────────────────────────────┘    │
│             │                                                │
│  ┌──────────┴──────────────────────────────────────────┐    │
│  │  live_strategy_engine_rolling.py (策略引擎)         │    │
│  │  - 信号生成 (MA5/MA20交叉)                          │    │
│  │  - 开仓/平仓逻辑                                     │    │
│  │  - 风控检查                                          │    │
│  └──────────┬──────────────────────────────────────────┘    │
│             │                                                │
│  ┌──────────┴──────────────────────────────────────────┐    │
│  │  rolling_manager.py (滚仓管理器)                    │    │
│  │  - 阶段管理 (Stage1-5)                              │    │
│  │  - 仓位计算                                          │    │
│  │  - 止损止盈                                          │    │
│  └──────────┬──────────────────────────────────────────┘    │
│             │                                                │
│  ┌──────────┴──────────────────────────────────────────┐    │
│  │  kucoin_trader.py (KuCoin交易器)                    │    │
│  │  - API调用                                           │    │
│  │  - 订单执行                                          │    │
│  │  - 账户查询                                          │    │
│  └──────────┬──────────────────────────────────────────┘    │
│             │                                                │
│  ┌──────────┴──────────────────────────────────────────┐    │
│  │  db_sync.py (数据库同步)                            │    │
│  │  - 写入交易记录                                      │    │
│  │  - 更新账户状态                                      │    │
│  │  - 保存余额快照                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│             │                                                │
│  ┌──────────┴──────────────────────────────────────────┐    │
│  │  telegram_notifier.py (Telegram通知)                │    │
│  │  - 开仓通知                                          │    │
│  │  - 平仓通知                                          │    │
│  │  - 风险警告                                          │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 核心文件说明

### Python交易系统

| 文件 | 说明 | 来源 |
|------|------|------|
| `start_trading_system.py` | **主启动脚本**，集成所有组件 | 新创建 |
| `live_strategy_engine_rolling.py` | **策略引擎**，信号生成和交易执行 | 原项目 |
| `rolling_manager.py` | **滚仓管理器**，阶段管理和仓位计算 | 原项目 |
| `kucoin_trader.py` | **KuCoin交易器**，API调用和订单执行 | 原项目 |
| `kucoin_api.py` | **KuCoin API封装** | 原项目 |
| `live_trading_config.py` | **策略配置**，MA参数、风控参数等 | 原项目 |
| `db_sync.py` | **数据库同步模块** | Web项目 |
| `telegram_notifier.py` | **Telegram通知模块** | Web项目 |

### Web Dashboard

| 目录/文件 | 说明 |
|-----------|------|
| `client/src/pages/Dashboard.tsx` | 主界面，显示所有监控面板 |
| `client/src/components/` | 各种UI组件（K线图、参数面板等） |
| `server/routers.ts` | tRPC API接口定义 |
| `drizzle/schema.ts` | 数据库表结构定义 |

## 策略参数配置

编辑 `scripts/live_trading_config.py`：

```python
# 信号配置
SIGNAL_CONFIG = {
    'short_ma_period': 5,      # 短期MA周期
    'long_ma_period': 20,      # 长期MA周期
    'timeframe': '1h',         # 时间框架
}

# 策略配置
STRATEGY_CONFIG = {
    'leverage': 10,            # 杠杆倍数
    'check_interval': 60,      # 检查间隔（秒）
}

# 安全配置
SAFETY_CONFIG = {
    'max_daily_trades': 10,    # 单日最大交易次数
    'max_daily_loss': 2.0,     # 单日最大亏损（USDT）
    'min_balance': 5.0,        # 最小余额（USDT）
    'emergency_stop_loss': 0.5, # 紧急止损比例（50%）
}
```

## 滚仓阶段说明

系统会根据资金自动切换阶段：

| 阶段 | 资金范围 | 保证金比例 | 止损 | 止盈 |
|------|----------|------------|------|------|
| Stage1 | 10-20U | 90% | 5% | 10% |
| Stage2 | 20-40U | 85% | 6% | 12% |
| Stage3 | 40-80U | 80% | 7% | 15% |
| Stage4 | 80-160U | 75% | 8% | 18% |
| Stage5 | 160U+ | 70% | 10% | 20% |

## 数据流说明

### 开仓流程

```
1. 策略引擎检测到信号 (MA5上穿MA20)
   ↓
2. 滚仓管理器计算仓位大小
   ↓
3. KuCoin交易器执行开仓
   ↓
4. 数据库同步模块写入持仓记录
   ↓
5. Telegram通知模块发送开仓通知
   ↓
6. Web Dashboard实时显示持仓状态
```

### 平仓流程

```
1. 策略引擎检测到平仓条件 (止损/止盈/反向信号)
   ↓
2. KuCoin交易器执行平仓
   ↓
3. 滚仓管理器计算盈亏
   ↓
4. 数据库同步模块写入交易记录
   ↓
5. Telegram通知模块发送平仓通知
   ↓
6. Web Dashboard更新交易历史和盈亏曲线
```

## 监控和维护

### 查看日志

```bash
# 实时查看日志
tail -f /home/ubuntu/trading_dashboard/scripts/trading_system_*.log

# 查看最近100行
tail -n 100 /home/ubuntu/trading_dashboard/scripts/trading_system_*.log
```

### 停止系统

```bash
# 按 Ctrl+C 优雅停止
# 系统会自动：
# 1. 平掉所有持仓
# 2. 保存状态到数据库
# 3. 发送停止通知
```

### 重启系统

```bash
# 停止后重新启动
cd /home/ubuntu/trading_dashboard/scripts
python3 start_trading_system.py
```

## Web Dashboard功能

### 1. 账户概览

- 当前余额
- 总盈亏
- 当前阶段
- 持仓信息

### 2. K线图表

- 实时K线数据
- MA5/MA20指标
- 买卖信号标记

### 3. 交易历史

- 所有交易记录
- 盈亏曲线
- 胜率统计

### 4. 风险控制

- 当前回撤
- 连续亏损次数
- 仓位风险比例
- 风险等级

### 5. 参数调整

- MA周期调整
- 时间框架切换
- 参数回测
- AI优化推荐

### 6. 实时信号

- WebSocket实时推送
- 信号通知
- 状态更新

## 故障排查

### 问题：交易系统无法启动

**检查**：
1. 环境变量是否正确设置
2. KuCoin API密钥是否有效
3. 数据库连接是否正常

```bash
# 测试数据库连接
cd /home/ubuntu/trading_dashboard/scripts
python3 -c "from db_sync import DatabaseSync; db = DatabaseSync(); print('OK' if db.connect() else 'FAIL')"
```

### 问题：无法接收Telegram通知

**检查**：
1. TELEGRAM_BOT_TOKEN是否正确
2. TELEGRAM_CHAT_ID是否正确
3. Bot是否已启动对话

```bash
# 测试Telegram通知
cd /home/ubuntu/trading_dashboard/scripts
python3 telegram_notifier.py
```

### 问题：Web Dashboard不显示数据

**检查**：
1. 交易系统是否正在运行
2. 数据库中是否有数据
3. 浏览器控制台是否有错误

## 安全建议

1. **API密钥安全**
   - 不要将API密钥提交到代码仓库
   - 使用环境变量管理敏感信息
   - 定期更换API密钥

2. **资金安全**
   - 先在沙盒环境测试
   - 设置合理的止损比例
   - 不要投入超过承受范围的资金

3. **系统安全**
   - 定期备份数据库
   - 监控系统日志
   - 及时更新依赖包

## 下一步优化建议

1. **添加更多策略**
   - 支持多种技术指标组合
   - 实现策略切换功能

2. **完善风控系统**
   - 添加更多风险指标
   - 实现自动风险预警

3. **优化用户体验**
   - 添加移动端App
   - 实现语音通知

4. **扩展功能**
   - 支持多交易对
   - 添加网格交易策略

## 技术支持

如遇问题，请查看：
- 系统日志文件
- Web Dashboard错误提示
- Telegram通知消息

或联系技术支持。
