# 部署脚本说明

## 📋 可用的部署脚本

项目提供了两种部署方式：

### 1. 简化版部署（推荐）⭐

**文件：** `SIMPLE-DEPLOY.bat`

**特点：**
- ✅ 简单易用，步骤清晰
- ✅ 自动检查环境
- ✅ 自动安装依赖
- ✅ 交互式引导
- ✅ 兼容性好

**使用方法：**
```cmd
# 右键点击 SIMPLE-DEPLOY.bat
# 选择"以管理员身份运行"
```

**适用场景：**
- 首次部署
- 快速部署
- 不熟悉PowerShell的用户

---

### 2. 完整版部署

**文件：** `DEPLOY.bat`

**特点：**
- ✅ 功能完整
- ✅ 自动配置环境变量
- ✅ 详细的检查和验证
- ✅ 完整的错误处理

**使用方法：**
```cmd
# 右键点击 DEPLOY.bat
# 选择"以管理员身份运行"
```

**适用场景：**
- 需要自动生成配置文件
- 需要详细的部署日志
- 熟悉PowerShell的用户

---

## 🚀 快速开始

### 推荐流程：

#### 步骤1：创建.env配置文件
在项目根目录创建 `.env` 文件，内容参考 `DEPLOYMENT_WITH_YOUR_CONFIG.md`

#### 步骤2：准备MySQL数据库
```sql
CREATE DATABASE IF NOT EXISTS trading_dashboard;
CREATE USER IF NOT EXISTS 'trading'@'localhost' IDENTIFIED BY 'Zdm351026';
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
```

#### 步骤3：运行部署脚本
右键点击 `SIMPLE-DEPLOY.bat`，选择"以管理员身份运行"

#### 步骤4：验证部署
```cmd
pm2 list
pm2 logs
```

访问：http://localhost:3000

---

## 🔧 故障排除

### 问题1：PowerShell脚本无法运行

**错误信息：**
```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决方法：**
```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题2：编码显示乱码

**解决方法：**
- 使用 `SIMPLE-DEPLOY.bat` 而不是直接运行.ps1文件
- 批处理文件已自动设置UTF-8编码

### 问题3：数据库初始化失败

**手动初始化：**
```cmd
mysql -u trading -pZdm351026 trading_dashboard < database\schema.sql
```

### 问题4：依赖安装失败

**解决方法：**
```cmd
# 手动安装
npm install -g pnpm
npm install -g pm2
pnpm install
pip install -r requirements.txt
```

---

## 📝 手动部署

如果自动部署脚本无法使用，可以手动执行以下步骤：

### 1. 安装全局依赖
```cmd
npm install -g pnpm
npm install -g pm2
npm install -g pm2-windows-startup
pm2-startup install
```

### 2. 安装项目依赖
```cmd
pnpm install
pip install -r requirements.txt
```

### 3. 创建.env文件
参考 `DEPLOYMENT_WITH_YOUR_CONFIG.md`

### 4. 初始化数据库
```cmd
mysql -u trading -pZdm351026 trading_dashboard < database\schema.sql
```

### 5. 启动服务
```cmd
pm2 start ecosystem.config.cjs
pm2 save
pm2 list
```

---

## ✅ 部署检查清单

部署前：
- [ ] MySQL服务正在运行
- [ ] Python 3.11+ 已安装
- [ ] Node.js 20+ 已安装
- [ ] .env文件已创建

部署后：
- [ ] 所有5个服务状态为online
- [ ] Dashboard可访问 (http://localhost:3000)
- [ ] Telegram收到启动通知
- [ ] 日志无严重错误

---

## 📞 常用命令

```cmd
# 查看服务状态
pm2 list

# 查看日志
pm2 logs

# 重启服务
pm2 restart all

# 停止服务
pm2 stop all

# 监控服务
pm2 monit
```

---

## 📚 相关文档

- `DEPLOYMENT_WITH_YOUR_CONFIG.md` - 详细部署指南（包含您的配置）
- `README_WINDOWS_DEPLOY.md` - Windows部署完整指南
- `DEPLOYMENT_TOOLS.md` - 部署工具说明

---

**推荐使用 `SIMPLE-DEPLOY.bat` 进行部署！** 🚀
