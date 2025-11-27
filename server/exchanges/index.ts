/**
 * 交易所抽象接口和工厂模式
 * 支持多交易所扩展
 */

// 通用合约信息接口
export interface Contract {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: string;
  maxLeverage: number;
  price: number;
  volume24h: number;
  turnover24h: number;
  priceChange24hPercent: number;
  high24h: number;
  low24h: number;
  fundingRate?: number;
  openInterest?: string;
}

// 通用订单簿接口
export interface OrderBook {
  symbol: string;
  bids: [string, number][];
  asks: [string, number][];
  timestamp: number;
}

// 通用K线数据接口
export interface Kline {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 交易所接口
export interface Exchange {
  name: string;
  
  // 获取所有USDT永续合约
  getUSDTPerpetualContracts(): Promise<Contract[]>;
  
  // 获取指定合约信息
  getContractInfo(symbol: string): Promise<Contract | null>;
  
  // 获取订单簿
  getOrderBook(symbol: string, depth?: number): Promise<OrderBook>;
  
  // 获取K线数据
  getKlines(
    symbol: string,
    interval: string,
    from?: number,
    to?: number
  ): Promise<Kline[]>;
  
  // 计算买卖价差
  calculateSpreadPercent(orderBook: OrderBook): number;
  
  // 计算订单簿深度
  calculateDepth(orderBook: OrderBook, pricePercent?: number): {
    bidDepth: number;
    askDepth: number;
    bidDepthValue: number;
    askDepthValue: number;
  };
}

// 交易所类型
export type ExchangeType = "kucoin" | "binance" | "okx" | "bybit";

// 导入各交易所实现
import { KuCoinExchange } from "./kucoin_exchange";

// 交易所工厂
export class ExchangeFactory {
  private static instances: Map<ExchangeType, Exchange> = new Map();
  
  /**
   * 获取交易所实例（单例模式）
   */
  static getExchange(type: ExchangeType): Exchange {
    if (!this.instances.has(type)) {
      switch (type) {
        case "kucoin":
          this.instances.set(type, new KuCoinExchange());
          break;
        case "binance":
          throw new Error("Binance exchange not implemented yet");
        case "okx":
          throw new Error("OKX exchange not implemented yet");
        case "bybit":
          throw new Error("Bybit exchange not implemented yet");
        default:
          throw new Error(`Unknown exchange type: ${type}`);
      }
    }
    
    return this.instances.get(type)!;
  }
  
  /**
   * 获取所有支持的交易所类型
   */
  static getSupportedExchanges(): ExchangeType[] {
    return ["kucoin"]; // 目前只支持KuCoin，后续扩展
  }
}

// 默认使用KuCoin
export const defaultExchange = ExchangeFactory.getExchange("kucoin");
