# v32.0 风险管理真实数据集成

## 概述

v32.0版本实现了风险管理系统的真实数据集成，包括API端点、数据库Schema和Python脚本集成。

---

## 新增功能

### 1. 风险数据API

**文件：** `server/risk_data_api.ts`

提供两个主要端点：

#### 获取当前风险状态
```typescript
trpc.riskData.getCurrentRisk.useQuery()
```

返回数据：
```json
{
  "success": true,
  "data": {
    "volatility": {
      "atr": 150.5,
      "historical": 0.035,
      "trend": "stable"
    },
    "riskLevel": "medium",
    "positionMultiplier": 0.7,
    "isPaused": false,
    "lastUpdate": "2024-11-22T10:30:00Z"
  }
}
```

#### 获取风险历史
```typescript
trpc.riskData.getRiskHistory.useQuery()
```

返回数据：
```json
{
  "success": true,
  "data": {
    "volatilityHistory": [...],
    "pauseEvents": [...],
    "positionAdjustments": [...]
  }
}
```

---

### 2. Python集成脚本

#### get_risk_status.py
从风险管理模块获取实时风险状态。

**使用方法：**
```bash
cd scripts
python3 get_risk_status.py
```

**输出示例：**
```json
{
  "volatility": {
    "atr": 150.5,
    "historical": 0.035,
    "trend": "stable"
  },
  "riskLevel": "medium",
  "positionMultiplier": 0.7,
  "isPaused": false,
  "lastUpdate": "2024-11-22T10:30:00Z"
}
```

#### get_risk_history.py
从数据库获取风险历史数据。

**使用方法：**
```bash
cd scripts
python3 get_risk_history.py
```

---

### 3. 数据库Schema

#### 风险配置表 (risk_config)

存储风险管理参数配置。

```sql
CREATE TABLE risk_config (
  id INT AUTO_INCREMENT PRIMARY KEY,
  -- 波动率阈值
  low_vol_threshold VARCHAR(20) DEFAULT '0.02',
  medium_vol_threshold VARCHAR(20) DEFAULT '0.05',
  high_vol_threshold VARCHAR(20) DEFAULT '0.08',
  extreme_vol_threshold VARCHAR(20) DEFAULT '0.10',
  -- 仓位系数
  low_risk_multiplier VARCHAR(20) DEFAULT '1.0',
  medium_risk_multiplier VARCHAR(20) DEFAULT '0.7',
  high_risk_multiplier VARCHAR(20) DEFAULT '0.4',
  extreme_risk_multiplier VARCHAR(20) DEFAULT '0.0',
  -- 其他参数
  atr_period INT DEFAULT 14,
  volatility_period INT DEFAULT 30,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 风险历史表 (risk_history)

记录所有风险事件。

```sql
CREATE TABLE risk_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event_type ENUM('volatility', 'pause', 'resume', 'position_adjust'),
  risk_level ENUM('low', 'medium', 'high', 'extreme'),
  volatility VARCHAR(20),
  atr VARCHAR(20),
  position_multiplier VARCHAR(20),
  reason TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 集成指南

### 前端集成

#### 1. 替换Dashboard模拟数据

在 `client/src/components/RiskMonitorCard.tsx` 中：

```typescript
// 旧代码（模拟数据）
const mockData = {
  volatility: { atr: 150, historical: 0.03, trend: "stable" },
  riskLevel: "medium",
  positionMultiplier: 0.7,
  isPaused: false
};

// 新代码（真实数据）
import { trpc } from "@/lib/trpc";

const { data, isLoading } = trpc.riskData.getCurrentRisk.useQuery(
  undefined,
  { refetchInterval: 5000 } // 每5秒刷新
);

if (isLoading) return <Skeleton />;
if (!data?.success) return <ErrorMessage />;

const riskData = data.data;
```

#### 2. 替换风险分析页面模拟数据

在 `client/src/pages/RiskAnalysis.tsx` 中：

```typescript
// 旧代码（模拟数据）
const mockHistory = generateMockData();

// 新代码（真实数据）
const { data, isLoading } = trpc.riskData.getRiskHistory.useQuery();

if (isLoading) return <Loading />;
if (!data?.success) return <ErrorMessage />;

const historyData = data.data;
```

---

### Python模块集成

#### 1. 保存风险事件到数据库

