import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, LineData, Time } from "lightweight-charts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RefreshCw } from "lucide-react";

interface KlineChartProps {
  symbol?: string;
  interval?: string;
}

export function KlineChart({ symbol = "BTC-USDT", interval = "1hour" }: KlineChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<any | null>(null);
  const ma5SeriesRef = useRef<any | null>(null);
  const ma20SeriesRef = useRef<any | null>(null);
  
  const [selectedInterval, setSelectedInterval] = useState(interval);
  const [loading, setLoading] = useState(false);

  const fetchKlineData = async () => {
    setLoading(true);
    try {
      // 使用KuCoin API获取K线数据
      const endTime = Math.floor(Date.now() / 1000);
      const startTime = endTime - 24 * 60 * 60; // 最近24小时
      
      const response = await fetch(
        `/api/kucoin-proxy/api/v1/market/candles?type=${selectedInterval}&symbol=${symbol}&startAt=${startTime}&endAt=${endTime}`
      );
      
      const result = await response.json();
      
      if (result.code === "200000" && result.data) {
        const klines = result.data.reverse(); // KuCoin返回的数据是倒序的
        
        // 转换为图表数据格式
        const candlestickData: CandlestickData[] = [];
        const ma5Data: LineData[] = [];
        const ma20Data: LineData[] = [];
        
        for (let i = 0; i < klines.length; i++) {
          const [time, open, close, high, low, volume] = klines[i];
          const timestamp = parseInt(time);
          
          candlestickData.push({
            time: timestamp as Time,
            open: parseFloat(open),
            high: parseFloat(high),
            low: parseFloat(low),
            close: parseFloat(close),
          });
          
          // 计算MA5
          if (i >= 4) {
            let sum5 = 0;
            for (let j = 0; j < 5; j++) {
              sum5 += parseFloat(klines[i - j][2]); // close price
            }
            ma5Data.push({
              time: timestamp as Time,
              value: sum5 / 5,
            });
          }
          
          // 计算MA20
          if (i >= 19) {
            let sum20 = 0;
            for (let j = 0; j < 20; j++) {
              sum20 += parseFloat(klines[i - j][2]); // close price
            }
            ma20Data.push({
              time: timestamp as Time,
              value: sum20 / 20,
            });
          }
        }
        
        // 更新图表数据
        if (candlestickSeriesRef.current) {
          candlestickSeriesRef.current.setData(candlestickData);
        }
        if (ma5SeriesRef.current) {
          ma5SeriesRef.current.setData(ma5Data);
        }
        if (ma20SeriesRef.current) {
          ma20SeriesRef.current.setData(ma20Data);
        }
      }
    } catch (error) {
      console.error("Failed to fetch kline data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: "transparent" },
        textColor: "#d1d4dc",
      },
      grid: {
        vertLines: { color: "rgba(197, 203, 206, 0.1)" },
        horzLines: { color: "rgba(197, 203, 206, 0.1)" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // 添加K线系列
    const candlestickSeries = (chart as any).addSeries('Candlestick', {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candlestickSeriesRef.current = candlestickSeries;

    // 添加MA5线
    const ma5Series = (chart as any).addSeries('Line', {
      color: "#2962FF",
      lineWidth: 2,
      title: "MA5",
    });
    ma5SeriesRef.current = ma5Series;

    // 添加MA20线
    const ma20Series = (chart as any).addSeries('Line', {
      color: "#FF6D00",
      lineWidth: 2,
      title: "MA20",
    });
    ma20SeriesRef.current = ma20Series;

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    // 获取初始数据
    fetchKlineData();

    // 定时刷新（每分钟）
    const interval_id = setInterval(fetchKlineData, 60000);

    return () => {
      window.removeEventListener("resize", handleResize);
      clearInterval(interval_id);
      chart.remove();
    };
  }, [selectedInterval]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>实时K线图表</CardTitle>
            <CardDescription>{symbol} - MA5/MA20指标</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={selectedInterval} onValueChange={setSelectedInterval}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="15min">15分钟</SelectItem>
                <SelectItem value="30min">30分钟</SelectItem>
                <SelectItem value="1hour">1小时</SelectItem>
                <SelectItem value="2hour">2小时</SelectItem>
                <SelectItem value="4hour">4小时</SelectItem>
                <SelectItem value="1day">1天</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              onClick={fetchKlineData}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} className="w-full" />
        <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-[#2962FF]" />
            <span>MA5</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-[#FF6D00]" />
            <span>MA20</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-[#26a69a]" />
            <span>上涨</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-[#ef5350]" />
            <span>下跌</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
