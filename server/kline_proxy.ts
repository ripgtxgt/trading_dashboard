import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";

/**
 * KuCoin K线数据代理
 * 解决前端直接调用KuCoin API的CORS问题
 */
export const klineProxyRouter = router({
  /**
   * 获取K线数据
   */
  getKlines: publicProcedure
    .input(
      z.object({
        symbol: z.string().default("XBTUSDTM"),
        interval: z.string().default("1hour"),
        startAt: z.number().optional(),
        endAt: z.number().optional(),
      })
    )
    .query(async ({ input }) => {
      const { symbol, interval, startAt, endAt } = input;

      // 默认获取最近24小时的数据
      const end = endAt || Math.floor(Date.now() / 1000);
      const start = startAt || end - 24 * 60 * 60;

      try {
        const url = `https://api.kucoin.com/api/v1/market/candles?type=${interval}&symbol=${symbol}&startAt=${start}&endAt=${end}`;
        
        const response = await fetch(url);
        const result = await response.json();

        if (result.code === "200000" && result.data) {
          // KuCoin返回的数据格式: [time, open, close, high, low, volume, turnover]
          // 数据是倒序的，需要反转
          const klines = result.data.reverse();
          
          return {
            success: true,
            data: klines.map((k: any[]) => ({
              time: parseInt(k[0]),
              open: parseFloat(k[1]),
              close: parseFloat(k[2]),
              high: parseFloat(k[3]),
              low: parseFloat(k[4]),
              volume: parseFloat(k[5]),
            })),
          };
        } else {
          return {
            success: false,
            error: result.msg || "Failed to fetch kline data",
            data: [],
          };
        }
      } catch (error: any) {
        console.error("[KlineProxy] Error fetching kline data:", error);
        return {
          success: false,
          error: error.message || "Network error",
          data: [],
        };
      }
    }),
});
