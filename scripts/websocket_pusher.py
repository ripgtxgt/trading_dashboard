#!/usr/bin/env python3
"""
增强的WebSocket实时数据推送服务
推送账户状态、持仓信息、K线数据和风险状态到Dashboard
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 添加父目录到路径
sys.path.append(os.path.dirname(__file__))

try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("请安装websockets: pip install websockets")
    sys.exit(1)


class WebSocketPusher:
    """WebSocket推送服务"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.running = False
    
    async def register(self, websocket):
        """注册客户端"""
        self.clients.add(websocket)
        print(f"✅ 客户端已连接，当前连接数: {len(self.clients)}")
        
        # 发送欢迎消息
        await self.send_to_client(websocket, {
            'type': 'welcome',
            'message': 'WebSocket连接成功',
            'timestamp': datetime.now().isoformat()
        })
    
    async def unregister(self, websocket):
        """注销客户端"""
        self.clients.discard(websocket)
        print(f"❌ 客户端已断开，当前连接数: {len(self.clients)}")
    
    async def send_to_client(self, websocket, data: Dict):
        """发送数据到单个客户端"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            print(f"发送失败: {e}")
    
    async def broadcast(self, data: Dict):
        """广播数据到所有客户端"""
        if not self.clients:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in self.clients:
            try:
                await websocket.send(message)
            except Exception as e:
                print(f"广播失败: {e}")
                disconnected.add(websocket)
        
        # 移除断开的客户端
        for websocket in disconnected:
            await self.unregister(websocket)
    
    async def handler(self, websocket, path):
        """WebSocket连接处理器"""
        await self.register(websocket)
        
        try:
            async for message in websocket:
                # 处理客户端消息
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    await self.send_to_client(websocket, {
                        'type': 'error',
                        'message': '无效的JSON格式'
                    })
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def handle_message(self, websocket, data: Dict):
        """处理客户端消息"""
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await self.send_to_client(websocket, {
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        elif msg_type == 'subscribe':
            # 订阅特定数据流
            channels = data.get('channels', [])
            await self.send_to_client(websocket, {
                'type': 'subscribed',
                'channels': channels
            })
    
    async def start(self):
        """启动WebSocket服务器"""
        self.running = True
        print(f"🚀 WebSocket服务器启动: ws://{self.host}:{self.port}")
        
        async with serve(self.handler, self.host, self.port):
            # 启动数据推送任务
            await asyncio.gather(
                self.push_account_status(),
                self.push_positions(),
                self.push_kline_data(),
                self.push_risk_status(),
                self.push_trade_signals()
            )
    
    async def push_account_status(self):
        """推送账户状态"""
        while self.running:
            try:
                # 获取账户状态
                account_status = await self.get_account_status()
                
                if account_status:
                    await self.broadcast({
                        'type': 'account_status',
                        'data': account_status,
                        'timestamp': datetime.now().isoformat()
                    })
                
                await asyncio.sleep(5)  # 每5秒推送一次
            except Exception as e:
                print(f"推送账户状态失败: {e}")
                await asyncio.sleep(5)
    
    async def push_positions(self):
        """推送持仓信息"""
        while self.running:
            try:
                # 获取持仓信息
                positions = await self.get_positions()
                
                if positions:
                    await self.broadcast({
                        'type': 'positions',
                        'data': positions,
                        'timestamp': datetime.now().isoformat()
                    })
                
                await asyncio.sleep(3)  # 每3秒推送一次
            except Exception as e:
                print(f"推送持仓信息失败: {e}")
                await asyncio.sleep(3)
    
    async def push_kline_data(self):
        """推送K线数据"""
        while self.running:
            try:
                # 获取最新K线
                kline = await self.get_latest_kline()
                
                if kline:
                    await self.broadcast({
                        'type': 'kline',
                        'data': kline,
                        'timestamp': datetime.now().isoformat()
                    })
                
                await asyncio.sleep(60)  # 每60秒推送一次
            except Exception as e:
                print(f"推送K线数据失败: {e}")
                await asyncio.sleep(60)
    
    async def push_risk_status(self):
        """推送风险状态"""
        while self.running:
            try:
                # 获取风险状态
                risk_status = await self.get_risk_status()
                
                if risk_status:
                    await self.broadcast({
                        'type': 'risk_status',
                        'data': risk_status,
                        'timestamp': datetime.now().isoformat()
                    })
                
                await asyncio.sleep(10)  # 每10秒推送一次
            except Exception as e:
                print(f"推送风险状态失败: {e}")
                await asyncio.sleep(10)
    
    async def push_trade_signals(self):
        """推送交易信号"""
        while self.running:
            try:
                # 检查交易信号
                signal = await self.check_trade_signal()
                
                if signal:
                    await self.broadcast({
                        'type': 'trade_signal',
                        'data': signal,
                        'timestamp': datetime.now().isoformat()
                    })
                
                await asyncio.sleep(30)  # 每30秒检查一次
            except Exception as e:
                print(f"推送交易信号失败: {e}")
                await asyncio.sleep(30)
    
    # ========== 数据获取方法 ==========
    
    async def get_account_status(self) -> Optional[Dict]:
        """获取账户状态"""
        try:
            # 从测试模式或真实API获取
            from test_mode import is_test_mode, get_simulated_exchange
            
            if is_test_mode():
                exchange = get_simulated_exchange()
                balance = exchange.get_balance()
                
                return {
                    'balance': balance['total'],
                    'available': balance['available'],
                    'used': balance['used'],
                    'currency': 'USDT',
                    'mode': 'test'
                }
            else:
                # TODO: 从真实API获取
                return None
        except Exception as e:
            print(f"获取账户状态失败: {e}")
            return None
    
    async def get_positions(self) -> Optional[List[Dict]]:
        """获取持仓信息"""
        try:
            from test_mode import is_test_mode, get_simulated_exchange
            
            if is_test_mode():
                exchange = get_simulated_exchange()
                positions = exchange.get_positions()
                return positions
            else:
                # TODO: 从真实API获取
                return []
        except Exception as e:
            print(f"获取持仓信息失败: {e}")
            return []
    
    async def get_latest_kline(self) -> Optional[Dict]:
        """获取最新K线"""
        try:
            # TODO: 从API获取最新K线
            return None
        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return None
    
    async def get_risk_status(self) -> Optional[Dict]:
        """获取风险状态"""
        try:
            from risk_manager import RiskManager
            
            # 创建风险管理器实例
            risk_manager = RiskManager()
            status = risk_manager.get_risk_status()
            
            return status
        except Exception as e:
            print(f"获取风险状态失败: {e}")
            return None
    
    async def check_trade_signal(self) -> Optional[Dict]:
        """检查交易信号"""
        try:
            # TODO: 实现信号检测逻辑
            return None
        except Exception as e:
            print(f"检查交易信号失败: {e}")
            return None
    
    def stop(self):
        """停止服务"""
        self.running = False
        print("⏹️  WebSocket服务器已停止")


async def main():
    """主函数"""
    pusher = WebSocketPusher(host='0.0.0.0', port=8765)
    
    try:
        await pusher.start()
    except KeyboardInterrupt:
        pusher.stop()
        print("\n👋 服务已关闭")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
