#!/usr/bin/env python3
"""
集成WebSocket的交易机器人示例
演示如何在交易脚本中实时推送数据
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
    """集成WebSocket推送的交易机器人"""
    
    def __init__(self, ws_url: str = "ws://localhost:8765"):
        """
        初始化交易机器人
        
        Args:
            ws_url: WebSocket服务器地址
        """
        self.ws_client = get_websocket_client(ws_url)
        self.risk_manager = RiskManager()
        self.is_running = False
        self.balance = 100.0  # 初始余额
        self.positions = []  # 持仓列表
        
    async def start(self):
        """启动交易机器人"""
        logger.info("启动交易机器人...")
        
        # 连接WebSocket
        if not await self.ws_client.connect():
            logger.error("WebSocket连接失败，无法启动")
            return
        
        self.is_running = True
        logger.info("交易机器人已启动")
        
        # 推送初始状态
        await self.push_account_status()
        await self.push_risk_status()
        
        # 主循环
        try:
            while self.is_running:
                await self.trading_loop()
                await asyncio.sleep(5)  # 每5秒执行一次
        finally:
            await self.ws_client.disconnect()
    
    async def stop(self):
        """停止交易机器人"""
        logger.info("停止交易机器人...")
        self.is_running = False
    
    async def trading_loop(self):
        """交易主循环"""
        try:
            # 1. 检查风险状态
            risk_status = self.risk_manager.get_risk_status()
            
            if not risk_status['is_trading_allowed']:
                logger.warning(f"交易已暂停: {risk_status['pause_reason']}")
                await self.push_risk_status()
                return
            
            # 2. 获取市场数据
            # (这里应该调用真实的API获取数据)
            market_price = 50000.0  # 示例价格
            
            # 3. 生成交易信号
            signal = self.generate_signal(market_price)
            
            # 4. 执行交易
            if signal:
                await self.execute_trade(signal, market_price)
            
            # 5. 更新持仓
            await self.update_positions(market_price)
            
            # 6. 推送状态更新
            await self.push_account_status()
            await self.push_risk_status()
            
        except Exception as e:
            logger.error(f"交易循环错误: {e}")
    
    def generate_signal(self, price: float) -> Dict[str, Any] | None:
        """
        生成交易信号
        
        Args:
            price: 当前价格
            
        Returns:
            交易信号或None
        """
        # 这里应该实现真实的策略逻辑
        # 示例：随机生成信号
        import random
        if random.random() < 0.1:  # 10%概率生成信号
            return {
                "side": random.choice(["buy", "sell"]),
                "size": 0.001,
                "price": price
            }
        return None
    
    async def execute_trade(self, signal: Dict[str, Any], price: float):
        """
        执行交易
        
        Args:
            signal: 交易信号
            price: 当前价格
        """
        try:
            logger.info(f"执行交易: {signal}")
            
            # 1. 创建订单
            order_id = f"order_{int(time.time())}"
            
            # 推送订单创建
            await self.ws_client.push_order_update(
                order_id=order_id,
                symbol="XBTUSDTM",
                side=signal["side"],
                order_type="market",
                status="submitted",
                price=price,
                size=signal["size"]
            )
            
            # 2. 模拟订单成交
            await asyncio.sleep(0.5)
            
            # 推送订单成交
            await self.ws_client.push_order_update(
                order_id=order_id,
                symbol="XBTUSDTM",
                side=signal["side"],
                order_type="market",
                status="filled",
                price=price,
                size=signal["size"]
            )
            
            # 3. 更新持仓
            if signal["side"] == "buy":
                self.positions.append({
                    "symbol": "XBTUSDTM",
                    "side": "long",
                    "size": signal["size"],
                    "entry_price": price,
                    "unrealized_pnl": 0.0
                })
            else:
                # 平仓逻辑
                if self.positions:
                    position = self.positions.pop(0)
                    pnl = (price - position["entry_price"]) * signal["size"] * 10  # 简化计算
                    
                    # 推送交易记录
                    await self.ws_client.push_trade_update(
                        trade_id=f"trade_{int(time.time())}",
                        symbol="XBTUSDTM",
                        side=signal["side"],
                        price=price,
                        size=signal["size"],
                        pnl=pnl
                    )
                    
                    # 更新余额
                    self.balance += pnl
                    
                    # 记录到风险管理器
                    self.risk_manager.record_trade(pnl, pnl > 0)
            
            logger.info(f"交易执行成功: {order_id}")
            
        except Exception as e:
            logger.error(f"执行交易失败: {e}")
    
    async def update_positions(self, current_price: float):
        """
        更新持仓信息
        
        Args:
            current_price: 当前价格
        """
        for position in self.positions:
            # 计算未实现盈亏
            position["unrealized_pnl"] = (
                (current_price - position["entry_price"]) * 
                position["size"] * 10
            )
            
            # 推送持仓更新
            await self.ws_client.push_position_update(
                symbol=position["symbol"],
                side=position["side"],
                size=position["size"],
                entry_price=position["entry_price"],
                unrealized_pnl=position["unrealized_pnl"]
            )
    
    async def push_account_status(self):
        """推送账户状态"""
        used = sum(p["entry_price"] * p["size"] for p in self.positions)
        available = self.balance - used
        
        await self.ws_client.push_account_update(
            balance=self.balance,
            available=available,
            used=used
        )
    
    async def push_risk_status(self):
        """推送风险状态"""
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
        logger.info("接收到停止信号")
        await bot.stop()


if __name__ == "__main__":
    print("=" * 60)
    print("集成WebSocket的交易机器人示例")
    print("=" * 60)
    print("\n功能说明:")
    print("- 实时推送账户余额变化")
    print("- 实时推送持仓信息")
    print("- 实时推送订单状态")
    print("- 实时推送交易记录")
    print("- 实时推送风险状态")
    print("\n按 Ctrl+C 停止运行\n")
    print("=" * 60)
    
    asyncio.run(main())
