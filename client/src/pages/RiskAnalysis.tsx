import Navigation from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertTriangle, TrendingUp, PauseCircle, Activity } from "lucide-react";

export default function RiskAnalysis() {
  // 模拟数据
  const volatilityData = [
    { time: '10:00', volatility: 2.1 },
    { time: '11:00', volatility: 2.5 },
    { time: '12:00', volatility: 3.2 },
    { time: '13:00', volatility: 4.5 },
    { time: '14:00', volatility: 6.8 },
    { time: '15:00', volatility: 5.2 },
    { time: '16:00', volatility: 3.8 },
    { time: '17:00', volatility: 2.9 },
  ];

  const pauseEvents = [
    { time: '14:15', reason: '波动率超过10%', duration: 25 },
    { time: '16:30', reason: '市场剧烈波动', duration: 15 },
  ];

  const positionAdjustments = [
    { time: '13:00', from: 0.01, to: 0.007, reason: '波动率上升至中等' },
    { time: '14:00', from: 0.007, to: 0.004, reason: '波动率上升至高等' },
    { time: '15:00', from: 0.004, to: 0.007, reason: '波动率降低' },
  ];

  return (
    <>
      <Navigation />
      <div className="container mx-auto p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold">风险历史分析</h1>
          <p className="text-muted-foreground mt-1">波动率趋势和风险事件记录</p>
        </div>

        {/* 波动率趋势图 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              波动率趋势
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={volatilityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: '波动率 (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="volatility" stroke="#8884d8" name="波动率" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
              <div className="p-3 bg-green-50 rounded">
                <div className="text-gray-600">低风险</div>
                <div className="font-bold text-green-600">&lt; 2%</div>
              </div>
              <div className="p-3 bg-yellow-50 rounded">
                <div className="text-gray-600">中等风险</div>
                <div className="font-bold text-yellow-600">2-5%</div>
              </div>
              <div className="p-3 bg-orange-50 rounded">
                <div className="text-gray-600">高风险</div>
                <div className="font-bold text-orange-600">5-10%</div>
              </div>
              <div className="p-3 bg-red-50 rounded">
                <div className="text-gray-600">极高风险</div>
                <div className="font-bold text-red-600">&gt; 10%</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 暂停事件时间线 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PauseCircle className="h-5 w-5" />
              暂停事件记录
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pauseEvents.map((event, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-orange-900">{event.time}</span>
                      <Badge variant="outline" className="text-orange-700 border-orange-300">
                        暂停 {event.duration}分钟
                      </Badge>
                    </div>
                    <div className="text-sm text-orange-700 mt-1">{event.reason}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 仓位调整记录 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              仓位调整记录
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {positionAdjustments.map((adj, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <Activity className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-blue-900">{adj.time}</span>
                      <div className="text-sm">
                        <span className="text-gray-600">{adj.from.toFixed(4)}</span>
                        <span className="mx-2">→</span>
                        <span className="font-medium text-blue-700">{adj.to.toFixed(4)}</span>
                      </div>
                    </div>
                    <div className="text-sm text-blue-700 mt-1">{adj.reason}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
