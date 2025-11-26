'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { api } from '@/lib/api';
import type { PlateEvent, Camera } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';

export default function Dashboard() {
  const { isConnected, events, latestEvent } = useWebSocket();
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalToday: 0,
    totalWeek: 0,
    activeCameras: 0,
  });

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      const data = await api.getCameras();
      setCameras(data);
      setStats((prev) => ({ ...prev, activeCameras: data.filter((c) => c.enabled).length }));
    } catch (error) {
      console.error('Failed to load cameras:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCameraName = (cameraId: number) => {
    const camera = cameras.find((c) => c.id === cameraId);
    return camera?.name || `Camera ${cameraId}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">ANPR Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Real-time license plate recognition system
        </p>
      </header>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Status</p>
              <div className="mt-2 flex items-center">
                <span
                  className={`inline-flex h-3 w-3 rounded-full mr-2 ${
                    isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                  }`}
                />
                <span className="text-lg font-semibold text-gray-900">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Active Cameras</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {stats.activeCameras}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Detections Today</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {events.length}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Last Detection</p>
          <p className="mt-2 text-lg font-semibold text-gray-900">
            {latestEvent
              ? formatDistanceToNow(new Date(latestEvent.timestamp), {
                  addSuffix: true,
                })
              : 'None'}
          </p>
        </div>
      </div>

      {/* Latest Detections */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Live Plate Detections
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plate Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Camera
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {events.length === 0 ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-12 text-center text-gray-500"
                  >
                    {isConnected
                      ? 'Waiting for plate detections...'
                      : 'Connecting to server...'}
                  </td>
                </tr>
              ) : (
                events.map((event, index) => (
                  <tr
                    key={`${event.id}-${index}`}
                    className={
                      index === 0 ? 'bg-green-50 animate-pulse' : undefined
                    }
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-lg font-mono font-semibold text-gray-900">
                        {event.plate_text}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {getCameraName(event.camera_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          event.confidence >= 0.8
                            ? 'bg-green-100 text-green-800'
                            : event.confidence >= 0.6
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {(event.confidence * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDistanceToNow(new Date(event.timestamp), {
                        addSuffix: true,
                      })}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <a
          href="/cameras"
          className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Manage Cameras
          </h3>
          <p className="text-sm text-gray-600">
            Configure and monitor camera streams
          </p>
        </a>

        <a
          href="/zones"
          className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Zones & Models
          </h3>
          <p className="text-sm text-gray-600">
            Configure detection zones and AI models
          </p>
        </a>

        <a
          href="/exporters"
          className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Integrations
          </h3>
          <p className="text-sm text-gray-600">
            Setup webhooks and external integrations
          </p>
        </a>
      </div>
    </div>
  );
}
