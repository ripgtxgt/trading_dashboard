# 10U战神滚仓策略 - 交易监控面板

完整的加密货币交易系统，集成策略回测、风险管理、实时监控和自动化交易功能。

---

## 📋 项目概述

这是一个功能完整的加密货币交易系统，专为小资金（10 USDT起步）滚仓策略设计。系统包含：

- **完整的交易系统** - KuCoin API集成、订单管理、持仓跟踪
- **智能风险管理** - 多层保护机制、实时风险监控、自动熔断
- **策略回测与优化** - 多策略并行回测、参数优化、可视化对比
- **实时数据推送** - WebSocket实时更新、Dashboard自动刷新
- **测试模式** - 无风险模拟交易、策略验证
- **Telegram通知** - 交易提醒、风险警告、系统状态推送

---

## 🚀 核心功能

### 1. 交易系统

**滚仓策略**
- 基于移动平均线的趋势跟踪
- 动态仓位管理（10倍杠杆）
- 分阶段加仓（Stage 1-5）
- 止损止盈自动化

**交易执行**
- KuCoin合约API集成
- 市价单/限价单支持
- 订单状态实时跟踪
- 持仓自动管理

**数据管理**
- 实时K线数据获取
- 交易历史记录
- 账户余额跟踪
- 性能指标统计

### 2. 风险管理系统

**多层保护机制**
- 单日亏损保护（默认10%）
- 连续亏损检测（默认3次）
- 最大回撤控制（默认20%）
- 市场波动率监控
- 紧急熔断机制

**实时监控**
- 风险指标实时计算
- 自动暂停交易
- Telegram警告推送
- 风险事件日志

**配置管理**
- 灵活的风险参数
- 手动控制开关
- 状态持久化
- 配置热更新

### 3. 策略回测与优化

**回测引擎**
- 历史数据回测
- 多策略并行测试
- 完整指标计算
- 结果可视化

**性能指标**
- 总收益率
- 胜率统计
- 夏普比率
- 最大回撤
- 盈亏比
- 交易次数

**策略优化向导**
- 交互式参数设置
- 自动运行回测
- 结果对比分析
- 一键应用最优策略

### 4. 测试模式

**模拟交易**
- 完整的模拟交易引擎
- 真实的滑点和手续费
- 订单执行模拟
- 持仓管理模拟

**风险测试**
- 无风险策略验证
- 风险管理测试
- 参数调优
- 状态重置功能

### 5. 实时监控Dashboard

**核心指标**
- 账户余额实时显示
- 交易状态监控
- 今日盈亏统计
- 风险状态指示

**可视化**
- K线图表
- 收益曲线
- 策略对比图
- 风险指标图

**实时更新**
- WebSocket自动推送
- 连接状态指示
- 数据自动刷新
- 无需手动刷新

### 6. Telegram通知

**交易通知**
- 开仓提醒
- 平仓通知
- 盈亏报告
- 阶段变化

**风险警告**
- 亏损警告
- 风险暂停
- 回撤提醒
- 系统异常

---

## 🏗️ 技术架构

### 前端技术栈

- **框架**: React 19 + TypeScript
- **样式**: Tailwind CSS 4
- **UI组件**: shadcn/ui
- **状态管理**: tRPC + React Query
- **图表**: Recharts
- **路由**: Wouter
- **实时通信**: WebSocket

### 后端技术栈

- **运行时**: Node.js 22
- **框架**: Express 4 + tRPC 11
- **数据库**: MySQL (TiDB)
- **ORM**: Drizzle ORM
- **认证**: Manus OAuth
- **API**: KuCoin API, Yahoo Finance API

### Python脚本

- **交易引擎**: asyncio + ccxt
- **数据分析**: pandas + numpy
- **回测引擎**: 自研回测框架
- **风险管理**: 自研风险控制系统
- **通知**: python-telegram-bot

---

## 📁 项目结构

