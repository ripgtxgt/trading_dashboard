/**
 * KuCoin Futures API服务
 * 用于获取合约交易对信息、价格数据等
 * 文档: https://www.kucoin.com/docs/rest/futures-trading/market-data
 */

const KUCOIN_FUTURES_API_BASE = "https://api-futures.kucoin.com";

export interface KuCoinContract {
  symbol: string;                    // 合约符号，如 "XBTUSDTM"
  baseCurrency: string;              // 基础货币，如 "XBT"
  quoteCurrency: string;             // 报价货币，如 "USDT"
  settleCurrency: string;            // 结算货币
  type: string;                      // 合约类型
  status: string;                    // 状态: "Open", "Closed"等
  maxLeverage: number;               // 最大杠杆
  fundingFeeRate: number;            // 当前资金费率
  markPrice: number;                 // 标记价格
  indexPrice: number;                // 指数价格
  lastTradePrice: number;            // 最新成交价
  turnoverOf24h: number;             // 24h交易额（USDT）
  volumeOf24h: number;               // 24h交易量
  priceChgPct: number;               // 24h价格变化百分比
  highPrice: number;                 // 24h最高价
  lowPrice: number;                  // 24h最低价
  openInterest: string;              // 持仓量
}

export interface KuCoinTicker {
  symbol: string;
  sequence: number;
  side: string;
  size: number;
  price: string;
  bestBidSize: number;
  bestBidPrice: string;
  bestAskPrice: string;
  tradeId: string;
  ts: number;
}

export interface KuCoinOrderBook {
  symbol: string;
  sequence: number;
  asks: [string, number][];          // [价格, 数量]
  bids: [string, number][];
  ts: number;
}

/**
 * 获取所有活跃合约
 */
