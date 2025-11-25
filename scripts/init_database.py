#!/usr/bin/env python3
"""
数据库初始化脚本
创建交易机器人所需的所有数据库表
"""

import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'trading_data.db')

def init_database():
    """初始化数据库，创建所有必需的表"""
    
    print(f"正在初始化数据库: {DB_PATH}")
    
    # 连接数据库（如果不存在会自动创建）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 创建机器人状态表
        print("创建 bot_state 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                current_balance REAL NOT NULL,
                initial_balance REAL NOT NULL,
                total_profit REAL NOT NULL,
                profit_rate REAL NOT NULL,
                current_stage TEXT NOT NULL,
                today_trades INTEGER NOT NULL DEFAULT 0,
                total_trades INTEGER NOT NULL DEFAULT 0,
                win_rate REAL,
                risk_level TEXT NOT NULL DEFAULT 'low',
                market_volatility REAL NOT NULL DEFAULT 0.0,
                suggested_position REAL NOT NULL DEFAULT 100.0
            )
        ''')
        
        # 2. 创建持仓表
        print("创建 positions 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                leverage INTEGER NOT NULL,
                margin REAL NOT NULL,
                liquidation_price REAL
            )
        ''')
        
        # 3. 创建交易记录表
        print("创建 trades 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                pnl REAL,
                pnl_rate REAL,
                status TEXT NOT NULL,
                signal_type TEXT,
                stage TEXT NOT NULL,
                reason TEXT
            )
        ''')
        
        # 4. 创建余额快照表
        print("创建 balance_snapshots 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                margin_used REAL NOT NULL,
                available_balance REAL NOT NULL
            )
        ''')
        
        # 5. 创建K线数据表（用于图表显示）
        print("创建 klines 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS klines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                ma5 REAL,
                ma20 REAL,
                UNIQUE(timestamp, symbol, interval)
            )
        ''')
        
        # 6. 创建信号记录表
        print("创建 signals 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                price REAL NOT NULL,
                ma5 REAL NOT NULL,
                ma20 REAL NOT NULL,
                reason TEXT,
                executed BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        
        # 提交更改
        conn.commit()
        
        print("\n✅ 数据库初始化成功！")
        print(f"数据库位置: {DB_PATH}")
        print("\n创建的表:")
        print("  - bot_state (机器人状态)")
        print("  - positions (持仓信息)")
        print("  - trades (交易记录)")
        print("  - balance_snapshots (余额快照)")
        print("  - klines (K线数据)")
        print("  - signals (交易信号)")
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n当前数据库中的表: {[t[0] for t in tables]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("交易机器人数据库初始化工具")
    print("=" * 60)
    print()
    
    success = init_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 初始化完成！现在可以启动交易机器人了。")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 初始化失败，请检查错误信息。")
        print("=" * 60)
