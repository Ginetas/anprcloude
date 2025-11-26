/**
 * System Overview Component
 * Displays real-time system status, health, and key metrics
 */

'use client';

import { useEffect, useState } from 'react';
import { Server, Cpu, Camera, Eye, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { useSettingsWebSocket } from '@/lib/hooks/useSettingsWebSocket';

interface SystemStatus {
  status: 'healthy' | 'warning' | 'error';
  worker_id: string;
  uptime: number;
  hardware_type: string;
  active_cameras: number;
  active_models: number;
  last_updated: string;
}

export default function SystemOverview() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    status: 'healthy',
    worker_id: 'worker-001',
    uptime: 0,
    hardware_type: 'GPU',
    active_cameras: 0,
    active_models: 0,
    last_updated: new Date().toISOString(),
  });

  // Connect to WebSocket for real-time updates
  const { isConnected, systemStatus: wsSystemStatus, lastUpdate } = useSettingsWebSocket({
    autoConnect: true,
    onSystemStatus: (status) => {
      setSystemStatus({
        ...status,
        last_updated: new Date().toISOString(),
      });
    },
    onNotification: (notification) => {
      // TODO: Show toast notification
      console.log('Notification:', notification);
    },
  });

  // Update uptime every second
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus((prev) => ({
        ...prev,
        uptime: prev.uptime + 1,
        last_updated: new Date().toISOString(),
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else {
      return `${minutes}m ${secs}s`;
    }
  };

  const getStatusIcon = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
    }
  };

  const getStatusColor = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
    }
  };

  const getStatusText = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return 'All Systems Operational';
      case 'warning':
        return 'System Warning';
      case 'error':
        return 'System Error';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">System Overview</h2>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Status Banner */}
        <div
          className={`flex items-center gap-4 p-4 rounded-lg border ${getStatusColor()}`}
        >
          {getStatusIcon()}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {getStatusText()}
            </h3>
            <p className="text-sm text-gray-600">
              Worker ID: {systemStatus.worker_id} • Uptime:{' '}
              {formatUptime(systemStatus.uptime)}
            </p>
          </div>
          <div className="text-sm text-gray-500">
            <div className={`w-2 h-2 ${isConnected ? 'bg-green-500' : 'bg-gray-400'} rounded-full ${isConnected ? 'animate-pulse' : ''} inline-block mr-2`} />
            {isConnected ? 'Live' : 'Disconnected'}
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          {/* Hardware Type */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Cpu className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Hardware</p>
                <p className="text-xl font-semibold text-gray-900">
                  {systemStatus.hardware_type}
                </p>
              </div>
            </div>
          </div>

          {/* Active Cameras */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Camera className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Active Cameras</p>
                <p className="text-xl font-semibold text-gray-900">
                  {systemStatus.active_cameras}
                </p>
              </div>
            </div>
          </div>

          {/* Active Models */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Eye className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Active Models</p>
                <p className="text-xl font-semibold text-gray-900">
                  {systemStatus.active_models}
                </p>
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Server className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-xl font-semibold text-gray-900 capitalize">
                  {systemStatus.status}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 flex gap-3">
          <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
            Run Diagnostics
          </button>
          <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            View Logs
          </button>
          <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            Restart System
          </button>
        </div>
      </div>
    </div>
  );
}
