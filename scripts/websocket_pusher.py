#!/usr/bin/env python3
"""
Enhanced WebSocket Real-time Data Push Service
Push account status, positions, kline data and risk status to Dashboard
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

try:
 import websockets
 from websockets.server import serve
except ImportError:
 print("Please install websockets: pip install websockets")
 sys.exit(1)


class WebSocketPusher:
 """WebSocket Push Service"""
 
 def __init__(self, host: str = '0.0.0.0', port: int = 8765):
 self.host = host
 self.port = port
 self.clients = set()
 self.running = False
 
 async def register(self, websocket):
 """Register client"""
 self.clients.add(websocket)
 print(f"[+] Client connected, total: {len(self.clients)}")
 
 # Send welcome message
 await self.send_to_client(websocket, {
 'type': 'welcome',
 'message': 'WebSocket connected successfully',
 'timestamp': datetime.now().isoformat()
 })
 
 async def unregister(self, websocket):
 """Unregister client"""
 self.clients.discard(websocket)
 print(f"[-] Client disconnected, total: {len(self.clients)}")
 
 async def send_to_client(self, websocket, data: Dict):
 """Send data to single client"""
 try:
 await websocket.send(json.dumps(data))
 except Exception as e:
 print(f"Send failed: {e}")
 
 async def broadcast(self, data: Dict):
 """Broadcast data to all clients"""
 if not self.clients:
 return
 
 message = json.dumps(data)
 disconnected = set()
 
 for websocket in self.clients:
 try:
 await websocket.send(message)
 except Exception as e:
 print(f"Broadcast failed: {e}")
 disconnected.add(websocket)
 
 # Remove disconnected clients
 for websocket in disconnected:
 await self.unregister(websocket)
 
 async def handler(self, websocket, path):
 """WebSocket connection handler"""
 await self.register(websocket)
 
 try:
 async for message in websocket:
 # Handle client messages
 try:
 data = json.loads(message)
 await self.handle_message(websocket, data)
 except json.JSONDecodeError:
 await self.send_to_client(websocket, {
 'type': 'error',
 'message': 'Invalid JSON format'
 })
 except websockets.exceptions.ConnectionClosed:
 pass
 finally:
 await self.unregister(websocket)
 
 async def handle_message(self, websocket, data: Dict):
 """Handle client messages"""
 msg_type = data.get('type')
 
 if msg_type == 'ping':
 await self.send_to_client(websocket, {
 'type': 'pong',
 'timestamp': datetime.now().isoformat()
 })
 elif msg_type == 'subscribe':
 # Subscribe to specific data streams
 channels = data.get('channels', [])
 await self.send_to_client(websocket, {
 'type': 'subscribed',
 'channels': channels
 })
 
 async def start(self):
 """Start WebSocket server"""
 self.running = True
 print(f"[*] WebSocket server started: ws://{self.host}:{self.port}")
 
 async with serve(self.handler, self.host, self.port):
 # Start data push tasks
 await asyncio.gather(
 self.push_account_status(),
 self.push_positions(),
 self.push_kline_data(),
 self.push_risk_status(),
 self.push_trade_signals()
)
 
 async def push_account_status(self):
 """Push account status"""
 while self.running:
 try:
 # Get account status
 account_status = await self.get_account_status()
 
 if account_status:
 await self.broadcast({
 'type': 'account_status',
 'data': account_status,
 'timestamp': datetime.now().isoformat()
 })
 
 await asyncio.sleep(5) # Push every 5 seconds
 except Exception as e:
 print(f"Push account status failed: {e}")
 await asyncio.sleep(5)
 
 async def push_positions(self):
 """Push positions"""
 while self.running:
 try:
 # Get positions
 positions = await self.get_positions()
 
 if positions:
 await self.broadcast({
 'type': 'positions',
 'data': positions,
 'timestamp': datetime.now().isoformat()
 })
 
 await asyncio.sleep(3) # Push every 3 seconds
 except Exception as e:
 print(f"Push positions failed: {e}")
 await asyncio.sleep(3)
 
 async def push_kline_data(self):
 """Push kline data"""
 while self.running:
 try:
 # Get latest kline
 kline = await self.get_latest_kline()
 
 if kline:
 await self.broadcast({
 'type': 'kline',
 'data': kline,
 'timestamp': datetime.now().isoformat()
 })
 
 await asyncio.sleep(60) # Push every 60 seconds
 except Exception as e:
 print(f"Push kline data failed: {e}")
 await asyncio.sleep(60)
 
 async def push_risk_status(self):
 """Push risk status"""
 while self.running:
 try:
 # Get risk status
 risk_status = await self.get_risk_status()
 
 if risk_status:
 await self.broadcast({
 'type': 'risk_status',
 'data': risk_status,
 'timestamp': datetime.now().isoformat()
 })
 
 await asyncio.sleep(10) # Push every 10 seconds
 except Exception as e:
 print(f"Push risk status failed: {e}")
 await asyncio.sleep(10)
 
 async def push_trade_signals(self):
 """Push trade signals"""
 while self.running:
 try:
 # Check trade signals
 signal = await self.check_trade_signal()
 
 if signal:
 await self.broadcast({
 'type': 'trade_signal',
 'data': signal,
 'timestamp': datetime.now().isoformat()
 })
 
 await asyncio.sleep(30) # Check every 30 seconds
 except Exception as e:
 print(f"Push trade signals failed: {e}")
 await asyncio.sleep(30)
 
 # ========== Data fetching methods ==========
 
 async def get_account_status(self) -> Optional[Dict]:
 """Get account status"""
 try:
 # Get from test mode or real API
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
 # TODO: Get from real API
 return None
 except Exception as e:
 print(f"Get account status failed: {e}")
 return None
 
 async def get_positions(self) -> Optional[List[Dict]]:
 """Get positions"""
 try:
 from test_mode import is_test_mode, get_simulated_exchange
 
 if is_test_mode():
 exchange = get_simulated_exchange()
 positions = exchange.get_positions()
 return positions
 else:
 # TODO: Get from real API
 return []
 except Exception as e:
 print(f"Get positions failed: {e}")
 return []
 
 async def get_latest_kline(self) -> Optional[Dict]:
 """Get latest kline"""
 try:
 # TODO: Get latest kline from API
 return None
 except Exception as e:
 print(f"Get kline data failed: {e}")
 return None
 
 async def get_risk_status(self) -> Optional[Dict]:
 """Get risk status"""
 try:
 from risk_manager import RiskManager
 
 # Create risk manager instance
 risk_manager = RiskManager()
 status = risk_manager.get_risk_status()
 
 return status
 except Exception as e:
 print(f"Get risk status failed: {e}")
 return None
 
 async def check_trade_signal(self) -> Optional[Dict]:
 """Check trade signals"""
 try:
 # TODO: Implement signal detection logic
 return None
 except Exception as e:
 print(f"Check trade signals failed: {e}")
 return None
 
 def stop(self):
 """Stop service"""
 self.running = False
 print("[*] WebSocket server stopped")


async def main():
 """Main function"""
 pusher = WebSocketPusher(host='0.0.0.0', port=8765)
 
 try:
 await pusher.start()
 except KeyboardInterrupt:
 pusher.stop()
 print("\n[*] Service closed")


if __name__ == '__main__':
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 print("\n[*] Program exited")
