import { Wifi, WifiOff } from 'lucide-react';
import { useRealtimeData } from '@/contexts/RealtimeDataContext';
import { Button } from '@/components/ui/button';

export function ConnectionStatus() {
  const { isConnected, reconnect } = useRealtimeData();

  return (
    <div className="flex items-center gap-2">
      {isConnected ? (
        <div className="flex items-center gap-2 text-green-600">
          <Wifi className="h-4 w-4 animate-pulse" />
          <span className="text-sm font-medium">实时连接</span>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-red-600">
            <WifiOff className="h-4 w-4" />
            <span className="text-sm font-medium">连接断开</span>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={reconnect}
            className="h-7 text-xs"
          >
            重新连接
          </Button>
        </div>
      )}
    </div>
  );
}
