'use client';

import { useEffect } from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { wsClient } from '@/lib/websocket';
import { cn } from '@/lib/utils';
import { formatPercentage } from '@/lib/utils';

export function Header() {
  const { systemStatus, setSystemStatus } = useStore();

  useEffect(() => {
    // Fetch system status on mount
    const fetchStatus = async () => {
      try {
        const status = await api.getSystemStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    fetchStatus();

    // Poll system status every 10 seconds
    const interval = setInterval(fetchStatus, 10000);

    return () => clearInterval(interval);
  }, [setSystemStatus]);

  const isHealthy = systemStatus?.status === 'healthy';
  const isDegraded = systemStatus?.status === 'degraded';

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-6">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">ANPR System</h1>
        </div>

        <div className="flex items-center space-x-6">
          {/* System Status */}
          <div className="flex items-center space-x-2">
            <Activity
              className={cn(
                'h-5 w-5',
                isHealthy && 'text-green-600',
                isDegraded && 'text-yellow-600',
                !isHealthy && !isDegraded && 'text-red-600'
              )}
            />
            <div className="text-sm">
              <div className="font-medium text-gray-900">
                {systemStatus?.status || 'Unknown'}
              </div>
              <div className="text-gray-500">
                {systemStatus?.version || 'v0.0.0'}
              </div>
            </div>
          </div>

          {/* Camera Status */}
          <div className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-md">
            {wsClient.isConnected() ? (
              <Wifi className="h-4 w-4 text-green-600" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-600" />
            )}
            <div className="text-sm">
              <div className="font-medium text-gray-900">
                {systemStatus?.cameras.online || 0} / {systemStatus?.cameras.total || 0}
              </div>
              <div className="text-gray-500 text-xs">Cameras Online</div>
            </div>
          </div>

          {/* Resource Usage */}
          {systemStatus && (
            <div className="flex items-center space-x-4 text-sm">
              <div>
                <div className="text-gray-500 text-xs">CPU</div>
                <div className="font-medium text-gray-900">
                  {formatPercentage(systemStatus.cpu_usage)}
                </div>
              </div>
              <div>
                <div className="text-gray-500 text-xs">Memory</div>
                <div className="font-medium text-gray-900">
                  {formatPercentage(systemStatus.memory_usage)}
                </div>
              </div>
              <div>
                <div className="text-gray-500 text-xs">Disk</div>
                <div className="font-medium text-gray-900">
                  {formatPercentage(systemStatus.disk_usage)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
