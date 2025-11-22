import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, Award, Target } from "lucide-react";

/**
 * 回测历史可视化组件
 * 显示不同参数组合的历史回测结果对比
 */
export function BacktestHistoryChart() {
  const { data: history, isLoading } = trpc.strategy.getBacktestHistory.useQuery({ limit: 20 });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>回测历史</CardTitle>
          <CardDescription>策略参数优化历史记录</CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!history || history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>回测历史</CardTitle>
          <CardDescription>策略参数优化历史记录</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">暂无回测历史</p>
        </CardContent>
      </Card>
    );
  }

  // 准备图表数据
  const chartData = history.map((item: any, index: number) => ({
    name: `MA${item.shortMaPeriod}/${item.longMaPeriod}`,
    date: new Date(item.createdAt).toLocaleDateString("zh-CN", { month: "short", day: "numeric" }),
    winRate: parseFloat(item.winRate),
    totalPnl: parseFloat(item.totalPnl),
    sharpeRatio: parseFloat(item.sharpeRatio),
    compositeScore: parseFloat(item.compositeScore),
    index: history.length - index, // 反转索引，最新的在右边
  })).reverse(); // 反转数组，时间从左到右

  // 找出最佳结果
  const bestWinRate = history.reduce((prev: any, current: any) =>
    parseFloat(current.winRate) > parseFloat(prev.winRate) ? current : prev
  );
  const bestPnl = history.reduce((prev: any, current: any) =>
    parseFloat(current.totalPnl) > parseFloat(prev.totalPnl) ? current : prev
  );
  const bestComposite = history.reduce((prev: any, current: any) =>
    parseFloat(current.compositeScore) > parseFloat(prev.compositeScore) ? current : prev
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>回测历史</CardTitle>
        <CardDescription>策略参数优化历史记录（最近20次）</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 最佳结果统计 */}
        <div className="grid gap-4 md:grid-cols-3">
          <div className="flex items-center gap-3 p-4 border rounded-lg">
            <Award className="h-8 w-8 text-yellow-500" />
            <div>
              <p className="text-sm text-muted-foreground">最高胜率</p>
              <p className="text-lg font-semibold">{parseFloat(bestWinRate.winRate).toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground">
                MA{bestWinRate.shortMaPeriod}/{bestWinRate.longMaPeriod} {bestWinRate.timeframe}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 border rounded-lg">
            <TrendingUp className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-sm text-muted-foreground">最高收益</p>
              <p className="text-lg font-semibold">{parseFloat(bestPnl.totalPnl).toFixed(2)}%</p>
              <p className="text-xs text-muted-foreground">
                MA{bestPnl.shortMaPeriod}/{bestPnl.longMaPeriod} {bestPnl.timeframe}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 border rounded-lg">
            <Target className="h-8 w-8 text-blue-500" />
            <div>
              <p className="text-sm text-muted-foreground">最佳综合</p>
              <p className="text-lg font-semibold">{parseFloat(bestComposite.compositeScore).toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">
                MA{bestComposite.shortMaPeriod}/{bestComposite.longMaPeriod} {bestComposite.timeframe}
              </p>
            </div>
          </div>
        </div>

        {/* 胜率和收益趋势图 */}
        <div>
          <h4 className="text-sm font-medium mb-4">胜率和收益趋势</h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12 }}
                label={{ value: "胜率 (%)", angle: -90, position: "insideLeft" }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12 }}
                label={{ value: "收益 (%)", angle: 90, position: "insideRight" }}
              />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: any, name: string) => {
                  if (name === "胜率") return `${value.toFixed(1)}%`;
                  if (name === "收益") return `${value.toFixed(2)}%`;
                  return value;
                }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="winRate"
                stroke="#8b5cf6"
                name="胜率"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="totalPnl"
                stroke="#10b981"
                name="收益"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 综合得分趋势图 */}
        <div>
          <h4 className="text-sm font-medium mb-4">综合得分趋势</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                label={{ value: "综合得分", angle: -90, position: "insideLeft" }}
              />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: any) => value.toFixed(2)}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="compositeScore"
                stroke="#3b82f6"
                name="综合得分"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 历史记录表格 */}
        <div>
          <h4 className="text-sm font-medium mb-4">详细记录</h4>
          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-2 text-left">时间</th>
                    <th className="px-4 py-2 text-left">参数</th>
                    <th className="px-4 py-2 text-right">交易数</th>
                    <th className="px-4 py-2 text-right">胜率</th>
                    <th className="px-4 py-2 text-right">收益</th>
                    <th className="px-4 py-2 text-right">夏普</th>
                    <th className="px-4 py-2 text-right">综合得分</th>
                  </tr>
                </thead>
                <tbody>
                  {history.slice(0, 10).map((item: any) => (
                    <tr key={item.id} className="border-t hover:bg-muted/50">
                      <td className="px-4 py-2">
                        {new Date(item.createdAt).toLocaleString("zh-CN", {
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td className="px-4 py-2">
                        MA{item.shortMaPeriod}/{item.longMaPeriod} {item.timeframe}
                      </td>
                      <td className="px-4 py-2 text-right">{item.totalTrades}</td>
                      <td className="px-4 py-2 text-right">{parseFloat(item.winRate).toFixed(1)}%</td>
                      <td className={`px-4 py-2 text-right ${parseFloat(item.totalPnl) > 0 ? "text-green-600" : "text-red-600"}`}>
                        {parseFloat(item.totalPnl) > 0 ? "+" : ""}{parseFloat(item.totalPnl).toFixed(2)}%
                      </td>
                      <td className="px-4 py-2 text-right">{parseFloat(item.sharpeRatio).toFixed(2)}</td>
                      <td className="px-4 py-2 text-right font-semibold">{parseFloat(item.compositeScore).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
