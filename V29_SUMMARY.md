# v29.0 功能总结

## 新增功能

1. **策略配置入口** - Dashboard添加策略配置按钮和对话框
2. **自动交易日志** - 完整记录交易决策、市场条件和执行结果
3. **性能监控仪表盘** - 实时监控CPU、内存和系统信息

## 技术实现

- 新增 trade_logs 数据库表
- 新增 TradeLogger Python模块
- 新增 /logs 和 /monitor 页面路由
- 新增 systemMonitor API

## 测试状态

所有20个单元测试通过 ✅

