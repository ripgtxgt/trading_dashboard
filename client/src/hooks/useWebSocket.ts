import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
}

export interface WebSocketOptions {
  url: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export interface WebSocketHook {
  isConnected: boolean;
  send: (data: any) => void;
  lastMessage: WebSocketMessage | null;
  reconnect: () => void;
}

export function useWebSocket(options: WebSocketOptions): WebSocketHook {
  const {
    url,
    reconnect = true,
    reconnectInterval = 3000,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(reconnect);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('WebSocket连接成功');
        setIsConnected(true);
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        onError?.(error);
      };

      ws.onclose = () => {
        console.log('WebSocket连接关闭');
        setIsConnected(false);
        onDisconnect?.();

        // 自动重连
        if (shouldReconnectRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('尝试重新连接WebSocket...');
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
    }
  }, [url, reconnectInterval, onConnect, onMessage, onDisconnect, onError]);

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket未连接，无法发送消息');
    }
  }, []);

  const manualReconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    isConnected,
    send,
    lastMessage,
    reconnect: manualReconnect,
  };
}
