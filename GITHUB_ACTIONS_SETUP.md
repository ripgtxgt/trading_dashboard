# GitHub Actions 自动部署配置指南

## 📋 前置准备

### 1. 服务器端配置

#### 安装OpenSSH Server

```powershell
# 检查是否已安装
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'

# 如果未安装，执行
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动服务
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 配置防火墙
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

#### 生成SSH密钥对

```powershell
# 生成密钥对（在本地电脑执行，不是服务器）
ssh-keygen -t rsa -b 4096 -f trading_dashboard_deploy_key

# 会生成两个文件：
# - trading_dashboard_deploy_key (私钥，用于GitHub Secrets)
# - trading_dashboard_deploy_key.pub (公钥，用于服务器)
```

#### 配置服务器authorized_keys

```powershell
# 在服务器上执行
# 创建.ssh目录
New-Item -ItemType Directory -Force -Path C:\Users\Administrator\.ssh

# 将公钥内容添加到authorized_keys
# 方法1：手动复制
notepad C:\Users\Administrator\.ssh\authorized_keys
# 粘贴 trading_dashboard_deploy_key.pub 的内容

# 方法2：使用PowerShell
$pubKey = Get-Content trading_dashboard_deploy_key.pub
Add-Content -Path C:\Users\Administrator\.ssh\authorized_keys -Value $pubKey

# 设置权限
icacls C:\Users\Administrator\.ssh\authorized_keys /inheritance:r
icacls C:\Users\Administrator\.ssh\authorized_keys /grant:r "Administrator:F"
```

#### 配置Git仓库

```powershell
# 在服务器上执行
cd C:\trading_dashboard_fixed

# 如果是新部署，克隆仓库
git clone https://github.com/YOUR_USERNAME/trading_dashboard.git C:\trading_dashboard_fixed

# 如果已有代码，初始化Git
git init
git remote add origin https://github.com/YOUR_USERNAME/trading_dashboard.git
git fetch
git reset --hard origin/main
```

---

## 🔐 GitHub Secrets 配置

在GitHub仓库设置中添加以下Secrets：

### Settings → Secrets and variables → Actions → New repository secret

| Secret Name | 说明 | 示例值 |
|------------|------|--------|
| `SERVER_HOST` | 服务器IP地址 | `123.45.67.89` |
| `SERVER_USER` | Windows用户名 | `Administrator` |
| `SERVER_SSH_KEY` | SSH私钥内容 | `trading_dashboard_deploy_key`文件的完整内容 |
| `SERVER_PORT` | SSH端口（可选） | `22`（默认） |

### 如何获取SSH私钥内容

```bash
# 在本地电脑执行
cat trading_dashboard_deploy_key

# 复制完整输出（包括BEGIN和END行）
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

---

## 🚀 部署流程

### 自动部署（推荐）

1. **在Manus开发环境修改代码**
2. **提交并推送到GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. **GitHub Actions自动触发部署**
   - 自动SSH到服务器
   - 拉取最新代码
   - 安装依赖
   - 构建项目
   - 重启服务

### 手动触发部署

在GitHub仓库页面：
1. 点击 **Actions** 标签
2. 选择 **Deploy to Windows Server** 工作流
3. 点击 **Run workflow** 按钮
4. 选择分支并运行

---

## 🔍 故障排查

### 1. SSH连接失败

**检查服务器SSH服务**
```powershell
Get-Service sshd
# 如果未运行，启动它
Start-Service sshd
```

**检查防火墙**
```powershell
Get-NetFirewallRule -Name sshd
```

**测试SSH连接**
```bash
# 在本地电脑测试
ssh -i trading_dashboard_deploy_key Administrator@YOUR_SERVER_IP
```

### 2. Git pull失败

**检查Git配置**
```powershell
cd C:\trading_dashboard_fixed
git remote -v
git status
```

**重置到远程版本**
```powershell
git fetch origin
git reset --hard origin/main
```

### 3. 构建失败

**手动执行部署脚本**
```powershell
cd C:\trading_dashboard_fixed
.\deploy-auto.ps1
```

**查看详细错误日志**
- GitHub Actions页面查看工作流日志
- 服务器上查看PM2日志：`pm2 logs`

---

## 📝 本地测试部署脚本

在推送到GitHub之前，可以在服务器上手动测试：

```powershell
cd C:\trading_dashboard_fixed
git pull origin main
.\deploy-auto.ps1
```

---

## ⚙️ 自定义配置

### 修改部署分支

编辑 `.github/workflows/deploy.yml`：

```yaml
on:
  push:
    branches:
      - main  # 改为其他分支，如 production
```

### 添加部署前测试

在 `deploy.yml` 中添加测试步骤：

```yaml
- name: Run tests
  run: |
    pnpm install
    pnpm test
```

---

## 🎯 完整部署流程图

```
开发 → Git Push → GitHub Actions → SSH连接 → 拉取代码 → 安装依赖 → 构建 → 重启 → 完成
```

---

## 📞 需要帮助？

如果遇到问题，请检查：
1. GitHub Actions工作流日志
2. 服务器SSH连接状态
3. PM2服务日志
4. Nginx错误日志
