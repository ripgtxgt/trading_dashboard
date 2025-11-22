import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, TrendingUp, TrendingDown, Minus, PauseCircle, PlayCircle } from "lucide-react";

interface RiskMonitorCardProps {
  volatility: number | null;
  riskLevel: 'low' | 'medium' | 'high' | 'extreme' | 'unknown';
  positionMultiplier: number;
  isPaused: boolean;
  trend?: 'increasing' | 'decreasing' | 'stable' | null;
}

export default function RiskMonitorCard({
  volatility,
  riskLevel,
  positionMultiplier,
  isPaused,
  trend
}: RiskMonitorCardProps) {
  
  // 风险等级配置
  const riskConfig = {
    low: { label: '低风险', color: 'bg-green-500', textColor: 'text-green-700', bgColor: 'bg-green-50' },
    medium: { label: '中等风险', color: 'bg-yellow-500', textColor: 'text-yellow-700', bgColor: 'bg-yellow-50' },
    high: { label: '高风险', color: 'bg-orange-500', textColor: 'text-orange-700', bgColor: 'bg-orange-50' },
    extreme: { label: '极高风险', color: 'bg-red-500', textColor: 'text-red-700', bgColor: 'bg-red-50' },
    unknown: { label: '未知', color: 'bg-gray-500', textColor: 'text-gray-700', bgColor: 'bg-gray-50' }
  };

  const config = riskConfig[riskLevel];

  // 趋势图标
  const TrendIcon = trend === 'increasing' ? TrendingUp : 
                    trend === 'decreasing' ? TrendingDown : Minus;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            风险监控
          </span>
          {isPaused && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <PauseCircle className="h-3 w-3" />
              交易已暂停
            </Badge>
          )}
          {!isPaused && (
            <Badge variant="outline" className="flex items-center gap-1 text-green-600 border-green-600">
              <PlayCircle className="h-3 w-3" />
              正常运行
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 风险等级 */}
        <div className={`p-4 rounded-lg ${config.bgColor}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">风险等级</span>
            <div className={`w-3 h-3 rounded-full ${config.color}`} />
          </div>
          <div className={`text-2xl font-bold ${config.textColor}`}>
            {config.label}
          </div>
        </div>

        {/* 波动率 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">市场波动率</div>
            <div className="text-xl font-bold">
              {volatility !== null ? `${(volatility * 100).toFixed(2)}%` : 'N/A'}
            </div>
            {trend && (
              <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                <TrendIcon className="h-3 w-3" />
                {trend === 'increasing' && '上升'}
                {trend === 'decreasing' && '下降'}
                {trend === 'stable' && '稳定'}
              </div>
            )}
          </div>

          {/* 仓位建议 */}
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">建议仓位</div>
            <div className="text-xl font-bold">
              {(positionMultiplier * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              基础仓位的 {(positionMultiplier * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        {/* 风险提示 */}
        {riskLevel === 'extreme' && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5" />
              <div className="text-sm text-red-700">
                <div className="font-medium">市场剧烈波动</div>
                <div className="text-xs mt-1">
                  建议暂停交易，等待市场稳定后再操作
                </div>
              </div>
            </div>
          </div>
        )}

        {riskLevel === 'high' && (
          <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5" />
              <div className="text-sm text-orange-700">
                <div className="font-medium">波动较大</div>
                <div className="text-xs mt-1">
                  建议降低仓位，谨慎交易
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
