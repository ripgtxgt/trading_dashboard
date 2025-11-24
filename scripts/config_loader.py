#!/usr/bin/env python3
"""
ConfigLoad模块 - fromDatabase读取StrategyConfig
支持RealtimefromDatabaseLoad最新StrategyParameter
"""

import os
import mysql.connector
from typing import Optional, Dict, Any
import time


class ConfigLoader:
 """ConfigLoad器"""
 
 def __init__(self):
 """InitializeConfigLoad器"""
 self.db_url = os.getenv("DATABASE_URL", "")
 self.conn = None
 self.cursor = None
 self.last_config = None
 self.last_load_time = 0
 self.cache_duration = 5 # 缓存5second，避免频繁Query
 
 if self.db_url:
 self._connect()
 
 def _connect(self):
 """建立DatabaseConnection"""
 try:
 if self.db_url.startswith("mysql://"):
 url = self.db_url.replace("mysql://", "")
 if "@" in url:
 auth, location = url.split("@")
 user, password = auth.split(":")
 host_port, database = location.split("/")
 
 if ":" in host_port:
 host, port = host_port.split(":")
 port = int(port)
 else:
 host = host_port
 port = 3306
 
 self.conn = mysql.connector.connect(
 host=host,
 port=port,
 user=user,
 password=password,
 database=database
)
 self.cursor = self.conn.cursor(dictionary=True)
 print("[Config] Database connected")
 except Exception as e:
 print(f"[Config] Failed to connect: {e}")
 self.conn = None
 self.cursor = None
 
 def load_config(self, force_reload=False) -> Optional[Dict[str, Any]]:
 """
 LoadStrategyConfig
 
 Args:
 force_reload: is否强制re-Load（忽略缓存）
 
 Returns:
 Config字典，如果LoadFailed返回None
 """
 # 检查缓存
 current_time = time.time()
 if (
 not force_reload
 and self.last_config
 and (current_time - self.last_load_time) < self.cache_duration
):
 return self.last_config
 
 if not self.conn or not self.cursor:
 print("[Config] No database connection")
 return self.last_config # 返回缓存Config
 
 try:
 self.cursor.execute("SELECT * FROM strategy_config LIMIT 1")
 result = self.cursor.fetchone()
 
 if result:
 # 转换asPython友好格式
 config = {
 "symbol": result["symbol"],
 "roll_multiplier": float(result["rollMultiplier"]),
 "take_profit_pct": float(result["takeProfitPct"]),
 "stop_loss_pct": float(result["stopLossPct"]),
 "max_daily_loss": float(result["maxDailyLoss"]),
 "max_drawdown": float(result["maxDrawdown"]),
 "consecutive_loss_limit": result["consecutiveLossLimit"],
 "leverage": result["leverage"],
 "position_size": float(result["positionSize"]),
 "is_active": result["isActive"] == "true",
 }
 
 self.last_config = config
 self.last_load_time = current_time
 print(f"[Config] Loaded: {config}")
 return config
 else:
 print("[Config] No configuration found in database")
 return None
 
 except Exception as e:
 print(f"[Config] Failed to load config: {e}")
 return self.last_config # 返回缓存Config
 
 def get_param(self, key: str, default: Any = None) -> Any:
 """
 Get单ConfigParameter
 
 Args:
 key: Parameter键名
 default: default值
 
 Returns:
 Parameter值
 """
 config = self.load_config()
 if config:
 return config.get(key, default)
 return default
 
 def is_active(self) -> bool:
 """检查Strategyis否enable"""
 return self.get_param("is_active", True)
 
 def close(self):
 """closeDatabaseConnection"""
 if self.cursor:
 self.cursor.close()
 if self.conn:
 self.conn.close()
 print("[Config] Connection closed")


# 全局ConfigLoad器实例
_global_loader = None


def get_config_loader() -> ConfigLoader:
 """Get全局ConfigLoad器实例"""
 global _global_loader
 if _global_loader is None:
 _global_loader = ConfigLoader()
 return _global_loader


# 使用示例
if __name__ == "__main__":
 loader = ConfigLoader()
 
 # Load完整Config
 config = loader.load_config()
 if config:
 print("\n=== StrategyConfig ===")
 print(f"Tradefor: {config['symbol']}")
 print(f": {config['roll_multiplier']}")
 print(f"Take profit: {config['take_profit_pct']}%")
 print(f"Stop loss: {config['stop_loss_pct']}%")
 print(f"MaxdailyLoss: {config['max_daily_loss']}%")
 print(f"MaxDrawdown: {config['max_drawdown']}%")
 print(f"consecutiveLosslimit: {config['consecutive_loss_limit']}")
 print(f": {config['leverage']}x")
 print(f"Position: {config['position_size']}")
 print(f"Strategyenable: {config['is_active']}")
 
 # Get单Parameter
 print(f"\n: {loader.get_param('roll_multiplier', 2.0)}")
 print(f"Strategyisenable: {loader.is_active()}")
 
 loader.close()
