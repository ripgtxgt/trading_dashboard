import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from "recharts";
import { ArrowUpIcon, ArrowDownIcon } from "lucide-react";
import { useMemo } from "react";

export function TradeHistory() {
  const { data: trades, isLoading } = trpc.trading.getTrades.useQuery(
    { limit: 50 },
    { refetchInterval: 10000 }
  );

  const { data: state } = trpc.trading.getState.useQuery(undefined, {
    refetchInterval: 5000,
  });

  // 计算累计盈亏曲线数据
  const chartData = useMemo(() => {
    if (!trades || !state) return [];

    const initialCapital = parseFloat(state.initialCapital);
    let cumulativePnL = 0;
    
    return trades
      .slice()
      .reverse() // 按时间正序
      .map((trade, index) => {
        const pnl = parseFloat(trade.pnl);
        cumulativePnL += pnl;
        const capital = initialCapital + cumulativePnL;
        
        return {
          index: index + 1,
          capital: parseFloat(capital.toFixed(2)),
          pnl: parseFloat(pnl.toFixed(2)),
          direction: trade.direction,
          entryPrice: parseFloat(trade.entryPrice),
          exitPrice: parseFloat(trade.exitPrice),
          time: new Date(trade.exitTime).toLocaleString(),
        };
      });
  }, [trades, state]);

  // 找出最大盈利和最大亏损的交易
  const maxProfit = useMemo(() => {
    if (!chartData.length) return null;
    return chartData.reduce((max, current) => 
      current.pnl > max.pnl ? current : max
    );
  }, [chartData]);

  const maxLoss = useMemo(() => {
    if (!chartData.length) return null;
    return chartData.reduce((min, current) => 
      current.pnl < min.pnl ? current : min
    );
  }, [chartData]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>交易历史分析</CardTitle>
          <CardDescription>加载中...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!chartData.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>交易历史分析</CardTitle>
          <CardDescription>暂无交易数据</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-12">
            开始交易后，这里将显示盈亏曲线和交易分析
          </p>
        </CardContent>
      </Card>
    );
  }

  const initialCapital = state ? parseFloat(state.initialCapital) : 0;
  const finalCapital = chartData[chartData.length - 1]?.capital || initialCapital;
  const totalReturn = ((finalCapital - initialCapital) / initialCapital) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>交易历史分析</CardTitle>
        <CardDescription>
          累计盈亏曲线 · 共{chartData.length}笔交易
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 统计卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">初始资金</p>
            <p className="text-lg font-semibold">{initialCapital.toFixed(2)} U</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">当前资金</p>
            <p className={`text-lg font-semibold ${totalReturn >= 0 ? "text-green-600" : "text-red-600"}`}>
              {finalCapital.toFixed(2)} U
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">总收益率</p>
            <p className={`text-lg font-semibold ${totalReturn >= 0 ? "text-green-600" : "text-red-600"}`}>
              {totalReturn >= 0 ? "+" : ""}{totalReturn.toFixed(2)}%
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">交易次数</p>
            <p className="text-lg font-semibold">{chartData.length}</p>
          </div>
        </div>

        {/* 盈亏曲线图 */}
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="index" 
                label={{ value: "交易序号", position: "insideBottom", offset: -5 }}
              />
              <YAxis 
                label={{ value: "资金 (USDT)", angle: -90, position: "insideLeft" }}
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0]?.payload;
                    return (
                      <div className="bg-background border rounded-lg p-3 shadow-lg">
                        <p className="font-semibold mb-2">交易 #{data.index}</p>
                        <div className="space-y-1 text-sm">
                          <div className="flex items-center gap-2">
                            {data.direction === "long" ? (
                              <ArrowUpIcon className="h-3 w-3 text-green-600" />
                            ) : (
                              <ArrowDownIcon className="h-3 w-3 text-red-600" />
                            )}
                            <span>{data.direction === "long" ? "做多" : "做空"}</span>
                          </div>
                          <p>入场: ${data.entryPrice.toFixed(2)}</p>
                          <p>出场: ${data.exitPrice.toFixed(2)}</p>
                          <p className={data.pnl >= 0 ? "text-green-600" : "text-red-600"}>
                            盈亏: {data.pnl >= 0 ? "+" : ""}{data.pnl.toFixed(2)} U
                          </p>
                          <p>资金: {data.capital.toFixed(2)} U</p>
                          <p className="text-xs text-muted-foreground">{data.time}</p>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="capital" 
                stroke="#3b82f6" 
                strokeWidth={2}
                name="账户资金"
                dot={false}
              />
              
              {/* 标记最大盈利点 */}
              {maxProfit && (
                <ReferenceDot
                  x={maxProfit.index}
                  y={maxProfit.capital}
                  r={6}
                  fill="#22c55e"
                  stroke="#fff"
                  strokeWidth={2}
                />
              )}
              
              {/* 标记最大亏损点 */}
              {maxLoss && maxLoss.pnl < 0 && (
                <ReferenceDot
                  x={maxLoss.index}
                  y={maxLoss.capital}
                  r={6}
                  fill="#ef4444"
                  stroke="#fff"
                  strokeWidth={2}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 关键交易点 */}
        {(maxProfit || maxLoss) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {maxProfit && (
              <div className="rounded-lg border bg-green-50 dark:bg-green-950/20 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <ArrowUpIcon className="h-4 w-4 text-green-600" />
                  <span className="font-semibold text-green-600">最大盈利交易</span>
                </div>
                <div className="space-y-1 text-sm">
                  <p>交易 #{maxProfit.index}</p>
                  <p>盈利: +{maxProfit.pnl.toFixed(2)} U</p>
                  <p className="text-xs text-muted-foreground">{maxProfit.time}</p>
                </div>
              </div>
            )}
            
            {maxLoss && maxLoss.pnl < 0 && (
              <div className="rounded-lg border bg-red-50 dark:bg-red-950/20 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <ArrowDownIcon className="h-4 w-4 text-red-600" />
                  <span className="font-semibold text-red-600">最大亏损交易</span>
                </div>
                <div className="space-y-1 text-sm">
                  <p>交易 #{maxLoss.index}</p>
                  <p>亏损: {maxLoss.pnl.toFixed(2)} U</p>
                  <p className="text-xs text-muted-foreground">{maxLoss.time}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
