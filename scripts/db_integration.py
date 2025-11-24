#!/usr/bin/env python3
"""
Database集成模块 - willTrade数据写入MySQLDatabase
用atwillPythonTrade脚本Realtime数据同步toWeb Dashboard
"""

import os
import mysql.connector
from datetime import datetime
from typing import Optional, Dict, Any
import json
import sys

# try导入WebSocket客户端（optional）
try:
 from websocket_client import WebSocketClient
 WS_AVAILABLE = True
except ImportError:
 WS_AVAILABLE = False
 print("[DB] WebSocket client not available, real-time push disabled")


class DatabaseIntegration:
 """Database集成类"""
 
 def __init__(self, enable_websocket=True):
 """
 InitializeDatabaseConnection
 
 Args:
 enable_websocket: is否enableWebSocketRealtimepush
 """
 # fromenv var读取DatabaseConfig
 self.db_url = os.getenv("DATABASE_URL", "")
 self.conn = None
 self.cursor = None
 
 # WebSocket客户端
 self.ws_client = None
 if enable_websocket and WS_AVAILABLE:
 try:
 self.ws_client = WebSocketClient()
 print("[DB] WebSocket client initialized")
 except Exception as e:
 print(f"[DB] Failed to initialize WebSocket: {e}")
 
 if self.db_url:
 self._connect()
 
 def _connect(self):
 """建立DatabaseConnection"""
 try:
 # 解析DATABASE_URL
 # 格式: mysql://user:password@host:port/database
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
 print("[DB] Database connected successfully")
 except Exception as e:
 print(f"[DB] Failed to connect to database: {e}")
 self.conn = None
 self.cursor = None
 
 def save_trade(
 self,
 symbol: str,
 direction: str,
 entry_price: float,
 exit_price: float,
 quantity: float,
 pnl: float,
 pnl_pct: float,
 fee: float = 0.0,
 entry_time: Optional[datetime] = None,
 exit_time: Optional[datetime] = None,
) -> bool:
 """
 SaveTradeRecord
 
 Args:
 symbol: Tradefor，如 XBTUSDTM
 direction: 方向，long or short
 entry_price: 入场Price
 exit_price: 出场Price
 quantity: TradeAmount
 pnl: PnL金额
 pnl_pct: PnL百分比
 fee: Fee
 entry_time: 入场Time
 exit_time: 出场Time
 
 Returns:
 bool: is否SaveSuccess
 """
 if not self.conn or not self.cursor:
 print("[DB] No database connection")
 return False
 
 try:
 entry_time = entry_time or datetime.now()
 exit_time = exit_time or datetime.now()
 
 sql = """
 INSERT INTO trades (
 symbol, direction, entryPrice, exitPrice, quantity,
 pnl, pnlPct, fee, entryTime, exitTime
) VALUES (
 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
 """
 
 values = (
 symbol,
 direction,
 str(entry_price),
 str(exit_price),
 str(quantity),
 str(pnl),
 str(pnl_pct),
 str(fee),
 entry_time,
 exit_time,
)
 
 self.cursor.execute(sql, values)
 self.conn.commit()
 print(f"[DB] Trade saved: {direction} {symbol} PnL={pnl:.2f} USDT")
 
 # WebSocketRealtimepush
 if self.ws_client:
 try:
 self.ws_client.push_trade({
 "symbol": symbol,
 "direction": direction,
 "entryPrice": entry_price,
 "exitPrice": exit_price,
 "quantity": quantity,
 "pnl": pnl,
 "pnlPct": pnl_pct,
 "fee": fee,
 "timestamp": datetime.now().isoformat(),
 })
 except Exception as e:
 print(f"[DB] WebSocket push failed: {e}")
 
 return True
 
 except Exception as e:
 print(f"[DB] Failed to save trade: {e}")
 if self.conn:
 self.conn.rollback()
 return False
 
 def update_position(
 self,
 symbol: str,
 direction: Optional[str],
 entry_price: Optional[float],
 quantity: Optional[float],
 current_price: Optional[float] = None,
) -> bool:
 """
 UpdatePositionInfo
 
 Args:
 symbol: Tradefor
 direction: 方向，long/short/None(空仓)
 entry_price: 入场Price
 quantity: PositionAmount
 current_price: CurrentPrice
 
 Returns:
 bool: is否UpdateSuccess
 """
 if not self.conn or not self.cursor:
 return False
 
 try:
 # 先Queryis否存at该symbolRecord
 self.cursor.execute(
 "SELECT id FROM positions WHERE symbol = %s LIMIT 1",
 (symbol,)
)
 existing = self.cursor.fetchone()
 
 if existing:
 # Update现HasRecord
 sql = """
 UPDATE positions SET
 direction = %s,
 entryPrice = %s,
 quantity = %s,
 currentPrice = %s,
 updatedAt = NOW()
 WHERE symbol = %s
 """
 values = (
 direction,
 str(entry_price) if entry_price else None,
 str(quantity) if quantity else None,
 str(current_price) if current_price else None,
 symbol,
)
 else:
 # Insert新Record
 sql = """
 INSERT INTO positions (
 symbol, direction, entryPrice, quantity, currentPrice
) VALUES (%s, %s, %s, %s, %s)
 """
 values = (
 symbol,
 direction,
 str(entry_price) if entry_price else None,
 str(quantity) if quantity else None,
 str(current_price) if current_price else None,
)
 
 self.cursor.execute(sql, values)
 self.conn.commit()
 print(f"[DB] Position updated: {symbol} {direction}")
 
 # WebSocketRealtimepush
 if self.ws_client:
 try:
 self.ws_client.push_position({
 "symbol": symbol,
 "direction": direction,
 "entryPrice": entry_price,
 "quantity": quantity,
 "currentPrice": current_price,
 "timestamp": datetime.now().isoformat(),
 })
 except Exception as e:
 print(f"[DB] WebSocket push failed: {e}")
 
 return True
 
 except Exception as e:
 print(f"[DB] Failed to update position: {e}")
 if self.conn:
 self.conn.rollback()
 return False
 
 def update_account_state(
 self,
 balance: float,
 profit_rate: float,
 stage: str = "stage1",
 symbol: str = "XBTUSDTM",
) -> bool:
 """
 UpdateaccountStatus
 
 Args:
 balance: CurrentBalance
 profit_rate: 盈利率
 stage: Current阶段
 symbol: Tradefor
 
 Returns:
 bool: is否UpdateSuccess
 """
 if not self.conn or not self.cursor:
 return False
 
 try:
 # 先Queryis否存atRecord
 self.cursor.execute("SELECT id FROM trading_state LIMIT 1")
 existing = self.cursor.fetchone()
 
 if existing:
 # Update现HasRecord
 sql = """
 UPDATE trading_state SET
 balance = %s,
 profitRate = %s,
 stage = %s,
 symbol = %s,
 updatedAt = NOW()
 WHERE id = %s
 """
 values = (str(balance), str(profit_rate), stage, symbol, existing["id"])
 else:
 # Insert新Record
 sql = """
 INSERT INTO trading_state (balance, profitRate, stage, symbol)
 VALUES (%s, %s, %s, %s)
 """
 values = (str(balance), str(profit_rate), stage, symbol)
 
 self.cursor.execute(sql, values)
 self.conn.commit()
 print(f"[DB] Account state updated: balance={balance:.2f}, profit={profit_rate:.2f}%")
 
 # WebSocketRealtimepush
 if self.ws_client:
 try:
 self.ws_client.push_account({
 "balance": balance,
 "profitRate": profit_rate,
 "stage": stage,
 "symbol": symbol,
 "timestamp": datetime.now().isoformat(),
 })
 except Exception as e:
 print(f"[DB] WebSocket push failed: {e}")
 
 return True
 
 except Exception as e:
 print(f"[DB] Failed to update account state: {e}")
 if self.conn:
 self.conn.rollback()
 return False
 
 def close(self):
 """closeDatabaseConnection"""
 if self.cursor:
 self.cursor.close()
 if self.conn:
 self.conn.close()
 if self.ws_client:
 try:
 self.ws_client.close()
 except:
 pass
 print("[DB] Database connection closed")


# 使用示例
if __name__ == "__main__":
 # InitializeDatabase集成
 db = DatabaseIntegration()
 
 # 示例：SaveTradeRecord
 db.save_trade(
 symbol="XBTUSDTM",
 direction="long",
 entry_price=50000.0,
 exit_price=51000.0,
 quantity=0.01,
 pnl=10.0,
 pnl_pct=2.0,
 fee=0.5,
)
 
 # 示例：UpdatePosition
 db.update_position(
 symbol="XBTUSDTM",
 direction="long",
 entry_price=50000.0,
 quantity=0.01,
 current_price=50500.0,
)
 
 # 示例：UpdateaccountStatus
 db.update_account_state(
 balance=11.0,
 profit_rate=10.0,
 stage="stage1",
)
 
 # closeConnection
 db.close()
