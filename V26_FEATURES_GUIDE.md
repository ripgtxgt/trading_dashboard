# v26.0 功能指南

## 📋 新增功能概览

v26.0版本新增三大核心功能：

1. **历史交易记录页面** - 完整的交易历史管理和分析
2. **多币种支持基础** - 数据库Schema扩展，为多交易对做准备
3. **性能分析报告** - 自动生成日报、周报、月报

---

## 1. 历史交易记录页面

### 功能特性

- ✅ **交易记录表格** - 显示所有历史交易的详细信息
- ✅ **多维度筛选** - 按交易对、方向、日期范围筛选
- ✅ **灵活排序** - 按时间、盈亏、盈亏百分比排序
- ✅ **分页浏览** - 支持大量数据的分页展示
- ✅ **统计汇总** - 实时计算总交易次数、胜率、总盈亏等
- ✅ **CSV导出** - 一键导出交易记录到CSV文件

### 访问方式

在浏览器中访问：`/history`

或在Dashboard中点击"交易历史"导航链接

### 使用示例

#### 筛选特定日期的交易

```typescript
// 通过UI选择日期范围
startDate: "2024-01-01"
endDate: "2024-01-31"
```

#### 导出交易记录

点击页面右上角的"导出CSV"按钮，系统会自动下载包含所有筛选后交易记录的CSV文件。

### API接口

#### 获取交易历史列表

```typescript
const { data } = trpc.tradeHistory.list.useQuery({
  page: 1,
  pageSize: 20,
  symbol: "XBTUSDTM", // 可选
  direction: "long", // "long" | "short" | "all"
  startDate: "2024-01-01", // ISO string
  endDate: "2024-01-31",
  sortBy: "exitTime", // "exitTime" | "pnl" | "pnlPct"
  sortOrder: "desc", // "asc" | "desc"
});
```

#### 获取交易统计

```typescript
const { data: stats } = trpc.tradeHistory.stats.useQuery({
  symbol: "XBTUSDTM",
  startDate: "2024-01-01",
  endDate: "2024-01-31",
});

// 返回数据
{
  totalTrades: 100,
  winTrades: 65,
  lossTrades: 35,
  winRate: "65.00",
  totalPnl: "125.50",
  totalFee: "12.30",
  avgPnl: "1.26",
  avgWin: "3.50",
  avgLoss: "-2.10",
  maxWin: "15.80",
  maxLoss: "-8.50"
}
```

#### 导出CSV

```typescript
const { data } = trpc.tradeHistory.exportCsv.useQuery({
  symbol: "XBTUSDTM",
  direction: "all",
  startDate: "2024-01-01",
  endDate: "2024-01-31",
});

// data.csv 包含完整的CSV内容
```

---

## 2. 多币种支持基础

### 数据库扩展

v26.0已扩展数据库Schema以支持多币种交易：

#### 新增字段

**trades表**
- `symbol` - 交易对标识（如XBTUSDTM, ETHUSDTM）
- `quantity` - 交易数量
- `fee` - 手续费

**positions表**
- `symbol` - 交易对标识
- `quantity` - 持仓数量

#### 新增表

**symbol_configs表** - 币种配置管理

```typescript
{
  id: number;
  symbol: string; // 交易对，如 XBTUSDTM
  displayName: string; // 显示名称，如 BTC/USDT
  isActive: number; // 是否启用
  initialCapital: string; // 初始资金
  leverage: number; // 杠杆倍数
  shortMaPeriod: number; // 短期均线
  longMaPeriod: number; // 长期均线
  timeframe: string; // 时间周期
  sensitivity: "loose" | "standard" | "strict";
}
```

### 后续开发建议

要完整实现多币种交易，需要：

1. **修改Python交易脚本** - 支持多个交易对同时运行
2. **创建币种管理界面** - 添加/编辑/删除交易对配置
3. **实现币种切换** - 在Dashboard中切换查看不同币种
4. **独立风险管理** - 每个币种独立的风险控制

---

## 3. 性能分析报告

### 功能特性

- ✅ **日报生成** - 当日交易统计和分析
- ✅ **周报生成** - 近7天交易汇总，包含每日统计
- ✅ **月报生成** - 近30天交易汇总，包含每周统计
- ✅ **关键指标** - 胜率、盈亏比、夏普比率等
- ✅ **智能建议** - 基于数据自动生成优化建议
- ✅ **报告导出** - 导出为Markdown格式

### 访问方式

在浏览器中访问：`/report`

或在Dashboard中点击"性能报告"导航链接

### 核心指标说明

#### 基础指标

- **总交易次数** - 统计期内的所有交易数量
- **盈利交易 / 亏损交易** - 盈利和亏损的交易数量
- **胜率** - 盈利交易占总交易的百分比
- **总盈亏** - 所有交易的净盈亏（扣除手续费前）
- **总手续费** - 所有交易产生的手续费总和

#### 高级指标

- **平均盈亏** - 每笔交易的平均盈亏
- **平均盈利 / 平均亏损** - 盈利交易和亏损交易的平均值
- **最大盈利 / 最大亏损** - 单笔交易的最大盈利和最大亏损
- **盈亏比 (Profit Factor)** - 总盈利 / 总亏损的比值
  - > 1 表示整体盈利
  - < 1 表示整体亏损
  - 建议 > 1.5
