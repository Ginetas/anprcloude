'use client';

import { useEffect } from 'react';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function SystemStatus() {
  const { systemStatus, setSystemStatus, setLoading, setError } = useStore();

  useEffect(() => {
    const fetchStatus = async () => {
      setLoading('systemStatus', true);
      try {
        const status = await api.getSystemStatus();
        setSystemStatus(status);
        setError('systemStatus', null);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
        setError('systemStatus', (error as Error).message);
      } finally {
        setLoading('systemStatus', false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, [setSystemStatus, setLoading, setError]);

  if (!systemStatus) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center text-gray-500">
            Loading system status...
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusIcon = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'down':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      case 'down':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const uptimeHours = Math.floor(systemStatus.uptime / 3600);
  const uptimeMinutes = Math.floor((systemStatus.uptime % 3600) / 60);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>System Status</span>
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span
              className={cn(
                'px-3 py-1 rounded-full text-sm font-medium',
                getStatusColor()
              )}
            >
              {systemStatus.status.toUpperCase()}
            </span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-500">Uptime</div>
            <div className="text-lg font-semibold">
              {uptimeHours}h {uptimeMinutes}m
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Cameras Online</div>
            <div className="text-lg font-semibold">
              {systemStatus.cameras.online} / {systemStatus.cameras.total}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Events (1h)</div>
            <div className="text-lg font-semibold">
              {systemStatus.events.last_hour.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Events (24h)</div>
            <div className="text-lg font-semibold">
              {systemStatus.events.last_24h.toLocaleString()}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
