# 10U战神滚仓策略 - 交易监控面板

完整的Web交易监控系统，用于管理和监控加密货币滚仓交易策略。

## 功能特性

### 核心功能
- ✅ **实时交易监控**：显示当前资金、盈亏、阶段等关键指标
- ✅ **策略参数调整**：可视化调整MA周期、时间框架和信号灵敏度
- ✅ **参数回测分析**：基于历史数据测试不同参数的胜率和收益
- ✅ **AI参数优化**：自动推荐最优参数组合
- ✅ **参数对比分析**：对比多组参数的回测表现
- ✅ **交易历史可视化**：累计盈亏曲线和交易统计
- ✅ **风险控制面板**：实时监控回撤、连续亏损和仓位风险
- ✅ **机器人控制**：Web界面启动/停止Python交易脚本
- ✅ **移动端适配**：响应式设计支持手机访问

### Python脚本集成
- ✅ **数据库同步模块**：`scripts/db_sync.py` 提供MySQL数据同步
- ✅ **交易数据写入**：自动记录开仓、平仓、持仓信息
- ✅ **状态实时更新**：同步资金、盈亏、阶段等状态
- ✅ **余额历史记录**：定期保存余额快照用于图表显示

## 技术栈

### 前端
- React 19 + TypeScript
- Tailwind CSS 4
- tRPC 11（类型安全的API调用）
- Recharts（图表可视化）
- shadcn/ui（UI组件库）

### 后端
- Express 4
- tRPC 11
- Drizzle ORM
- MySQL/TiDB
- Python 3（交易脚本）

### 数据源
- KuCoin API（K线数据）
- Yahoo Finance API（股票数据，用于回测）

## 快速开始

### 1. 解压项目

```bash
tar -xzf trading_dashboard_complete.tar.gz
cd trading_dashboard
```

### 2. 安装依赖

```bash
pnpm install
```

### 3. 配置环境变量

项目已包含 `.env` 文件，包含所有必要的环境变量：
- `DATABASE_URL`: MySQL数据库连接
- `JWT_SECRET`: 会话加密密钥
- `VITE_APP_TITLE`: 应用标题
- 其他Manus平台自动注入的变量

### 4. 初始化数据库

```bash
pnpm db:push
```

### 5. 启动开发服务器

```bash
pnpm dev
```

访问 `http://localhost:3000` 查看应用。

## Python交易脚本集成

### 安装Python依赖

```bash
pip3 install mysql-connector-python requests
```

### 快速开始 - 运行完整示例

我们提供了一个完整的交易机器人示例，可以直接运行：

```bash
# 设置数据库连接
export DATABASE_URL="mysql://user:pass@host:port/dbname"

# 运行示例脚本
cd scripts
python3 trading_example_full.py
```

这个示例展示了：
- 如何连接数据库
- 如何获取K线数据
- 如何计算MA指标和检测信号
- 如何开仓/平仓并记录到数据库
- 如何更新机器人状态

### 集成到你的交易脚本

参考 `PYTHON_INTEGRATION.md` 文档，将 `scripts/db_sync.py` 模块集成到你的交易脚本中。

基本步骤：

1. 导入数据库同步模块
```python
from db_sync import DatabaseSync

db = DatabaseSync()
db.connect()
```

2. 在交易循环中更新状态
```python
# 更新机器人状态
db.update_bot_state(
    is_running=1,
    capital=current_balance,
    initial_capital=INITIAL_CAPITAL,
    current_stage=current_stage,
    total_profit=current_balance - INITIAL_CAPITAL,
    total_trades=total_trades_count,
    win_trades=win_trades_count
)

# 开仓时创建交易记录
trade_id = db.create_trade(
    symbol="XBTUSDTM",
    side="long",
    entry_price=50000.0,
    quantity=0.001,
    leverage=10,
    stage="stage1"
)

# 平仓时关闭交易记录
db.close_trade(
    trade_id=trade_id,
    exit_price=51000.0,
    pnl=10.0,
    pnl_pct=0.02
)
```

详细文档请查看 `PYTHON_INTEGRATION.md`。

## 项目结构

