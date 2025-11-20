import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, Play, Square, AlertTriangle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface ControlPanelProps {
  isRunning: boolean;
  emergencyStopped: boolean;
}

export function ControlPanel({ isRunning, emergencyStopped }: ControlPanelProps) {
  const [showStopDialog, setShowStopDialog] = useState(false);
  const [showEmergencyDialog, setShowEmergencyDialog] = useState(false);

  const handleStart = () => {
    // TODO: 实现启动功能
    console.log("Starting bot...");
  };

  const handleStop = () => {
    // TODO: 实现停止功能
    console.log("Stopping bot...");
    setShowStopDialog(false);
  };

  const handleEmergencyStop = () => {
    // TODO: 实现紧急停止功能
    console.log("Emergency stop!");
    setShowEmergencyDialog(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>控制面板</CardTitle>
        <CardDescription>启动、停止和紧急控制</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {emergencyStopped && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              机器人已触发紧急停止！请检查日志并重新配置后再启动。
            </AlertDescription>
          </Alert>
        )}

        <div className="flex gap-3">
          {!isRunning ? (
            <Button
              onClick={handleStart}
              className="flex-1"
              size="lg"
              disabled={emergencyStopped}
            >
              <Play className="mr-2 h-4 w-4" />
              启动机器人
            </Button>
          ) : (
            <Button
              onClick={() => setShowStopDialog(true)}
              variant="secondary"
              className="flex-1"
              size="lg"
            >
              <Square className="mr-2 h-4 w-4" />
              停止机器人
            </Button>
          )}

          <Button
            onClick={() => setShowEmergencyDialog(true)}
            variant="destructive"
            size="lg"
            disabled={!isRunning}
          >
            <AlertTriangle className="mr-2 h-4 w-4" />
            紧急停止
          </Button>
        </div>

        <div className="text-sm text-muted-foreground space-y-1">
          <p>• 启动：开始自动交易</p>
          <p>• 停止：安全退出，平掉所有持仓</p>
          <p>• 紧急停止：立即市价平仓并停止</p>
        </div>

        {/* Stop Confirmation Dialog */}
        <AlertDialog open={showStopDialog} onOpenChange={setShowStopDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>确认停止机器人？</AlertDialogTitle>
              <AlertDialogDescription>
                停止后，机器人将自动平掉所有持仓并取消所有挂单。您可以随时重新启动。
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>取消</AlertDialogCancel>
              <AlertDialogAction onClick={handleStop}>确认停止</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Emergency Stop Dialog */}
        <AlertDialog open={showEmergencyDialog} onOpenChange={setShowEmergencyDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="text-destructive">
                ⚠️ 紧急停止确认
              </AlertDialogTitle>
              <AlertDialogDescription>
                这将<strong>立即市价平掉所有持仓</strong>并停止机器人。
                此操作不可撤销，可能会造成滑点损失。
                <br /><br />
                请确认您真的需要紧急停止！
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>取消</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleEmergencyStop}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                确认紧急停止
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </CardContent>
    </Card>
  );
}
