#!/usr/bin/env python3
"""
集成WebSocketTrade机器人示例
演示如何atTrade脚本inRealtimepush数据
"""

import asyncio
import time
from typing import Dict, Any
from websocket_client import get_websocket_client
from risk_manager import RiskManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingBotWithWebSocket:
 """集成WebSocketpushTrade机器人"""
 
 def __init__(self, ws_url: str = "ws://localhost:8765"):
 """
 InitializeTrade机器人
 
 Args:
 ws_url: WebSocketserver地址
 """
 self.ws_client = get_websocket_client(ws_url)
 self.risk_manager = RiskManager()
 self.is_running = False
 self.balance = 100.0 # 初始Balance
 self.positions = [] # Position列表
 
 async def start(self):
 """StartTrade机器人"""
 logger.info("StartTrade...")
 
 # ConnectionWebSocket
 if not await self.ws_client.connect():
 logger.error("WebSocketConnectionFailedNoStart")
 return
 
 self.is_running = True
 logger.info("TradeAlreadyStart")
 
 # push初始Status
 await self.push_account_status()
 await self.push_risk_status()
 
 # 主循环
 try:
 while self.is_running:
 await self.trading_loop()
 await asyncio.sleep(5) # 每5secondExecute一times
 finally:
 await self.ws_client.disconnect()
 
 async def stop(self):
 """StopTrade机器人"""
 logger.info("StopTrade...")
 self.is_running = False
 
 async def trading_loop(self):
 """Trade主循环"""
 try:
 # 1. 检查RiskStatus
 risk_status = self.risk_manager.get_risk_status()
 
 if not risk_status['is_trading_allowed']:
 logger.warning(f"TradeAlreadyPause: {risk_status['pause_reason']}")
 await self.push_risk_status()
 return
 
 # 2. Get市场数据
 # (这里should该调用真实APIGet数据)
 market_price = 50000.0 # 示例Price
 
 # 3. 生成TradeSignal
 signal = self.generate_signal(market_price)
 
 # 4. ExecuteTrade
 if signal:
 await self.execute_trade(signal, market_price)
 
 # 5. UpdatePosition
 await self.update_positions(market_price)
 
 # 6. pushStatusUpdate
 await self.push_account_status()
 await self.push_risk_status()
 
 except Exception as e:
 logger.error(f"TradeError: {e}")
 
 def generate_signal(self, price: float) -> Dict[str, Any] | None:
 """
 生成TradeSignal
 
 Args:
 price: CurrentPrice
 
 Returns:
 TradeSignalorNone
 """
 # 这里should该实现真实Strategy逻辑
 # 示例：随机生成Signal
 import random
 if random.random() < 0.1: # 10%概率生成Signal
 return {
 "side": random.choice(["buy", "sell"]),
 "size": 0.001,
 "price": price
 }
 return None
 
 async def execute_trade(self, signal: Dict[str, Any], price: float):
 """
 ExecuteTrade
 
 Args:
 signal: TradeSignal
 price: CurrentPrice
 """
 try:
 logger.info(f"ExecuteTrade: {signal}")
 
 # 1. 创建Order
 order_id = f"order_{int(time.time())}"
 
 # pushOrder创建
 await self.ws_client.push_order_update(
 order_id=order_id,
 symbol="XBTUSDTM",
 side=signal["side"],
 order_type="market",
 status="submitted",
 price=price,
 size=signal["size"]
)
 
 # 2. 模拟Order成交
 await asyncio.sleep(0.5)
 
 # pushOrder成交
 await self.ws_client.push_order_update(
 order_id=order_id,
 symbol="XBTUSDTM",
 side=signal["side"],
 order_type="market",
 status="filled",
 price=price,
 size=signal["size"]
)
 
 # 3. UpdatePosition
 if signal["side"] == "buy":
 self.positions.append({
 "symbol": "XBTUSDTM",
 "side": "long",
 "size": signal["size"],
 "entry_price": price,
 "unrealized_pnl": 0.0
 })
 else:
 # Close position逻辑
 if self.positions:
 position = self.positions.pop(0)
 pnl = (price - position["entry_price"]) * signal["size"] * 10 # 简化Calculate
 
 # pushTradeRecord
 await self.ws_client.push_trade_update(
 trade_id=f"trade_{int(time.time())}",
 symbol="XBTUSDTM",
 side=signal["side"],
 price=price,
 size=signal["size"],
 pnl=pnl
)
 
 # UpdateBalance
 self.balance += pnl
 
 # RecordtoRisk管理器
 self.risk_manager.record_trade(pnl, pnl > 0)
 
 logger.info(f"TradeExecuteSuccess: {order_id}")
 
 except Exception as e:
 logger.error(f"ExecuteTradeFailed: {e}")
 
 async def update_positions(self, current_price: float):
 """
 UpdatePositionInfo
 
 Args:
 current_price: CurrentPrice
 """
 for position in self.positions:
 # CalculateNot实现PnL
 position["unrealized_pnl"] = (
 (current_price - position["entry_price"]) * 
 position["size"] * 10
)
 
 # pushPositionUpdate
 await self.ws_client.push_position_update(
 symbol=position["symbol"],
 side=position["side"],
 size=position["size"],
 entry_price=position["entry_price"],
 unrealized_pnl=position["unrealized_pnl"]
)
 
 async def push_account_status(self):
 """pushaccountStatus"""
 used = sum(p["entry_price"] * p["size"] for p in self.positions)
 available = self.balance - used
 
 await self.ws_client.push_account_update(
 balance=self.balance,
 available=available,
 used=used
)
 
 async def push_risk_status(self):
 """pushRiskStatus"""
 risk_status = self.risk_manager.get_risk_status()
 
 await self.ws_client.push_risk_update(
 is_trading_allowed=risk_status['is_trading_allowed'],
 pause_reason=risk_status.get('pause_reason'),
 daily_pnl=risk_status['daily_pnl'],
 total_pnl=risk_status['total_pnl'],
 consecutive_losses=risk_status['consecutive_losses']
)


async def main():
 """主函数"""
 bot = TradingBotWithWebSocket()
 
 try:
 await bot.start()
 except KeyboardInterrupt:
 logger.info("Receivetostop signal")
 await bot.stop()


if __name__ == "__main__":
 print("=" * 60)
 print("WebSocketTrade")
 print("=" * 60)
 print("\ndescription:")
 print("- RealtimepushaccountBalance")
 print("- RealtimepushPositionInfo")
 print("- RealtimepushOrderStatus")
 print("- RealtimepushTradeRecord")
 print("- RealtimepushRiskStatus")
 print("\n Ctrl+C StopRunning\n")
 print("=" * 60)
 
 asyncio.run(main())
