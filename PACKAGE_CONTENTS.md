# 项目打包清单

## 📦 打包信息

- **版本**: v33.2
- **打包时间**: 2024-11-24
- **文件名**: trading_dashboard_v33.2_windows_deployment.tar.gz
- **修复**: 批处理文件编码问题（移除中文字符，使用纯ASCII）
- **适用系统**: Windows Server 2022 / Windows 10/11

---

## 📂 目录结构

```
trading_dashboard/
├── client/                    # 前端代码
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # UI组件
│   │   ├── contexts/         # React上下文
│   │   ├── hooks/            # 自定义Hooks
│   │   └── lib/              # 工具库
│   └── public/               # 静态资源
│
├── server/                    # 后端代码
│   ├── api/                  # API路由
│   ├── db.ts                 # 数据库操作
│   └── routers.ts            # tRPC路由
│
├── scripts/                   # Python脚本
│   ├── kucoin_api.py         # KuCoin交易API
│   ├── rolling_manager.py    # 滚仓管理
│   ├── risk_manager.py       # 风险管理
│   ├── volatility_monitor.py # 波动率监控
│   ├── auto_pause_manager.py # 自动暂停
│   ├── db_integration.py     # 数据库集成
│   ├── websocket_pusher.py   # WebSocket推送
│   ├── telegram_bot.py       # Telegram Bot
│   ├── requirements.txt      # Python依赖
│   ├── check_windows_environment.ps1  # 环境检测
│   └── deploy_windows.ps1    # 自动部署
│
├── drizzle/                   # 数据库Schema
│   └── schema.prisma         # 数据库表定义
│
├── 批处理文件 (双击运行)
│   ├── check_environment.bat # 环境检测
│   ├── deploy.bat            # 自动部署
│   ├── start_all.bat         # 启动所有服务
│   ├── start_trading_bot.bat # 启动交易机器人
│   └── stop_all.bat          # 停止所有服务
│
├── 配置文件
│   ├── .env.example          # 环境变量示例
│   ├── ecosystem.config.js   # PM2配置
│   ├── package.json          # Node.js依赖
│   └── tsconfig.json         # TypeScript配置
│
└── 文档
    ├── README.md             # 项目说明
    ├── QUICK_START.md        # 快速开始指南
    ├── WINDOWS_SERVER_DEPLOYMENT.md  # 详细部署指南
    ├── TELEGRAM_SETUP_GUIDE.md       # Telegram配置
    ├── WINDOWS_DEPLOYMENT_GUIDE.md   # Windows部署指南
    └── PACKAGE_CONTENTS.md   # 本文件
```

---

## 🚀 快速开始

### 1. 解压文件

将 `trading_dashboard_v33.1_windows_deployment.tar.gz` 解压到 `C:\trading_dashboard`

**Windows解压工具**：
- 7-Zip (推荐): https://www.7-zip.org/
- WinRAR: https://www.winrar.com/

### 2. 检测环境

双击运行：`check_environment.bat`

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，填入配置

### 4. 一键部署

右键点击 `deploy.bat`，选择 "以管理员身份运行"

### 5. 访问系统

浏览器打开：`http://localhost:3000`

---

## 📋 核心功能

### Web Dashboard
- ✅ 实时账户状态监控
- ✅ 交易历史记录
- ✅ 资金曲线图表
- ✅ 风险管理面板
- ✅ 策略参数配置
- ✅ 性能分析报告

### 交易系统
- ✅ 10U战神滚仓策略
- ✅ 自动开平仓
- ✅ 动态仓位调整
- ✅ 止盈止损控制

### 风险管理
- ✅ 波动率实时监控
- ✅ 自动暂停机制
- ✅ 四级风险评估
- ✅ 仓位动态调整
- ✅ 亏损保护机制

### 实时通信
- ✅ WebSocket实时推送
- ✅ Telegram通知
- ✅ 风险警报

---

## 🔧 系统要求

### 必需软件
- Windows Server 2019/2022 或 Windows 10/11
- Node.js 18.x 或更高
- Python 3.8 或更高
- MySQL 5.7 或更高
- PM2 (通过npm安装)

### 硬件要求
- CPU: 2核心或以上
- 内存: 4GB 或以上
- 硬盘: 20GB 可用空间

---

## 📚 文档说明

### QUICK_START.md
最简化的部署步骤，适合快速上手

### WINDOWS_SERVER_DEPLOYMENT.md
完整的部署指南，包含：
- 详细的安装步骤
- 环境配置说明
- 常见问题解决
- 维护管理指南
- 性能优化建议
- 安全配置建议

### TELEGRAM_SETUP_GUIDE.md
Telegram Bot配置图文教程

---

## 🔑 重要配置

### KuCoin API
需要在KuCoin官网创建API密钥：
1. 登录 https://www.kucoin.com/
2. 进入 API Management
3. 创建新的API Key
4. 权限：General + Trade（不要开启Transfer和Withdraw）

### 数据库
需要创建MySQL数据库：
```sql
CREATE DATABASE trading_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Telegram (可选但推荐)
用于接收交易通知和风险警报

---

## ⚠️ 注意事项

1. **不要在生产环境中开启KuCoin API的提现权限**
2. **请务必设置合理的止损止盈参数**
3. **建议先在测试模式下运行，验证策略**
4. **定期备份数据库和配置文件**
5. **启用Telegram通知以便及时了解交易状态**

---

## 🆘 获取帮助

遇到问题请按以下顺序排查：

1. 查看 `QUICK_START.md` 快速开始指南
2. 查看 `WINDOWS_SERVER_DEPLOYMENT.md` 详细部署指南
3. 运行 `check_environment.bat` 检测环境
4. 查看日志：`pm2 logs`
5. 重启服务：`pm2 restart all`

---

## 📝 版本历史

### v33.2 (2024-11-24)
- ✅ 修复批处理文件编码问题
- ✅ 移除所有中文字符，使用纯ASCII
- ✅ 确保在Windows上正常运行

### v33.1 (2024-11-24)
- ✅ 修复PowerShell脚本双击运行问题
- ✅ 创建批处理包装器文件
- ✅ 创建快速开始指南
- ✅ 优化部署流程

### v33.0 (2024-11-24)
- ✅ 完整的Windows Server 2022部署方案
- ✅ 环境检测脚本
- ✅ 自动化部署脚本
- ✅ PM2配置和开机自启

### v32.0
- ✅ 风险管理真实数据集成
- ✅ 数据库表结构完善

### v31.0
- ✅ 风险管理UI和通知完善
- ✅ Dashboard集成风险监控

### v30.0
- ✅ 增强风险管理模块
- ✅ 波动率实时监控
- ✅ 动态仓位调整

---

**祝您使用愉快！** 🎉
