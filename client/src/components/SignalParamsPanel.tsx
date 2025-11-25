import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Loader2, RefreshCw, Save } from "lucide-react";

export default function SignalParamsPanel() {
  const { data: currentParams, isLoading, refetch } = trpc.signalParams.getParams.useQuery();
  const updateMutation = trpc.signalParams.updateParams.useMutation();
  const resetMutation = trpc.signalParams.resetParams.useMutation();

  const [shortMa, setShortMa] = useState(5);
  const [longMa, setLongMa] = useState(20);
  const [timeframe, setTimeframe] = useState<"15m" | "30m" | "1h" | "2h" | "4h">("1h");

  useEffect(() => {
    if (currentParams) {
      setShortMa(currentParams.shortMaPeriod);
      setLongMa(currentParams.longMaPeriod);
      setTimeframe(currentParams.timeframe as any);
    }
  }, [currentParams]);

  const handleSave = async () => {
    if (shortMa >= longMa) {
      toast.error("Short MA must be less than Long MA");
      return;
    }

    try {
      await updateMutation.mutateAsync({
        shortMaPeriod: shortMa,
        longMaPeriod: longMa,
        timeframe,
      });
      toast.success("Signal parameters updated successfully!");
      refetch();
    } catch (error) {
      toast.error("Failed to update parameters");
      console.error(error);
    }
  };

  const handleReset = async () => {
    try {
      await resetMutation.mutateAsync();
      toast.success("Parameters reset to default");
      refetch();
    } catch (error) {
      toast.error("Failed to reset parameters");
      console.error(error);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Signal Parameters</CardTitle>
          <CardDescription>Adjust MA5/MA20 trading signal parameters</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Signal Parameters</CardTitle>
        <CardDescription>
          Adjust MA5/MA20 trading signal parameters. Changes will take effect on next trading cycle.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="shortMa">Short MA Period</Label>
            <Input
              id="shortMa"
              type="number"
              min={3}
              max={20}
              value={shortMa}
              onChange={(e) => setShortMa(parseInt(e.target.value) || 5)}
            />
            <p className="text-xs text-muted-foreground">Range: 3-20</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="longMa">Long MA Period</Label>
            <Input
              id="longMa"
              type="number"
              min={10}
              max={60}
              value={longMa}
              onChange={(e) => setLongMa(parseInt(e.target.value) || 20)}
            />
            <p className="text-xs text-muted-foreground">Range: 10-60</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="timeframe">Timeframe</Label>
            <Select value={timeframe} onValueChange={(v: any) => setTimeframe(v)}>
              <SelectTrigger id="timeframe">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="15m">15 minutes</SelectItem>
                <SelectItem value="30m">30 minutes</SelectItem>
                <SelectItem value="1h">1 hour</SelectItem>
                <SelectItem value="2h">2 hours</SelectItem>
                <SelectItem value="4h">4 hours</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">K-line period</p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="flex-1"
          >
            {updateMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </>
            )}
          </Button>

          <Button
            variant="outline"
            onClick={handleReset}
            disabled={resetMutation.isPending}
          >
            {resetMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Resetting...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Reset to Default
              </>
            )}
          </Button>
        </div>

        {currentParams && (
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm font-medium mb-2">Current Active Parameters:</p>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">Short MA:</span>{" "}
                <span className="font-medium">{currentParams.shortMaPeriod}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Long MA:</span>{" "}
                <span className="font-medium">{currentParams.longMaPeriod}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Timeframe:</span>{" "}
                <span className="font-medium">{currentParams.timeframe}</span>
              </div>
            </div>
            {currentParams.appliedAt && (
              <p className="text-xs text-muted-foreground mt-2">
                Last updated: {new Date(currentParams.appliedAt).toLocaleString()}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
