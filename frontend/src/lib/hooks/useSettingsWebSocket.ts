/**
 * Settings WebSocket Hook
 * Real-time settings updates, system status, and notifications
 */

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp: string;
}

interface SettingUpdate {
  key: string;
  old_value: any;
  new_value: any;
  timestamp: string;
}

interface SystemStatus {
  status: 'healthy' | 'warning' | 'error';
  worker_id: string;
  uptime: number;
  hardware_type: string;
  active_cameras: number;
  active_models: number;
}

interface Notification {
  notification_type: string;
  message: string;
  level: 'info' | 'warning' | 'error';
  timestamp: string;
}

interface PerformanceMetrics {
  [key: string]: any;
}

interface UseSettingsWebSocketOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onSettingUpdate?: (update: SettingUpdate) => void;
  onSystemStatus?: (status: SystemStatus) => void;
  onNotification?: (notification: Notification) => void;
  onPerformanceMetrics?: (metrics: PerformanceMetrics) => void;
}

export function useSettingsWebSocket(options: UseSettingsWebSocketOptions = {}) {
  const {
    autoConnect = true,
    reconnectInterval = 2000,
    maxReconnectAttempts = 5,
    onSettingUpdate,
    onSystemStatus,
    onNotification,
    onPerformanceMetrics,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const wsUrl =
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws/settings';

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastUpdate(new Date());

        switch (message.type) {
          case 'connection_established':
            console.log('Settings WebSocket connected:', message.data);
            setIsConnected(true);
            reconnectAttemptsRef.current = 0;
            break;

          case 'setting_update':
            if (onSettingUpdate && message.data) {
              onSettingUpdate(message.data as SettingUpdate);
            }
            break;

          case 'system_status':
            if (message.data) {
              setSystemStatus(message.data as SystemStatus);
              if (onSystemStatus) {
                onSystemStatus(message.data as SystemStatus);
              }
            }
            break;

          case 'notification':
            if (onNotification && message.data) {
              onNotification(message.data as Notification);
            }
            break;

          case 'performance_metrics':
            if (onPerformanceMetrics && message.data) {
              onPerformanceMetrics(message.data as PerformanceMetrics);
            }
            break;

          case 'heartbeat':
            // Heartbeat received, connection is alive
            break;

          case 'pong':
            // Pong received in response to ping
            break;

          case 'error':
            console.error('WebSocket error from server:', message.data);
            break;

          default:
            console.warn('Unknown message type:', message.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    },
    [onSettingUpdate, onSystemStatus, onNotification, onPerformanceMetrics]
  );

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('Settings WebSocket connection opened');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error('Settings WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('Settings WebSocket connection closed');
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect
        if (
          autoConnect &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectAttemptsRef.current++;
          const delay = reconnectInterval * reconnectAttemptsRef.current;

          console.log(
            `Attempting to reconnect in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setIsConnected(false);
    }
  }, [wsUrl, autoConnect, reconnectInterval, maxReconnectAttempts, handleMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const ping = useCallback(() => {
    sendMessage({ type: 'ping' });
  }, [sendMessage]);

  const requestSystemStatus = useCallback(() => {
    sendMessage({ type: 'get_status' });
  }, [sendMessage]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    systemStatus,
    lastUpdate,
    connect,
    disconnect,
    sendMessage,
    ping,
    requestSystemStatus,
  };
}
