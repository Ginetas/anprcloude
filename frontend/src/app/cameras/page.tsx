'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Camera, CameraCreate, Zone } from '@/lib/types';

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [camerasData, zonesData] = await Promise.all([
        api.getCameras(),
        api.getZones(),
      ]);
      setCameras(camerasData);
      setZones(zonesData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this camera?')) return;

    try {
      await api.deleteCamera(id);
      setCameras(cameras.filter((c) => c.id !== id));
    } catch (error) {
      console.error('Failed to delete camera:', error);
      alert('Failed to delete camera');
    }
  };

  const handleToggleEnabled = async (camera: Camera) => {
    try {
      const updated = await api.updateCamera(camera.id, {
        enabled: !camera.enabled,
      });
      setCameras(cameras.map((c) => (c.id === camera.id ? updated : c)));
    } catch (error) {
      console.error('Failed to update camera:', error);
      alert('Failed to update camera');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Camera Management</h1>
          <p className="text-gray-600 mt-1">
            Configure and monitor RTSP camera streams
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Add Camera
        </button>
      </div>

      {/* Cameras Grid */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading cameras...</p>
        </div>
      ) : cameras.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 mb-4">No cameras configured yet.</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add Your First Camera
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera) => (
            <div
              key={camera.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {camera.name}
                  </h3>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      camera.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {camera.enabled ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="space-y-2 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Location:</span>{' '}
                    {camera.location || 'Not set'}
                  </div>
                  <div>
                    <span className="font-medium">Resolution:</span>{' '}
                    {camera.resolution_width}x{camera.resolution_height}
                  </div>
                  <div>
                    <span className="font-medium">FPS:</span> {camera.fps}
                  </div>
                  <div className="truncate">
                    <span className="font-medium">RTSP:</span>{' '}
                    <span className="font-mono text-xs">{camera.rtsp_url}</span>
                  </div>
                </div>

                <div className="mt-6 flex gap-2">
                  <button
                    onClick={() => handleToggleEnabled(camera)}
                    className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      camera.enabled
                        ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {camera.enabled ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    onClick={() => setEditingCamera(camera)}
                    className="flex-1 bg-blue-100 text-blue-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(camera.id)}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Modal Placeholder */}
      {(showAddModal || editingCamera) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {editingCamera ? 'Edit Camera' : 'Add Camera'}
            </h2>
            <p className="text-gray-600 mb-4">
              Form implementation would go here...
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setEditingCamera(null);
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Back to Dashboard */}
      <div className="mt-8">
        <a
          href="/"
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Dashboard
        </a>
      </div>
    </div>
  );
}
