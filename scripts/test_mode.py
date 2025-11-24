#!/usr/bin/env python3
"""
测试模式配置模块
提供模拟交易功能, 用于测试风险管理和策略逻辑, 无需真实资金
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import random


class TestModeConfig:
    """测试模式配置"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'test_mode_config.json')
        self.config = self._load_config()
    
    def _default_config(self) -> Dict:
        """默认测试配置"""
        return {
            'enabled': False,  # 是否启用测试模式
            'initial_balance': 100.0,  # 初始资金(USDT)
            'leverage': 10,  # 杠杆倍数
            'maker_fee': 0.0002,  # Maker手续费 0.02%
            'taker_fee': 0.0006,  # Taker手续费 0.06%
            'slippage': 0.0005,  # 滑点 0.05%
            'simulate_latency': True,  # 模拟网络延迟
            'latency_ms': 100,  # 延迟毫秒数
            'simulate_failures': False,  # 模拟订单失败
            'failure_rate': 0.01,  # 失败率 1%
        }
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"LoadConfigFailed: {e}")
                return self._default_config()
        return self._default_config()
    
    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"SaveConfigFailed: {e}")
    
    def is_enabled(self) -> bool:
        """是否启用测试模式"""
        return self.config.get('enabled', False)
    
    def enable(self):
        """启用测试模式"""
        self.config['enabled'] = True
        self._save_config()
        print("[OK] ")
    
    def disable(self):
        """禁用测试模式"""
        self.config['enabled'] = False
        self._save_config()
        print("[OK] ")
    
    def get_config(self) -> Dict:
        """获取配置"""
        return self.config.copy()
    
    def update_config(self, updates: Dict):
        """更新配置"""
        self.config.update(updates)
        self._save_config()


