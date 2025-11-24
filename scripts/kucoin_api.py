"""
KuCoin Futures API 原生封装
版本: 3.0 (No第三方broker ID)
not依赖CCXT，直接调用KuCoin官方API
"""
import hmac
import hashlib
import base64
import time
import requests
import json
import logging
from typing import Optional, Dict, List, Any


class KuCoinFuturesAPI:
 """KuCoin合约API封装类"""
 
 def __init__(self, api_key: str, api_secret: str, api_passphrase: str, sandbox: bool = False):
 """
 InitializeKuCoin API
 
 Args:
 api_key: API Key
 api_secret: API Secret
 api_passphrase: API Passphrase
 sandbox: is否使用沙盒环境
 """
 self.logger = logging.getLogger('KuCoinAPI')
 self.api_key = api_key
 self.api_secret = api_secret
 self.api_passphrase = api_passphrase
 
 # APIbaseURL
 if sandbox:
 self.base_url = "https://api-sandbox-futures.kucoin.com"
 else:
 self.base_url = "https://api-futures.kucoin.com"
 
 self.session = requests.Session()
 self.session.headers.update({
 'Content-Type': 'application/json',
 'User-Agent': 'KuCoin-Futures-Python-SDK/3.0'
 })
 
 def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: str = '') -> tuple:
 """
 生成API签名
 
 Args:
 timestamp: Time戳（毫second）
 method: Please求方法 (GET/POST/DELETE)
 endpoint: API端点
 body: Please求体（JSON字符串）
 
 Returns:
 (signature, passphrase)
 """
 # 构造待签名字符串
 str_to_sign = timestamp + method + endpoint + body
 
 # 生成签名
 signature = base64.b64encode(
 hmac.new(
 self.api_secret.encode('utf-8'),
 str_to_sign.encode('utf-8'),
 hashlib.sha256
).digest()
).decode('utf-8')
 
 # 加密passphrase
 passphrase = base64.b64encode(
 hmac.new(
 self.api_secret.encode('utf-8'),
 self.api_passphrase.encode('utf-8'),
 hashlib.sha256
).digest()
).decode('utf-8')
 
 return signature, passphrase
 
 def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
 """
 SendAPIPlease求
 
 Args:
 method: Please求方法
 endpoint: API端点
 params: URLParameter
 data: Please求体数据
 
 Returns:
 响should数据
 """
 # 生成Time戳
 timestamp = str(int(time.time() * 1000))
 
 # 构造Please求体
 body = ''
 if data:
 body = json.dumps(data)
 
 # foratGETandDELETEPlease求，需要willparams拼接toendpointin进行签名
 sign_endpoint = endpoint
 if method in ['GET', 'DELETE'] and params:
 query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
 sign_endpoint = f"{endpoint}?{query_string}"
 
 # 生成签名
 signature, passphrase = self._generate_signature(timestamp, method, sign_endpoint, body)
 
 # 构造Please求头
 headers = {
 'KC-API-KEY': self.api_key,
 'KC-API-SIGN': signature,
 'KC-API-TIMESTAMP': timestamp,
 'KC-API-PASSPHRASE': passphrase,
 'KC-API-KEY-VERSION': '2'
 }
 
 # SendPlease求
 url = self.base_url + endpoint
 
 self.logger.debug(f"APIPlease: {method} {url}")
 if params:
 self.logger.debug(f" Parameter: {params}")
 if data:
 self.logger.debug(f" : {data}")
 
 try:
 if method == 'GET':
 response = self.session.get(url, headers=headers, params=params, timeout=10)
 elif method == 'POST':
 response = self.session.post(url, headers=headers, json=data, timeout=10)
 elif method == 'DELETE':
 response = self.session.delete(url, headers=headers, params=params, timeout=10)
 else:
 raise ValueError(f"not支持Please求方法: {method}")
 
 self.logger.debug(f" shouldStatus: {response.status_code}")
 
 response.raise_for_status()
 result = response.json()
 
 # 检查API返回code
 if result.get('code')!= '200000':
 error_msg = f"KuCoin APIError: {result.get('msg', 'Unknown error')}"
 self.logger.error(error_msg)
 raise Exception(error_msg)
 
 self.logger.debug(f" PleaseSuccess")
 return result.get('data', {})
 
 except requests.exceptions.RequestException as e:
 error_msg = f"APIPlease求Failed: {str(e)}"
 self.logger.error(error_msg)
 raise Exception(error_msg)
 
 # ==================== account相关 ====================
 
 def get_account_overview(self, currency: str = 'USDT') -> Dict:
 """
 Getaccount概览
 
 Args:
 currency: 币种（defaultUSDT）
 
 Returns:
 accountInfo
 """
 endpoint = f'/api/v1/account-overview'
 params = {'currency': currency}
 return self._request('GET', endpoint, params=params)
 
 def get_balance(self, currency: str = 'USDT') -> float:
 """
 Get可用Balance
 
 Args:
 currency: 币种
 
 Returns:
 可用Balance
 """
 account = self.get_account_overview(currency)
 return float(account.get('availableBalance', 0))
 
 # ==================== 市场数据 ====================
 
 def get_klines(self, symbol: str, granularity: int, from_time: Optional[int] = None, to_time: Optional[int] = None) -> List[List]:
 """
 GetK线数据
 
 Args:
 symbol: 合约代码，如 'XBTUSDTM'
 granularity: K线cycle（minute）: 1, 5, 15, 30, 60, 120, 240, 480, 720, 1440, 10080
 from_time: BeginTime（second级Time戳）
 to_time: EndTime（second级Time戳）
 
 Returns:
 K线数据列表 [[Time, 开, 高, 低, 收, 成交量],...]
 """
 endpoint = f'/api/v1/kline/query'
 params = {
 'symbol': symbol,
 'granularity': granularity
 }
 
 # KuCoin需要毫second级Time戳，且from/to都is必须
 if not to_time:
 to_time = int(time.time())
 if not from_time:
 from_time = to_time - (200 * granularity * 60) # default200
 
 params['from'] = from_time * 1000 # 转毫second
 params['to'] = to_time * 1000
 
 data = self._request('GET', endpoint, params=params)
 return data if isinstance(data, list) else []
 
 def get_ticker(self, symbol: str) -> Dict:
 """
 GetRealtime行情
 
 Args:
 symbol: 合约代码
 
 Returns:
 行情数据
 """
 endpoint = f'/api/v1/ticker'
 params = {'symbol': symbol}
 return self._request('GET', endpoint, params=params)
 
 def get_current_price(self, symbol: str) -> float:
 """
 GetCurrentPrice
 
 Args:
 symbol: 合约代码
 
 Returns:
 CurrentPrice
 """
 ticker = self.get_ticker(symbol)
 return float(ticker.get('price', 0))
 
 # ==================== Position相关 ====================
 
 def get_position(self, symbol: str) -> Optional[Dict]:
 """
 GetPositionInfo
 
 Args:
 symbol: 合约代码
 
 Returns:
 PositionInfo，NoPosition返回None
 """
 endpoint = f'/api/v1/position'
 params = {'symbol': symbol}
 data = self._request('GET', endpoint, params=params)
 
 # 检查is否HasPosition
 if data and float(data.get('currentQty', 0))!= 0:
 return data
 return None
 
 def get_all_positions(self) -> List[Dict]:
 """
 Get所HasPosition
 
 Returns:
 Position列表
 """
 endpoint = f'/api/v1/positions'
 data = self._request('GET', endpoint)
 return data if isinstance(data, list) else []
 
 # ==================== Trade相关 ====================
 
 def set_leverage(self, symbol: str, leverage: int) -> Dict:
 """
 Set杠杆倍数
 
 Args:
 symbol: 合约代码
 leverage: 杠杆倍数
 
 Returns:
 Setresult
 """
 endpoint = f'/api/v1/position/margin/auto-deposit-status'
 data = {
 'symbol': symbol,
 'leverage': leverage
 }
 return self._request('POST', endpoint, data=data)
 
 def create_order(
 self,
 symbol: str,
 side: str,
 order_type: str,
 size: int,
 price: Optional[float] = None,
 leverage: Optional[int] = None,
 stop_loss: Optional[float] = None,
 take_profit: Optional[float] = None,
 client_oid: Optional[str] = None
) -> Dict:
 """
 创建Order
 
 Args:
 symbol: 合约代码，如 'XBTUSDTM'
 side: 方向 'buy' or 'sell'
 order_type: Order类型 'limit' or 'market'
 size: Amount（张数）
 price: Price（限价单必填）
 leverage: 杠杆倍数
 stop_loss: Stop loss价
 take_profit: Take profit价
 client_oid: 客户端OrderID
 
 Returns:
 OrderInfo
 """
 endpoint = f'/api/v1/orders'
 
 data = {
 'symbol': symbol,
 'side': side,
 'type': order_type,
 'size': size
 }
 
 if price:
 data['price'] = price
 if leverage:
 data['leverage'] = leverage
 if stop_loss:
 data['stopLoss'] = stop_loss
 if take_profit:
 data['takeProfit'] = take_profit
 if client_oid:
 data['clientOid'] = client_oid
 else:
 data['clientOid'] = str(int(time.time() * 1000))
 
 return self._request('POST', endpoint, data=data)
 
 def cancel_order(self, order_id: str) -> Dict:
 """
 CancelOrder
 
 Args:
 order_id: OrderID
 
 Returns:
 Cancelresult
 """
 endpoint = f'/api/v1/orders/{order_id}'
 return self._request('DELETE', endpoint)
 
 def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict:
 """
 Cancel所HasOrder
 
 Args:
 symbol: 合约代码（optional，not填则Cancel所Has）
 
 Returns:
 Cancelresult
 """
 endpoint = f'/api/v1/orders'
 params = {}
 if symbol:
 params['symbol'] = symbol
 return self._request('DELETE', endpoint, params=params)
 
 def get_order(self, order_id: str) -> Dict:
 """
 QueryOrder
 
 Args:
 order_id: OrderID
 
 Returns:
 OrderInfo
 """
 endpoint = f'/api/v1/orders/{order_id}'
 return self._request('GET', endpoint)
 
 # ==================== 辅助方法 ====================
 
 def symbol_to_kucoin(self, symbol: str) -> str:
 """
 will通用symbol转换asKuCoin格式
 
 Args:
 symbol: 通用格式 'BTC/USDT:USDT'
 
 Returns:
 KuCoin格式 'XBTUSDTM'
 """
 # BTC/USDT:USDT -> XBTUSDTM
 if symbol == 'BTC/USDT:USDT':
 return 'XBTUSDTM'
 elif symbol == 'ETH/USDT:USDT':
 return 'ETHUSDTM'
 else:
 # 通用转换规则
 base = symbol.split('/')[0]
 return f"{base}USDTM"
 
 def calculate_contract_size(self, symbol: str, usdt_amount: float, price: float, leverage: int) -> int:
 """
 Calculate合约张数
 
 Args:
 symbol: 合约代码
 usdt_amount: USDT金额（保证金）
 price: CurrentPrice
 leverage: 杠杆倍数
 
 Returns:
 合约张数
 """
 # BTC合约：1张 = 0.001 BTC
 if 'XBT' in symbol or 'BTC' in symbol:
 contract_value = 0.001 # 每张value0.001 BTC
 else:
 contract_value = 0.01 # 其他币种一般as0.01
 
 # 名义value = 保证金 * 杠杆
 notional_value = usdt_amount * leverage
 
 # 张数 = 名义value / (Price * 合约value)
 size = int(notional_value / (price * contract_value))
 
 return max(1, size) # 至少1张


# 使用示例
if __name__ == "__main__":
 # 测试代码
 from live_trading_config import KUCOIN_CONFIG
 
 api = KuCoinFuturesAPI(
 api_key=KUCOIN_CONFIG['api_key'],
 api_secret=KUCOIN_CONFIG['api_secret'],
 api_passphrase=KUCOIN_CONFIG['api_passphrase'],
 sandbox=KUCOIN_CONFIG.get('sandbox', False)
)
 
 try:
 # 测试GetBalance
 balance = api.get_balance()
 print(f"[OK] Account balance: {balance} USDT")
 
 # 测试GetPrice
 symbol = 'XBTUSDTM'
 price = api.get_current_price(symbol)
 print(f"[OK] BTC current price: {price} USDT")
 
 # 测试GetK线
 klines = api.get_klines(symbol, 60, limit=5)
 print(f"[OK] Retrieved {len(klines)} kline data points")
 
 print("\n[SUCCESS] All tests passed!")
 
 except Exception as e:
 print(f"[ERROR] Test failed: {e}")
