import { useState, useEffect } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Activity, 
  TrendingUp, 
  DollarSign, 
  AlertTriangle,
  Settings,
  PlayCircle,
  PauseCircle,
  TestTube,
  Zap,
  BarChart3,
  StopCircle,
  Play
} from "lucide-react";
import { APP_TITLE } from "@/const";
import { trpc } from "@/lib/trpc";
import { ConnectionStatus } from "@/components/ConnectionStatus";
import { StrategyComparison } from "@/components/StrategyComparison";
import { StrategyWizard } from "@/components/StrategyWizard";
import { toast } from "sonner";

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const [testModeEnabled, setTestModeEnabled] = useState(false);

  // 获取测试模式状态
  const { data: testModeStatus, refetch: refetchTestMode } = trpc.v24.getTestModeStatus.useQuery();
  
  // 获取模拟余额
  const { data: simulatedBalance } = trpc.v24.getSimulatedBalance.useQuery(undefined, {
    enabled: testModeEnabled,
    refetchInterval: 5000,
  });

  // 获取风险状态
  const { data: riskStatus } = trpc.v24.getRiskStatus.useQuery(undefined, {
    refetchInterval: 10000,
  });

  // 获取交易状态
  const { data: botState } = trpc.trading.getState.useQuery(undefined, {
    refetchInterval: 5000,
  });

  // 获取策略对比结果
  const { data: strategyComparison } = trpc.v24.getStrategyComparison.useQuery();

  // 切换测试模式
  const setTestModeMutation = trpc.v24.setTestMode.useMutation({
    onSuccess: () => {
      refetchTestMode();
      toast.success(testModeEnabled ? "已切换到实盘模式" : "已切换到测试模式");
    },
    onError: (error) => {
      toast.error("切换模式失败: " + error.message);
    },
  });

  // 重置测试模式
  const resetTestModeMutation = trpc.v24.resetTestMode.useMutation({
    onSuccess: () => {
      toast.success("测试状态已重置");
    },
  });

  // 同步测试模式状态
  useEffect(() => {
    if (testModeStatus) {
      setTestModeEnabled(testModeStatus.enabled);
    }
  }, [testModeStatus]);

  // 处理测试模式切换
  const handleTestModeToggle = (checked: boolean) => {
    setTestModeEnabled(checked);
    setTestModeMutation.mutate({ enabled: checked });
  };

  // 处理重置测试模式
  const handleResetTestMode = () => {
    if (confirm("确定要重置测试状态吗？这将清除所有模拟交易记录。")) {
      resetTestModeMutation.mutate();
    }
  };

  // 紧急停止
  const emergencyStopMutation = trpc.trading.emergencyStop.useMutation({
    onSuccess: () => {
      toast.success("紧急停止已激活！所有交易活动已暂停。");
    },
    onError: (error) => {
      toast.error("紧急停止失败: " + error.message);
    },
  });

  // 恢复Bot
  const resumeBotMutation = trpc.trading.resumeBot.useMutation({
    onSuccess: () => {
      toast.success("Bot已恢复！交易活动已重新启动。");
    },
    onError: (error) => {
      toast.error("恢复失败: " + error.message);
    },
  });

  // 处理紧急停止
  const handleEmergencyStop = () => {
    if (confirm("确定要紧急停止所有交易吗？\n\n这将：\n- 暂停所有交易活动\n- 关闭当前持仓\n- 停止新交易")) {
      emergencyStopMutation.mutate();
    }
  };

  // 处理恢复交易
  const handleResumeBot = () => {
    if (confirm("确定要恢复交易活动吗？")) {
      resumeBotMutation.mutate();
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-2xl text-center">{APP_TITLE}</CardTitle>
            <CardDescription className="text-center">
              请登录以访问交易Dashboard
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <Button size="lg" onClick={() => window.location.href = "/api/oauth/login"}>
              登录
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{APP_TITLE}</h1>
                <p className="text-sm text-gray-500">交易监控与策略优化平台</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* 连接状态 */}
              <ConnectionStatus />
              
              {/* 测试模式开关 */}
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-lg">
                <TestTube className={`h-4 w-4 ${testModeEnabled ? 'text-orange-600' : 'text-gray-400'}`} />
                <Label htmlFor="test-mode" className="cursor-pointer text-sm font-medium">
                  测试模式
                </Label>
                <Switch
                  id="test-mode"
                  checked={testModeEnabled}
                  onCheckedChange={handleTestModeToggle}
                />
              </div>

              {/* 用户信息 */}
              <div className="flex items-center gap-2">
                <div className="text-right">
                  <p className="text-sm font-medium">{user?.name || "用户"}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="container mx-auto px-4 py-6">
        {/* 紧急停止控制区 */}
        <Card className="mb-6 border-red-200 bg-gradient-to-r from-red-50 to-orange-50">
          <CardContent className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <StopCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <p className="font-bold text-red-900">紧急控制</p>
                <p className="text-sm text-red-700">
                  {botState?.emergencyStopped === 1 
                    ? "⚠️ 交易已暂停 - 点击恢复按钮重新启动" 
                    : "在紧急情况下立即停止所有交易活动"}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              {botState?.emergencyStopped === 1 ? (
                <Button
                  variant="default"
                  size="lg"
                  onClick={handleResumeBot}
                  disabled={resumeBotMutation.isPending}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Play className="h-5 w-5 mr-2" />
                  恢复交易
                </Button>
              ) : (
                <Button
                  variant="destructive"
                  size="lg"
                  onClick={handleEmergencyStop}
                  disabled={emergencyStopMutation.isPending}
                  className="bg-red-600 hover:bg-red-700"
                >
                  <StopCircle className="h-5 w-5 mr-2" />
                  紧急停止
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 测试模式警告 */}
        {testModeEnabled && (
          <Card className="mb-6 border-orange-200 bg-orange-50">
            <CardContent className="flex items-center justify-between py-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                <div>
                  <p className="font-medium text-orange-900">当前为测试模式</p>
                  <p className="text-sm text-orange-700">
                    使用模拟资金进行交易，不会影响真实账户
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetTestMode}
                disabled={resetTestModeMutation.isPending}
              >
                重置测试状态
              </Button>
            </CardContent>
          </Card>
        )}

        {/* 核心指标卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* 账户余额 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                账户余额
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {testModeEnabled 
                  ? `${simulatedBalance?.total.toFixed(2) || "0.00"} USDT`
                  : `${botState?.capital || "N/A"}`
                }
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {testModeEnabled ? "模拟资金" : "实盘资金"}
              </p>
            </CardContent>
          </Card>

          {/* 交易状态 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <Activity className="h-4 w-4" />
                交易状态
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {botState?.isRunning ? (
                  <>
                    <PlayCircle className="h-5 w-5 text-green-600" />
                    <span className="text-lg font-semibold text-green-600">运行中</span>
                  </>
                ) : (
                  <>
                    <PauseCircle className="h-5 w-5 text-gray-400" />
                    <span className="text-lg font-semibold text-gray-600">已停止</span>
                  </>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                当前阶段: {botState?.currentStage || "N/A"}
              </p>
            </CardContent>
          </Card>

          {/* 今日盈亏 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                今日盈亏
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${
                (riskStatus?.daily_pnl || 0) >= 0 ? "text-green-600" : "text-red-600"
              }`}>
                {riskStatus?.daily_pnl?.toFixed(2) || "0.00"} USDT
              </div>
              <p className="text-xs text-gray-500 mt-1">
                总盈亏: {riskStatus?.total_pnl?.toFixed(2) || "0.00"} USDT
              </p>
            </CardContent>
          </Card>

          {/* 风险状态 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                风险状态
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {riskStatus?.is_trading_allowed ? (
                  <Badge variant="default" className="bg-green-600">
                    <Zap className="h-3 w-3 mr-1" />
                    正常
                  </Badge>
                ) : (
                  <Badge variant="destructive">
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    暂停
                  </Badge>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {riskStatus?.pause_reason || "交易运行正常"}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 标签页内容 */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4 lg:w-auto">
            <TabsTrigger value="overview">
              <Activity className="h-4 w-4 mr-2" />
              概览
            </TabsTrigger>
            <TabsTrigger value="wizard">
              <Zap className="h-4 w-4 mr-2" />
              策略向导
            </TabsTrigger>
            <TabsTrigger value="strategy">
              <BarChart3 className="h-4 w-4 mr-2" />
              策略对比
            </TabsTrigger>
            <TabsTrigger value="settings">
              <Settings className="h-4 w-4 mr-2" />
              设置
            </TabsTrigger>
          </TabsList>

          {/* 概览标签 */}
          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>交易概览</CardTitle>
                <CardDescription>
                  查看实时交易数据和系统状态
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center text-gray-500 py-8">
                  <Activity className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>交易数据加载中...</p>
                  <p className="text-sm mt-2">
                    实时数据将通过WebSocket自动更新
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 策略向导标签 */}
          <TabsContent value="wizard" className="space-y-4">
            <StrategyWizard />
          </TabsContent>

          {/* 策略对比标签 */}
          <TabsContent value="strategy" className="space-y-4">
            <StrategyComparison results={strategyComparison?.results || []} />
          </TabsContent>

          {/* 设置标签 */}
          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>系统设置</CardTitle>
                <CardDescription>
                  配置交易参数和风险控制
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>测试模式</Label>
                      <p className="text-sm text-gray-500">
                        使用模拟资金进行交易测试
                      </p>
                    </div>
                    <Switch
                      checked={testModeEnabled}
                      onCheckedChange={handleTestModeToggle}
                    />
                  </div>

                  {testModeEnabled && (
                    <div className="pt-4 border-t">
                      <h4 className="font-medium mb-2">测试模式配置</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">初始资金:</span>
                          <span className="font-medium">
                            {testModeStatus?.initial_balance || 100} USDT
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">杠杆倍数:</span>
                          <span className="font-medium">
                            {testModeStatus?.leverage || 10}x
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">当前余额:</span>
                          <span className="font-medium">
                            {simulatedBalance?.total.toFixed(2) || "0.00"} USDT
                          </span>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full mt-4"
                        onClick={handleResetTestMode}
                        disabled={resetTestModeMutation.isPending}
                      >
                        重置测试状态
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
