#!/usr/bin/env python3
"""
WebSocket信号推送模块
用于从Python交易脚本向Web前端推送实时交易信号
"""

import requests
import json
from datetime import datetime

class SignalPusher:
    """信号推送器"""
    
    def __init__(self, websocket_url="http://localhost:3000"):
        self.websocket_url = websocket_url
        self.api_url = f"{websocket_url}/api/signal"
    
    def push_signal(self, signal_type, data):
        """
        推送信号到WebSocket服务器
        
        Args:
            signal_type: 信号类型 ('open', 'close', 'alert')
            data: 信号数据字典
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
                print(f"[信号推送] 成功推送 {signal_type} 信号")
                return True
            else:
                print(f"[信号推送] 失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[信号推送] 异常: {e}")
            return False
    
    def push_open_signal(self, symbol, side, price, quantity):
        """推送开仓信号"""
        return self.push_signal("open", {
            "symbol": symbol,
            "side": side,
            "price": price,
            "quantity": quantity
        })
    
    def push_close_signal(self, symbol, side, entry_price, exit_price, pnl, pnl_pct):
        """推送平仓信号"""
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
        推送警告信号
        
        Args:
            level: 警告级别 ('info', 'warning', 'error')
            message: 警告消息
        """
        return self.push_signal("alert", {
            "level": level,
            "message": message
        })

# 使用示例
if __name__ == "__main__":
    pusher = SignalPusher()
    
    # 测试开仓信号
    pusher.push_open_signal(
        symbol="XBTUSDTM",
        side="long",
        price=50000.0,
        quantity=0.001
    )
    
    # 测试平仓信号
    pusher.push_close_signal(
        symbol="XBTUSDTM",
        side="long",
        entry_price=50000.0,
        exit_price=51000.0,
        pnl=10.0,
        pnl_pct=0.02
    )
    
    # 测试警告信号
    pusher.push_alert("warning", "仓位风险过高")
