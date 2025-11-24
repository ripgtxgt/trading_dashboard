#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10U战神滚仓管理器
负责滚仓策略的核心逻辑: 阶段管理、加仓、移动止损、分批平仓
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Position:
    """持仓信息"""
    position_id: str          # 持仓ID
    entry_price: float        # 开仓价格
    size: int                 # 持仓数量(张数)
    side: str                 # 方向: 'long' 或 'short'
    margin: float             # 保证金(USDT)
    unrealized_pnl: float     # 未实现盈亏
    stop_loss: float          # 止损价格
    take_profit: float        # 止盈价格
    stage: str                # 所属阶段
    entry_time: float         # 开仓时间戳
    last_add_time: float      # 最后加仓时间
    add_count: int            # 加仓次数
    
    def to_dict(self):
        return asdict(self)


@dataclass
class StageConfig:
    """阶段配置"""
    name: str                 # 阶段名称
    balance_min: float        # 最小余额
    balance_max: float        # 最大余额
    position_ratio: float     # 仓位比例(0-1)
    stop_loss_ratio: float    # 止损比例
    take_profit_ratio: float  # 止盈比例
    max_add_count: int        # 最大加仓次数
    add_profit_threshold: float  # 加仓盈利阈值


class RollingManager:
    """
    10U战神滚仓管理器
    
    核心功能: 
    1. 资金阶段管理(10U->80U->200U->1000U)
    2. 动态仓位计算
    3. 盈利加仓逻辑
    4. 移动止损机制
    5. 分批平仓管理
    """
    
    # 阶段配置
    STAGES = [
        StageConfig(
            name="初始阶段",
            balance_min=0,
            balance_max=20,
            position_ratio=0.5,      # 50%仓位
            stop_loss_ratio=0.20,    # 止损20%
            take_profit_ratio=1.0,   # 止盈100%
            max_add_count=1,         # 最多加仓1次
            add_profit_threshold=0.5 # 盈利50%后加仓
        ),
        StageConfig(
            name="翻倍阶段",
            balance_min=20,
            balance_max=80,
            position_ratio=0.5,      # 50%仓位
            stop_loss_ratio=0.20,
            take_profit_ratio=1.0,
            max_add_count=2,
            add_profit_threshold=0.4
        ),
        StageConfig(
            name="分仓阶段",
            balance_min=80,
            balance_max=200,
            position_ratio=0.125,    # 12.5%仓位(10U固定)
            stop_loss_ratio=0.15,
            take_profit_ratio=0.5,
            max_add_count=2,
            add_profit_threshold=0.3
        ),
        StageConfig(
            name="阶梯阶段",
            balance_min=200,
            balance_max=1000,
            position_ratio=0.1,      # 10%仓位(20U)
            stop_loss_ratio=0.15,
            take_profit_ratio=0.4,
            max_add_count=3,
            add_profit_threshold=0.25
        ),
        StageConfig(
            name="稳健阶段",
            balance_min=1000,
            balance_max=float('inf'),
            position_ratio=0.05,     # 5%仓位(50U)
            stop_loss_ratio=0.10,
            take_profit_ratio=0.3,
            max_add_count=4,
            add_profit_threshold=0.2
        ),
    ]
    
    def __init__(self, leverage: int = 100):
        """
        初始化滚仓管理器
        
        Args:
            leverage: 杠杆倍数, 默认100倍
        """
        self.leverage = leverage
        self.current_position: Optional[Position] = None
        self.balance = 0.0
        self.total_profit = 0.0
        self.trade_history: List[Dict] = []
        
        # 风险控制
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3
        self.is_paused = False
        
        print(f"[] InitializeComplete, : {leverage}x")
    
    def get_current_stage(self, balance: float) -> StageConfig:
        """
        根据余额确定当前阶段
        
        Args:
            balance: 当前余额
            
        Returns:
            当前阶段配置
        """
        for stage in self.STAGES:
            if stage.balance_min <= balance < stage.balance_max:
                return stage
        return self.STAGES[-1]  # 默认返回最后一个阶段
    
    def calculate_position_size(self, balance: float, price: float) -> Tuple[float, int]:
        """
        计算开仓大小
        
        Args:
            balance: 当前余额
            price: 当前价格
            
        Returns:
            (保证金, 张数)
        """
        stage = self.get_current_stage(balance)
        
        # 计算保证金
        margin = balance * stage.position_ratio
        
        # 计算张数(KuCoin BTC合约1张=1USD)
        # 张数 = 保证金 × 杠杆 / 价格
        size = int(margin * self.leverage)
        
        print(f"[] : {stage.name}, Balance: {balance:.2f}U, "
              f"仓位比例: {stage.position_ratio*100:.1f}%, "
              f"保证金: {margin:.2f}U, 张数: {size}")
        
        return margin, size
    
    def create_position(self, entry_price: float, size: int, side: str, 
                       margin: float, balance: float) -> Position:
        """
        创建新持仓
        
        Args:
            entry_price: 开仓价格
            size: 持仓数量
            side: 方向 'long' 或 'short'
            margin: 保证金
            balance: 当前余额
            
        Returns:
            Position对象
        """
        stage = self.get_current_stage(balance)
        
        # 计算止损止盈价格
        if side == 'long':
            stop_loss = entry_price * (1 - stage.stop_loss_ratio / self.leverage)
            take_profit = entry_price * (1 + stage.take_profit_ratio / self.leverage)
        else:  # short
            stop_loss = entry_price * (1 + stage.stop_loss_ratio / self.leverage)
            take_profit = entry_price * (1 - stage.take_profit_ratio / self.leverage)
        
        position = Position(
            position_id=f"pos_{int(time.time())}",
            entry_price=entry_price,
            size=size,
            side=side,
            margin=margin,
            unrealized_pnl=0.0,
            stop_loss=stop_loss,
            take_profit=take_profit,
            stage=stage.name,
            entry_time=time.time(),
            last_add_time=time.time(),
            add_count=0
        )
        
        self.current_position = position
        
        print(f"[Position] {side.upper()} {size} @ {entry_price:.1f}, "
              f"止损: {stop_loss:.1f}, 止盈: {take_profit:.1f}")
        
        return position
    
    def update_position_pnl(self, current_price: float) -> float:
        """
        更新持仓盈亏
        
        Args:
            current_price: 当前价格
            
        Returns:
            未实现盈亏
        """
        if not self.current_position:
            return 0.0
        
        pos = self.current_position
        
        # 计算盈亏
        if pos.side == 'long':
            pnl = (current_price - pos.entry_price) * pos.size / current_price
        else:  # short
            pnl = (pos.entry_price - current_price) * pos.size / current_price
        
        pos.unrealized_pnl = pnl
        
        return pnl
    
    def should_add_position(self, balance: float) -> Tuple[bool, float, str]:
        """
        判断是否应该加仓
        
        Args:
            balance: 当前余额
            
        Returns:
            (是否加仓, 加仓保证金, 原因)
        """
        if not self.current_position:
            return False, 0.0, "无持仓"
        
        pos = self.current_position
        stage = self.get_current_stage(balance)
        
        # 检查加仓次数
        if pos.add_count >= stage.max_add_count:
            return False, 0.0, f"已达最大加仓次数 {stage.max_add_count}"
        
        # 检查盈利比例
        pnl_ratio = pos.unrealized_pnl / pos.margin
        if pnl_ratio < stage.add_profit_threshold:
            return False, 0.0, f"盈利未达阈值 {stage.add_profit_threshold*100:.0f}%"
        
        # 检查加仓间隔(至少5分钟)
        if time.time() - pos.last_add_time < 300:
            return False, 0.0, "加仓间隔太短"
        
        # 计算加仓保证金(使用利润的80%)
        add_margin = pos.unrealized_pnl * 0.8
        
        # 确保加仓保证金不超过当前余额的20%
        max_add_margin = balance * 0.2
        add_margin = min(add_margin, max_add_margin)
        
        if add_margin < 1.0:  # 至少1U
            return False, 0.0, "加仓金额太小"
        
        return True, add_margin, f"盈利{pnl_ratio*100:.1f}%, 可加仓{add_margin:.2f}U"
    
    def add_position(self, current_price: float, add_size: int, add_margin: float):
        """
        执行加仓
        
        Args:
            current_price: 当前价格
            add_size: 加仓数量
            add_margin: 加仓保证金
        """
        if not self.current_position:
            print("[Failed] Position")
            return
        
        pos = self.current_position
        
        # 更新持仓信息
        total_margin = pos.margin + add_margin
        total_size = pos.size + add_size
        
        # 计算新的平均开仓价
        if pos.side == 'long':
            new_entry = (pos.entry_price * pos.size + current_price * add_size) / total_size
        else:
            new_entry = (pos.entry_price * pos.size + current_price * add_size) / total_size
        
        pos.entry_price = new_entry
        pos.size = total_size
        pos.margin = total_margin
        pos.add_count += 1
        pos.last_add_time = time.time()
        
        # 更新移动止损到保本线
        self.update_trailing_stop(current_price)
        
        print(f"[Success] {pos.add_count}, {add_size}, "
              f"总仓位{total_size}张, 平均价{new_entry:.1f}")
    
    def update_trailing_stop(self, current_price: float):
        """
        更新移动止损
        
        Args:
            current_price: 当前价格
        """
        if not self.current_position:
            return
        
        pos = self.current_position
        pnl_ratio = pos.unrealized_pnl / pos.margin
        
        old_stop = pos.stop_loss
        
        # 根据盈利比例调整止损
        if pnl_ratio >= 1.0:  # 盈利100%
            # 止损保护50%利润
            if pos.side == 'long':
                new_stop = pos.entry_price * 1.5
            else:
                new_stop = pos.entry_price * 0.5
        elif pnl_ratio >= 0.5:  # 盈利50%
            # 止损移到保本
            new_stop = pos.entry_price
        elif pnl_ratio >= 0.2:  # 盈利20%
            # 止损移到-10%
            if pos.side == 'long':
                new_stop = pos.entry_price * 0.9
            else:
                new_stop = pos.entry_price * 1.1
        else:
            # 保持原止损
            return
        
        # 只在止损价格更优时更新
        if pos.side == 'long':
            if new_stop > old_stop:
                pos.stop_loss = new_stop
                print(f"[Stop loss] {old_stop:.1f} -> {new_stop:.1f} (Profit{pnl_ratio*100:.1f}%)")
        else:
            if new_stop < old_stop:
                pos.stop_loss = new_stop
                print(f"[Stop loss] {old_stop:.1f} -> {new_stop:.1f} (Profit{pnl_ratio*100:.1f}%)")
    
    def should_partial_close(self) -> Tuple[bool, float, str]:
        """
        判断是否应该分批平仓
        
        Returns:
            (是否平仓, 平仓比例, 原因)
        """
        if not self.current_position:
            return False, 0.0, "无持仓"
        
        pos = self.current_position
        pnl_ratio = pos.unrealized_pnl / pos.margin
        
        # 分批平仓策略
        if pnl_ratio >= 1.0:  # 盈利100%
            return True, 0.3, f"盈利{pnl_ratio*100:.1f}%, 平仓30%锁定利润"
        elif pnl_ratio >= 0.8:  # 盈利80%
            return True, 0.4, f"盈利{pnl_ratio*100:.1f}%, 平仓40%锁定利润"
        elif pnl_ratio >= 0.5:  # 盈利50%
            return True, 0.3, f"盈利{pnl_ratio*100:.1f}%, 平仓30%锁定利润"
        
        return False, 0.0, "盈利未达分批平仓阈值"
    
    def check_stop_conditions(self, current_price: float) -> Tuple[bool, str]:
        """
        检查止损止盈条件
        
        Args:
            current_price: 当前价格
            
        Returns:
            (是否触发, 原因)
        """
        if not self.current_position:
            return False, "无持仓"
        
        pos = self.current_position
        
        # 检查止损
        if pos.side == 'long':
            if current_price <= pos.stop_loss:
                return True, f"触发止损 {current_price:.1f} <= {pos.stop_loss:.1f}"
        else:
            if current_price >= pos.stop_loss:
                return True, f"触发止损 {current_price:.1f} >= {pos.stop_loss:.1f}"
        
        # 检查止盈
        if pos.side == 'long':
            if current_price >= pos.take_profit:
                return True, f"触发止盈 {current_price:.1f} >= {pos.take_profit:.1f}"
        else:
            if current_price <= pos.take_profit:
                return True, f"触发止盈 {current_price:.1f} <= {pos.take_profit:.1f}"
        
        return False, "未触发"
    
    def close_position(self, close_price: float, close_ratio: float = 1.0) -> Dict:
        """
        平仓
        
        Args:
            close_price: 平仓价格
            close_ratio: 平仓比例(0-1), 1.0表示全平
            
        Returns:
            平仓记录
        """
        if not self.current_position:
            print("[Close positionFailed] Position")
            return {}
        
        pos = self.current_position
        
        # 计算平仓数量
        close_size = int(pos.size * close_ratio)
        
        # 计算实际盈亏
        if pos.side == 'long':
            pnl = (close_price - pos.entry_price) * close_size / close_price
        else:
            pnl = (pos.entry_price - close_price) * close_size / close_price
        
        # 记录平仓
        record = {
            'position_id': pos.position_id,
            'side': pos.side,
            'entry_price': pos.entry_price,
            'close_price': close_price,
            'size': close_size,
            'margin': pos.margin * close_ratio,
            'pnl': pnl,
            'pnl_ratio': pnl / (pos.margin * close_ratio),
            'close_ratio': close_ratio,
            'stage': pos.stage,
            'add_count': pos.add_count,
            'close_time': time.time(),
            'duration': time.time() - pos.entry_time
        }
        
        self.trade_history.append(record)
        self.total_profit += pnl
        
        # 更新连续亏损计数
        if pnl < 0:
            self.consecutive_losses += 1
            print(f"[Close position] Loss {pnl:.2f}U ({record['pnl_ratio']*100:.1f}%), "
                  f"连续亏损 {self.consecutive_losses} 次")
        else:
            self.consecutive_losses = 0
            print(f"[Close position] Profit {pnl:.2f}U ({record['pnl_ratio']*100:.1f}%)")
        
        # 检查是否需要暂停
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.is_paused = True
            print(f"[RiskControl] Loss{self.consecutive_losses}, PausedTrade!")
        
        # 如果是全平, 清除持仓
        if close_ratio >= 1.0:
            self.current_position = None
            print(f"[Close position] {pos.side.upper()} {close_size} @ {close_price:.1f}")
        else:
            # 部分平仓, 更新持仓
            pos.size -= close_size
            pos.margin *= (1 - close_ratio)
            print(f"[Close position] {pos.side.upper()} {close_size} @ {close_price:.1f}, "
                  f"剩余 {pos.size}张")
        
        return record
    
    def get_status(self) -> Dict:
        """
        获取滚仓管理器状态
        
        Returns:
            状态字典
        """
        status = {
            'balance': self.balance,
            'total_profit': self.total_profit,
            'consecutive_losses': self.consecutive_losses,
            'is_paused': self.is_paused,
            'trade_count': len(self.trade_history),
            'current_position': None,
            'current_stage': None
        }
        
        if self.current_position:
            pos = self.current_position
            status['current_position'] = pos.to_dict()
            status['current_stage'] = self.get_current_stage(self.balance).name
        
        return status
    
    def reset_pause(self):
        """重置暂停状态"""
        self.is_paused = False
        self.consecutive_losses = 0
        print("[RiskControl] Paused")
    
    def save_state(self, filepath: str = 'rolling_state.json'):
        """
        保存状态到文件
        
        Args:
            filepath: 文件路径
        """
        state = {
            'balance': self.balance,
            'total_profit': self.total_profit,
            'consecutive_losses': self.consecutive_losses,
            'is_paused': self.is_paused,
            'current_position': self.current_position.to_dict() if self.current_position else None,
            'trade_history': self.trade_history,
            'timestamp': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"[Save] Save {filepath}")
    
    def load_state(self, filepath: str = 'rolling_state.json'):
        """
        从文件加载状态
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.balance = state.get('balance', 0.0)
            self.total_profit = state.get('total_profit', 0.0)
            self.consecutive_losses = state.get('consecutive_losses', 0)
            self.is_paused = state.get('is_paused', False)
            self.trade_history = state.get('trade_history', [])
            
            if state.get('current_position'):
                pos_data = state['current_position']
                self.current_position = Position(**pos_data)
            
            print(f"[Load]  {filepath} Load")
            print(f"  Balance: {self.balance:.2f}U, Profit: {self.total_profit:.2f}U, "
                  f"交易次数: {len(self.trade_history)}")
            
        except FileNotFoundError:
            print(f"[Load] : {filepath}")
        except Exception as e:
            print(f"[Load] LoadFailed: {e}")


if __name__ == '__main__':
    """测试代码"""
    print("=" * 60)
    print("10U - ")
    print("=" * 60)
    
    # 创建管理器
    manager = RollingManager(leverage=100)
    
    # 模拟初始余额
    manager.balance = 10.0
    
    # 测试1: 计算开仓大小
    print("\n[1] Open position")
    margin, size = manager.calculate_position_size(manager.balance, 80000)
    print(f": ={margin}U, ={size}")
    
    # 测试2: 创建持仓
    print("\n[2] Position")
    pos = manager.create_position(
        entry_price=80000,
        size=size,
        side='long',
        margin=margin,
        balance=manager.balance
    )
    print(f"Position: {pos.side} {pos.size} @ {pos.entry_price}")
    
    # 测试3: 更新盈亏
    print("\n[3] Update")
    current_price = 84000  # 上涨5%
    pnl = manager.update_position_pnl(current_price)
    print(f"CurrentPrice: {current_price}, : {pnl:.2f}U ({pnl/margin*100:.1f}%)")
    
    # 测试4: 检查加仓
    print("\n[4] Check")
    should_add, add_margin, reason = manager.should_add_position(manager.balance + pnl)
    print(f": {should_add}, : {add_margin:.2f}U, : {reason}")
    
    # 测试5: 检查分批平仓
    print("\n[5] CheckClose position")
    should_close, close_ratio, reason = manager.should_partial_close()
    print(f"Close position: {should_close}, Close position: {close_ratio*100:.0f}%, : {reason}")
    
    # 测试6: 检查止损止盈
    print("\n[6] CheckStop lossTake profit")
    triggered, reason = manager.check_stop_conditions(current_price)
    print(f": {triggered}, : {reason}")
    
    # 测试7: 平仓
    print("\n[7] Close position")
    record = manager.close_position(current_price, 1.0)
    print(f"Close position: ={record['pnl']:.2f}U, ={record['pnl_ratio']*100:.1f}%")
    
    # 测试8: 获取状态
    print("\n[8] Get")
    status = manager.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("Complete")
    print("=" * 60)
