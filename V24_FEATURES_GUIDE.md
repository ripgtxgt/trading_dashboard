# v24.0 系统增强功能使用指南

## 📋 目录

1. [功能概述](#功能概述)
2. [测试模式和模拟交易](#测试模式和模拟交易)
3. [实时数据推送](#实时数据推送)
4. [多策略回测对比](#多策略回测对比)
5. [使用示例](#使用示例)
6. [常见问题](#常见问题)

---

## 功能概述

v24.0版本在保持完整交易系统的基础上，新增了三大增强功能：

### 1. 测试模式和模拟交易

- **无风险测试** - 使用模拟资金测试策略和风险管理
- **完整交易模拟** - 模拟订单执行、滑点、手续费
- **风险管理验证** - 在模拟环境中测试所有风险控制机制
- **状态持久化** - 测试数据自动保存，可随时查看

### 2. 实时数据推送

- **WebSocket连接** - 建立实时双向通信
- **自动更新** - Dashboard数据自动刷新，无需手动操作
- **多数据流** - 同时推送账户、持仓、K线、风险状态
- **连接管理** - 自动重连，连接状态可视化

### 3. 多策略回测对比

- **并行回测** - 同时回测多个策略配置
- **全面指标** - 胜率、收益、夏普比率、最大回撤等
- **可视化对比** - 收益曲线图和指标对比表
- **结果保存** - 回测结果自动保存，可随时查看

---

## 测试模式和模拟交易

### 功能说明

测试模式允许您在不使用真实资金的情况下，完整测试交易策略和风险管理功能。

### 核心特性

#### 1. 模拟交易引擎

```python
from test_mode import get_simulated_exchange

# 获取模拟交易所
exchange = get_simulated_exchange()

# 查看余额
balance = exchange.get_balance()
print(f"总余额: {balance['total']} USDT")
print(f"可用余额: {balance['available']} USDT")

# 创建订单
result = exchange.create_order(
    symbol='XBTUSDTM',
    side='buy',
    size=0.001,
    price=50000
)

if result['success']:
    print(f"订单创建成功: {result['order']['order_id']}")
```

#### 2. 完整的交易模拟

模拟交易引擎包含：

- **滑点模拟** - 默认0.05%滑点
- **手续费计算** - Maker 0.02%, Taker 0.06%
- **保证金管理** - 根据杠杆计算保证金占用
- **余额检查** - 自动检查余额是否充足
- **订单失败模拟** - 可配置失败率（默认关闭）

#### 3. 风险管理测试

```python
from risk_manager import RiskManager
from test_mode import get_simulated_exchange

# 创建风险管理器
risk_manager = RiskManager()

# 获取模拟交易所
exchange = get_simulated_exchange()

# 模拟交易循环
while True:
    # 获取当前价格和余额
    current_price = get_market_price()
    balance = exchange.get_balance()
    
    # 检查风险
    allowed, reason = risk_manager.check_risk(current_price, balance['total'])
    
    if not allowed:
        print(f"风险控制触发: {reason}")
        break
    
    # 执行交易
    # ...
```

### 配置说明

测试模式配置文件：`scripts/test_mode_config.json`

```json
{
  "enabled": false,
  "initial_balance": 100.0,
  "leverage": 10,
  "maker_fee": 0.0002,
  "taker_fee": 0.0006,
  "slippage": 0.0005,
  "simulate_latency": true,
  "latency_ms": 100,
  "simulate_failures": false,
  "failure_rate": 0.01
}
```

**配置项说明：**

- `enabled` - 是否启用测试模式
- `initial_balance` - 初始资金（USDT）
- `leverage` - 杠杆倍数
- `maker_fee` - Maker手续费率
- `taker_fee` - Taker手续费率
- `slippage` - 滑点率
- `simulate_latency` - 是否模拟网络延迟
- `latency_ms` - 延迟毫秒数
- `simulate_failures` - 是否模拟订单失败
- `failure_rate` - 失败率

### 使用步骤

#### 1. 启用测试模式

```python
from test_mode import get_test_config

config = get_test_config()
config.enable()
```

#### 2. 运行交易脚本

```python
from test_mode import is_test_mode, get_simulated_exchange
from kucoin_trader import KuCoinTrader

if is_test_mode():
    print("⚠️  当前为测试模式")
    exchange = get_simulated_exchange()
else:
    print("✅ 当前为实盘模式")
    exchange = KuCoinTrader()

# 使用统一的接口
balance = exchange.get_balance()
positions = exchange.get_positions()
```

#### 3. 查看测试结果

```python
# 获取交易历史
trades = exchange.get_trades(limit=100)

for trade in trades:
    print(f"交易: {trade['side']} @ {trade['exit_price']}")
    print(f"盈亏: {trade['net_pnl']:.2f} USDT")
```

#### 4. 重置测试状态

```python
exchange.reset()
print("✅ 测试状态已重置")
```

### 测试场景

#### 场景1：测试风险管理

```python
# 模拟连续亏损
for i in range(5):
    result = exchange.create_order('XBTUSDTM', 'buy', 0.001, 50000)
    # 模拟价格下跌，平仓亏损
    exchange.close_position(result['position']['position_id'], 49000)
    
    # 记录到风险管理器
    risk_manager.record_trade(-10, False)
    
    # 检查是否触发风险控制
    allowed, reason = risk_manager.check_risk(49000, exchange.get_balance()['total'])
    if not allowed:
        print(f"触发风险控制: {reason}")
        break
```

#### 场景2：测试策略表现

```python
# 运行策略回测
from strategy_comparison import StrategyBacktester, StrategyConfig

backtester = StrategyBacktester(symbol='BTC/USDT', initial_capital=100.0)

config = StrategyConfig('测试策略', {
    'ma_short': 5,
    'ma_long': 20,
    'position_size': 0.1
})

result = backtester.backtest_strategy(config, historical_data)
print(f"胜率: {result.win_rate*100:.2f}%")
print(f"总收益: {result.total_return:.2f} USDT")
```

---

## 实时数据推送

### 功能说明

通过WebSocket建立实时连接，自动推送最新数据到Dashboard，无需手动刷新。

### 推送数据类型

#### 1. 账户状态

```typescript
{
  type: 'account_status',
  data: {
    balance: 105.8,
    available: 95.3,
    used: 10.5,
    currency: 'USDT',
    mode: 'test'
  }
}
```

推送频率：每5秒

#### 2. 持仓信息

```typescript
{
  type: 'positions',
  data: [
    {
      position_id: 'TEST_1',
      symbol: 'XBTUSDTM',
      side: 'buy',
      size: 0.001,
      entry_price: 50025.0,
      margin: 5.0,
      leverage: 10,
      unrealized_pnl: 0.97,
      timestamp: '2025-11-22T12:00:00'
    }
  ]
}
```

推送频率：每3秒

#### 3. K线数据

```typescript
{
  type: 'kline',
  data: {
    timestamp: '2025-11-22T12:00:00',
    open: 50000,
    high: 50500,
    low: 49800,
    close: 50200,
    volume: 1234.56
  }
}
```

推送频率：每60秒

#### 4. 风险状态

```typescript
{
  type: 'risk_status',
  data: {
    is_trading_allowed: true,
    pause_reason: null,
    daily_pnl: -2.5,
    total_pnl: 5.8,
    current_drawdown_pct: 0.05,
    consecutive_losses: 1,
    volatility: 0.02
  }
}
```

推送频率：每10秒

#### 5. 交易信号

```typescript
{
  type: 'trade_signal',
  data: {
    signal: 'long',
    price: 50200,
    timestamp: '2025-11-22T12:00:00',
    reason: 'MA交叉做多'
  }
}
```

推送频率：有信号时立即推送

### 前端集成

#### 1. 使用实时数据Context

```typescript
import { useRealtimeData } from '@/contexts/RealtimeDataContext';

function MyComponent() {
  const {
    isConnected,
    accountStatus,
    positions,
    riskStatus,
    reconnect
  } = useRealtimeData();

  return (
    <div>
      {isConnected ? (
        <div>
          <p>余额: {accountStatus?.balance} USDT</p>
          <p>持仓数量: {positions.length}</p>
        </div>
      ) : (
        <button onClick={reconnect}>重新连接</button>
      )}
    </div>
  );
}
```

#### 2. 显示连接状态

```typescript
import { ConnectionStatus } from '@/components/ConnectionStatus';

function Dashboard() {
  return (
    <div>
      <header>
        <h1>交易Dashboard</h1>
        <ConnectionStatus />
      </header>
      {/* 其他内容 */}
    </div>
  );
}
```

### 服务端配置

#### 启动WebSocket服务

```bash
cd /home/ubuntu/trading_dashboard
python3 scripts/websocket_pusher.py
```

#### 配置WebSocket URL

在 `.env` 文件中配置：

```
VITE_WS_URL=ws://localhost:8765
```

或在生产环境使用：

```
VITE_WS_URL=wss://your-domain.com/ws
```

### 连接管理

#### 自动重连

WebSocket客户端会在连接断开后自动尝试重连：

- 重连间隔：3秒
- 无限次重试
- 连接状态实时显示

#### 手动重连

```typescript
const { reconnect } = useRealtimeData();

// 点击按钮手动重连
<button onClick={reconnect}>重新连接</button>
```

---

## 多策略回测对比

### 功能说明

同时回测多个策略配置，通过可视化图表对比不同参数的表现。

### 使用方法

#### 1. 创建策略配置

```python
from strategy_comparison import StrategyConfig

strategies = [
    StrategyConfig('保守型 MA(5,20)', {
        'ma_short': 5,
        'ma_long': 20,
        'position_size': 0.1
    }),
    StrategyConfig('平衡型 MA(10,30)', {
        'ma_short': 10,
        'ma_long': 30,
        'position_size': 0.15
    }),
    StrategyConfig('激进型 MA(3,15)', {
        'ma_short': 3,
        'ma_long': 15,
        'position_size': 0.2
    })
]
```

#### 2. 运行对比回测

```python
from strategy_comparison import StrategyBacktester

# 创建回测器
backtester = StrategyBacktester(
    symbol='BTC/USDT',
    initial_capital=100.0
)

# 对比回测
results = backtester.compare_strategies(
    configs=strategies,
    timeframe='1h',
    days=30
)

# 保存结果
backtester.save_results(results)
```

#### 3. 查看结果

```python
# 结果按总收益排序
for i, result in enumerate(results, 1):
    print(f"\n第 {i} 名: {result.config.name}")
    print(f"  总收益: {result.total_return:.2f} USDT ({result.total_return_pct:.2f}%)")
    print(f"  胜率: {result.win_rate*100:.2f}%")
    print(f"  夏普比率: {result.sharpe_ratio:.2f}")
    print(f"  最大回撤: {result.max_drawdown_pct:.2f}%")
```

### 对比指标

#### 基本指标

- **总交易次数** - 回测期间的交易总数
- **盈利交易** - 盈利的交易数量
- **亏损交易** - 亏损的交易数量
- **胜率** - 盈利交易占比

#### 收益指标

- **总收益** - 绝对收益金额（USDT）
- **收益率** - 相对初始资金的百分比
- **平均盈利** - 每笔盈利交易的平均金额
- **平均亏损** - 每笔亏损交易的平均金额

#### 风险指标

- **夏普比率** - 风险调整后收益（越高越好）
- **最大回撤** - 从峰值到谷底的最大跌幅
- **盈利因子** - 总盈利/总亏损（>1为盈利）

### 可视化组件

#### 在Dashboard中使用

```typescript
import { StrategyComparison } from '@/components/StrategyComparison';

function BacktestPage() {
  const [results, setResults] = useState([]);

  // 加载回测结果
  useEffect(() => {
    fetch('/api/strategy-comparison')
      .then(res => res.json())
      .then(data => setResults(data.results));
  }, []);

  return (
    <div>
      <h1>策略对比</h1>
      <StrategyComparison results={results} />
    </div>
  );
}
```

#### 功能特性

1. **策略选择** - 点击策略卡片选择/取消选择
2. **收益曲线** - 多条曲线同时显示，颜色区分
3. **指标对比表** - 并排对比所有关键指标
4. **最佳标记** - 自动标记收益最高的策略

---

## 使用示例

### 完整测试流程

```python
#!/usr/bin/env python3
"""
完整测试流程示例
演示如何使用测试模式、风险管理和策略对比
"""

from test_mode import get_test_config, get_simulated_exchange
from risk_manager import RiskManager
from strategy_comparison import StrategyBacktester, StrategyConfig

# 1. 启用测试模式
print("=== 步骤1: 启用测试模式 ===")
config = get_test_config()
config.enable()

# 2. 创建模拟交易所和风险管理器
print("\n=== 步骤2: 初始化组件 ===")
exchange = get_simulated_exchange()
risk_manager = RiskManager()

# 3. 查看初始状态
print("\n=== 步骤3: 初始状态 ===")
balance = exchange.get_balance()
print(f"初始余额: {balance['total']} USDT")

# 4. 模拟交易
print("\n=== 步骤4: 模拟交易 ===")
for i in range(3):
    # 检查风险
    allowed, reason = risk_manager.check_risk(50000, balance['total'])
    if not allowed:
        print(f"风险控制触发: {reason}")
        break
    
    # 创建订单
    result = exchange.create_order('XBTUSDTM', 'buy', 0.001, 50000)
    if result['success']:
        print(f"订单 {i+1}: 创建成功")
        
        # 模拟价格变动后平仓
        new_price = 50000 + (i - 1) * 500  # 第一笔亏，后两笔盈
        close_result = exchange.close_position(
            result['position']['position_id'],
            new_price
        )
        
        if close_result['success']:
            pnl = close_result['trade']['net_pnl']
            print(f"  平仓盈亏: {pnl:.2f} USDT")
            risk_manager.record_trade(pnl, pnl > 0)

# 5. 查看最终状态
print("\n=== 步骤5: 最终状态 ===")
final_balance = exchange.get_balance()
print(f"最终余额: {final_balance['total']:.2f} USDT")

risk_status = risk_manager.get_risk_status()
print(f"总盈亏: {risk_status['total_pnl']:.2f} USDT")
print(f"连续亏损: {risk_status['consecutive_losses']}")

# 6. 策略对比回测
print("\n=== 步骤6: 策略对比回测 ===")
backtester = StrategyBacktester(symbol='BTC/USDT', initial_capital=100.0)

strategies = [
    StrategyConfig('保守型', {'ma_short': 5, 'ma_long': 20, 'position_size': 0.1}),
    StrategyConfig('激进型', {'ma_short': 3, 'ma_long': 15, 'position_size': 0.2})
]

results = backtester.compare_strategies(strategies, timeframe='1h', days=7)

print("\n✅ 测试流程完成！")
```

---

## 常见问题

### Q1: 如何在测试模式和实盘模式之间切换？

**A:** 使用配置管理：

```python
from test_mode import get_test_config

config = get_test_config()

# 启用测试模式
config.enable()

# 禁用测试模式（切换到实盘）
config.disable()
```

### Q2: 测试模式的数据会影响实盘吗？

**A:** 不会。测试模式的所有数据都保存在独立的文件中：

- 配置：`scripts/test_mode_config.json`
- 状态：`scripts/test_mode_state.json`

与实盘数据完全隔离。

### Q3: WebSocket连接不上怎么办？

**A:** 检查以下几点：

1. 确认WebSocket服务已启动：
   ```bash
   python3 scripts/websocket_pusher.py
   ```

2. 检查端口是否被占用：
   ```bash
   netstat -an | grep 8765
   ```

3. 确认防火墙设置允许8765端口

4. 检查前端配置的WebSocket URL是否正确

### Q4: 如何保存策略回测结果？

**A:** 回测结果会自动保存：

```python
# 自动保存到 scripts/strategy_comparison.json
backtester.save_results(results)

# 或指定文件名
backtester.save_results(results, filename='my_backtest.json')
```

### Q5: 可以同时运行多个回测吗？

**A:** 可以，但需要注意：

- 回测会调用API获取历史数据
- 请遵守交易所的API限制
- 建议使用缓存避免重复请求

### Q6: 测试模式支持哪些交易对？

**A:** 测试模式支持任何交易对，因为它是完全模拟的。但建议使用与实盘相同的交易对进行测试，以保证参数的一致性。

---

## 技术支持

如有问题，请参考：

1. **主文档：** `INTEGRATED_SYSTEM_GUIDE.md`
2. **风险管理：** `RISK_MANAGEMENT_GUIDE.md`
3. **Windows部署：** `WINDOWS_部署教程.md`
4. **Python集成：** `PYTHON_INTEGRATION.md`

---

**祝您测试顺利，策略优化成功！** 🚀
