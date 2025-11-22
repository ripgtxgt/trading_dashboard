# 生产部署指南

本文档详细说明如何将10U战神滚仓策略交易监控面板部署到生产环境。

## 部署前检查清单

### 1. 环境要求

- [x] Node.js 22.x 或更高版本
- [x] Python 3.11 或更高版本
- [x] MySQL 8.0 或 TiDB Cloud 数据库
- [x] 稳定的网络连接（用于访问KuCoin API）

### 2. 必需的环境变量

以下环境变量已由Manus平台自动注入，无需手动配置：

```bash
# 数据库连接
DATABASE_URL=mysql://user:pass@host:port/dbname

# OAuth认证
JWT_SECRET=<自动生成>
OAUTH_SERVER_URL=<平台提供>
VITE_OAUTH_PORTAL_URL=<平台提供>
VITE_APP_ID=<平台提供>

# 应用配置
VITE_APP_TITLE=10U战神滚仓策略
VITE_APP_LOGO=<默认logo>

# Manus内置服务
BUILT_IN_FORGE_API_URL=<平台提供>
BUILT_IN_FORGE_API_KEY=<平台提供>
VITE_FRONTEND_FORGE_API_KEY=<平台提供>
```

### 3. 可选的环境变量

如需使用Telegram通知功能，需要在Management UI的Settings → Secrets中添加：

```bash
TELEGRAM_BOT_TOKEN=<你的Telegram Bot Token>
TELEGRAM_CHAT_ID=<你的Telegram Chat ID>
```

## 部署步骤

### 方法一：通过Manus Management UI部署（推荐）

1. **保存Checkpoint**
   - 确保所有代码更改已保存
   - 系统会自动创建checkpoint

2. **发布项目**
   - 点击Management UI右上角的"Publish"按钮
   - 系统会自动构建并部署项目
   - 部署完成后会获得一个公开访问URL

3. **配置自定义域名（可选）**
   - 进入Management UI → Settings → Domains
   - 修改自动生成的域名前缀（xxx.manus.space）
   - 或绑定自己的自定义域名

4. **配置Telegram通知（可选）**
   - 进入Management UI → Settings → Secrets
   - 添加`TELEGRAM_BOT_TOKEN`和`TELEGRAM_CHAT_ID`
   - 保存后重启应用

### 方法二：本地构建部署

```bash
# 1. 安装依赖
pnpm install

# 2. 构建生产版本
pnpm build

# 3. 启动生产服务器
pnpm start
```

## 运行Python交易机器人

### 1. 安装Python依赖

```bash
pip3 install mysql-connector-python requests
```

### 2. 配置数据库连接

从Management UI → Settings → Database获取完整的数据库连接信息，然后设置环境变量：

```bash
export DATABASE_URL="mysql://user:pass@host:port/dbname?ssl=true"
```

### 3. 运行交易机器人

```bash
cd scripts
python3 trading_example_full.py
```

### 4. 后台运行（推荐）

使用`screen`或`tmux`在后台运行：

```bash
# 使用screen
screen -S trading_bot
python3 scripts/trading_example_full.py
# 按 Ctrl+A 然后按 D 退出screen

# 重新连接
screen -r trading_bot
```

或使用`nohup`：

```bash
nohup python3 scripts/trading_example_full.py > trading.log 2>&1 &
```

### 5. 监控机器人状态

通过Web界面实时监控：
- 访问部署的URL
- 查看Dashboard页面
- 实时信号会通过WebSocket推送到前端

## 数据库管理

### 访问数据库

1. 进入Management UI → Database
2. 使用内置的CRUD界面管理数据
3. 或使用底部的连接信息通过MySQL客户端连接

### 数据库备份

```bash
# 导出数据
mysqldump -h <host> -P <port> -u <user> -p <database> > backup.sql

# 导入数据
mysql -h <host> -P <port> -u <user> -p <database> < backup.sql
```

## 安全建议

### 1. 数据库安全

- ✅ 已启用SSL连接（TiDB Cloud默认）
- ✅ 使用强密码
- ✅ 限制数据库访问IP（在TiDB Cloud控制台配置）

### 2. API密钥安全