在风险管理模块中添加数据库写入：

```python
import mysql.connector
from datetime import datetime

def save_risk_event(event_type, risk_level, volatility, atr, position_mult, reason):
    """保存风险事件到数据库"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "trading_dashboard")
        )
        
        cursor = conn.cursor()
        sql = """
        INSERT INTO risk_history 
        (event_type, risk_level, volatility, atr, position_multiplier, reason)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            event_type,
            risk_level,
            str(volatility),
            str(atr),
            str(position_mult),
            reason
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"[DB] 保存风险事件失败: {e}")
        return False

# 使用示例
save_risk_event(
    event_type="pause",
    risk_level="extreme",
    volatility=0.125,
    atr=250.5,
    position_mult=0.0,
    reason="波动率过高，自动暂停交易"
)
```

#### 2. 读取风险配置

```python
def load_risk_config():
    """从数据库读取风险配置"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "trading_dashboard")
        )
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM risk_config ORDER BY id DESC LIMIT 1")
        config = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if config:
            return {
                "low_vol_threshold": float(config["low_vol_threshold"]),
                "medium_vol_threshold": float(config["medium_vol_threshold"]),
                "high_vol_threshold": float(config["high_vol_threshold"]),
                "extreme_vol_threshold": float(config["extreme_vol_threshold"]),
                "low_risk_multiplier": float(config["low_risk_multiplier"]),
                "medium_risk_multiplier": float(config["medium_risk_multiplier"]),
                "high_risk_multiplier": float(config["high_risk_multiplier"]),
                "extreme_risk_multiplier": float(config["extreme_risk_multiplier"]),
                "atr_period": config["atr_period"],
                "volatility_period": config["volatility_period"],
            }
        else:
            # 返回默认配置
            return {
                "low_vol_threshold": 0.02,
                "medium_vol_threshold": 0.05,
                "high_vol_threshold": 0.08,
                "extreme_vol_threshold": 0.10,
                "low_risk_multiplier": 1.0,
                "medium_risk_multiplier": 0.7,
                "high_risk_multiplier": 0.4,
                "extreme_risk_multiplier": 0.0,
                "atr_period": 14,
                "volatility_period": 30,
            }
    except Exception as e:
        print(f"[DB] 读取风险配置失败: {e}")
        return None
```

---

## 测试

### 1. 测试API端点

```bash
# 启动开发服务器
cd /home/ubuntu/trading_dashboard
pnpm dev

# 在浏览器中访问
http://localhost:3000
```

### 2. 测试Python脚本

```bash
cd /home/ubuntu/trading_dashboard/scripts

# 测试风险状态获取
python3 get_risk_status.py

# 测试风险历史获取
python3 get_risk_history.py
```

### 3. 测试数据库

```sql
-- 查看风险配置
SELECT * FROM risk_config;

-- 查看风险历史
SELECT * FROM risk_history ORDER BY created_at DESC LIMIT 10;

-- 插入测试数据
INSERT INTO risk_history (event_type, risk_level, volatility, atr, position_multiplier, reason)
VALUES ('pause', 'extreme', '0.125', '250.5', '0.0', '测试数据');
```

---

## 下一步

1. **实现风险配置API** - 创建CRUD端点管理风险配置
2. **创建风险配置UI** - 在Dashboard添加配置对话框
3. **完善历史记录** - 在Python模块中自动保存所有风险事件
4. **添加数据验证** - 确保配置参数在合理范围内
5. **实现配置热更新** - 配置变化时通知Python进程重新加载

---

## 注意事项

1. **数据库连接** - 确保Python脚本可以连接到MySQL数据库
2. **权限配置** - 确保数据库用户有读写权限
3. **错误处理** - API端点在Python脚本失败时返回默认数据
4. **性能优化** - 考虑添加缓存减少数据库查询
5. **数据清理** - 定期清理过期的历史数据

---

## 总结

v32.0版本完成了风险管理系统的数据基础设施，包括：

- ✅ API端点（getCurrentRisk, getRiskHistory）
- ✅ Python集成脚本（get_risk_status.py, get_risk_history.py）
- ✅ 数据库Schema（risk_config, risk_history）
- ⏳ 前端集成（待实现）
- ⏳ Python模块数据持久化（待实现）

系统已具备真实数据支持的基础，可以逐步替换模拟数据实现完全的实时监控。
