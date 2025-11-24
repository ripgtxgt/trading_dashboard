#!/usr/bin/env python3
"""
数据库集成模块 - 将交易数据写入MySQL数据库
用于将Python交易脚本的实时数据同步到Web Dashboard
"""

import os
import mysql.connector
from datetime import datetime
from typing import Optional, Dict, Any
import json
import sys

# 尝试导入WebSocket客户端(可选)
try:
    from websocket_client import WebSocketClient
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False
    print("[DB] WebSocket client not available, real-time push disabled")


class DatabaseIntegration:
    """数据库集成类"""
    
    def __init__(self, enable_websocket=True):
        """
        初始化数据库连接
        
        Args:
            enable_websocket: 是否启用WebSocket实时推送
        """
        # 从环境变量读取数据库配置
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
        """建立数据库连接"""
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
        保存交易记录
        
        Args:
            symbol: 交易对, 如 XBTUSDTM
            direction: 方向, long 或 short
            entry_price: 入场价格
            exit_price: 出场价格
            quantity: 交易数量
            pnl: 盈亏金额
            pnl_pct: 盈亏百分比
            fee: 手续费
            entry_time: 入场时间
            exit_time: 出场时间
        
        Returns:
            bool: 是否保存成功
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
            
            # WebSocket实时推送
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
        更新持仓信息
        
        Args:
            symbol: 交易对
            direction: 方向, long/short/None(空仓)
            entry_price: 入场价格
            quantity: 持仓数量
            current_price: 当前价格
        
        Returns:
            bool: 是否更新成功
        """
        if not self.conn or not self.cursor:
            return False
        
        try:
            # 先查询是否存在该symbol的记录
            self.cursor.execute(
                "SELECT id FROM positions WHERE symbol = %s LIMIT 1",
                (symbol,)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                # 更新现有记录
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
                # 插入新记录
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
            
            # WebSocket实时推送
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
        更新账户状态
        
        Args:
            balance: 当前余额
            profit_rate: 盈利率
            stage: 当前阶段
            symbol: 交易对
        
        Returns:
            bool: 是否更新成功
        """
        if not self.conn or not self.cursor:
            return False
        
        try:
            # 先查询是否存在记录
            self.cursor.execute("SELECT id FROM trading_state LIMIT 1")
            existing = self.cursor.fetchone()
            
            if existing:
                # 更新现有记录
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
                # 插入新记录
                sql = """
                INSERT INTO trading_state (balance, profitRate, stage, symbol)
                VALUES (%s, %s, %s, %s)
                """
                values = (str(balance), str(profit_rate), stage, symbol)
            
            self.cursor.execute(sql, values)
            self.conn.commit()
            print(f"[DB] Account state updated: balance={balance:.2f}, profit={profit_rate:.2f}%")
            
            # WebSocket实时推送
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
        """关闭数据库连接"""
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
    # 初始化数据库集成
    db = DatabaseIntegration()
    
    # 示例: 保存交易记录
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
    
    # 示例: 更新持仓
    db.update_position(
        symbol="XBTUSDTM",
        direction="long",
        entry_price=50000.0,
        quantity=0.01,
        current_price=50500.0,
    )
    
    # 示例: 更新账户状态
    db.update_account_state(
        balance=11.0,
        profit_rate=10.0,
        stage="stage1",
    )
    
    # 关闭连接
    db.close()
