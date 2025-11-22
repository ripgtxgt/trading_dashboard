import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RefreshCw } from "lucide-react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Bar,
} from "recharts";

interface KlineData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  ma5?: number;
  ma20?: number;
  // 用于显示K线的辅助字段
  candleBottom: number;
  candleTop: number;
  wickBottom: number;
  wickTop: number;
  isUp: boolean;
}

interface KlineChartProps {
  symbol?: string;
  interval?: string;
}

export function KlineChartSimple({ symbol = "XBTUSDTM", interval = "1hour" }: KlineChartProps) {
  const [data, setData] = useState<KlineData[]>([]);
  const [selectedInterval, setSelectedInterval] = useState(interval);
  const [loading, setLoading] = useState(false);

  const fetchKlineData = async () => {
    setLoading(true);
    try {
      const endTime = Math.floor(Date.now() / 1000);
      const startTime = endTime - 24 * 60 * 60; // 最近24小时
      
      const response = await fetch(
        `https://api.kucoin.com/api/v1/market/candles?type=${selectedInterval}&symbol=${symbol}&startAt=${startTime}&endAt=${endTime}`
      );
      
      const result = await response.json();
      
      if (result.code === "200000" && result.data) {
        const klines = result.data.reverse();
        
        const processedData: KlineData[] = [];
        
        for (let i = 0; i < klines.length; i++) {
          const [time, open, close, high, low] = klines[i];
          const openPrice = parseFloat(open);
          const closePrice = parseFloat(close);
          const highPrice = parseFloat(high);
          const lowPrice = parseFloat(low);
          const isUp = closePrice >= openPrice;
          
          const dataPoint: KlineData = {
            time: new Date(parseInt(time) * 1000).toLocaleTimeString('zh-CN', { 
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            }),
            open: openPrice,
            high: highPrice,
            low: lowPrice,
            close: closePrice,
            candleBottom: Math.min(openPrice, closePrice),
            candleTop: Math.max(openPrice, closePrice),
            wickBottom: lowPrice,
            wickTop: highPrice,
            isUp,
          };
          
          // 计算MA5
          if (i >= 4) {
            let sum5 = 0;
            for (let j = 0; j < 5; j++) {
              sum5 += parseFloat(klines[i - j][2]);
            }
            dataPoint.ma5 = sum5 / 5;
          }
          
          // 计算MA20
          if (i >= 19) {
            let sum20 = 0;
            for (let j = 0; j < 20; j++) {
              sum20 += parseFloat(klines[i - j][2]);
            }
            dataPoint.ma20 = sum20 / 20;
          }
          
          processedData.push(dataPoint);
        }
        
        setData(processedData);
      }
    } catch (error) {
      console.error("Failed to fetch kline data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKlineData();
    const intervalId = setInterval(fetchKlineData, 60000); // 每分钟刷新
    return () => clearInterval(intervalId);
  }, [selectedInterval]);

  // 自定义K线渲染
  const CustomCandlestick = (props: any) => {
    const { x, y, width, height, payload } = props;
    if (!payload) return null;
    
    const { candleBottom, candleTop, wickBottom, wickTop, isUp } = payload;
    const color = isUp ? "#26a69a" : "#ef5350";
    
    // 计算Y坐标（需要根据图表的Y轴范围）
    const yScale = props.yAxis;
    if (!yScale) return null;
    
    const candleBottomY = yScale.scale(candleTop);
    const candleTopY = yScale.scale(candleBottom);
    const wickBottomY = yScale.scale(wickBottom);
    const wickTopY = yScale.scale(wickTop);
    
    const candleHeight = Math.abs(candleTopY - candleBottomY);
    const candleWidth = width * 0.6;
    const candleX = x - candleWidth / 2;
    
    return (
      <g>
        {/* 上影线 */}
        <line
          x1={x}
          y1={wickTopY}
          x2={x}
          y2={candleBottomY}
          stroke={color}
          strokeWidth={1}
        />
        {/* K线实体 */}
        <rect
          x={candleX}
          y={candleBottomY}
          width={candleWidth}
          height={candleHeight || 1}
          fill={color}
          stroke={color}
        />
        {/* 下影线 */}
        <line
          x1={x}
          y1={candleTopY}
          x2={x}
          y2={wickBottomY}
          stroke={color}
          strokeWidth={1}
        />
      </g>
    );
  };

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
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(197, 203, 206, 0.1)" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              domain={['dataMin - 100', 'dataMax + 100']}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: 'none',
                borderRadius: '4px',
                color: '#fff',
              }}
              formatter={(value: any) => {
                if (typeof value === 'number') {
                  return value.toFixed(2);
                }
                return value;
              }}
            />
            <Legend />
            
            {/* K线（使用Bar模拟） */}
            <Bar
              dataKey="close"
              fill="#26a69a"
              shape={<CustomCandlestick />}
              name="价格"
            />
            
            {/* MA5线 */}
            <Line
              type="monotone"
              dataKey="ma5"
              stroke="#2962FF"
              strokeWidth={2}
              dot={false}
              name="MA5"
            />
            
            {/* MA20线 */}
            <Line
              type="monotone"
              dataKey="ma20"
              stroke="#FF6D00"
              strokeWidth={2}
              dot={false}
              name="MA20"
            />
          </ComposedChart>
        </ResponsiveContainer>
        
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
