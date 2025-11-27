# 部署工具说明

## 📦 文件清单

### 一键部署工具

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `DEPLOY.bat` | 批处理 | **主部署程序**，双击运行即可 |
| `deploy.ps1` | PowerShell | 部署主脚本，自动化所有步骤 |
| `quick-config.ps1` | PowerShell | 快速配置向导，生成.env文件 |
| `check-environment.ps1` | PowerShell | 环境检查工具 |

### 配置文件

| 文件名 | 说明 |
|--------|------|
| `ecosystem.config.cjs` | PM2服务配置 |
| `.env.example` | 环境变量模板 |
| `.env` | 环境变量配置（运行后生成） |

### 文档

| 文件名 | 说明 |
|--------|------|
| `README_WINDOWS_DEPLOY.md` | **Windows部署完整指南** |
| `DEPLOYMENT_INSTRUCTIONS.md` | 通用部署说明 |
| `DEPLOYMENT_TOOLS.md` | 本文件 |
| `FIXES_APPLIED.md` | 修复内容详情 |
| `TEST_REPORT.md` | 测试报告 |

---

## 🚀 使用流程

### 标准流程（推荐）

```
1. check-environment.ps1  → 检查环境
2. quick-config.ps1       → 配置参数
3. DEPLOY.bat             → 一键部署
```

### 快速流程（已配置环境）

```
直接运行 DEPLOY.bat
```

---

## 📋 工具详解

### 1. DEPLOY.bat - 主部署程序

**功能：**
- 自动请求管理员权限
- 调用PowerShell部署脚本
- 显示部署结果

**使用方法：**
```cmd
# 方式1：双击运行
DEPLOY.bat

# 方式2：命令行运行
.\DEPLOY.bat
```

**注意事项：**
- 会自动请求管理员权限
- 首次运行可能需要几分钟（下载依赖）
- 确保已配置.env文件

---

### 2. deploy.ps1 - 部署主脚本

**功能：**
- 检查管理员权限
- 检查Python、Node.js、MySQL环境
- 自动安装pnpm和PM2
- 安装Node.js和Python依赖
- 配置环境变量（交互式）
- 初始化数据库
- 启动所有服务

**使用方法：**
```powershell
# 以管理员身份运行PowerShell
.\deploy.ps1
```

**执行步骤：**
1. 环境检查
2. 依赖安装
3. 配置应用
4. 初始化数据库
5. 启动服务

**预期输出：**
```
✓ 管理员权限检查通过
✓ Python环境检查通过
✓ Node.js环境检查通过
✓ pnpm安装成功
✓ PM2安装成功
✓ Node.js依赖安装成功
✓ Python依赖安装成功
✓ 环境变量配置完成
✓ 数据库初始化成功
✓ 服务启动成功
```

---

### 3. quick-config.ps1 - 快速配置向导

**功能：**
- 交互式配置环境变量
- 自动生成.env文件
- 配置验证

**使用方法：**
```powershell
.\quick-config.ps1
```

**配置项：**

#### KuCoin API配置
- API Key（必填）
- API Secret（必填）
- API Passphrase（必填）
- 沙盒环境（可选，默认false）

#### 数据库配置
- 主机（默认localhost）
- 端口（默认3306）
- 用户名（默认trading）
- 密码（必填）
- 数据库名（默认trading_dashboard）

#### Telegram配置
- Bot Token（必填）
- Chat ID（必填）

#### 交易配置
- 杠杆倍数（默认100）
- 初始资金（默认10）

**输出：**
- 生成 `.env` 文件

---

### 4. check-environment.ps1 - 环境检查工具

**功能：**
- 检查Windows版本
- 检查Python版本（需要3.11+）
- 检查Node.js版本（需要v20+）
- 检查npm
- 检查pnpm（可选）
- 检查PM2（可选）
- 检查MySQL版本（需要8.0+）
- 检查Git（可选）

**使用方法：**
```powershell
.\check-environment.ps1
```

