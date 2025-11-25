import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, FileJson, Database } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";

export default function DataExportPanel() {
  const exportAllMutation = trpc.dataExport.exportAllData.useQuery(undefined, {
    enabled: false,
  });

  const exportBotStateMutation = trpc.dataExport.exportBotState.useQuery(undefined, {
    enabled: false,
  });

  const handleExportAll = async () => {
    try {
      const data = await exportAllMutation.refetch();
      if (data.data) {
        downloadJSON(data.data, `trading_data_export_${Date.now()}.json`);
        toast.success("Data exported successfully!");
      }
    } catch (error) {
      toast.error("Failed to export data: " + (error as Error).message);
    }
  };

  const handleExportBotState = async () => {
    try {
      const data = await exportBotStateMutation.refetch();
      if (data.data) {
        downloadJSON(data.data, `bot_state_export_${Date.now()}.json`);
        toast.success("Bot state exported successfully!");
      }
    } catch (error) {
      toast.error("Failed to export bot state: " + (error as Error).message);
    }
  };

  const downloadJSON = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Data Export
        </CardTitle>
        <CardDescription>
          Export trading data for analysis and debugging
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-3">
          <Button
            onClick={handleExportAll}
            disabled={exportAllMutation.isFetching}
            className="w-full justify-start"
          >
            <FileJson className="h-4 w-4 mr-2" />
            {exportAllMutation.isFetching ? "Exporting..." : "Export All Data (JSON)"}
          </Button>
          
          <Button
            onClick={handleExportBotState}
            disabled={exportBotStateMutation.isFetching}
            variant="outline"
            className="w-full justify-start"
          >
            <Download className="h-4 w-4 mr-2" />
            {exportBotStateMutation.isFetching ? "Exporting..." : "Export Bot State Only"}
          </Button>
        </div>

        <div className="text-sm text-gray-500 space-y-1">
          <p>• <strong>All Data</strong>: Includes bot state, positions, trades, balance snapshots, and strategy config</p>
          <p>• <strong>Bot State Only</strong>: Current bot status and capital information</p>
        </div>
      </CardContent>
    </Card>
  );
}