```
trading_dashboard/
├── client/                 # 前端代码
│   ├── src/
│   │   ├── components/    # UI组件
│   │   │   ├── BalanceChart.tsx        # 余额曲线图
│   │   │   ├── ControlPanel.tsx        # 控制面板
│   │   │   ├── ParamsPanel.tsx         # 参数调整面板
│   │   │   ├── ParamsComparison.tsx    # 参数对比分析
│   │   │   ├── TradeHistory.tsx        # 交易历史
│   │   │   ├── RiskControlPanel.tsx    # 风险控制面板
│   │   │   └── ...
│   │   ├── pages/         # 页面组件
│   │   │   ├── Dashboard.tsx           # 主控制台
│   │   │   └── Home.tsx                # 首页
│   │   └── lib/           # 工具库
│   └── public/            # 静态资源
├── server/                # 后端代码
│   ├── routers.ts         # tRPC路由定义
│   ├── db.ts              # 数据库操作
│   ├── bot_integration.ts # 机器人控制API
│   └── _core/             # 核心框架代码
├── drizzle/               # 数据库schema
│   └── schema.ts          # 表结构定义
├── scripts/               # Python脚本
│   ├── db_sync.py         # 数据库同步模块
│   ├── signal_simulator.py # 信号模拟
│   ├── backtest.py        # 参数回测
│   └── optimize_params.py # 参数优化
├── PYTHON_INTEGRATION.md  # Python集成文档
└── README.md              # 本文档
```

## 数据库表结构

### bot_state（机器人状态）
- `isRunning`: 运行状态
- `capital`: 当前资金
- `initialCapital`: 初始资金
- `currentStage`: 当前阶段
- `totalProfit`: 总盈利
- `totalTrades`: 总交易次数
- `winTrades`: 盈利交易次数

### trades（交易记录）
- `symbol`: 交易对
- `side`: 方向（long/short）
- `entryPrice`: 入场价格
- `exitPrice`: 出场价格
- `quantity`: 数量
- `leverage`: 杠杆
- `pnl`: 盈亏金额
- `pnlPct`: 盈亏百分比
- `status`: 状态（open/closed）

### positions（当前持仓）
- `symbol`: 交易对
- `side`: 方向
- `entryPrice`: 入场价格
- `quantity`: 数量
- `leverage`: 杠杆
- `unrealizedPnl`: 未实现盈亏

### balance_history（余额历史）
- `balance`: 余额
- `timestamp`: 时间戳

### strategy_params（策略参数）
- `shortMaPeriod`: 短期MA周期
- `longMaPeriod`: 长期MA周期
- `timeframe`: 时间框架
- `sensitivity`: 信号灵敏度
- `isActive`: 是否激活

## API接口

### tRPC路由

#### trading.*
- `getState`: 获取机器人状态
- `getPosition`: 获取当前持仓
- `getTrades`: 获取交易历史
- `getBalanceHistory`: 获取余额历史

#### strategy.*
- `getActiveParams`: 获取激活的策略参数
- `getAllParams`: 获取所有策略参数
- `createParams`: 创建新参数
- `activateParams`: 激活参数
- `simulateSignals`: 模拟信号
- `backtestParams`: 回测参数
- `optimizeParams`: 优化参数

#### bot.*
- `getStatus`: 获取机器人状态
- `start`: 启动机器人
- `stop`: 停止机器人
- `getLogs`: 获取日志

## 开发指南

### 添加新功能

1. **数据库表**：在 `drizzle/schema.ts` 定义表结构
2. **数据库操作**：在 `server/db.ts` 添加查询函数
3. **API接口**：在 `server/routers.ts` 添加tRPC procedure
4. **UI组件**：在 `client/src/components/` 创建组件
5. **页面集成**：在 `client/src/pages/Dashboard.tsx` 引入组件

### 运行测试

```bash
pnpm test
```

### 构建生产版本

```bash
pnpm build
```

## 常见问题

### Q: 如何修改数据库连接？

A: 编辑 `.env` 文件中的 `DATABASE_URL`。

### Q: Python脚本如何连接数据库？

A: 设置环境变量：
```bash
export DATABASE_URL="mysql://user:pass@host:port/dbname"
python3 your_trading_script.py
```

### Q: 如何添加新的策略参数？

A: 
1. 在 `drizzle/schema.ts` 的 `strategyParams` 表添加字段
2. 运行 `pnpm db:push` 更新数据库
3. 在 `client/src/components/ParamsPanel.tsx` 添加UI控件

### Q: 如何自定义回测逻辑？

A: 修改 `scripts/backtest.py` 中的 `backtest_strategy` 函数。

## 部署

### 使用Manus平台

项目已配置为Manus Web项目，可以直接在Manus平台部署：

1. 在Management UI点击"Publish"按钮
2. 配置域名和环境变量
3. 等待部署完成

### 自行部署

1. 构建生产版本：`pnpm build`
2. 配置环境变量
3. 启动服务器：`pnpm start`
4. 配置Nginx反向代理

## 许可证

MIT License

## 联系方式

如有问题请通过Manus平台反馈。

---

**版本**: v16.0  
**最后更新**: 2025-11-22
# Auto-Deployment Test - 2025-11-27 02:16:29

This is a test commit to verify GitHub Actions auto-deployment.

## Auto-Deployment Test - 2025-11-27 02:53:41

✅ SSH connection successful
✅ Repository cloned to C:\trading_dashboard_fixed
✅ Testing GitHub Actions auto-deployment...