**输出示例：**
```
检查 Windows版本... ✓ 已安装 (Microsoft Windows Server 2022)
检查 Python... ✓ 已安装 (Python 3.11.0)
检查 Node.js... ✓ 已安装 (v22.0.0)
检查 npm... ✓ 已安装 (v10.0.0)
检查 pnpm... ✗ 未安装或版本过低
检查 PM2... ✗ 未安装或版本过低
检查 MySQL... ✓ 已安装 (v8.0.35)
检查 Git... ✓ 已安装 (v2.43.0)

✓ 所有必需组件已安装，可以开始部署！
```

---

## 🔧 故障排除

### PowerShell脚本无法运行

**问题：** "无法加载文件，因为在此系统上禁止运行脚本"

**解决：**
```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 管理员权限问题

**问题：** 脚本提示需要管理员权限

**解决：**
1. 右键点击PowerShell
2. 选择"以管理员身份运行"
3. 运行脚本

### 环境检查失败

**问题：** 某些组件显示未安装

**解决：**
1. 按照提示的下载地址安装缺失组件
2. 重新运行环境检查
3. 确保所有必需组件都显示✓

### 依赖安装失败

**问题：** Node.js或Python依赖安装失败

**解决：**
```cmd
# 手动安装Node.js依赖
pnpm install

# 手动安装Python依赖
pip install -r requirements.txt
```

### 数据库初始化失败

**问题：** 数据库连接失败或SQL执行错误

**解决：**
1. 确认MySQL服务正在运行
2. 验证.env中的数据库配置
3. 手动执行SQL：
```cmd
mysql -u trading -p trading_dashboard < database\schema.sql
```

### 服务启动失败

**问题：** PM2服务无法启动

**解决：**
```cmd
# 查看详细错误
pm2 logs

# 手动启动
pm2 start ecosystem.config.cjs

# 重启服务
pm2 restart all
```

---

## 📊 部署流程图

```
开始
  ↓
检查环境 (check-environment.ps1)
  ↓
配置参数 (quick-config.ps1)
  ↓
运行部署 (DEPLOY.bat)
  ↓
  ├─ 检查管理员权限
  ├─ 验证环境依赖
  ├─ 安装pnpm和PM2
  ├─ 安装Node.js依赖
  ├─ 安装Python依赖
  ├─ 初始化数据库
  └─ 启动所有服务
  ↓
验证部署
  ├─ pm2 list (查看服务状态)
  ├─ pm2 logs (查看日志)
  └─ 访问 http://localhost:3000
  ↓
完成
```

---

## 🎯 最佳实践

### 部署前

1. ✓ 运行环境检查确保所有组件已安装
2. ✓ 准备好KuCoin API密钥
3. ✓ 准备好Telegram Bot Token和Chat ID
4. ✓ 确认MySQL服务正在运行
5. ✓ 备份现有数据（如果有）

### 部署中

1. ✓ 使用管理员权限运行
2. ✓ 仔细检查配置信息
3. ✓ 等待依赖安装完成（不要中断）
4. ✓ 观察部署日志输出

### 部署后

1. ✓ 验证所有服务状态（pm2 list）
2. ✓ 检查日志是否有错误（pm2 logs）
3. ✓ 访问Dashboard确认可用
4. ✓ 测试Telegram通知
5. ✓ 保存PM2配置（pm2 save）

---

## 📞 获取帮助

### 文档

- `README_WINDOWS_DEPLOY.md` - 完整部署指南
- `DEPLOYMENT_INSTRUCTIONS.md` - 通用部署说明
- `FIXES_APPLIED.md` - 修复内容详情

### 日志

```cmd
# 查看所有日志
pm2 logs

# 查看特定服务日志
pm2 logs trading-bot --lines 100
```

### 重新部署

```cmd
# 停止所有服务
pm2 delete all

# 重新运行部署
DEPLOY.bat
```

---

**版本：** 1.0  
**更新日期：** 2025-11-26  
**适用系统：** Windows Server 2019/2022, Windows 10/11
