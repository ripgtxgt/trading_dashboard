#!/usr/bin/env python3
"""
WebSocket客户端模块
用于Python交易脚本实时推送数据到WebSocket服务
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket客户端，用于推送交易数据"""
    
    def __init__(self, url: str = "ws://localhost:8765"):
        """
        初始化WebSocket客户端
        
        Args:
            url: WebSocket服务器地址
        """
        self.url = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_delay = 5  # 重连延迟（秒）
        self.max_reconnect_attempts = 3  # 最大重连次数
        
    async def connect(self) -> bool:
        """
        连接到WebSocket服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            logger.info(f"已连接到WebSocket服务器: {self.url}")
            return True
        except Exception as e:
            logger.error(f"连接WebSocket服务器失败: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("已断开WebSocket连接")
    
    async def send_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        """
        发送数据到WebSocket服务器
        
        Args:
            data_type: 数据类型 (account, position, kline, risk, trade, order)
            data: 要发送的数据
            
        Returns:
            bool: 发送是否成功
        """
        if not self.connected or not self.websocket:
            logger.warning("WebSocket未连接，尝试重新连接...")
            if not await self.connect():
                return False
        
        try:
            message = {
                "type": data_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            logger.debug(f"已发送 {data_type} 数据")
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket连接已关闭")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"发送数据失败: {e}")
            return False
    
    async def push_account_update(self, balance: float, available: float, used: float):
        """
        推送账户更新
        
        Args:
            balance: 总余额
            available: 可用余额
            used: 已用余额
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
        推送持仓更新
        
        Args:
            symbol: 交易对
            side: 方向 (long/short)
            size: 持仓数量
            entry_price: 开仓价格
            unrealized_pnl: 未实现盈亏
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
        推送交易更新
        
        Args:
            trade_id: 交易ID
            symbol: 交易对
            side: 方向
            price: 成交价格
            size: 成交数量
            pnl: 盈亏
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
        推送订单更新
        
        Args:
            order_id: 订单ID
            symbol: 交易对
            side: 方向
            order_type: 订单类型
            status: 订单状态
            price: 价格
            size: 数量
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
        推送风险状态更新
        
        Args:
            is_trading_allowed: 是否允许交易
            pause_reason: 暂停原因
            daily_pnl: 今日盈亏
            total_pnl: 总盈亏
            consecutive_losses: 连续亏损次数
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
        推送K线更新
        
        Args:
            symbol: 交易对
            timeframe: 时间周期
            timestamp: 时间戳
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
    获取WebSocket客户端单例
    
    Args:
        url: WebSocket服务器地址
        
    Returns:
        WebSocketClient实例
    """
    global _ws_client
    if _ws_client is None:
        _ws_client = WebSocketClient(url)
    return _ws_client


# 同步包装函数，方便在同步代码中使用
def push_account_sync(balance: float, available: float, used: float):
    """同步推送账户更新"""
    client = get_websocket_client()
    try:
        asyncio.get_event_loop().run_until_complete(
            client.push_account_update(balance, available, used)
        )
    except Exception as e:
        logger.error(f"推送账户更新失败: {e}")


def push_position_sync(symbol: str, side: str, size: float, 
                       entry_price: float, unrealized_pnl: float):
    """同步推送持仓更新"""
    client = get_websocket_client()
    try:
        asyncio.get_event_loop().run_until_complete(
            client.push_position_update(symbol, side, size, entry_price, unrealized_pnl)
        )
    except Exception as e:
        logger.error(f"推送持仓更新失败: {e}")


def push_trade_sync(trade_id: str, symbol: str, side: str,
                   price: float, size: float, pnl: float):
    """同步推送交易更新"""
    client = get_websocket_client()
    try:
        asyncio.get_event_loop().run_until_complete(
            client.push_trade_update(trade_id, symbol, side, price, size, pnl)
        )
    except Exception as e:
        logger.error(f"推送交易更新失败: {e}")


def push_risk_sync(is_trading_allowed: bool, pause_reason: Optional[str],
                  daily_pnl: float, total_pnl: float, consecutive_losses: int):
    """同步推送风险状态更新"""
    client = get_websocket_client()
    try:
        asyncio.get_event_loop().run_until_complete(
            client.push_risk_update(is_trading_allowed, pause_reason, 
                                   daily_pnl, total_pnl, consecutive_losses)
        )
    except Exception as e:
        logger.error(f"推送风险状态失败: {e}")


# 测试代码
if __name__ == "__main__":
    async def test_websocket():
        """测试WebSocket客户端"""
        client = get_websocket_client()
        
        # 连接
        if await client.connect():
            print("✅ WebSocket连接成功")
            
            # 测试推送账户数据
            await client.push_account_update(100.0, 80.0, 20.0)
            print("✅ 推送账户数据")
            
            # 测试推送持仓数据
            await client.push_position_update("XBTUSDTM", "long", 0.001, 50000.0, 10.5)
            print("✅ 推送持仓数据")
            
            # 测试推送交易数据
            await client.push_trade_update("trade_001", "XBTUSDTM", "buy", 50000.0, 0.001, 10.5)
            print("✅ 推送交易数据")
            
            # 测试推送风险数据
            await client.push_risk_update(True, None, 10.5, 25.3, 0)
            print("✅ 推送风险数据")
            
            # 断开连接
            await client.disconnect()
            print("✅ WebSocket断开连接")
        else:
            print("❌ WebSocket连接失败")
    
    # 运行测试
    asyncio.run(test_websocket())
