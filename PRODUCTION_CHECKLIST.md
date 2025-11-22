# 生产环境部署检查清单

在将交易监控面板部署到生产环境之前，请按照此清单逐项检查，确保系统稳定可靠。

---

## ✅ 部署前检查

### 1. 环境变量配置

确保以下环境变量已正确配置：

#### 必需变量（系统自动注入）
- [x] `DATABASE_URL` - MySQL/TiDB连接字符串
- [x] `JWT_SECRET` - Session签名密钥
- [x] `VITE_APP_ID` - Manus OAuth应用ID
- [x] `OAUTH_SERVER_URL` - OAuth服务器地址
- [x] `BUILT_IN_FORGE_API_KEY` - Manus API密钥
- [x] `BUILT_IN_FORGE_API_URL` - Manus API地址

#### 可选变量（需手动配置）
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram Bot Token（推荐）
- [ ] `TELEGRAM_CHAT_ID` - Telegram Chat ID（推荐）

**配置方法：**
1. 打开Management UI → Settings → Secrets
2. 点击"Add Secret"添加环境变量
3. 参考`TELEGRAM_SETUP.md`获取Telegram配置

---

### 2. 数据库初始化

确保数据库表已正确创建：

```bash
cd /home/ubuntu/trading_dashboard
pnpm db:push
```

**检查要点：**
- [ ] 所有表创建成功（users, bot_state, trades, positions, balance_snapshots, strategy_params, param_simulations, backtest_history）
- [ ] 初始数据已插入（strategy_params默认参数）
- [ ] 数据库连接正常

**验证方法：**
```sql
SHOW TABLES;
SELECT * FROM strategy_params LIMIT 1;
```

---

### 3. 代码质量检查

运行测试确保功能正常：

```bash
cd /home/ubuntu/trading_dashboard
pnpm test
```

**检查要点：**
- [ ] 所有单元测试通过
- [ ] TypeScript编译无错误
- [ ] ESLint检查通过（如有）

---

### 4. 功能测试

在本地开发环境测试所有核心功能：

#### 4.1 Dashboard显示
- [ ] 账户状态卡片正常显示
- [ ] 策略状态卡片正常显示
- [ ] 资金曲线图表正常渲染
- [ ] 交易历史表格正常显示

#### 4.2 参数调整
- [ ] 参数调整面板正常显示
- [ ] 信号模拟功能正常
- [ ] 历史回测功能正常
- [ ] AI优化功能正常
- [ ] 参数应用功能正常

#### 4.3 机器人控制
- [ ] 启动/停止按钮正常
- [ ] 状态查询正常
- [ ] 日志读取正常

#### 4.4 实时功能
- [ ] WebSocket连接正常
- [ ] 实时信号推送正常
- [ ] 数据自动刷新正常

---

### 5. 性能优化

确保系统性能符合预期：

- [ ] K线数据缓存机制启用
- [ ] API响应时间 < 1秒
- [ ] 图表渲染流畅（无卡顿）
- [ ] 内存使用正常（< 500MB）

**性能测试方法：**
```bash
# 检查API响应时间
curl -w "@-" -o /dev/null -s "http://localhost:3000/api/trpc/trading.getState" <<'EOF'
time_total: %{time_total}s
EOF
```

---

### 6. 安全检查

确保系统安全性：

- [ ] 敏感信息（Token, API Key）不在代码中硬编码
- [ ] 所有API接口有适当的权限控制
- [ ] Session Cookie设置了HttpOnly和Secure标志
- [ ] 数据库连接使用SSL（生产环境）
- [ ] CORS配置正确

---

## 🚀 部署步骤

### 步骤1：保存Checkpoint

在Management UI中点击右上角的"Publish"按钮前，确保已保存最新checkpoint：

```bash
# 或在代码中使用webdev_save_checkpoint
```

### 步骤2：发布项目

1. 打开Management UI
2. 点击右上角的"Publish"按钮
3. 等待部署完成（通常需要1-2分钟）
4. 记录生成的域名（例如：`https://xxx.manus.space`）

### 步骤3：配置自定义域名（可选）

1. 打开Management UI → Settings → Domains
2. 点击"Add Custom Domain"
3. 输入你的域名（例如：`trading.yourdomain.com`）
4. 按照提示配置DNS记录
5. 等待SSL证书自动签发

### 步骤4：验证部署

访问生产环境URL，检查以下功能：

- [ ] 页面正常加载
- [ ] OAuth登录正常
- [ ] Dashboard数据正常显示
- [ ] API接口正常响应
- [ ] WebSocket连接正常

---

## 📊 监控和维护

### 1. 日志监控

定期检查系统日志：

**Web服务器日志：**
- 访问Management UI → Dashboard → Logs
- 检查错误日志和异常

**Python脚本日志：**
```bash
tail -f /path/to/trading_rolling_*.log
```

### 2. 数据库维护

定期备份数据库：

```bash
# 导出数据库
mysqldump -h <host> -u <user> -p <database> > backup_$(date +%Y%m%d).sql

# 定期清理旧数据（可选）
DELETE FROM balance_snapshots WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

### 3. 性能监控

使用Management UI的Dashboard面板监控：

- UV/PV统计
- API响应时间
- 错误率
- 资源使用情况

### 4. 告警配置

建议配置以下告警：

- [ ] 交易失败告警（通过Telegram）
- [ ] 资金异常告警（大额亏损）
- [ ] 系统错误告警（API异常）
- [ ] 连接断开告警（WebSocket断开）

---

## 🔧 故障排查

### 问题1：页面无法访问

**可能原因：**
- 部署失败
- DNS未生效
- SSL证书未签发

**解决方法：**
1. 检查Management UI的部署状态
2. 等待DNS传播（最多48小时）
3. 检查SSL证书状态

### 问题2：数据不显示

**可能原因：**
- 数据库连接失败
- Python脚本未运行
- 数据同步未配置

**解决方法：**
1. 检查DATABASE_URL环境变量
2. 启动Python交易脚本
3. 检查db_sync模块是否正确集成

### 问题3：Telegram通知不工作

**可能原因：**
- 环境变量未配置
- Bot Token或Chat ID错误
- 网络连接问题

**解决方法：**
1. 检查TELEGRAM_BOT_TOKEN和TELEGRAM_CHAT_ID
2. 运行telegram_notifier.py测试
3. 检查防火墙设置

### 问题4：WebSocket连接失败

**可能原因：**
- 代理服务器不支持WebSocket
- CORS配置错误
- 端口被占用

**解决方法：**
1. 检查Nginx/代理配置
2. 检查CORS设置
3. 重启Web服务器

---

## 📝 部署后清单

部署完成后，完成以下任务：

- [ ] 记录生产环境URL
- [ ] 更新README.md中的访问地址
- [ ] 通知团队成员访问方式
- [ ] 配置监控告警
- [ ] 设置数据库备份计划
- [ ] 启动Python交易脚本
- [ ] 测试Telegram通知
- [ ] 验证所有功能正常

---

## 🎯 优化建议

部署后可以考虑的优化：

1. **CDN加速**：配置CDN加速静态资源
2. **数据库优化**：添加索引提升查询性能
3. **缓存策略**：使用Redis缓存热点数据
4. **负载均衡**：多实例部署提升可用性
5. **自动扩容**：根据流量自动扩容

---

## 📞 支持

如遇到问题，可以：

1. 查看项目文档（README.md, DEPLOYMENT.md）
2. 检查日志文件
3. 访问 https://help.manus.im 提交工单

---

**祝部署顺利！🎉**
