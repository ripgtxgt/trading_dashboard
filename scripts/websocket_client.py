#!/usr/bin/env python3
"""
WebSocket客户端模块
用atPythonTrade脚本Realtimepush数据toWebSocket服务
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Config日志
logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebSocketClient:
 """WebSocket客户端，用atpushTrade数据"""
 
 def __init__(self, url: str = "ws://localhost:8765"):
 """
 InitializeWebSocket客户端
 
 Args:
 url: WebSocketserver地址
 """
 self.url = url
 self.websocket: Optional[websockets.WebSocketClientProtocol] = None
 self.connected = False
 self.reconnect_delay = 5 # 重连延迟（second）
 self.max_reconnect_attempts = 3 # Max重连count
 
 async def connect(self) -> bool:
 """
 ConnectiontoWebSocketserver
 
 Returns:
 bool: Connectionis否Success
 """
 try:
 self.websocket = await websockets.connect(self.url)
 self.connected = True
 logger.info(f"AlreadyConnectiontoWebSocketserver: {self.url}")
 return True
 except Exception as e:
 logger.error(f"ConnectionWebSocketserverFailed: {e}")
 self.connected = False
 return False
 
 async def disconnect(self):
 """disconnectWebSocketConnection"""
 if self.websocket:
 await self.websocket.close()
 self.connected = False
 logger.info("AlreadydisconnectWebSocketConnection")
 
 async def send_data(self, data_type: str, data: Dict[str, Any]) -> bool:
 """
 Send数据toWebSocketserver
 
 Args:
 data_type: 数据类型 (account, position, kline, risk, trade, order)
 data: 要Send数据
 
 Returns:
 bool: Sendis否Success
 """
 if not self.connected or not self.websocket:
 logger.warning("WebSocketNotConnectiontryre-Connection...")
 if not await self.connect():
 return False
 
 try:
 message = {
 "type": data_type,
 "data": data,
 "timestamp": datetime.now().isoformat()
 }
 
 await self.websocket.send(json.dumps(message))
 logger.debug(f"AlreadySend {data_type} ")
 return True
 
 except websockets.exceptions.ConnectionClosed:
 logger.error("WebSocketConnectionAlreadyclose")
 self.connected = False
 return False
 except Exception as e:
 logger.error(f"SendFailed: {e}")
 return False
 
 async def push_account_update(self, balance: float, available: float, used: float):
 """
 pushaccountUpdate
 
 Args:
 balance: 总Balance
 available: 可用Balance
 used: Already用Balance
 """
 data = {
 "balance": balance,
 "available": available,
 "used": used,
 "currency": "USDT"
 }
 return await self.send_data("account", data)
 
 async def push_position_update(self, symbol: str, side: str, size: float, 
 entry_price: float, unrealized_pnl: float):
 """
 pushPositionUpdate
 
 Args:
 symbol: Tradefor
 side: 方向 (long/short)
 size: PositionAmount
 entry_price: 开仓Price
 unrealized_pnl: Not实现PnL
 """
 data = {
 "symbol": symbol,
 "side": side,
 "size": size,
 "entry_price": entry_price,
 "unrealized_pnl": unrealized_pnl
 }
 return await self.send_data("position", data)
 
 async def push_trade_update(self, trade_id: str, symbol: str, side: str,
 price: float, size: float, pnl: float):
 """
 pushTradeUpdate
 
 Args:
 trade_id: TradeID
 symbol: Tradefor
 side: 方向
 price: 成交Price
 size: 成交Amount
 pnl: PnL
 """
 data = {
 "trade_id": trade_id,
 "symbol": symbol,
 "side": side,
 "price": price,
 "size": size,
 "pnl": pnl
 }
 return await self.send_data("trade", data)
 
 async def push_order_update(self, order_id: str, symbol: str, side: str,
 order_type: str, status: str, price: float, size: float):
 """
 pushOrderUpdate
 
 Args:
 order_id: OrderID
 symbol: Tradefor
 side: 方向
 order_type: Order类型
 status: OrderStatus
 price: Price
 size: Amount
 """
 data = {
 "order_id": order_id,
 "symbol": symbol,
 "side": side,
 "type": order_type,
 "status": status,
 "price": price,
 "size": size
 }
 return await self.send_data("order", data)
 
 async def push_risk_update(self, is_trading_allowed: bool, pause_reason: Optional[str],
 daily_pnl: float, total_pnl: float, consecutive_losses: int):
 """
 pushRiskStatusUpdate
 
 Args:
 is_trading_allowed: is否允许Trade
 pause_reason: Pausereason
 daily_pnl: 今日PnL
 total_pnl: 总PnL
 consecutive_losses: consecutiveLosscount
 """
 data = {
 "is_trading_allowed": is_trading_allowed,
 "pause_reason": pause_reason,
 "daily_pnl": daily_pnl,
 "total_pnl": total_pnl,
 "consecutive_losses": consecutive_losses
 }
 return await self.send_data("risk", data)
 
 async def push_kline_update(self, symbol: str, timeframe: str, timestamp: int,
 open_price: float, high: float, low: float, 
 close: float, volume: float):
 """
 pushK线Update
 
 Args:
 symbol: Tradefor
 timeframe: Timecycle
 timestamp: Time戳
 open_price: 开盘价
 high: 最高价
 low: 最低价
 close: 收盘价
 volume: 成交量
 """
 data = {
 "symbol": symbol,
 "timeframe": timeframe,
 "timestamp": timestamp,
 "open": open_price,
 "high": high,
 "low": low,
 "close": close,
 "volume": volume
 }
 return await self.send_data("kline", data)


# 全局WebSocket客户端实例
_ws_client: Optional[WebSocketClient] = None


def get_websocket_client(url: str = "ws://localhost:8765") -> WebSocketClient:
 """
 GetWebSocket客户端单例
 
 Args:
 url: WebSocketserver地址
 
 Returns:
 WebSocketClient实例
 """
 global _ws_client
 if _ws_client is None:
 _ws_client = WebSocketClient(url)
 return _ws_client


# 同步包装函数，方便at同步代码in使用
def push_account_sync(balance: float, available: float, used: float):
 """同步pushaccountUpdate"""
 client = get_websocket_client()
 try:
 asyncio.get_event_loop().run_until_complete(
 client.push_account_update(balance, available, used)
)
 except Exception as e:
 logger.error(f"pushaccountUpdateFailed: {e}")


def push_position_sync(symbol: str, side: str, size: float, 
 entry_price: float, unrealized_pnl: float):
 """同步pushPositionUpdate"""
 client = get_websocket_client()
 try:
 asyncio.get_event_loop().run_until_complete(
 client.push_position_update(symbol, side, size, entry_price, unrealized_pnl)
)
 except Exception as e:
 logger.error(f"pushPositionUpdateFailed: {e}")


def push_trade_sync(trade_id: str, symbol: str, side: str,
 price: float, size: float, pnl: float):
 """同步pushTradeUpdate"""
 client = get_websocket_client()
 try:
 asyncio.get_event_loop().run_until_complete(
 client.push_trade_update(trade_id, symbol, side, price, size, pnl)
)
 except Exception as e:
 logger.error(f"pushTradeUpdateFailed: {e}")


def push_risk_sync(is_trading_allowed: bool, pause_reason: Optional[str],
 daily_pnl: float, total_pnl: float, consecutive_losses: int):
 """同步pushRiskStatusUpdate"""
 client = get_websocket_client()
 try:
 asyncio.get_event_loop().run_until_complete(
 client.push_risk_update(is_trading_allowed, pause_reason, 
 daily_pnl, total_pnl, consecutive_losses)
)
 except Exception as e:
 logger.error(f"pushRiskStatusFailed: {e}")


# 测试代码
if __name__ == "__main__":
 async def test_websocket():
 """测试WebSocket客户端"""
 client = get_websocket_client()
 
 # Connection
 if await client.connect():
 print("[OK] WebSocketConnectionSuccess")
 
 # 测试pushaccount数据
 await client.push_account_update(100.0, 80.0, 20.0)
 print("[OK] pushaccount")
 
 # 测试pushPosition数据
 await client.push_position_update("XBTUSDTM", "long", 0.001, 50000.0, 10.5)
 print("[OK] pushPosition")
 
 # 测试pushTrade数据
 await client.push_trade_update("trade_001", "XBTUSDTM", "buy", 50000.0, 0.001, 10.5)
 print("[OK] pushTrade")
 
 # 测试pushRisk数据
 await client.push_risk_update(True, None, 10.5, 25.3, 0)
 print("[OK] pushRisk")
 
 # disconnectConnection
 await client.disconnect()
 print("[OK] WebSocketdisconnectConnection")
 else:
 print("[ERROR] WebSocketConnectionFailed")
 
 # Running测试
 asyncio.run(test_websocket())