class SimulatedExchange:
    """模拟交易所"""
    
    def __init__(self, config: TestModeConfig):
        self.config = config
        self.balance = config.config['initial_balance']
        self.positions: List[Dict] = []
        self.orders: List[Dict] = []
        self.trades: List[Dict] = []
        self.order_id_counter = 1
        
        # 加载状态
        self._load_state()
    
    def _load_state(self):
        """加载状态"""
        state_file = os.path.join(os.path.dirname(__file__), 'test_mode_state.json')
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.balance = state.get('balance', self.config.config['initial_balance'])
                    self.positions = state.get('positions', [])
                    self.orders = state.get('orders', [])
                    self.trades = state.get('trades', [])
                    self.order_id_counter = state.get('order_id_counter', 1)
            except Exception as e:
                print(f"LoadFailed: {e}")
    
    def _save_state(self):
        """保存状态"""
        state_file = os.path.join(os.path.dirname(__file__), 'test_mode_state.json')
        try:
            state = {
                'balance': self.balance,
                'positions': self.positions,
                'orders': self.orders,
                'trades': self.trades,
                'order_id_counter': self.order_id_counter,
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"SaveFailed: {e}")
    
    def get_balance(self) -> Dict:
        """获取账户余额"""
        # 计算持仓占用保证金
        used_margin = sum(pos['margin'] for pos in self.positions)
        available = self.balance - used_margin
        
        return {
            'total': self.balance,
            'available': available,
            'used': used_margin,
            'currency': 'USDT'
        }
    
    def get_positions(self) -> List[Dict]:
        """获取持仓"""
        return self.positions.copy()
    
    def create_order(self, symbol: str, side: str, size: float, price: float, 
                     order_type: str = 'market') -> Dict:
        """创建订单"""
        
        # 模拟订单失败
        if self.config.config.get('simulate_failures', False):
            if random.random() < self.config.config.get('failure_rate', 0.01):
                return {
                    'success': False,
                    'error': '模拟订单失败'
                }
        
        # 生成订单ID
        order_id = f"TEST_{self.order_id_counter}"
        self.order_id_counter += 1
        
        # 计算滑点价格
        slippage = self.config.config.get('slippage', 0.0005)
        if side == 'buy':
            exec_price = price * (1 + slippage)
        else:
            exec_price = price * (1 - slippage)
        
        # 计算手续费
        fee_rate = self.config.config.get('taker_fee', 0.0006)
        fee = size * exec_price * fee_rate
        
        # 计算保证金
        leverage = self.config.config.get('leverage', 10)
        margin = (size * exec_price) / leverage
        
        # 检查余额
        balance_info = self.get_balance()
        if margin + fee > balance_info['available']:
            return {
                'success': False,
                'error': '余额不足'
            }
        
        # 创建订单
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'size': size,
            'price': exec_price,
            'type': order_type,
            'status': 'filled',
            'fee': fee,
            'margin': margin,
            'leverage': leverage,
            'timestamp': datetime.now().isoformat()
        }
        
        self.orders.append(order)
        
        # 创建持仓
        position = {
            'position_id': order_id,
            'symbol': symbol,
            'side': side,
            'size': size,
            'entry_price': exec_price,
            'margin': margin,
            'leverage': leverage,
            'unrealized_pnl': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.positions.append(position)
        
        # 扣除手续费
        self.balance -= fee
        
        self._save_state()
        
        return {
            'success': True,
            'order': order,
            'position': position
        }
    
    def close_position(self, position_id: str, current_price: float) -> Dict:
        """平仓"""
        
        # 查找持仓
        position = None
        for i, pos in enumerate(self.positions):
            if pos['position_id'] == position_id:
                position = pos
                position_index = i
                break
        
        if not position:
            return {
                'success': False,
                'error': '持仓不存在'
            }
        
        # 模拟订单失败
        if self.config.config.get('simulate_failures', False):
            if random.random() < self.config.config.get('failure_rate', 0.01):
                return {
                    'success': False,
                    'error': '模拟平仓失败'
                }
        
        # 计算滑点价格
        slippage = self.config.config.get('slippage', 0.0005)
        if position['side'] == 'buy':
            exec_price = current_price * (1 - slippage)
        else:
            exec_price = current_price * (1 + slippage)
        
        # 计算盈亏
        if position['side'] == 'buy':
            pnl = (exec_price - position['entry_price']) * position['size']
        else:
            pnl = (position['entry_price'] - exec_price) * position['size']
        
        # 计算手续费
        fee_rate = self.config.config.get('taker_fee', 0.0006)
        fee = position['size'] * exec_price * fee_rate
        
        # 净盈亏
        net_pnl = pnl - fee
        
        # 释放保证金
        self.balance += position['margin']
        
        # 更新余额
        self.balance += net_pnl
        
        # 记录交易
        trade = {
            'trade_id': f"TRADE_{len(self.trades) + 1}",
            'position_id': position_id,
            'symbol': position['symbol'],
            'side': position['side'],
            'size': position['size'],
            'entry_price': position['entry_price'],
            'exit_price': exec_price,
            'pnl': pnl,
            'fee': fee,
            'net_pnl': net_pnl,
            'timestamp': datetime.now().isoformat()
        }
        
        self.trades.append(trade)
        
        # 移除持仓
        self.positions.pop(position_index)
        
        self._save_state()
        
        return {
            'success': True,
            'trade': trade,
            'balance': self.balance
        }
    
    def update_positions(self, current_price: float):
        """更新持仓未实现盈亏"""
        for position in self.positions:
            if position['side'] == 'buy':
                unrealized_pnl = (current_price - position['entry_price']) * position['size']
            else:
                unrealized_pnl = (position['entry_price'] - current_price) * position['size']
            
            position['unrealized_pnl'] = unrealized_pnl
        
        self._save_state()
    
    def get_trades(self, limit: int = 100) -> List[Dict]:
        """获取交易历史"""
        return self.trades[-limit:]
    
    def reset(self):
        """重置状态"""
        self.balance = self.config.config['initial_balance']
        self.positions = []
        self.orders = []
        self.trades = []
        self.order_id_counter = 1
        self._save_state()
        print("[OK] ")


# 全局实例
_test_config = None
_simulated_exchange = None


def get_test_config() -> TestModeConfig:
    """获取测试配置实例"""
    global _test_config
    if _test_config is None:
        _test_config = TestModeConfig()
    return _test_config


def get_simulated_exchange() -> SimulatedExchange:
    """获取模拟交易所实例"""
    global _simulated_exchange
    if _simulated_exchange is None:
        _simulated_exchange = SimulatedExchange(get_test_config())
    return _simulated_exchange


def is_test_mode() -> bool:
    """是否为测试模式"""
    return get_test_config().is_enabled()


if __name__ == '__main__':
    # 测试示例
    print("===  ===\n")
    
    # 启用测试模式
    config = get_test_config()
    config.enable()
    
    # 获取模拟交易所
    exchange = get_simulated_exchange()
    
    # 查看初始余额
    balance = exchange.get_balance()
    print(f"Balance: {balance['total']} USDT")
    print(f"Balance: {balance['available']} USDT\n")
    
    # 创建订单
    print("...")
    result = exchange.create_order('XBTUSDTM', 'buy', 0.001, 50000)
    if result['success']:
        print(f"[OK] OrderSuccess: {result['order']['order_id']}")
        print(f"   Price: {result['order']['price']}")
        print(f"   : {result['order']['fee']} USDT")
        print(f"   : {result['order']['margin']} USDT\n")
    
    # 查看持仓
    positions = exchange.get_positions()
    print(f"CurrentPositionAmount: {len(positions)}")
    for pos in positions:
        print(f"  - {pos['symbol']} {pos['side']} {pos['size']} @ {pos['entry_price']}\n")
    
    # 更新持仓盈亏
    current_price = 51000
    exchange.update_positions(current_price)
    positions = exchange.get_positions()
    for pos in positions:
        print(f"Not: {pos['unrealized_pnl']:.2f} USDT\n")
    
    # 平仓
    print("Close position...")
    result = exchange.close_position(positions[0]['position_id'], current_price)
    if result['success']:
        print(f"[OK] Close positionSuccess")
        print(f"   : {result['trade']['pnl']:.2f} USDT")
        print(f"   : {result['trade']['fee']:.2f} USDT")
        print(f"   : {result['trade']['net_pnl']:.2f} USDT")
        print(f"   CurrentBalance: {result['balance']:.2f} USDT\n")
    
    # 查看交易历史
    trades = exchange.get_trades()
    print(f"TradeHistory: {len(trades)} ")
