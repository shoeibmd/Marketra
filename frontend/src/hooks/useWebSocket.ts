import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useMarketStore } from '../store/useMarketStore';

const RAW_WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
// Strip trailing /ws if provided in VITE_WS_BASE_URL to avoid /ws/ws URL duplication
const WS_BASE_URL = RAW_WS_BASE_URL.replace(/\/ws\/?$/, '');

export function useWebSocket() {
  const token = useAuthStore((state) => state.token);
  const updateQuote = useMarketStore((state) => state.updateQuote);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!token) {
      setIsConnected(false);
      return;
    }

    let reconnectAttempts = 0;

    function connect() {
      const wsUrl = `${WS_BASE_URL}/ws?token=${encodeURIComponent(token)}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttempts = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.data && message.data.last_price !== undefined) {
            updateQuote(message.data);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential backoff reconnect
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
        reconnectAttempts += 1;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      };

      ws.onerror = (err) => {
        console.error('WebSocket connection error:', err);
        ws.close();
      };
    }

    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [token, updateQuote]);

  const subscribe = (channel: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', channel }));
    }
  };

  const unsubscribe = (channel: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'unsubscribe', channel }));
    }
  };

  return { isConnected, subscribe, unsubscribe };
}
