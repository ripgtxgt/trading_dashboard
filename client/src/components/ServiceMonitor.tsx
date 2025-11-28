import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { trpc } from "@/lib/trpc";
import { RefreshCw, Play, Square, RotateCw, AlertCircle, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { useState } from "react";

interface PM2Process {
  name: string;
  pm_id: number;
  status: string;
  cpu: number;
  memory: number;
  uptime: number;
  restarts: number;
}

/**
 * Format memory size in bytes to human readable format
 */
function formatMemory(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
}

/**
 * Format uptime in milliseconds to human readable format
 */
function formatUptime(ms: number): string {
  if (ms === 0) return "0s";
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
}

/**
 * Get status badge variant based on process status
 */
function getStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "online":
      return "default";
    case "stopped":
      return "secondary";
    case "errored":
      return "destructive";
    default:
      return "outline";
  }
}

/**
 * Process row component
 */
function ProcessRow({ process }: { process: PM2Process }) {
  const utils = trpc.useUtils();
  const [isRestarting, setIsRestarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  const restartMutation = trpc.systemMonitor.restartProcess.useMutation({
    onMutate: () => setIsRestarting(true),
    onSuccess: (data) => {
      toast.success(data.message);
      utils.systemMonitor.getProcesses.invalidate();
    },
    onError: (error) => {
      toast.error(`Failed to restart: ${error.message}`);
    },
    onSettled: () => setIsRestarting(false),
  });

  const stopMutation = trpc.systemMonitor.stopProcess.useMutation({
    onMutate: () => setIsStopping(true),
    onSuccess: (data) => {
      toast.success(data.message);
      utils.systemMonitor.getProcesses.invalidate();
    },
    onError: (error) => {
      toast.error(`Failed to stop: ${error.message}`);
    },
    onSettled: () => setIsStopping(false),
  });

  const startMutation = trpc.systemMonitor.startProcess.useMutation({
    onMutate: () => setIsStarting(true),
    onSuccess: (data) => {
      toast.success(data.message);
      utils.systemMonitor.getProcesses.invalidate();
    },
    onError: (error) => {
      toast.error(`Failed to start: ${error.message}`);
    },
    onSettled: () => setIsStarting(false),
  });

  const handleRestart = () => {
    restartMutation.mutate({ name: process.name });
  };

  const handleStop = () => {
    stopMutation.mutate({ name: process.name });
  };

  const handleStart = () => {
    startMutation.mutate({ name: process.name });
  };

  return (
    <div className="flex items-center justify-between p-4 border rounded-lg">
      <div className="flex-1 grid grid-cols-1 md:grid-cols-6 gap-4 items-center">
        {/* Name and Status */}
        <div className="md:col-span-2">
          <div className="font-medium">{process.name}</div>
          <Badge variant={getStatusVariant(process.status)} className="mt-1">
            {process.status}
          </Badge>
        </div>

        {/* CPU */}
        <div className="text-sm">
          <div className="text-muted-foreground">CPU</div>
          <div className="font-medium">{process.cpu.toFixed(1)}%</div>
        </div>

        {/* Memory */}
        <div className="text-sm">
          <div className="text-muted-foreground">Memory</div>
          <div className="font-medium">{formatMemory(process.memory)}</div>
        </div>

        {/* Uptime */}
        <div className="text-sm">
          <div className="text-muted-foreground">Uptime</div>
          <div className="font-medium">{formatUptime(Date.now() - process.uptime)}</div>
        </div>

        {/* Restarts */}
        <div className="text-sm">
          <div className="text-muted-foreground">Restarts</div>
          <div className="font-medium">{process.restarts}</div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 ml-4">
        {process.status === "online" ? (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRestart}
              disabled={isRestarting}
            >
              {isRestarting ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <RotateCw className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleStop}
              disabled={isStopping}
            >
              {isStopping ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Square className="h-4 w-4" />
              )}
            </Button>
          </>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={handleStart}
            disabled={isStarting}
          >
            {isStarting ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

/**
 * Service Monitor Component
 * Displays PM2 processes status and provides control actions
 */
export function ServiceMonitor() {
  const { data, isLoading, error, refetch } = trpc.systemMonitor.getProcesses.useQuery(
    undefined,
    {
      refetchInterval: 5000, // Auto refresh every 5 seconds
    }
  );

  const utils = trpc.useUtils();
  const [isRestartingAll, setIsRestartingAll] = useState(false);

  const restartAllMutation = trpc.systemMonitor.restartAll.useMutation({
    onMutate: () => setIsRestartingAll(true),
    onSuccess: (data) => {
      toast.success(data.message);
      utils.systemMonitor.getProcesses.invalidate();
    },
    onError: (error) => {
      toast.error(`Failed to restart all: ${error.message}`);
    },
    onSettled: () => setIsRestartingAll(false),
  });

  const handleRestartAll = () => {
    if (confirm("Are you sure you want to restart all services?")) {
      restartAllMutation.mutate();
    }
  };

  const handleRefresh = () => {
    refetch();
    toast.success("Refreshed service status");
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Service Monitor</CardTitle>
          <CardDescription>Loading service status...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Service Monitor</CardTitle>
          <CardDescription>Failed to load service status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 gap-4">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <p className="text-sm text-muted-foreground">{error.message}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Service Monitor
              {data.healthy ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-500" />
              )}
            </CardTitle>
            <CardDescription>
              {data.processes.length} services running
              {" • "}
              Last updated: {new Date(data.timestamp).toLocaleTimeString()}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button
              onClick={handleRestartAll}
              variant="outline"
              size="sm"
              disabled={isRestartingAll}
            >
              {isRestartingAll ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RotateCw className="h-4 w-4 mr-2" />
              )}
              Restart All
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.processes.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No services found
            </div>
          ) : (
            data.processes.map((process) => (
              <ProcessRow key={process.pm_id} process={process} />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
