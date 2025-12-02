# Linux服务器部署总结

## 服务器信息
- **服务器**: AWS Lightsail Ubuntu 22.04
- **IP地址**: 3.112.226.9
- **域名**: cryptoalpha.vip
- **部署时间**: 2025-12-02

## 已完成的配置

### 1. 系统环境
- ✅ Node.js 22.x
- ✅ Python 3.10
- ✅ pnpm包管理器
- ✅ PM2进程管理器
- ✅ Nginx反向代理
- ✅ Let's Encrypt SSL证书

### 2. Python依赖
所有Python依赖已安装：
```bash
pip3 install -r scripts/requirements.txt
pip3 install mysql-connector-python
```

依赖包括：
- ccxt (KuCoin交易API)
- pandas (数据分析)
- websockets (WebSocket通信)
- python-telegram-bot (Telegram机器人)
- mysql-connector-python (MySQL数据库连接)
- python-dotenv (环境变量管理)
- 其他依赖...

### 3. PM2服务配置
所有服务使用`ecosystem.config.cjs`管理：

| 服务名称 | 状态 | 端口 | 说明 |
|---------|------|------|------|
| trading-dashboard | ✅ online | 3000 | Web界面 (Node.js + tRPC) |
| webhook-deploy-server | ✅ online | 9000 | GitHub自动部署服务 |
| websocket-server | ✅ online | - | WebSocket实时推送 |
| telegram-bot | ✅ online | - | Telegram通知机器人 |
| daily-report | ✅ online | - | 每日报告生成 |
| trading-bot | ⚠️ errored | - | 交易机器人（需要环境变量） |

**PM2开机自启动已配置：**
```bash
pm2 startup systemd
pm2 save
```

### 4. Nginx配置
配置文件：`/etc/nginx/sites-available/cryptoalpha.vip`

**代理规则：**
- `/` → `http://localhost:3000` (主应用)
- `/socket.io/` → `http://localhost:3000` (WebSocket)
- `/webhook` → `http://localhost:9000/webhook` (自动部署webhook)

**SSL证书：**
- Let's Encrypt自动续期
- 证书路径：`/etc/letsencrypt/live/cryptoalpha.vip/`

### 5. GitHub Actions自动部署
**Webhook端点：** `https://cryptoalpha.vip/webhook`

**部署流程：**
1. 推送代码到GitHub main分支
2. GitHub Actions运行测试
3. 测试通过后触发webhook
4. 服务器自动执行：
   - `git pull origin main`
   - `pnpm install`
   - `pnpm build`
   - `pm2 restart trading-dashboard`
   - 检查并启动Nginx
5. Telegram通知部署结果

**部署脚本：** `deploy-auto.sh`

## 待配置项

### trading-bot环境变量
trading-bot服务需要以下环境变量才能运行，需要在服务器的`.env`文件中配置：

```bash
# 数据库配置
DATABASE_URL=mysql://用户名:密码@localhost:3306/数据库名

# Telegram配置
TELEGRAM_BOT_TOKEN=你的Telegram Bot Token
TELEGRAM_CHAT_ID=你的Telegram Chat ID

# KuCoin API配置
KUCOIN_API_KEY=你的KuCoin API Key
KUCOIN_API_SECRET=你的KuCoin API Secret
KUCOIN_API_PASSPHRASE=你的KuCoin API Passphrase
KUCOIN_SANDBOX=true  # 使用沙盒环境测试，正式环境改为false

# 交易配置
INITIAL_CAPITAL=10.0  # 初始资金（USDT）
```

### 配置步骤
1. SSH登录服务器：
   ```bash
   ssh ubuntu@3.112.226.9
   ```

2. 编辑`.env`文件：
   ```bash
   cd /home/ubuntu/trading_dashboard
   nano .env
   ```

3. 添加上述环境变量

4. 重启trading-bot服务：
   ```bash
   pm2 restart trading-bot
   pm2 save
   ```

5. 检查服务状态：
   ```bash
   pm2 list
   pm2 logs trading-bot
   ```

## 访问地址
- **Web界面**: https://cryptoalpha.vip
- **Webhook端点**: https://cryptoalpha.vip/webhook

## 常用命令

### PM2管理
```bash
# 查看所有服务状态
pm2 list

# 查看特定服务日志
pm2 logs trading-bot
pm2 logs webhook-deploy-server

# 重启服务
pm2 restart trading-bot
pm2 restart all

# 停止服务
pm2 stop trading-bot

# 保存PM2配置
pm2 save
```

### Nginx管理
```bash
# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx状态
sudo systemctl status nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 部署管理
```bash
# 手动部署
cd /home/ubuntu/trading_dashboard
bash deploy-auto.sh

# 查看部署历史
cat deployment-history.json
```

## 安全建议
1. ✅ 使用HTTPS加密通信
2. ✅ 配置防火墙规则（只开放22, 80, 443端口）
3. ⚠️ 定期更新系统和依赖包
4. ⚠️ 定期备份数据库
5. ⚠️ 监控服务器资源使用情况
6. ⚠️ 配置日志轮转避免磁盘占满

## 故障排查

### 服务无法启动
```bash
# 查看详细错误日志
pm2 logs 服务名 --err --lines 50

# 检查端口占用
sudo netstat -tulpn | grep :3000

# 检查进程
ps aux | grep node
ps aux | grep python
```

### Nginx问题
```bash
# 检查配置语法
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 自动部署失败
```bash
# 查看webhook日志
pm2 logs webhook-deploy-server

# 手动测试部署脚本
cd /home/ubuntu/trading_dashboard
bash deploy-auto.sh
```

## 监控和维护
- PM2自动重启崩溃的服务
- PM2每天0点自动重启所有服务（cron配置）
- Nginx自动续期SSL证书
- GitHub Actions自动运行测试
- Telegram自动发送部署通知

## 联系方式
如有问题，请查看：
- GitHub仓库：https://github.com/ripgtxgt/trading_dashboard
- 服务器日志：`pm2 logs`
- Nginx日志：`/var/log/nginx/`