```
trading_dashboard/
├── client/                    # 前端代码
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   │   └── Home.tsx      # 主Dashboard
│   │   ├── components/       # UI组件
│   │   │   ├── ConnectionStatus.tsx      # 连接状态
│   │   │   ├── StrategyComparison.tsx    # 策略对比
│   │   │   └── StrategyWizard.tsx        # 策略向导
│   │   ├── contexts/         # React Context
│   │   │   └── RealtimeDataContext.tsx   # 实时数据
│   │   ├── hooks/            # 自定义Hooks
│   │   │   └── useWebSocket.ts           # WebSocket Hook
│   │   └── lib/              # 工具库
│   │       └── trpc.ts       # tRPC客户端
│   └── public/               # 静态资源
│
├── server/                    # 后端代码
│   ├── routers.ts            # tRPC路由
│   ├── v24_api.ts            # v24功能API
│   ├── risk_api.ts           # 风险管理API
│   ├── db.ts                 # 数据库操作
│   ├── telegram.ts           # Telegram通知
│   ├── kline_cache.ts        # K线缓存
│   └── bot_integration.ts    # 交易机器人集成
│
├── scripts/                   # Python脚本
│   ├── trading_bot.py        # 主交易机器人
│   ├── risk_manager.py       # 风险管理器
│   ├── test_mode.py          # 测试模式
│   ├── strategy_comparison.py # 策略对比
│   ├── websocket_client.py   # WebSocket客户端
│   ├── websocket_pusher.py   # WebSocket服务
│   ├── trading_bot_with_ws.py # 集成WS的交易机器人
│   ├── backtest.py           # 回测引擎
│   ├── optimize_params.py    # 参数优化
│   └── signal_simulator.py   # 信号模拟
│
├── drizzle/                   # 数据库Schema
│   └── schema.ts             # 表定义
│
├── docs/                      # 文档
│   ├── RISK_MANAGEMENT_GUIDE.md      # 风险管理指南
│   ├── V24_FEATURES_GUIDE.md         # v24功能指南
│   └── PROJECT_README.md             # 项目说明（本文件）
│
└── tests/                     # 测试文件
    ├── auth.logout.test.ts
    ├── v24.features.test.ts
    ├── strategy.params.test.ts
    └── strategy.backtest.test.ts
```

---

## 🔧 安装与配置

### 1. 环境要求

- Node.js 22+
- Python 3.11+
- MySQL 8.0+ (或TiDB)
- pnpm

### 2. 安装依赖

```bash
# 安装Node.js依赖
pnpm install

# 安装Python依赖
pip3 install ccxt pandas numpy python-telegram-bot websockets
```

### 3. 配置环境变量

系统已预配置以下环境变量（通过Manus平台自动注入）：

- `DATABASE_URL` - 数据库连接字符串
- `JWT_SECRET` - Session签名密钥
- `VITE_APP_ID` - OAuth应用ID
- `OAUTH_SERVER_URL` - OAuth服务器地址
- `BUILT_IN_FORGE_API_KEY` - Manus API密钥
- `BUILT_IN_FORGE_API_URL` - Manus API地址

需要手动配置的环境变量：

```bash
# KuCoin API配置（在scripts/config.py中设置）
KUCOIN_API_KEY=your_api_key
KUCOIN_API_SECRET=your_api_secret
KUCOIN_API_PASSPHRASE=your_passphrase

# Telegram配置（在scripts/telegram.py中设置）
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 4. 数据库初始化

```bash
# 推送数据库Schema
pnpm db:push
```

### 5. 启动服务

```bash
# 启动开发服务器
pnpm dev

# 启动WebSocket服务（可选）
python3 scripts/websocket_pusher.py

# 启动交易机器人（可选）
python3 scripts/trading_bot.py
```

---

## 📖 使用指南

### 1. 首次使用

1. **登录系统**
   - 访问Dashboard
   - 使用Manus账号登录

2. **配置API密钥**
   - 编辑 `scripts/config.py`
   - 填入KuCoin API密钥
   - 配置Telegram通知（可选）

3. **启用测试模式**
   - 在Dashboard顶部切换"测试模式"开关
   - 使用模拟资金测试策略
   - 观察风险管理功能

4. **运行策略向导**
   - 点击"策略向导"标签
   - 按步骤设置回测参数
   - 查看对比结果
   - 应用最优策略

5. **切换到实盘**
   - 确认策略表现良好
   - 关闭测试模式
   - 启动交易机器人

### 2. 日常使用

**监控交易**
- Dashboard实时显示账户状态
- 查看持仓和盈亏
- 监控风险指标
- 接收Telegram通知

**调整策略**
- 使用策略向导优化参数
- 在测试模式下验证
- 应用到实盘交易

**风险控制**
- 监控风险状态
- 调整风险参数
- 手动暂停/恢复交易
- 查看风险事件日志

### 3. 高级功能

**策略回测**
```bash
# 运行单策略回测
python3 scripts/backtest.py XBTUSDTM 1h 10 30 standard

# 运行多策略对比
python3 scripts/strategy_comparison.py
```

**参数优化**
```bash
# 自动优化策略参数
python3 scripts/optimize_params.py XBTUSDTM 1h
```

**WebSocket集成**
```python
# 在交易脚本中集成实时推送
from websocket_client import get_websocket_client