export async function getActiveContracts(): Promise<KuCoinContract[]> {
  try {
    const response = await fetch(`${KUCOIN_FUTURES_API_BASE}/api/v1/contracts/active`);
    
    if (!response.ok) {
      throw new Error(`KuCoin API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.code !== "200000") {
      throw new Error(`KuCoin API error: ${result.msg || result.code}`);
    }
    
    return result.data;
  } catch (error) {
    console.error("[KuCoin] Failed to fetch active contracts:", error);
    throw error;
  }
}

/**
 * 获取所有USDT永续合约
 */
export async function getUSDTPerpetualContracts(): Promise<KuCoinContract[]> {
  try {
    const contracts = await getActiveContracts();
    
    // 筛选USDT永续合约（settleCurrency为USDT且无到期日）
    const usdtContracts = contracts.filter(c => 
      c.settleCurrency === "USDT" && 
      c.status === "Open" &&
      c.type === "FFWCSX"  // 永续合约类型
    );
    
    console.log(`[KuCoin] Found ${usdtContracts.length} USDT perpetual contracts`);
    return usdtContracts;
  } catch (error) {
    console.error("[KuCoin] Failed to fetch USDT perpetual contracts:", error);
    throw error;
  }
}

/**
 * 获取指定合约信息
 */
export async function getContractInfo(symbol: string): Promise<KuCoinContract | null> {
  try {
    const contracts = await getActiveContracts();
    const contract = contracts.find(c => c.symbol === symbol);
    return contract || null;
  } catch (error) {
    console.error(`[KuCoin] Failed to fetch contract info for ${symbol}:`, error);
    throw error;
  }
}

/**
 * 获取实时行情
 */
export async function getTicker(symbol: string): Promise<KuCoinTicker> {
  try {
    const response = await fetch(
      `${KUCOIN_FUTURES_API_BASE}/api/v1/ticker?symbol=${symbol}`
    );
    
    if (!response.ok) {
      throw new Error(`KuCoin API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.code !== "200000") {
      throw new Error(`KuCoin API error: ${result.msg || result.code}`);
    }
    
    return result.data;
  } catch (error) {
    console.error(`[KuCoin] Failed to fetch ticker for ${symbol}:`, error);
    throw error;
  }
}

/**
 * 获取订单簿
 */
export async function getOrderBook(symbol: string, depth: number = 20): Promise<KuCoinOrderBook> {
  try {
    const response = await fetch(
      `${KUCOIN_FUTURES_API_BASE}/api/v1/level2/depth${depth}?symbol=${symbol}`
    );
    
    if (!response.ok) {
      throw new Error(`KuCoin API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.code !== "200000") {
      throw new Error(`KuCoin API error: ${result.msg || result.code}`);
    }
    
    return result.data;
  } catch (error) {
    console.error(`[KuCoin] Failed to fetch order book for ${symbol}:`, error);
    throw error;
  }
}

/**
 * 获取K线数据
 */
export async function getKlines(
  symbol: string,
  granularity: number = 1440, // 分钟数：1, 5, 15, 30, 60, 120, 240, 480, 720, 1440, 10080
  from?: number,              // 开始时间（毫秒）
  to?: number                 // 结束时间（毫秒）
): Promise<Array<[number, number, number, number, number, number]>> {
  try {
    let url = `${KUCOIN_FUTURES_API_BASE}/api/v1/kline/query?symbol=${symbol}&granularity=${granularity}`;
    
    if (from) url += `&from=${from}`;
    if (to) url += `&to=${to}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`KuCoin API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.code !== "200000") {
      throw new Error(`KuCoin API error: ${result.msg || result.code}`);
    }
    
    // 返回格式: [时间戳, 开盘价, 最高价, 最低价, 收盘价, 交易量]
    return result.data;
  } catch (error) {
    console.error(`[KuCoin] Failed to fetch klines for ${symbol}:`, error);
    throw error;
  }
}

/**
 * 计算买卖价差百分比
 */
export function calculateSpreadPercent(orderBook: KuCoinOrderBook): number {
  if (orderBook.bids.length === 0 || orderBook.asks.length === 0) {
    return 0;
  }
  
  const bestBid = parseFloat(orderBook.bids[0][0]);
  const bestAsk = parseFloat(orderBook.asks[0][0]);
  
  const spread = bestAsk - bestBid;
  const midPrice = (bestBid + bestAsk) / 2;
  
  return (spread / midPrice) * 100;
}

/**
 * 计算订单簿深度（指定价差百分比内的总量）
 */
export function calculateDepth(orderBook: KuCoinOrderBook, pricePercent: number = 1): {
  bidDepth: number;
  askDepth: number;
  bidDepthValue: number;  // 买单深度价值（USDT）
  askDepthValue: number;  // 卖单深度价值（USDT）
} {
  if (orderBook.bids.length === 0 || orderBook.asks.length === 0) {
    return { bidDepth: 0, askDepth: 0, bidDepthValue: 0, askDepthValue: 0 };
  }
  
  const bestBid = parseFloat(orderBook.bids[0][0]);
  const bestAsk = parseFloat(orderBook.asks[0][0]);
  
  const bidThreshold = bestBid * (1 - pricePercent / 100);
  const askThreshold = bestAsk * (1 + pricePercent / 100);
  
  let bidDepth = 0;
  let bidDepthValue = 0;
  for (const [price, quantity] of orderBook.bids) {
    const p = parseFloat(price);
    if (p >= bidThreshold) {
      bidDepth += quantity;
      bidDepthValue += p * quantity;
    } else {
      break;
    }
  }
  
  let askDepth = 0;
  let askDepthValue = 0;
  for (const [price, quantity] of orderBook.asks) {
    const p = parseFloat(price);
    if (p <= askThreshold) {
      askDepth += quantity;
      askDepthValue += p * quantity;
    } else {
      break;
    }
  }
  
  return { bidDepth, askDepth, bidDepthValue, askDepthValue };
}

/**
 * 计算ATR（平均真实波幅）
 */
export function calculateATR(
  klines: Array<[number, number, number, number, number, number]>,
  period: number = 14
): number {
  if (klines.length < period + 1) {
    return 0;
  }
  
  const trueRanges: number[] = [];
  
  for (let i = 1; i < klines.length; i++) {
    const [, , high, low, close] = klines[i];
    const [, , , , prevClose] = klines[i - 1];
    
    const tr = Math.max(
      high - low,
      Math.abs(high - prevClose),
      Math.abs(low - prevClose)
    );
    
    trueRanges.push(tr);
  }
  
  // 计算最近period个TR的平均值
  const recentTRs = trueRanges.slice(-period);
  const atr = recentTRs.reduce((sum, tr) => sum + tr, 0) / period;
  
  return atr;
}

/**
 * 计算标准差（价格波动率）
 */
export function calculateStdDev(
  klines: Array<[number, number, number, number, number, number]>,
  period: number = 20
): number {
  if (klines.length < period) {
    return 0;
  }
  
  const closes = klines.slice(-period).map(k => k[4]);
  const mean = closes.reduce((sum, c) => sum + c, 0) / period;
  
  const variance = closes.reduce((sum, c) => sum + Math.pow(c - mean, 2), 0) / period;
  const stdDev = Math.sqrt(variance);
  
  return stdDev;
}
