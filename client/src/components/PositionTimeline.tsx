import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { trpc } from "@/lib/trpc";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area, ComposedChart } from "recharts";
import { TrendingUp, Target, Activity } from "lucide-react";

interface BalanceSnapshot {
  capital: string;
  timestamp: Date;
}

interface TimelineData {
  time: string;
  balance: number;
  stage: string;
  progress: number;
}

export function PositionTimeline() {
  const [timelineData, setTimelineData] = useState<TimelineData[]>([]);
  const [currentBalance, setCurrentBalance] = useState(0);
  const [currentStage, setCurrentStage] = useState("初始阶段");
  const [progress, setProgress] = useState(0);

  // 滚仓阶段定义
  const stages = [
    { name: "初始阶段", target: 10, color: "#3b82f6" },
    { name: "第一阶段", target: 20, color: "#8b5cf6" },
    { name: "第二阶段", target: 40, color: "#ec4899" },
    { name: "第三阶段", target: 80, color: "#f59e0b" },
    { name: "目标达成", target: 100, color: "#10b981" },
  ];

  // 获取余额快照数据
  const { data: snapshots, isLoading } = trpc.trading.getBalanceSnapshots.useQuery(
    { limit: 100 },
    { refetchInterval: 30000 } // 每30秒刷新一次
  );

  useEffect(() => {
    if (snapshots && snapshots.length > 0) {
      // 处理数据
      const processed = snapshots.map((snapshot: BalanceSnapshot) => {
        const balance = parseFloat(snapshot.capital);
        const stage = getStageForBalance(balance);
        const progress = (balance / 100) * 100; // 目标是100U

        return {
          time: snapshot.timestamp.toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
          }),
          balance,
          stage: stage.name,
          progress,
        };
      }).reverse(); // 按时间正序排列

      setTimelineData(processed);

      // 设置当前状态
      const latest = processed[processed.length - 1];
      if (latest) {
        setCurrentBalance(latest.balance);
        setCurrentStage(latest.stage);
        setProgress(latest.progress);
      }
    }
  }, [snapshots]);

  const getStageForBalance = (balance: number) => {
    if (balance >= 100) return stages[4];
    if (balance >= 80) return stages[3];
    if (balance >= 40) return stages[2];
    if (balance >= 20) return stages[1];
    return stages[0];
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-medium">{data.time}</p>
          <p className="text-sm text-primary font-bold">{data.balance.toFixed(2)} USDT</p>
          <p className="text-xs text-muted-foreground">{data.stage}</p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>仓位追踪</CardTitle>
          <CardDescription>10U滚仓进度</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[400px]">
            <Activity className="h-8 w-8 animate-pulse text-blue-500" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>仓位追踪</CardTitle>
            <CardDescription>10U滚仓进度 - 目标100U</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary">{currentBalance.toFixed(2)} USDT</div>
            <div className="text-sm text-muted-foreground">{currentStage}</div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 进度条 */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">整体进度</span>
            <span className="font-medium">{progress.toFixed(1)}%</span>
          </div>
          <div className="h-3 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-green-500 transition-all duration-500"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>10U</span>
            <span>20U</span>
            <span>40U</span>
            <span>80U</span>
            <span>100U</span>
          </div>
        </div>

        {/* 阶段里程碑 */}
        <div className="grid grid-cols-5 gap-2">
          {stages.map((stage, index) => {
            const isCompleted = currentBalance >= stage.target;
            const isCurrent = currentStage === stage.name;
            return (
              <div
                key={index}
                className={`text-center p-3 rounded-lg border-2 transition-all ${
                  isCurrent
                    ? "border-primary bg-primary/10"
                    : isCompleted
                    ? "border-green-500 bg-green-500/10"
                    : "border-border bg-secondary/50"
                }`}
              >
                <div className="flex items-center justify-center mb-1">
                  {isCompleted ? (
                    <TrendingUp className="h-5 w-5 text-green-500" />
                  ) : (
                    <Target className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                <div className="text-xs font-medium">{stage.name}</div>
                <div className="text-xs text-muted-foreground">{stage.target}U</div>
              </div>
            );
          })}
        </div>

        {/* 资金曲线图 */}
        {timelineData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={timelineData}>
              <defs>
                <linearGradient id="balanceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(197, 203, 206, 0.1)" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                domain={[0, 'dataMax + 10']}
                tick={{ fontSize: 12 }}
                label={{ value: 'USDT', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* 阶段参考线 */}
              <ReferenceLine y={20} stroke="#8b5cf6" strokeDasharray="3 3" label={{ value: '20U', position: 'right', fill: '#8b5cf6', fontSize: 12 }} />
              <ReferenceLine y={40} stroke="#ec4899" strokeDasharray="3 3" label={{ value: '40U', position: 'right', fill: '#ec4899', fontSize: 12 }} />
              <ReferenceLine y={80} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: '80U', position: 'right', fill: '#f59e0b', fontSize: 12 }} />
              <ReferenceLine y={100} stroke="#10b981" strokeDasharray="3 3" label={{ value: '100U (目标)', position: 'right', fill: '#10b981', fontSize: 12 }} />
              
              <Area
                type="monotone"
                dataKey="balance"
                stroke="#3b82f6"
                fill="url(#balanceGradient)"
                strokeWidth={0}
              />
              <Line
                type="monotone"
                dataKey="balance"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            <div className="text-center">
              <Activity className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p>暂无历史数据</p>
              <p className="text-xs mt-1">开始交易后将显示资金变化曲线</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