- ✅ 所有敏感配置通过环境变量管理
- ✅ 不要在代码中硬编码API密钥
- ✅ 使用Management UI的Secrets功能管理密钥

### 3. 应用安全

- ✅ OAuth认证已集成
- ✅ 仅项目owner可以访问管理功能
- ✅ WebSocket连接需要认证

## 性能优化

### 1. K线数据缓存

系统已实现K线数据缓存机制：
- 缓存时间：60秒
- 自动增量更新
- 减少API调用频率

### 2. 数据库查询优化

- 使用索引加速查询
- 限制返回结果数量
- 定期清理历史数据

### 3. WebSocket连接

- 自动重连机制
- 心跳检测
- 消息队列缓冲

## 监控和日志

### 1. 应用日志

查看服务器日志：
```bash
# 查看最近的日志
tail -f logs/app.log

# 查看Python机器人日志
tail -f trading.log
```

### 2. 数据库监控

- 进入Management UI → Dashboard
- 查看UV/PV统计
- 监控数据库连接状态

### 3. 交易监控

- 实时资金曲线
- 交易胜率统计
- 风险控制指标
- 实时信号推送

## 故障排查

### 问题1：数据库连接失败

**症状**：应用无法连接到数据库

**解决方案**：
1. 检查`DATABASE_URL`环境变量是否正确
2. 确认数据库服务器可访问
3. 检查SSL证书配置
4. 查看Management UI → Database的连接信息

### 问题2：WebSocket连接断开

**症状**：实时信号无法接收

**解决方案**：
1. 检查浏览器控制台错误
2. 确认WebSocket服务正常运行
3. 检查防火墙设置
4. 刷新页面重新连接

### 问题3：Python机器人无法运行

**症状**：交易机器人启动失败

**解决方案**：
1. 检查Python依赖是否安装
2. 确认`DATABASE_URL`环境变量已设置
3. 查看错误日志
4. 验证数据库表结构

### 问题4：K线数据获取失败

**症状**：图表无数据显示

**解决方案**：
1. 检查网络连接
2. 验证KuCoin API可访问性
3. 查看浏览器控制台错误
4. 系统会自动回退到模拟数据

## 升级和维护

### 代码更新

1. 在本地修改代码
2. 测试功能正常
3. 保存checkpoint
4. 点击Publish按钮重新部署

### 数据库迁移

```bash
# 推送schema更改
pnpm db:push

# 查看迁移历史
pnpm db:studio
```

### 回滚版本

1. 进入Management UI
2. 找到之前的checkpoint
3. 点击"Rollback"按钮
4. 系统会自动恢复到该版本

## 成本估算

### Manus平台费用

- 基础托管：免费
- 数据库：TiDB Cloud免费套餐
- 流量：根据实际使用计费

### 第三方服务

- KuCoin API：免费
- Telegram Bot：免费
- 自定义域名：可选（约$10-15/年）

## 技术支持

如遇到问题，请访问：
- Manus帮助中心：https://help.manus.im
- 项目文档：README.md
- Python集成文档：PYTHON_INTEGRATION.md

## 附录

### A. 完整的环境变量列表

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| DATABASE_URL | 数据库连接字符串 | ✅ | - |
| JWT_SECRET | JWT签名密钥 | ✅ | 自动生成 |
| TELEGRAM_BOT_TOKEN | Telegram Bot Token | ❌ | - |
| TELEGRAM_CHAT_ID | Telegram Chat ID | ❌ | - |
| NODE_ENV | 运行环境 | ✅ | production |

### B. 数据库表结构

主要表：
- `users` - 用户信息
- `bot_state` - 机器人状态
- `trades` - 交易记录
- `balance_history` - 资金历史
- `strategy_params` - 策略参数
- `backtest_history` - 回测历史（v19.0新增）

### C. API端点

- `/api/trpc/*` - tRPC API
- `/api/oauth/callback` - OAuth回调
- `/api/signal` - 信号推送接收
- `/api/socket.io` - WebSocket连接

### D. 推荐的监控指标

- 应用响应时间
- 数据库查询性能
- WebSocket连接数
- 交易信号频率
- 资金变化趋势
- 胜率和收益率
