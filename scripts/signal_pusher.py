#!/usr/bin/env python3
"""
WebSocketSignalpush模块
用atfromPythonTrade脚本向Web前端pushRealtimeTradeSignal
"""

import requests
import json
from datetime import datetime

class SignalPusher:
 """Signalpush器"""
 
 def __init__(self, websocket_url="http://localhost:3000"):
 self.websocket_url = websocket_url
 self.api_url = f"{websocket_url}/api/signal"
 
 def push_signal(self, signal_type, data):
 """
 pushSignaltoWebSocketserver
 
 Args:
 signal_type: Signal类型 ('open', 'close', 'alert')
 data: Signal数据字典
 """
 try:
 payload = {
 "type": signal_type,
 "data": data,
 "timestamp": datetime.now().isoformat()
 }
 
 response = requests.post(
 self.api_url,
 json=payload,
 timeout=5
)
 
 if response.status_code == 200:
 print(f"[Signalpush] Successpush {signal_type} Signal")
 return True
 else:
 print(f"[Signalpush] Failed: {response.status_code}")
 return False
 
 except Exception as e:
 print(f"[Signalpush] : {e}")
 return False
 
 def push_open_signal(self, symbol, side, price, quantity):
 """push开仓Signal"""
 return self.push_signal("open", {
 "symbol": symbol,
 "side": side,
 "price": price,
 "quantity": quantity
 })
 
 def push_close_signal(self, symbol, side, entry_price, exit_price, pnl, pnl_pct):
 """pushClose positionSignal"""
 return self.push_signal("close", {
 "symbol": symbol,
 "side": side,
 "entryPrice": entry_price,
 "exitPrice": exit_price,
 "pnl": pnl,
 "pnlPct": pnl_pct
 })
 
 def push_alert(self, level, message):
 """
 pushWarningSignal
 
 Args:
 level: Warning级别 ('info', 'warning', 'error')
 message: WarningMessage
 """
 return self.push_signal("alert", {
 "level": level,
 "message": message
 })

# 使用示例
if __name__ == "__main__":
 pusher = SignalPusher()
 
 # 测试开仓Signal
 pusher.push_open_signal(
 symbol="XBTUSDTM",
 side="long",
 price=50000.0,
 quantity=0.001
)
 
 # 测试Close positionSignal
 pusher.push_close_signal(
 symbol="XBTUSDTM",
 side="long",
 entry_price=50000.0,
 exit_price=51000.0,
 pnl=10.0,
 pnl_pct=0.02
)
 
 # 测试WarningSignal
 pusher.push_alert("warning", "PositionRisk过高")