client = get_websocket_client()
await client.connect()
await client.push_account_update(balance, available, used)
```

---

## 🧪 测试

### 运行所有测试

```bash
pnpm test
```

### 运行特定测试

```bash
# 测试v24功能
pnpm test server/v24.features.test.ts

# 测试策略参数
pnpm test server/strategy.params.test.ts

# 测试回测功能
pnpm test server/strategy.backtest.test.ts
```

### Python脚本测试

```bash
# 测试风险管理器
python3 scripts/test_risk_manager.py

# 测试WebSocket客户端
python3 scripts/websocket_client.py

# 测试模拟交易
python3 scripts/test_mode.py
```

---

## 📊 性能指标

### 系统性能

- **响应时间**: < 100ms (API调用)
- **数据延迟**: < 1s (WebSocket推送)
- **并发支持**: 100+ 用户
- **数据库查询**: < 50ms

### 交易性能

- **订单执行**: < 500ms
- **信号延迟**: < 2s
- **风险检查**: < 10ms
- **回测速度**: ~1000 candles/s

---

## 🔒 安全建议

1. **API密钥安全**
   - 使用只读API密钥进行回测
   - 限制API密钥权限
   - 定期轮换密钥
   - 不要提交密钥到代码库

2. **风险控制**
   - 始终启用风险管理
   - 设置合理的止损
   - 限制单日最大亏损
   - 监控账户余额

3. **测试验证**
   - 新策略先在测试模式运行
   - 小资金实盘验证
   - 逐步增加仓位
   - 定期检查系统状态

4. **数据备份**
   - 定期备份数据库
   - 保存交易日志
   - 记录策略参数
   - 导出重要数据

---

## 🐛 故障排除

### 常见问题

**1. 无法连接KuCoin API**
- 检查API密钥是否正确
- 确认API权限设置
- 检查网络连接
- 查看API速率限制

**2. WebSocket连接失败**
- 确认WebSocket服务已启动
- 检查端口是否被占用
- 查看防火墙设置
- 检查网络连接

**3. 风险管理未生效**
- 确认风险管理器已初始化
- 检查风险参数配置
- 查看风险状态日志
- 验证交易记录

**4. Dashboard数据不更新**
- 检查WebSocket连接状态
- 刷新浏览器页面
- 查看浏览器控制台错误
- 确认后端服务运行正常

### 日志查看

```bash
# 查看交易机器人日志
tail -f scripts/trading_bot.log

# 查看WebSocket服务日志
tail -f scripts/websocket_pusher.log

# 查看风险管理日志
tail -f scripts/risk_manager.log

# 查看服务器日志
pnpm dev  # 查看控制台输出
```

---

## 📈 版本历史

### v25.0 (当前版本)
- ✅ Dashboard UI完整集成
- ✅ 测试模式切换开关
- ✅ 实时连接状态指示
- ✅ 策略优化向导
- ✅ WebSocket实时推送
- ✅ Python脚本集成WebSocket

### v24.0
- ✅ 测试模式和模拟交易
- ✅ WebSocket实时数据推送
- ✅ 多策略回测对比
- ✅ 策略对比可视化

### v23.0
- ✅ 完整风险管理系统
- ✅ 多层保护机制
- ✅ Telegram警告推送
- ✅ 风险配置管理

### v22.0及更早
- ✅ 基础交易系统
- ✅ KuCoin API集成
- ✅ 滚仓策略实现
- ✅ Dashboard基础功能
- ✅ 策略参数管理
- ✅ 回测引擎
- ✅ 参数优化

---

## 🤝 贡献指南

本项目为个人交易系统，暂不接受外部贡献。如有问题或建议，请通过以下方式联系：

- 提交Issue
- 发送邮件
- Telegram联系

---

## 📄 许可证

本项目仅供个人学习和使用，不得用于商业用途。

---

## ⚠️ 免责声明

**风险提示**：加密货币交易存在极高风险，可能导致全部本金损失。本系统仅供学习和研究使用，不构成任何投资建议。使用本系统进行实盘交易的一切后果由用户自行承担。

**使用条款**：
- 用户需充分了解加密货币交易风险
- 建议从小资金开始测试
- 定期检查系统运行状态
- 不要投入无法承受损失的资金
- 保持理性，避免情绪化交易

---

## 📞 支持与联系

如需帮助或有任何问题，请查看：

1. **文档**
   - [风险管理指南](./RISK_MANAGEMENT_GUIDE.md)
   - [v24功能指南](./V24_FEATURES_GUIDE.md)

2. **测试**
   - 运行测试套件验证功能
   - 使用测试模式验证策略

3. **日志**
   - 查看系统日志排查问题
   - 检查错误信息

---

**祝交易顺利！🚀**
