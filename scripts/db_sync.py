#!/usr/bin/env python3
"""
数据库同步模块
用于将交易数据写入MySQL数据库
"""

import os
import mysql.connector
from datetime import datetime
from typing import Optional

class DatabaseSync:
    def __init__(self):
        # 从环境变量读取数据库连接信息
        database_url = os.getenv('DATABASE_URL', '')
        
        # 解析DATABASE_URL (格式: mysql://user:pass@host:port/dbname)
        if database_url.startswith('mysql://'):
            # 移除mysql://前缀
            url = database_url[8:]
            
            # 分离用户信息和主机信息
            if '@' in url:
                user_info, host_info = url.split('@', 1)
                
                # 解析用户名和密码
                if ':' in user_info:
                    user, password = user_info.split(':', 1)
                else:
                    user = user_info
                    password = ''
                
                # 解析主机、端口和数据库
                if '/' in host_info:
                    host_port, database = host_info.split('/', 1)
                    
                    # 移除查询参数
                    if '?' in database:
                        database = database.split('?')[0]
                    
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                        port = int(port)
                    else:
                        host = host_port
                        port = 3306
                else:
                    host = host_info
                    port = 3306
                    database = ''
                
                self.config = {
                    'host': host,
                    'port': port,
                    'user': user,
                    'password': password,
                    'database': database,
                }
            else:
                raise ValueError("Invalid DATABASE_URL format")
        else:
            raise ValueError("DATABASE_URL must start with mysql://")
        
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            print(f"[DB] Connected to {self.config['host']}:{self.config['port']}/{self.config['database']}")
            return True
        except Exception as e:
            print(f"[DB] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("[DB] Disconnected")
    
    def update_bot_state(self, is_running: int, capital: float, initial_capital: float, 
                        current_stage: str, total_profit: float, total_trades: int,
                        win_trades: int, emergency_stopped: int = 0):
        """更新机器人状态"""
        try:
            # 检查是否存在记录
            self.cursor.execute("SELECT id FROM bot_state LIMIT 1")
            result = self.cursor.fetchone()
            
            now = datetime.now()
            
            if result:
                # 更新现有记录
                sql = """
                UPDATE bot_state SET
                    isRunning = %s,
                    capital = %s,
                    initialCapital = %s,
                    currentStage = %s,
                    totalProfit = %s,
                    totalTrades = %s,
                    winTrades = %s,
                    emergencyStopped = %s,
                    updatedAt = %s
                WHERE id = %s
                """
                self.cursor.execute(sql, (
                    is_running, capital, initial_capital, current_stage,
                    total_profit, total_trades, win_trades, emergency_stopped,
                    now, result[0]
                ))
            else:
                # 插入新记录
                sql = """
                INSERT INTO bot_state (
                    isRunning, capital, initialCapital, currentStage,
                    totalProfit, totalTrades, winTrades, emergencyStopped,
                    createdAt, updatedAt
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (
                    is_running, capital, initial_capital, current_stage,
                    total_profit, total_trades, win_trades, emergency_stopped,
                    now, now
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Failed to update bot state: {e}")
            self.conn.rollback()
            return False
    
    def create_trade(self, symbol: str, side: str, entry_price: float,
                    quantity: float, leverage: int, stage: str):
        """创建新交易记录"""
        try:
            now = datetime.now()
            sql = """
            INSERT INTO trades (
                symbol, side, entryPrice, quantity, leverage, stage,
                status, createdAt, updatedAt
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (
                symbol, side, entry_price, quantity, leverage, stage,
                'open', now, now
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"[DB] Failed to create trade: {e}")
            self.conn.rollback()
            return None
    
    def close_trade(self, trade_id: int, exit_price: float, pnl: float, pnl_pct: float):
        """关闭交易记录"""
        try:
            now = datetime.now()
            sql = """
            UPDATE trades SET
                exitPrice = %s,
                pnl = %s,
                pnlPct = %s,
                status = 'closed',
                closedAt = %s,
                updatedAt = %s
            WHERE id = %s
            """
            self.cursor.execute(sql, (
                exit_price, pnl, pnl_pct, now, now, trade_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Failed to close trade: {e}")
            self.conn.rollback()
            return False
    
    def update_position(self, symbol: str, side: Optional[str], entry_price: Optional[float],
                       quantity: Optional[float], leverage: Optional[int], stage: str,
                       unrealized_pnl: float, stop_loss_pct: float, take_profit_pct: float):
        """更新当前持仓"""
        try:
            # 检查是否存在记录
            self.cursor.execute("SELECT id FROM positions LIMIT 1")
            result = self.cursor.fetchone()
            
            now = datetime.now()
            
            if result:
                # 更新现有记录
                sql = """
                UPDATE positions SET
                    symbol = %s,
                    side = %s,
                    entryPrice = %s,
                    quantity = %s,
                    leverage = %s,
                    stage = %s,
                    unrealizedPnl = %s,
                    stopLossPct = %s,
                    takeProfitPct = %s,
                    updatedAt = %s
                WHERE id = %s
                """
                self.cursor.execute(sql, (
                    symbol, side, entry_price, quantity, leverage, stage,
                    unrealized_pnl, stop_loss_pct, take_profit_pct,
                    now, result[0]
                ))
            else:
                # 插入新记录
                sql = """
                INSERT INTO positions (
                    symbol, side, entryPrice, quantity, leverage, stage,
                    unrealizedPnl, stopLossPct, takeProfitPct,
                    createdAt, updatedAt
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (
                    symbol, side, entry_price, quantity, leverage, stage,
                    unrealized_pnl, stop_loss_pct, take_profit_pct,
                    now, now
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Failed to update position: {e}")
            self.conn.rollback()
            return False
    
    def add_balance_snapshot(self, balance: float, timestamp: Optional[datetime] = None):
        """添加余额快照"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            sql = """
            INSERT INTO balance_history (balance, timestamp)
            VALUES (%s, %s)
            """
            self.cursor.execute(sql, (balance, timestamp))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Failed to add balance snapshot: {e}")
            self.conn.rollback()
            return False


# 使用示例
if __name__ == "__main__":
    db = DatabaseSync()
    
    if db.connect():
        # 更新机器人状态
        db.update_bot_state(
            is_running=1,
            capital=11.41,
            initial_capital=10.0,
            current_stage="stage1",
            total_profit=1.41,
            total_trades=0,
            win_trades=0
        )
        
        # 添加余额快照
        db.add_balance_snapshot(11.41)
        
        db.disconnect()
