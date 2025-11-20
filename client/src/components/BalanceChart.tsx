import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function BalanceChart() {
  const { data: history } = trpc.trading.getBalanceHistory.useQuery(
    { hours: 24 },
    { refetchInterval: 30000 }
  );

  if (!history || history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>资金曲线</CardTitle>
          <CardDescription>最近24小时资金变化</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            暂无数据
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = history.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    }),
    capital: parseFloat(item.capital),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>资金曲线</CardTitle>
        <CardDescription>最近24小时资金变化</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              tickMargin={10}
            />
            <YAxis
              tick={{ fontSize: 12 }}
              tickMargin={10}
              domain={["auto", "auto"]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "6px",
              }}
            />
            <Line
              type="monotone"
              dataKey="capital"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
