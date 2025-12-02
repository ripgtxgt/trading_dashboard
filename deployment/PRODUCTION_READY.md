# 生产环境部署完成

## 服务器信息
- **域名**: cryptoalpha.vip
- **IP地址**: 3.112.226.9
- **操作系统**: Ubuntu 22.04 LTS
- **云服务商**: AWS Lightsail (Tokyo Region)

## 部署状态

### ✅ 所有服务运行正常 (7个)

1. **trading-dashboard** - Web管理界面
   - 端口: 3000
   - 访问: https://cryptoalpha.vip
   - 状态: Online

2. **trading-bot** - 10U战神滚仓策略交易机器人
   - 初始资金: 10 USDT
   - 交易所: KuCoin (正式环境)
   - 状态: Online (当前暂停交易-回撤超限)

3. **telegram-bot** - Telegram通知机器人
   - 功能: 交易通知、系统状态查询
   - 状态: Online

4. **websocket-server** - WebSocket实时推送服务
   - 端口: 8765
   - 功能: 实时交易数据推送
   - 状态: Online

5. **daily-report** - 每日报告生成服务
   - 执行时间: 每天00:00 UTC
   - 功能: 生成每日交易报告
   - 状态: Online

6. **webhook-deploy-server** - GitHub自动部署服务
   - 端口: 9000 (通过Nginx代理到HTTPS)
   - Webhook URL: https://cryptoalpha.vip/webhook
   - 状态: Online

7. **server-monitor** - 服务器监控告警服务
   - 检查间隔: 5分钟
   - 告警方式: Telegram
   - 阈值: CPU 80%, Memory 85%, Disk 90%
   - 状态: Online

## 自动化配置

### 1. GitHub自动部署
- ✅ 推送到main分支自动触发部署
- ✅ GitHub Actions工作流配置完成
- ✅ Webhook服务器运行正常
- ✅ 部署脚本自动更新.env、安装依赖、构建项目、重启服务

### 2. 数据库备份
- ✅ 每天凌晨2:00 UTC (北京时间10:00) 自动备份
- ✅ 备份文件压缩存储
- ✅ 自动清理30天前的旧备份
- ✅ 备份目录: /home/ubuntu/trading_dashboard/backups/
- ✅ 恢复脚本: scripts/restore_database.sh

### 3. 服务器监控
- ✅ PM2守护所有服务进程
- ✅ server-monitor实时监控系统资源
- ✅ 超过阈值自动发送Telegram告警
- ✅ PM2进程异常自动告警
- ✅ PM2开机自启动配置完成

### 4. 定时任务 (Crontab)
```
# 数据库备份 - 每天凌晨2点
0 2 * * * /home/ubuntu/trading_dashboard/scripts/backup_database.sh

# 清理旧日志 - 每周日凌晨3点
0 3 * * 0 find /home/ubuntu/trading_dashboard/logs -name "*.log" -type f -mtime +30 -delete

# PM2保存 - 每天凌晨4点
0 4 * * * /usr/bin/pm2 save
```

## 环境变量配置

### KuCoin API (正式环境)
- ✅ KUCOIN_API_KEY: 已配置
- ✅ KUCOIN_API_SECRET: 已配置
- ✅ KUCOIN_API_PASSPHRASE: 已配置
- ✅ KUCOIN_SANDBOX: false (正式交易)

### Telegram Bot
- ✅ TELEGRAM_BOT_TOKEN: 已配置
- ✅ TELEGRAM_CHAT_ID: 已配置

### 数据库
- ✅ DATABASE_URL: mysql://trading:trading123@localhost:3306/trading_dashboard
- ✅ 数据库已创建并初始化

### 交易配置
- ✅ INITIAL_CAPITAL: 10.0 USDT (将从KuCoin账户余额自动检测)

## 安全配置

### Nginx HTTPS
- ✅ SSL证书配置完成
- ✅ HTTP自动重定向到HTTPS
- ✅ Webhook端点通过HTTPS访问

### 文件权限
- ✅ .env文件权限: 600 (仅owner可读写)
- ✅ 备份脚本可执行权限已设置
- ✅ 数据库凭证安全存储

### PM2进程管理
- ✅ 所有服务自动重启
- ✅ 内存限制配置
- ✅ 日志文件自动轮转

## 日志文件位置

所有日志文件位于: `/home/ubuntu/trading_dashboard/logs/`

- trading-bot-error.log / trading-bot-out.log
- telegram-bot-error.log / telegram-bot-out.log
- websocket-error.log / websocket-out.log
- daily-report-error.log / daily-report-out.log
- webhook-error.log / webhook-out.log
- server-monitor-error.log / server-monitor-out.log
- dashboard-error.log / dashboard-out.log
- backup-cron.log
- pm2-save.log

## 常用命令

### PM2进程管理
```bash
# 查看所有服务状态
pm2 list

# 查看特定服务日志
pm2 logs trading-bot

# 重启服务
pm2 restart trading-bot

# 停止服务
pm2 stop trading-bot

# 启动服务
pm2 start trading-bot

# 保存PM2进程列表
pm2 save
```

### 数据库操作
```bash
# 手动备份数据库
cd /home/ubuntu/trading_dashboard
./scripts/backup_database.sh

# 恢复数据库
./scripts/restore_database.sh backups/trading_dashboard_YYYYMMDD_HHMMSS.sql.gz

# 连接数据库
mysql -utrading -ptrading123 trading_dashboard
```

### 部署操作
```bash
# 手动触发部署
cd /home/ubuntu/trading_dashboard
./deployment/trigger-deploy.sh

# 查看部署日志
pm2 logs webhook-deploy-server
```

### 监控操作
```bash
# 查看监控日志
pm2 logs server-monitor

# 手动运行一次监控检查
cd /home/ubuntu/trading_dashboard
python3 scripts/monitor_server.py --once
```

## 访问地址

- **Web管理界面**: https://cryptoalpha.vip
- **Webhook端点**: https://cryptoalpha.vip/webhook
- **WebSocket**: wss://cryptoalpha.vip/ws

## 下一步建议

1. **监控交易表现**
   - 定期查看trading-bot日志
   - 关注Telegram通知
   - 检查Web界面的交易数据

2. **优化交易策略**
   - 根据实际交易数据调整参数
   - 监控回撤和盈利情况
   - 必要时调整风险控制参数

3. **系统维护**
   - 定期检查备份文件
   - 监控服务器资源使用
   - 及时处理告警通知

4. **扩展功能**
   - 添加更多交易对
   - 优化交易策略
   - 增加数据分析功能

## 故障排查

### 服务无法启动
```bash
# 检查日志
pm2 logs <service-name> --err

# 检查环境变量
pm2 env <service-id>

# 重启服务
pm2 restart <service-name>
```

### 数据库连接失败
```bash
# 检查MySQL服务
sudo systemctl status mysql

# 测试数据库连接
mysql -utrading -ptrading123 trading_dashboard -e "SELECT 1"
```

### Nginx配置问题
```bash
# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
```

## 联系信息

如有问题，请通过以下方式联系：
- Telegram: 通过配置的Telegram Bot
- GitHub Issues: https://github.com/ripgtxgt/trading_dashboard/issues

---

**部署完成时间**: 2025-12-02
**部署版本**: v1.0.0
**部署状态**: ✅ 生产环境就绪
