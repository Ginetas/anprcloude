'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Exporter } from '@/lib/types';

export default function ExportersPage() {
  const [exporters, setExporters] = useState<Exporter[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExporters();
  }, []);

  const loadExporters = async () => {
    try {
      const data = await api.getExporters();
      setExporters(data);
    } catch (error) {
      console.error('Failed to load exporters:', error);
      alert('Failed to load exporters');
    } finally {
      setLoading(false);
    }
  };

  const getExporterIcon = (type: string) => {
    switch (type) {
      case 'webhook':
        return '🔗';
      case 'rest':
        return '📡';
      case 'mqtt':
        return '📨';
      default:
        return '⚡';
    }
  };

  const getExporterColor = (type: string) => {
    switch (type) {
      case 'webhook':
        return 'bg-purple-100 text-purple-800';
      case 'rest':
        return 'bg-blue-100 text-blue-800';
      case 'mqtt':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Integrations & Exporters
          </h1>
          <p className="text-gray-600 mt-1">
            Configure webhooks and external integrations for plate events
          </p>
        </div>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          onClick={() => alert('Add exporter - Implementation coming soon')}
        >
          Add Integration
        </button>
      </div>

      {/* Exporters Grid */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading integrations...</p>
        </div>
      ) : exporters.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 mb-4">
            No integrations configured yet. Set up webhooks or API endpoints to
            receive plate events.
          </p>
          <button
            onClick={() => alert('Add exporter - Implementation coming soon')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Your First Integration
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exporters.map((exporter) => (
            <div
              key={exporter.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">
                      {getExporterIcon(exporter.exporter_type)}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {exporter.name}
                    </h3>
                  </div>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      exporter.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {exporter.enabled ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getExporterColor(
                        exporter.exporter_type
                      )}`}
                    >
                      {exporter.exporter_type.toUpperCase()}
                    </span>
                  </div>

                  {exporter.endpoint_url && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Endpoint:</span>
                      <div className="mt-1 font-mono text-xs break-all bg-gray-50 p-2 rounded">
                        {exporter.endpoint_url}
                      </div>
                    </div>
                  )}

                  {exporter.config && Object.keys(exporter.config).length > 0 && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Configuration:</span>
                      <div className="mt-1 text-xs text-gray-500">
                        {Object.keys(exporter.config).length} setting(s)
                        configured
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-gray-200">
                  <div className="text-xs text-gray-500">
                    Created: {new Date(exporter.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() =>
                      alert('Edit exporter - Implementation coming soon')
                    }
                    className="flex-1 bg-blue-100 text-blue-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                  >
                    Configure
                  </button>
                  <button
                    onClick={() =>
                      alert('Test exporter - Implementation coming soon')
                    }
                    className="px-3 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                  >
                    Test
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Integration Types Info */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-3">🔗</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Webhooks</h3>
          <p className="text-sm text-gray-600">
            Receive HTTP POST requests with plate event data to your webhook URL
            when plates are detected.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-3">📡</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            REST APIs
          </h3>
          <p className="text-sm text-gray-600">
            Push plate events to external REST APIs with custom headers and
            authentication.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-3">📨</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">MQTT</h3>
          <p className="text-sm text-gray-600">
            Publish plate events to MQTT topics for integration with IoT systems
            and message brokers.
          </p>
        </div>
      </div>

      {/* Example Payload */}
      <div className="mt-8 bg-gray-900 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-3">
          Example Event Payload
        </h3>
        <pre className="text-sm text-green-400 font-mono overflow-x-auto">
{`{
  "id": 123,
  "camera_id": 1,
  "plate_text": "ABC123",
  "confidence": 0.95,
  "detection_confidence": 0.96,
  "ocr_confidence": 0.94,
  "bbox": {
    "x": 100,
    "y": 200,
    "width": 300,
    "height": 100
  },
  "timestamp": "2025-11-26T14:30:00Z",
  "camera_name": "Main Entrance",
  "camera_location": "Building A"
}`}
        </pre>
      </div>

      {/* Back to Dashboard */}
      <div className="mt-8">
        <a href="/" className="text-blue-600 hover:text-blue-700 font-medium">
          ← Back to Dashboard
        </a>
      </div>
    </div>
  );
}
