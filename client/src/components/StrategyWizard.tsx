import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  Loader2,
  TrendingUp,
  Target,
  Zap
} from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";

type WizardStep = 1 | 2 | 3 | 4;

interface StrategyParams {
  name: string;
  ma_short: number;
  ma_long: number;
  position_size: number;
}

export function StrategyWizard() {
  const [currentStep, setCurrentStep] = useState<WizardStep>(1);
  const [timeframe, setTimeframe] = useState("1h");
  const [days, setDays] = useState(30);
  const [strategies, setStrategies] = useState<StrategyParams[]>([
    { name: "保守型", ma_short: 5, ma_long: 20, position_size: 0.1 },
    { name: "平衡型", ma_short: 10, ma_long: 30, position_size: 0.15 },
    { name: "激进型", ma_short: 15, ma_long: 40, position_size: 0.2 },
  ]);
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);

  // 获取策略对比结果
  const { data: comparisonData, refetch } = trpc.v24.getStrategyComparison.useQuery();

  // 启动回测
  const startBacktestMutation = trpc.v24.startStrategyBacktest.useMutation({
    onSuccess: () => {
      toast.success("回测已启动，请稍候...");
      setCurrentStep(3);
      // 每5秒刷新一次结果
      const interval = setInterval(() => {
        refetch();
      }, 5000);
      
      // 30秒后停止刷新
      setTimeout(() => {
        clearInterval(interval);
      }, 30000);
    },
    onError: (error) => {
      toast.error("启动回测失败: " + error.message);
    },
  });

  // 应用策略
  const applyStrategyMutation = trpc.strategy.createParams.useMutation({
    onSuccess: () => {
      toast.success("策略已保存！");
      setCurrentStep(4);
    },
    onError: (error) => {
      toast.error("应用策略失败: " + error.message);
    },
  });

  const handleNext = () => {
    if (currentStep === 2) {
      // 启动回测
      const strategyParams = strategies.map(s => ({
        name: s.name,
        params: {
          ma_short: String(s.ma_short),
          ma_long: String(s.ma_long),
          position_size: String(s.position_size),
        },
      }));

      startBacktestMutation.mutate({
        strategies: strategyParams,
        timeframe,
        days,
      });
    } else if (currentStep < 4) {
      setCurrentStep((prev) => (prev + 1) as WizardStep);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as WizardStep);
    }
  };

  const handleApplyStrategy = () => {
    if (!selectedStrategy) {
      toast.error("请先选择一个策略");
      return;
    }

    const strategy = strategies.find(s => s.name === selectedStrategy);
    if (!strategy) return;

    applyStrategyMutation.mutate({
      shortMaPeriod: strategy.ma_short,
      longMaPeriod: strategy.ma_long,
      timeframe: timeframe as "15m" | "30m" | "1h" | "2h" | "4h",
      sensitivity: "standard",
      isActive: 1,
    });
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">欢迎使用策略优化向导</h3>
              <p className="text-gray-600 mb-4">
                本向导将帮助您：
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  对比多个策略的历史表现
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  查看详细的回测指标
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  一键应用最优策略
                </li>
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">提示</p>
                  <p className="text-sm text-blue-700 mt-1">
                    回测基于历史数据，不代表未来表现。请结合实际情况谨慎选择策略。
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">设置回测参数</h3>
            </div>

            <div className="space-y-4">
              <div>
                <Label>时间周期</Label>
                <Select value={timeframe} onValueChange={setTimeframe}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15m">15分钟</SelectItem>
                    <SelectItem value="30m">30分钟</SelectItem>
                    <SelectItem value="1h">1小时</SelectItem>
                    <SelectItem value="2h">2小时</SelectItem>
                    <SelectItem value="4h">4小时</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>回测天数</Label>
                <Input
                  type="number"
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  min={7}
                  max={90}
                />
                <p className="text-xs text-gray-500 mt-1">
                  建议: 7-30天用于快速测试，30-90天用于全面评估
                </p>
              </div>

              <div>
                <Label className="mb-3 block">待对比策略</Label>
                <div className="space-y-3">
                  {strategies.map((strategy, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{strategy.name}</p>
                        <p className="text-xs text-gray-600">
                          MA({strategy.ma_short},{strategy.ma_long}) · 仓位 {(strategy.position_size * 100).toFixed(0)}%
                        </p>
                      </div>
                      <Badge variant="outline">待测试</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">回测结果</h3>
            </div>

            {!comparisonData?.results || comparisonData.results.length === 0 ? (
              <div className="text-center py-12">
                <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-600">正在运行回测...</p>
                <p className="text-sm text-gray-500 mt-2">
                  这可能需要几分钟时间，请耐心等待
                </p>
                <Progress value={33} className="mt-4 max-w-xs mx-auto" />
              </div>
            ) : (
              <div className="space-y-4">
                {comparisonData.results.map((result: any, index: number) => (
                  <Card
                    key={index}
                    className={`cursor-pointer transition-all ${
                      selectedStrategy === result.name
                        ? "ring-2 ring-blue-600 bg-blue-50"
                        : "hover:bg-gray-50"
                    }`}
                    onClick={() => setSelectedStrategy(result.name)}
                  >
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h4 className="font-semibold text-lg">{result.name}</h4>
                          <p className="text-sm text-gray-600">
                            MA({result.params.ma_short},{result.params.ma_long})
                          </p>
                        </div>
                        {selectedStrategy === result.name && (
                          <Badge className="bg-blue-600">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            已选择
                          </Badge>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">总收益</p>
                          <p className={`text-lg font-semibold ${
                            result.metrics.total_pnl >= 0 ? "text-green-600" : "text-red-600"
                          }`}>
                            {result.metrics.total_pnl?.toFixed(2) || "0.00"}%
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">胜率</p>
                          <p className="text-lg font-semibold">
                            {result.metrics.win_rate?.toFixed(1) || "0.0"}%
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">夏普比率</p>
                          <p className="text-lg font-semibold">
                            {result.metrics.sharpe_ratio?.toFixed(2) || "0.00"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">最大回撤</p>
                          <p className="text-lg font-semibold text-red-600">
                            {result.metrics.max_drawdown?.toFixed(2) || "0.00"}%
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {selectedStrategy && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Target className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-green-900">准备应用策略</p>
                        <p className="text-sm text-green-700 mt-1">
                          您已选择 "{selectedStrategy}"，点击下一步应用此策略
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">策略应用成功！</h3>
              <p className="text-gray-600">
                策略 "{selectedStrategy}" 已保存到系统
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">下一步建议</p>
                  <ul className="text-sm text-blue-700 mt-2 space-y-1">
                    <li>• 在测试模式下运行新策略，观察表现</li>
                    <li>• 根据实际情况调整参数</li>
                    <li>• 确认无误后切换到实盘模式</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>策略优化向导</CardTitle>
        <CardDescription>
          通过回测对比找到最适合的交易策略
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* 进度指示器 */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className="flex items-center"
              >
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full font-medium ${
                    step === currentStep
                      ? "bg-blue-600 text-white"
                      : step < currentStep
                      ? "bg-green-600 text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {step < currentStep ? (
                    <CheckCircle2 className="h-5 w-5" />
                  ) : (
                    step
                  )}
                </div>
                {step < 4 && (
                  <div
                    className={`w-full h-1 mx-2 ${
                      step < currentStep ? "bg-green-600" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>开始</span>
            <span>参数</span>
            <span>结果</span>
            <span>完成</span>
          </div>
        </div>

        {/* 步骤内容 */}
        <div className="min-h-[400px]">
          {renderStep()}
        </div>

        {/* 导航按钮 */}
        <div className="flex justify-between mt-8 pt-6 border-t">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 1 || currentStep === 4}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            上一步
          </Button>

          {currentStep < 3 ? (
            <Button
              onClick={handleNext}
              disabled={startBacktestMutation.isPending}
            >
              {startBacktestMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  启动中...
                </>
              ) : (
                <>
                  下一步
                  <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          ) : currentStep === 3 ? (
            <Button
              onClick={handleApplyStrategy}
              disabled={!selectedStrategy || applyStrategyMutation.isPending}
            >
              {applyStrategyMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  应用中...
                </>
              ) : (
                <>
                  应用策略
                  <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          ) : (
            <Button onClick={() => window.location.reload()}>
              完成
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
