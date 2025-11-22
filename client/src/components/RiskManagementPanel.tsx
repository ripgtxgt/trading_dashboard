import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { trpc } from "@/lib/trpc";
import { AlertTriangle, CheckCircle, Pause, Play, RotateCcw } from "lucide-react";
import { toast } from "sonner";
import { useState } from "react";

export function RiskManagementPanel() {
  const { data: riskStatus, refetch: refetchStatus } = trpc.risk.getStatus.useQuery(undefined, {
    refetchInterval: 5000, // 每5秒刷新
  });
  
  const { data: riskConfig } = trpc.risk.getConfig.useQuery();
  
  const resumeMutation = trpc.risk.resume.useMutation({
    onSuccess: () => {
      toast.success("交易已恢复");
      refetchStatus();
    },
    onError: (error) => {
      toast.error(`恢复失败: ${error.message}`);
    },
  });
  
  const pauseMutation = trpc.risk.pause.useMutation({
    onSuccess: () => {
      toast.success("交易已暂停");
      refetchStatus();
    },
    onError: (error) => {
      toast.error(`暂停失败: ${error.message}`);
    },
  });
  
  const resetDailyMutation = trpc.risk.resetDaily.useMutation({
    onSuccess: () => {
      toast.success("每日统计已重置");
      refetchStatus();
    },
    onError: (error) => {
      toast.error(`重置失败: ${error.message}`);
    },
  });
  
  const [pauseHours, setPauseHours] = useState(1);
  
  const handleResume = () => {
    resumeMutation.mutate();
  };
  
  const handlePause = () => {
    pauseMutation.mutate({
      reason: "手动暂停",
      hours: pauseHours,
    });
  };
  
  const handleResetDaily = () => {
    if (confirm("确定要重置每日统计吗？")) {
      resetDailyMutation.mutate();
    }
  };
  
  if (!riskStatus || !riskConfig) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>风险管理</CardTitle>
          <CardDescription>加载中...</CardDescription>
        </CardHeader>
      </Card>
    );
  }
  
  const isAllowed = riskStatus.is_trading_allowed;
  const drawdownPct = (riskStatus.current_drawdown_pct * 100).toFixed(2);
  const volatilityPct = (riskStatus.volatility * 100).toFixed(2);
  
  return (
    <div className="space-y-4">
      {/* 状态概览 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>风险管理状态</CardTitle>
              <CardDescription>实时监控交易风险</CardDescription>
            </div>
            <Badge variant={isAllowed ? "default" : "destructive"} className="text-lg px-4 py-2">
              {isAllowed ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  正常运行
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  已暂停
                </>
              )}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {!isAllowed && (
            <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-destructive mt-0.5" />
                <div>
                  <p className="font-semibold text-destructive">交易已暂停</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    原因: {riskStatus.pause_reason}
                  </p>
                  {riskStatus.pause_until && (
                    <p className="text-sm text-muted-foreground">
                      恢复时间: {new Date(riskStatus.pause_until).toLocaleString("zh-CN")}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">今日盈亏</p>
              <p className={`text-2xl font-bold ${riskStatus.daily_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {riskStatus.daily_pnl >= 0 ? '+' : ''}{riskStatus.daily_pnl.toFixed(2)} USDT
              </p>
            </div>
            
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">累计盈亏</p>
              <p className={`text-2xl font-bold ${riskStatus.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {riskStatus.total_pnl >= 0 ? '+' : ''}{riskStatus.total_pnl.toFixed(2)} USDT
              </p>
            </div>
            
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">当前回撤</p>
              <p className={`text-2xl font-bold ${parseFloat(drawdownPct) > riskConfig.max_drawdown_pct * 100 ? 'text-red-600' : 'text-foreground'}`}>
                {drawdownPct}%
              </p>
            </div>
            
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">连续亏损</p>
              <p className={`text-2xl font-bold ${riskStatus.consecutive_losses >= riskConfig.max_consecutive_losses ? 'text-red-600' : 'text-foreground'}`}>
                {riskStatus.consecutive_losses} 笔
              </p>
            </div>
          </div>
          
          <div className="flex gap-2">
            {isAllowed ? (
              <Button 
                onClick={handlePause} 
                variant="destructive"
                disabled={pauseMutation.isPending}
              >
                <Pause className="w-4 h-4 mr-2" />
                暂停交易
              </Button>
            ) : (
              <Button 
                onClick={handleResume}
                disabled={resumeMutation.isPending}
              >
                <Play className="w-4 h-4 mr-2" />
                恢复交易
              </Button>
            )}
            
            <Button 
              onClick={handleResetDaily} 
              variant="outline"
              disabled={resetDailyMutation.isPending}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              重置每日统计
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* 风险指标 */}
      <Card>
        <CardHeader>
          <CardTitle>风险指标</CardTitle>
          <CardDescription>当前市场风险状况</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>市场波动率</Label>
              <span className="text-sm font-medium">{volatilityPct}%</span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${parseFloat(volatilityPct) > riskConfig.max_volatility * 100 ? 'bg-red-600' : 'bg-blue-600'}`}
                style={{ width: `${Math.min(parseFloat(volatilityPct) / (riskConfig.max_volatility * 100) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              阈值: {(riskConfig.max_volatility * 100).toFixed(2)}%
            </p>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>最大回撤</Label>
              <span className="text-sm font-medium">{drawdownPct}%</span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${parseFloat(drawdownPct) > riskConfig.max_drawdown_pct * 100 ? 'bg-red-600' : 'bg-green-600'}`}
                style={{ width: `${Math.min(parseFloat(drawdownPct) / (riskConfig.max_drawdown_pct * 100) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              阈值: {(riskConfig.max_drawdown_pct * 100).toFixed(0)}%
            </p>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>今日亏损比例</Label>
              <span className="text-sm font-medium">
                {riskStatus.daily_pnl < 0 ? Math.abs(riskStatus.daily_pnl / 100 * 100).toFixed(2) : 0}%
              </span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-orange-600 transition-all"
                style={{ width: `${Math.min(Math.abs(riskStatus.daily_pnl) / (riskConfig.max_daily_loss_pct * 100) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              阈值: {(riskConfig.max_daily_loss_pct * 100).toFixed(0)}%
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* 风险事件 */}
      {riskStatus.recent_events && riskStatus.recent_events.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>最近风险事件</CardTitle>
            <CardDescription>最近10条风险事件记录</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {riskStatus.recent_events.slice().reverse().map((event: any, index: number) => (
                <div key={index} className="flex items-start gap-2 p-2 rounded-lg bg-secondary/50">
                  <AlertTriangle className="w-4 h-4 text-orange-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{event.description}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleString("zh-CN")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
