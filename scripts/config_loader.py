#!/usr/bin/env python3
"""
配置加载模块 - 从数据库读取策略配置
支持实时从数据库加载最新的策略参数
"""

import os
import mysql.connector
from typing import Optional, Dict, Any
import time


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self):
        """初始化配置加载器"""
        self.db_url = os.getenv("DATABASE_URL", "")
        self.conn = None
        self.cursor = None
        self.last_config = None
        self.last_load_time = 0
        self.cache_duration = 5  # 缓存5s, 避免频繁查询
        
        if self.db_url:
            self._connect()
    
    def _connect(self):
        """建立数据库连接"""
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
        加载策略配置
        
        Args:
            force_reload: 是否强制重新加载(忽略缓存)
        
        Returns:
            配置字典, 如果加载失败返回None
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
            return self.last_config  # 返回缓存的配置
        
        try:
            self.cursor.execute("SELECT * FROM strategy_config LIMIT 1")
            result = self.cursor.fetchone()
            
            if result:
                # 转换为Python友好的格式
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
            return self.last_config  # 返回缓存的配置
    
    def get_param(self, key: str, default: Any = None) -> Any:
        """
        获取单个配置参数
        
        Args:
            key: 参数键名
            default: 默认值
        
        Returns:
            参数值
        """
        config = self.load_config()
        if config:
            return config.get(key, default)
        return default
    
    def is_active(self) -> bool:
        """检查策略是否启用"""
        return self.get_param("is_active", True)
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("[Config] Connection closed")


# 全局配置加载器实例
_global_loader = None


def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader


# 使用示例
if __name__ == "__main__":
    loader = ConfigLoader()
    
    # 加载完整配置
    config = loader.load_config()
    if config:
        print("\n=== Config ===")
        print(f"Trade: {config['symbol']}")
        print(f": {config['roll_multiplier']}")
        print(f"Take profit: {config['take_profit_pct']}%")
        print(f"Stop loss: {config['stop_loss_pct']}%")
        print(f"Loss: {config['max_daily_loss']}%")
        print(f": {config['max_drawdown']}%")
        print(f"LossLimit: {config['consecutive_loss_limit']}")
        print(f": {config['leverage']}x")
        print(f": {config['position_size']}")
        print(f": {config['is_active']}")
    
    # 获取单个参数
    print(f"\n: {loader.get_param('roll_multiplier', 2.0)}")
    print(f": {loader.is_active()}")
    
    loader.close()
