"""
KuCoinTrade接口封装
版本: 3.0 (移除CCXT依赖)
使用纯KuCoin原生API
"""
import time
from typing import Optional, Dict
from kucoin_api import KuCoinFuturesAPI


class KuCoinTrader:
 """KuCoin合约Trade封装类"""
 
 def __init__(self, config: Dict):
 """
 InitializeTrade接口
 
 Args:
 config: Config字典，包含api_key, api_secret, api_passphrase, sandbox, leverage
 """
 self.api = KuCoinFuturesAPI(
 api_key=config['api_key'],
 api_secret=config['api_secret'],
 api_passphrase=config['api_passphrase'],
 sandbox=config.get('sandbox', False)
)
 
 # SaveConfig
 self.leverage = config.get('leverage', 100) # default100倍杠杆
 
 self.symbol_map = {
 'BTC/USDT:USDT': 'XBTUSDTM',
 'ETH/USDT:USDT': 'ETHUSDTM'
 }
 
 print(f"[OK] KuCoinTradeInitializeSuccess")
 print(f"[INFO] : {'' if config.get('sandbox') else ''}")
 print(f" : {self.leverage}x")
 
 def _convert_symbol(self, symbol: str) -> str:
 """转换symbol格式"""
 # 如果alreadyisKuCoin格式（以M结尾），直接返回
 if symbol.endswith('M'):
 return symbol
 # 否则转换
 return self.symbol_map.get(symbol, self.api.symbol_to_kucoin(symbol))
 
 def get_balance(self) -> Optional[float]:
 """
 GetUSDTBalance
 
 Returns:
 Balance，Failed返回None
 """
 try:
 balance = self.api.get_balance('USDT')
 return balance
 except Exception as e:
 print(f"[ERROR] GetBalanceFailed: {e}")
 return None
 
 def get_current_price(self, symbol: str) -> Optional[float]:
 """
 GetCurrentPrice
 
 Args:
 symbol: Tradefor
 
 Returns:
 CurrentPrice，Failed返回None
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol)
 price = self.api.get_current_price(kucoin_symbol)
 return price
 except Exception as e:
 print(f"[ERROR] GetPriceFailed: {e}")
 return None
 
 def get_klines(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[list]:
 """
 GetK线数据
 
 Args:
 symbol: Tradefor
 timeframe: Timecycle ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
 limit: Amount
 
 Returns:
 K线数据 [[timestamp, open, high, low, close, volume],...]
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol)
 
 # 转换timeframeasgranularity（minute）
 timeframe_map = {
 '1m': 1, '5m': 5, '15m': 15, '30m': 30,
 '1h': 60, '2h': 120, '4h': 240, '8h': 480,
 '12h': 720, '1d': 1440, '1w': 10080
 }
 granularity = timeframe_map.get(timeframe, 60)
 
 # CalculateTimerange
 to_time = int(time.time())
 from_time = to_time - (limit * granularity * 60)
 
 klines = self.api.get_klines(kucoin_symbol, granularity, from_time, to_time)
 
 # 转换格式: [Time, 开, 高, 低, 收, 成交量]
 result = []
 for k in klines:
 result.append([
 int(k[0]), # timestamp
 float(k[1]), # open
 float(k[2]), # high
 float(k[3]), # low
 float(k[4]), # close
 float(k[5]) # volume
 ])
 
 return result
 
 except Exception as e:
 print(f"[ERROR] GetKFailed: {e}")
 print(f" Symbol: {symbol} -> {kucoin_symbol}")
 print(f" Timeframe: {timeframe} -> {granularity}minute")
 print(f" Limit: {limit}")
 import traceback
 traceback.print_exc()
 return None
 
 def set_leverage(self, symbol: str, leverage: int) -> bool:
 """
 Set杠杆倍数
 
 Args:
 symbol: Tradefor
 leverage: 杠杆倍数
 
 Returns:
 is否Success
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol)
 self.api.set_leverage(kucoin_symbol, leverage)
 print(f"[OK] SetSuccess: {leverage}x")
 return True
 except Exception as e:
 print(f"[ERROR] SetFailed: {e}")
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
 symbol: Tradefor
 side: 方向 'long' or 'short'
 margin: 保证金（USDT）
 leverage: 杠杆倍数
 stop_loss_pct: Stop loss百分比（optional）
 take_profit_pct: Take profit百分比（optional）
 
 Returns:
 OrderInfo，Failed返回None
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol)
 
 # GetCurrentPrice
 price = self.api.get_current_price(kucoin_symbol)
 if not price:
 raise Exception("No法GetCurrentPrice")
 
 # Calculate合约张数
 size = self.api.calculate_contract_size(kucoin_symbol, margin, price, leverage)
 
 # 转换方向
 order_side = 'buy' if side == 'long' else 'sell'
 
 # CalculateStop lossTake profitPrice
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
 
 print(f"[OK] Success: {side.upper()} {size} @ {price}")
 
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
 print(f"[ERROR] Failed: {e}")
 return None
 
 def close_position(self, symbol: str, side: str) -> bool:
 """
 Close position
 
 Args:
 symbol: Tradefor
 side: Position方向 'long' or 'short'
 
 Returns:
 is否Success
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol)
 
 # GetCurrentPosition
 position = self.api.get_position(kucoin_symbol)
 if not position:
 print("[WARNING] HasPosition")
 return True
 
 # GetPositionAmount
 current_qty = int(position.get('currentQty', 0))
 if current_qty == 0:
 print("[WARNING] PositionAmountas0")
 return True
 
 # Close position方向and开仓相反
 close_side = 'sell' if side == 'long' else 'buy'
 size = abs(current_qty)
 
 # 市价Close position
 order = self.api.create_order(
 symbol=kucoin_symbol,
 side=close_side,
 order_type='market',
 size=size
)
 
 print(f"[OK] Close positionSuccess: {side.upper()} {size}")
 return True
 
 except Exception as e:
 print(f"[ERROR] Close positionFailed: {e}")
 return False
 
 def get_position(self, symbol: str) -> Optional[Dict]:
 """
 GetPositionInfo
 
 Args:
 symbol: Tradefor
 
 Returns:
 PositionInfo，NoPosition返回None
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol)
 position = self.api.get_position(kucoin_symbol)
 
 if not position:
 return None
 
 # 转换as统一格式
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
 print(f"[ERROR] GetPositionFailed: {e}")
 return None
 
 def cancel_all_orders(self, symbol: Optional[str] = None) -> bool:
 """
 Cancel所HasOrder
 
 Args:
 symbol: Tradefor（optional）
 
 Returns:
 is否Success
 """
 try:
 kucoin_symbol = self._convert_symbol(symbol) if symbol else None
 self.api.cancel_all_orders(kucoin_symbol)
 print(f"[OK] AlreadyCancelHasOrder")
 return True
 except Exception as e:
 print(f"[ERROR] CancelOrderFailed: {e}")
 return False
 
 def open_long(self, margin: float, stop_loss_pct: Optional[float] = None, take_profit_pct: Optional[float] = None) -> Optional[Dict]:
 """
 Long仓（快捷方法）
 
 Args:
 margin: 保证金（USDT）
 stop_loss_pct: Stop loss百分比
 take_profit_pct: Take profit百分比
 
 Returns:
 OrderInfo
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
 Short仓（快捷方法）
 
 Args:
 margin: 保证金（USDT）
 stop_loss_pct: Stop loss百分比
 take_profit_pct: Take profit百分比
 
 Returns:
 OrderInfo
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
 Get所HasPosition
 
 Returns:
 Position列表
 """
 try:
 positions = self.api.get_all_positions()
 if not positions:
 return []
 
 # 过滤出HasPosition
 result = []
 for pos in positions:
 current_qty = int(pos.get('currentQty', 0))
 if current_qty!= 0:
 result.append(pos)
 
 return result
 
 except Exception as e:
 print(f"[ERROR] GetPositionFailed: {e}")
 return []


# 测试代码
if __name__ == "__main__":
 from live_trading_config import KUCOIN_CONFIG, TRADING_CONFIG
 
 trader = KuCoinTrader(KUCOIN_CONFIG)
 
 # 测试GetBalance
 balance = trader.get_balance()
 print(f"\n[MONEY] accountBalance: {balance} USDT")
 
 # 测试GetPrice
 symbol = TRADING_CONFIG['symbol']
 price = trader.get_current_price(symbol)
 print(f"[DATA] {symbol} CurrentPrice: {price}")
 
 # 测试GetK线
 klines = trader.get_klines(symbol, '1h', 5)
 if klines:
 print(f" 5K:")
 for k in klines[-5:]:
 print(f" Time: {k[0]}, : {k[1]}, : {k[2]}, : {k[3]}, : {k[4]}")
 
 # 测试GetPosition
 position = trader.get_position(symbol)
 if position:
 print(f"\n[INFO] CurrentPosition: {position}")
 else:
 print(f"\n[INFO] NoPosition")
 
 print("\n[OK] HasComplete")
