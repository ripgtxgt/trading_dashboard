import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useWebSocket, WebSocketMessage } from '@/hooks/useWebSocket';

interface AccountStatus {
  balance: number;
  available: number;
  used: number;
  currency: string;
  mode?: string;
}

interface Position {
  position_id: string;
  symbol: string;
  side: string;
  size: number;
  entry_price: number;
  margin: number;
  leverage: number;
  unrealized_pnl: number;
  timestamp: string;
}

interface KlineData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface RiskStatus {
  is_trading_allowed: boolean;
  pause_reason: string | null;
  pause_until: string | null;
  daily_pnl: number;
  total_pnl: number;
  current_drawdown_pct: number;
  consecutive_losses: number;
  volatility: number;
  recent_events: any[];
}

interface TradeSignal {
  signal: string;
  price: number;
  timestamp: string;
  reason?: string;
}

interface RealtimeDataContextType {
  isConnected: boolean;
  accountStatus: AccountStatus | null;
  positions: Position[];
  latestKline: KlineData | null;
  riskStatus: RiskStatus | null;
  tradeSignal: TradeSignal | null;
  reconnect: () => void;
}

const RealtimeDataContext = createContext<RealtimeDataContextType | undefined>(undefined);

export function RealtimeDataProvider({ children }: { children: ReactNode }) {
  const [accountStatus, setAccountStatus] = useState<AccountStatus | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [latestKline, setLatestKline] = useState<KlineData | null>(null);
  const [riskStatus, setRiskStatus] = useState<RiskStatus | null>(null);
  const [tradeSignal, setTradeSignal] = useState<TradeSignal | null>(null);

  // WebSocket连接（使用环境变量或默认地址）
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';

  const handleMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'account_status':
        setAccountStatus(message.data);
        break;
      case 'positions':
        setPositions(message.data || []);
        break;
      case 'kline':
        setLatestKline(message.data);
        break;
      case 'risk_status':
        setRiskStatus(message.data);
        break;
      case 'trade_signal':
        setTradeSignal(message.data);
        break;
      case 'welcome':
        console.log('收到欢迎消息:', message.data?.message || 'WebSocket连接成功');
        break;
      default:
        console.log('未知消息类型:', message.type);
    }
  };

  const { isConnected, reconnect } = useWebSocket({
    url: wsUrl,
    reconnect: true,
    reconnectInterval: 3000,
    onMessage: handleMessage,
    onConnect: () => {
      console.log('✅ 实时数据连接已建立');
    },
    onDisconnect: () => {
      console.log('❌ 实时数据连接已断开');
    },
    onError: (error) => {
      console.error('实时数据连接错误:', error);
    },
  });

  return (
    <RealtimeDataContext.Provider
      value={{
        isConnected,
        accountStatus,
        positions,
        latestKline,
        riskStatus,
        tradeSignal,
        reconnect,
      }}
    >
      {children}
    </RealtimeDataContext.Provider>
  );
}

export function useRealtimeData() {
  const context = useContext(RealtimeDataContext);
  if (context === undefined) {
    throw new Error('useRealtimeData must be used within a RealtimeDataProvider');
  }
  return context;
}
