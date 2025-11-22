"""
KuCoin交易接口封装
版本: 3.0 (移除CCXT依赖)
使用纯KuCoin原生API
"""
import time
from typing import Optional, Dict
from kucoin_api import KuCoinFuturesAPI


class KuCoinTrader:
    """KuCoin合约交易封装类"""
    
    def __init__(self, config: Dict):
        """
        初始化交易接口
        
        Args:
            config: 配置字典，包含api_key, api_secret, api_passphrase, sandbox, leverage
        """
        self.api = KuCoinFuturesAPI(
            api_key=config['api_key'],
            api_secret=config['api_secret'],
            api_passphrase=config['api_passphrase'],
            sandbox=config.get('sandbox', False)
        )
        
        # 保存配置
        self.leverage = config.get('leverage', 100)  # 默认100倍杠杆
        
        self.symbol_map = {
            'BTC/USDT:USDT': 'XBTUSDTM',
            'ETH/USDT:USDT': 'ETHUSDTM'
        }
        
        print(f"✅ KuCoin交易接口初始化成功")
        print(f"📍 环境: {'沙盒' if config.get('sandbox') else '实盘'}")
        print(f"🔧 杠杆: {self.leverage}x")
    
    def _convert_symbol(self, symbol: str) -> str:
        """转换symbol格式"""
        # 如果已经是KuCoin格式（以M结尾），直接返回
        if symbol.endswith('M'):
            return symbol
        # 否则转换
        return self.symbol_map.get(symbol, self.api.symbol_to_kucoin(symbol))
    
    def get_balance(self) -> Optional[float]:
        """
        获取USDT余额
        
        Returns:
            余额，失败返回None
        """
        try:
            balance = self.api.get_balance('USDT')
            return balance
        except Exception as e:
            print(f"❌ 获取余额失败: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        获取当前价格
        
        Args:
            symbol: 交易对
            
        Returns:
            当前价格，失败返回None
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol)
            price = self.api.get_current_price(kucoin_symbol)
            return price
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
            return None
    
    def get_klines(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[list]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对
            timeframe: 时间周期 ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
            limit: 数量
            
        Returns:
            K线数据 [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol)
            
            # 转换timeframe为granularity（分钟）
            timeframe_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '2h': 120, '4h': 240, '8h': 480,
                '12h': 720, '1d': 1440, '1w': 10080
            }
            granularity = timeframe_map.get(timeframe, 60)
            
            # 计算时间范围
            to_time = int(time.time())
            from_time = to_time - (limit * granularity * 60)
            
            klines = self.api.get_klines(kucoin_symbol, granularity, from_time, to_time)
            
            # 转换格式: [时间, 开, 高, 低, 收, 成交量]
            result = []
            for k in klines:
                result.append([
                    int(k[0]),      # timestamp
                    float(k[1]),    # open
                    float(k[2]),    # high
                    float(k[3]),    # low
                    float(k[4]),    # close
                    float(k[5])     # volume
                ])
            
            return result
            
        except Exception as e:
            print(f"❌ 获取K线失败: {e}")
            print(f"   Symbol: {symbol} -> {kucoin_symbol}")
            print(f"   Timeframe: {timeframe} -> {granularity}分钟")
            print(f"   Limit: {limit}")
            import traceback
            traceback.print_exc()
            return None
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        设置杠杆倍数
        
        Args:
            symbol: 交易对
            leverage: 杠杆倍数
            
        Returns:
            是否成功
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol)
            self.api.set_leverage(kucoin_symbol, leverage)
            print(f"✅ 杠杆设置成功: {leverage}x")
            return True
        except Exception as e:
            print(f"❌ 设置杠杆失败: {e}")
            return False
    
    def open_position(
        self,
        symbol: str,
        side: str,
        margin: float,
        leverage: int,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None
    ) -> Optional[Dict]:
        """
        开仓
        
        Args:
            symbol: 交易对
            side: 方向 'long' 或 'short'
            margin: 保证金（USDT）
            leverage: 杠杆倍数
            stop_loss_pct: 止损百分比（可选）
            take_profit_pct: 止盈百分比（可选）
            
        Returns:
            订单信息，失败返回None
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol)
            
            # 获取当前价格
            price = self.api.get_current_price(kucoin_symbol)
            if not price:
                raise Exception("无法获取当前价格")
            
            # 计算合约张数
            size = self.api.calculate_contract_size(kucoin_symbol, margin, price, leverage)
            
            # 转换方向
            order_side = 'buy' if side == 'long' else 'sell'
            
            # 计算止损止盈价格
            stop_loss_price = None
            take_profit_price = None
            
            if stop_loss_pct:
                if side == 'long':
                    stop_loss_price = price * (1 - stop_loss_pct)
                else:
                    stop_loss_price = price * (1 + stop_loss_pct)
            
            if take_profit_pct:
                if side == 'long':
                    take_profit_price = price * (1 + take_profit_pct)
                else:
                    take_profit_price = price * (1 - take_profit_pct)
            
            # 下单
            order = self.api.create_order(
                symbol=kucoin_symbol,
                side=order_side,
                order_type='market',
                size=size,
                leverage=leverage,
                stop_loss=stop_loss_price,
                take_profit=take_profit_price
            )
            
            print(f"✅ 开仓成功: {side.upper()} {size}张 @ {price}")
            
            return {
                'order_id': order.get('orderId'),
                'symbol': symbol,
                'side': side,
                'size': size,
                'price': price,
                'margin': margin,
                'leverage': leverage
            }
            
        except Exception as e:
            print(f"❌ 开仓失败: {e}")
            return None
    
    def close_position(self, symbol: str, side: str) -> bool:
        """
        平仓
        
        Args:
            symbol: 交易对
            side: 持仓方向 'long' 或 'short'
            
        Returns:
            是否成功
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol)
            
            # 获取当前持仓
            position = self.api.get_position(kucoin_symbol)
            if not position:
                print("⚠️ 没有持仓")
                return True
            
            # 获取持仓数量
            current_qty = int(position.get('currentQty', 0))
            if current_qty == 0:
                print("⚠️ 持仓数量为0")
                return True
            
            # 平仓方向与开仓相反
            close_side = 'sell' if side == 'long' else 'buy'
            size = abs(current_qty)
            
            # 市价平仓
            order = self.api.create_order(
                symbol=kucoin_symbol,
                side=close_side,
                order_type='market',
                size=size
            )
            
            print(f"✅ 平仓成功: {side.upper()} {size}张")
            return True
            
        except Exception as e:
            print(f"❌ 平仓失败: {e}")
            return False
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        获取持仓信息
        
        Args:
            symbol: 交易对
            
        Returns:
            持仓信息，无持仓返回None
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol)
            position = self.api.get_position(kucoin_symbol)
            
            if not position:
                return None
            
            # 转换为统一格式
            current_qty = int(position.get('currentQty', 0))
            if current_qty == 0:
                return None
            
            return {
                'symbol': symbol,
                'side': 'long' if current_qty > 0 else 'short',
                'size': abs(current_qty),
                'entry_price': float(position.get('avgEntryPrice', 0)),
                'leverage': int(position.get('realLeverage', 0)),
                'unrealized_pnl': float(position.get('unrealisedPnl', 0)),
                'margin': float(position.get('posMaint', 0))
            }
            
        except Exception as e:
            print(f"❌ 获取持仓失败: {e}")
            return None
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> bool:
        """
        取消所有订单
        
        Args:
            symbol: 交易对（可选）
            
        Returns:
            是否成功
        """
        try:
            kucoin_symbol = self._convert_symbol(symbol) if symbol else None
            self.api.cancel_all_orders(kucoin_symbol)
            print(f"✅ 已取消所有订单")
            return True
        except Exception as e:
            print(f"❌ 取消订单失败: {e}")
            return False
    
    def open_long(self, margin: float, stop_loss_pct: Optional[float] = None, take_profit_pct: Optional[float] = None) -> Optional[Dict]:
        """
        开多仓（快捷方法）
        
        Args:
            margin: 保证金（USDT）
            stop_loss_pct: 止损百分比
            take_profit_pct: 止盈百分比
        
        Returns:
            订单信息
        """
        from live_trading_config import STRATEGY_CONFIG
        symbol = STRATEGY_CONFIG.get('symbol', 'BTC/USDT:USDT')
        leverage = STRATEGY_CONFIG.get('leverage', 100)
        
        return self.open_position(
            symbol=symbol,
            side='long',
            margin=margin,
            leverage=leverage,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def open_short(self, margin: float, stop_loss_pct: Optional[float] = None, take_profit_pct: Optional[float] = None) -> Optional[Dict]:
        """
        开空仓（快捷方法）
        
        Args:
            margin: 保证金（USDT）
            stop_loss_pct: 止损百分比
            take_profit_pct: 止盈百分比
        
        Returns:
            订单信息
        """
        from live_trading_config import STRATEGY_CONFIG
        symbol = STRATEGY_CONFIG.get('symbol', 'BTC/USDT:USDT')
        leverage = STRATEGY_CONFIG.get('leverage', 100)
        
        return self.open_position(
            symbol=symbol,
            side='short',
            margin=margin,
            leverage=leverage,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def get_positions(self) -> list:
        """
        获取所有持仓
        
        Returns:
            持仓列表
        """
        try:
            positions = self.api.get_all_positions()
            if not positions:
                return []
            
            # 过滤出有持仓的
            result = []
            for pos in positions:
                current_qty = int(pos.get('currentQty', 0))
                if current_qty != 0:
                    result.append(pos)
            
            return result
            
        except Exception as e:
            print(f"❌ 获取持仓列表失败: {e}")
            return []


# 测试代码
if __name__ == "__main__":
    from live_trading_config import KUCOIN_CONFIG, TRADING_CONFIG
    
    trader = KuCoinTrader(KUCOIN_CONFIG)
    
    # 测试获取余额
    balance = trader.get_balance()
    print(f"\n💰 账户余额: {balance} USDT")
    
    # 测试获取价格
    symbol = TRADING_CONFIG['symbol']
    price = trader.get_current_price(symbol)
    print(f"📊 {symbol} 当前价格: {price}")
    
    # 测试获取K线
    klines = trader.get_klines(symbol, '1h', 5)
    if klines:
        print(f"📈 最近5根K线:")
        for k in klines[-5:]:
            print(f"  时间: {k[0]}, 开: {k[1]}, 高: {k[2]}, 低: {k[3]}, 收: {k[4]}")
    
    # 测试获取持仓
    position = trader.get_position(symbol)
    if position:
        print(f"\n📍 当前持仓: {position}")
    else:
        print(f"\n📍 无持仓")
    
    print("\n✅ 所有测试完成！")