- **夏普比率 (Sharpe Ratio)** - 风险调整后的收益率
  - 衡量每单位风险的超额回报
  - > 1 表示良好，> 2 表示优秀

### 使用示例

#### 获取日报

```typescript
const { data: dailyReport } = trpc.performanceReport.dailyReport.useQuery({
  date: "2024-01-15", // 可选，默认今天
});
```

#### 获取周报

```typescript
const { data: weeklyReport } = trpc.performanceReport.weeklyReport.useQuery();

// 包含每日统计
weeklyReport.dailyStats.forEach((day) => {
  console.log(`${day.date}: ${day.trades} 笔交易, 盈亏 ${day.pnl} USDT`);
});
```

#### 获取月报

```typescript
const { data: monthlyReport } = trpc.performanceReport.monthlyReport.useQuery();

// 包含每周统计
monthlyReport.weeklyStats.forEach((week, idx) => {
  console.log(`第 ${idx + 1} 周: ${week.trades} 笔交易, 盈亏 ${week.pnl} USDT`);
});
```

#### 获取历史报告

```typescript
const { data } = trpc.performanceReport.reportHistory.useQuery({
  period: "day", // "day" | "week" | "month"
  limit: 10, // 最多30条
});

// 返回最近10个周期的报告摘要
```

### 智能建议系统

系统会根据数据自动生成建议：

#### 警告建议

- **胜率低于40%** - 建议优化策略参数或暂停交易
- **盈亏比小于1** - 亏损大于盈利，需要调整止损止盈
- **交易样本少于10笔** - 统计结果可能不准确

#### 正面建议

- **胜率≥60% 且 盈亏比≥1.5** - 策略表现良好，保持当前设置

---

## 数据库变更

### 新增表

```sql
-- 币种配置表
CREATE TABLE symbol_configs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  symbol VARCHAR(20) NOT NULL UNIQUE,
  display_name VARCHAR(50) NOT NULL,
  is_active INT DEFAULT 1 NOT NULL,
  initial_capital VARCHAR(20) DEFAULT '10' NOT NULL,
  leverage INT DEFAULT 10 NOT NULL,
  short_ma_period INT DEFAULT 5 NOT NULL,
  long_ma_period INT DEFAULT 20 NOT NULL,
  timeframe VARCHAR(10) DEFAULT '1h' NOT NULL,
  sensitivity ENUM('loose', 'standard', 'strict') DEFAULT 'standard' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
);
```

### 修改表

```sql
-- trades表新增字段
ALTER TABLE trades
  ADD COLUMN symbol VARCHAR(20) DEFAULT 'XBTUSDTM' NOT NULL,
  ADD COLUMN quantity VARCHAR(20) NOT NULL,
  ADD COLUMN fee VARCHAR(20) DEFAULT '0' NOT NULL;

-- positions表新增字段
ALTER TABLE positions
  ADD COLUMN symbol VARCHAR(20) DEFAULT 'XBTUSDTM' NOT NULL,
  ADD COLUMN quantity VARCHAR(20) NOT NULL;
```

---

## API路由

### 新增路由

```typescript
// 交易历史
trpc.tradeHistory.list
trpc.tradeHistory.stats
trpc.tradeHistory.exportCsv
trpc.tradeHistory.symbols

// 性能报告
trpc.performanceReport.dailyReport
trpc.performanceReport.weeklyReport
trpc.performanceReport.monthlyReport
trpc.performanceReport.reportHistory
```

---

## 测试覆盖

v26.0包含20个单元测试，全部通过：

- ✅ 认证测试 (1个)
- ✅ v24功能测试 (11个)
- ✅ 策略参数测试 (5个)
- ✅ 策略回测测试 (3个)

---

## 下一步建议

1. **完善多币种功能**
   - 修改Python交易脚本支持多交易对
   - 创建币种管理UI
   - 实现币种独立风险管理

2. **增强报告功能**
   - 添加图表可视化（收益曲线、回撤曲线）
   - 实现自动报告推送（Telegram/邮件）
   - 添加策略对比分析

3. **优化用户体验**
   - 添加导航菜单到Dashboard
   - 实现页面间跳转
   - 添加快捷操作按钮

---

## 技术栈

- **前端**: React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui
- **后端**: tRPC 11 + Express 4
- **数据库**: MySQL/TiDB (Drizzle ORM)
- **测试**: Vitest

---

## 更新日志

### v26.0 (2024-11-22)

**新增功能**
- 历史交易记录页面（筛选、排序、分页、导出）
- 多币种支持基础（数据库Schema扩展）
- 性能分析报告（日报、周报、月报）

**数据库变更**
- trades表新增symbol、quantity、fee字段
- positions表新增symbol、quantity字段
- 新增symbol_configs表

**API变更**
- 新增tradeHistory路由（4个API）
- 新增performanceReport路由（4个API）

**测试**
- 20个单元测试全部通过
- 覆盖核心功能和API

---

## 支持

如有问题或建议，请查看项目文档或联系开发团队。
