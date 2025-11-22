import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Award, AlertCircle } from 'lucide-react';

interface StrategyMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_return: number;
  total_return_pct: number;
  sharpe_ratio: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  profit_factor: number;
  avg_win: number;
  avg_loss: number;
}

interface StrategyConfig {
  name: string;
  params: Record<string, any>;
}

interface StrategyResult {
  config: StrategyConfig;
  metrics: StrategyMetrics;
  equity_curve: number[];
  timestamps: string[];
}

interface StrategyComparisonProps {
  results?: StrategyResult[];
}

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple
];

export function StrategyComparison({ results = [] }: StrategyComparisonProps) {
  const [selectedStrategies, setSelectedStrategies] = useState<number[]>([]);

  // 如果没有数据，显示示例数据
  const displayResults = results.length > 0 ? results : getExampleResults();

  // 准备图表数据
  const chartData = prepareChartData(displayResults, selectedStrategies);

  // 切换策略选择
  const toggleStrategy = (index: number) => {
    setSelectedStrategies((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  // 选择全部
  const selectAll = () => {
    setSelectedStrategies(displayResults.map((_, i) => i));
  };

  // 清除选择
  const clearAll = () => {
    setSelectedStrategies([]);
  };

  return (
    <div className="space-y-6">
      {/* 策略列表 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>策略对比</CardTitle>
              <CardDescription>对比不同参数配置的策略表现</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={selectAll}>
                全选
              </Button>
              <Button size="sm" variant="outline" onClick={clearAll}>
                清除
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {displayResults.map((result, index) => (
              <StrategyCard
                key={index}
                result={result}
                index={index}
                isSelected={selectedStrategies.includes(index)}
                onToggle={() => toggleStrategy(index)}
                color={COLORS[index % COLORS.length]}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 收益曲线对比图 */}
      {selectedStrategies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>收益曲线对比</CardTitle>
            <CardDescription>已选择 {selectedStrategies.length} 个策略</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="index"
                    label={{ value: '交易次数', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis label={{ value: '资金 (USDT)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  {selectedStrategies.map((strategyIndex) => (
                    <Line
                      key={strategyIndex}
                      type="monotone"
                      dataKey={`strategy_${strategyIndex}`}
                      name={displayResults[strategyIndex].config.name}
                      stroke={COLORS[strategyIndex % COLORS.length]}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 指标对比表格 */}
      {selectedStrategies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>指标对比</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">指标</th>
                    {selectedStrategies.map((index) => (
                      <th key={index} className="text-right p-2">
                        {displayResults[index].config.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <MetricRow
                    label="总交易次数"
                    values={selectedStrategies.map((i) => displayResults[i].metrics.total_trades)}
                  />
                  <MetricRow
                    label="胜率"
                    values={selectedStrategies.map((i) => `${displayResults[i].metrics.win_rate}%`)}
                  />
                  <MetricRow
                    label="总收益"
                    values={selectedStrategies.map(
                      (i) => `${displayResults[i].metrics.total_return.toFixed(2)} USDT`
                    )}
                    highlight
                  />
                  <MetricRow
                    label="收益率"
                    values={selectedStrategies.map(
                      (i) => `${displayResults[i].metrics.total_return_pct.toFixed(2)}%`
                    )}
                    highlight
                  />
                  <MetricRow
                    label="夏普比率"
                    values={selectedStrategies.map((i) => displayResults[i].metrics.sharpe_ratio.toFixed(2))}
                  />
                  <MetricRow
                    label="最大回撤"
                    values={selectedStrategies.map(
                      (i) => `${displayResults[i].metrics.max_drawdown_pct.toFixed(2)}%`
                    )}
                  />
                  <MetricRow
                    label="盈利因子"
                    values={selectedStrategies.map((i) => displayResults[i].metrics.profit_factor.toFixed(2))}
                  />
                  <MetricRow
                    label="平均盈利"
                    values={selectedStrategies.map((i) => `${displayResults[i].metrics.avg_win.toFixed(2)} USDT`)}
                  />
                  <MetricRow
                    label="平均亏损"
                    values={selectedStrategies.map((i) => `${displayResults[i].metrics.avg_loss.toFixed(2)} USDT`)}
                  />
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// 策略卡片组件
function StrategyCard({
  result,
  index,
  isSelected,
  onToggle,
  color,
}: {
  result: StrategyResult;
  index: number;
  isSelected: boolean;
  onToggle: () => void;
  color: string;
}) {
  const { config, metrics } = result;
  const isProfit = metrics.total_return > 0;

  return (
    <div
      className={`border rounded-lg p-4 cursor-pointer transition-all ${
        isSelected ? 'ring-2 ring-offset-2' : 'hover:border-gray-400'
      }`}
      style={{ 
        borderColor: isSelected ? color : undefined,
        '--tw-ring-color': color,
      } as React.CSSProperties}
      onClick={onToggle}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
          <h3 className="font-semibold">{config.name}</h3>
          {index === 0 && (
            <Badge variant="default" className="ml-2">
              <Award className="h-3 w-3 mr-1" />
              最佳
            </Badge>
          )}
        </div>
        <div className={`flex items-center gap-1 ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
          {isProfit ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          <span className="font-semibold">{metrics.total_return_pct.toFixed(2)}%</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 text-sm">
        <div>
          <div className="text-gray-500 text-xs">胜率</div>
          <div className="font-medium">{metrics.win_rate}%</div>
        </div>
        <div>
          <div className="text-gray-500 text-xs">交易次数</div>
          <div className="font-medium">{metrics.total_trades}</div>
        </div>
        <div>
          <div className="text-gray-500 text-xs">夏普比率</div>
          <div className="font-medium">{metrics.sharpe_ratio.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-gray-500 text-xs">最大回撤</div>
          <div className="font-medium text-red-600">{metrics.max_drawdown_pct.toFixed(2)}%</div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t text-xs text-gray-600">
        参数: {Object.entries(config.params).map(([key, value]) => `${key}=${value}`).join(', ')}
      </div>
    </div>
  );
}

// 指标行组件
function MetricRow({
  label,
  values,
  highlight = false,
}: {
  label: string;
  values: (string | number)[];
  highlight?: boolean;
}) {
  return (
    <tr className={`border-b ${highlight ? 'bg-blue-50' : ''}`}>
      <td className="p-2 font-medium">{label}</td>
      {values.map((value, i) => (
        <td key={i} className="text-right p-2">
          {value}
        </td>
      ))}
    </tr>
  );
}

// 准备图表数据
function prepareChartData(results: StrategyResult[], selectedIndices: number[]) {
  if (selectedIndices.length === 0) return [];

  // 找出最长的equity_curve
  const maxLength = Math.max(...selectedIndices.map((i) => results[i].equity_curve.length));

  // 构建数据点
  const data = [];
  for (let i = 0; i < maxLength; i++) {
    const point: any = { index: i };
    selectedIndices.forEach((strategyIndex) => {
      const curve = results[strategyIndex].equity_curve;
      point[`strategy_${strategyIndex}`] = curve[i] || null;
    });
    data.push(point);
  }

  return data;
}

// 示例数据
function getExampleResults(): StrategyResult[] {
  return [
    {
      config: {
        name: '保守型 MA(5,20)',
        params: { ma_short: 5, ma_long: 20, position_size: 0.1 },
      },
      metrics: {
        total_trades: 45,
        winning_trades: 28,
        losing_trades: 17,
        win_rate: 62.22,
        total_return: 15.8,
        total_return_pct: 15.8,
        sharpe_ratio: 1.45,
        max_drawdown: 8.2,
        max_drawdown_pct: 8.2,
        profit_factor: 1.85,
        avg_win: 1.2,
        avg_loss: 0.8,
      },
      equity_curve: generateEquityCurve(100, 15.8, 45),
      timestamps: [],
    },
    {
      config: {
        name: '平衡型 MA(10,30)',
        params: { ma_short: 10, ma_long: 30, position_size: 0.15 },
      },
      metrics: {
        total_trades: 32,
        winning_trades: 19,
        losing_trades: 13,
        win_rate: 59.38,
        total_return: 12.5,
        total_return_pct: 12.5,
        sharpe_ratio: 1.32,
        max_drawdown: 10.5,
        max_drawdown_pct: 10.5,
        profit_factor: 1.65,
        avg_win: 1.5,
        avg_loss: 0.9,
      },
      equity_curve: generateEquityCurve(100, 12.5, 32),
      timestamps: [],
    },
    {
      config: {
        name: '激进型 MA(3,15)',
        params: { ma_short: 3, ma_long: 15, position_size: 0.2 },
      },
      metrics: {
        total_trades: 68,
        winning_trades: 35,
        losing_trades: 33,
        win_rate: 51.47,
        total_return: 8.3,
        total_return_pct: 8.3,
        sharpe_ratio: 0.95,
        max_drawdown: 15.8,
        max_drawdown_pct: 15.8,
        profit_factor: 1.25,
        avg_win: 0.9,
        avg_loss: 0.7,
      },
      equity_curve: generateEquityCurve(100, 8.3, 68),
      timestamps: [],
    },
  ];
}

// 生成模拟资金曲线
function generateEquityCurve(initial: number, totalReturn: number, trades: number): number[] {
  const curve = [initial];
  const avgReturn = totalReturn / trades;

  for (let i = 0; i < trades; i++) {
    const randomReturn = avgReturn + (Math.random() - 0.5) * 4;
    curve.push(curve[curve.length - 1] + randomReturn);
  }

  return curve;
}
