'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Model } from '@/lib/types';

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const data = await api.getModels();
      setModels(data);
    } catch (error) {
      console.error('Failed to load models:', error);
      alert('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Models</h1>
        <p className="text-gray-600 mt-1">
          Manage detection and OCR models for license plate recognition
        </p>
      </div>

      {/* Models Grid */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading models...</p>
        </div>
      ) : models.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 mb-4">
            No AI models configured. Models are managed on the edge devices.
          </p>
          <a
            href="/cameras"
            className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Configure Cameras
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {models.map((model) => (
            <div
              key={model.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {model.name}
                  </h3>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      model.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {model.enabled ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {model.model_type.toUpperCase()}
                    </span>
                  </div>

                  <div className="text-sm text-gray-600">
                    <div className="mb-2">
                      <span className="font-medium">Version:</span>{' '}
                      {model.version || 'N/A'}
                    </div>
                    <div className="mb-2">
                      <span className="font-medium">Confidence Threshold:</span>{' '}
                      {(model.confidence_threshold * 100).toFixed(0)}%
                    </div>
                    <div className="mb-2 truncate">
                      <span className="font-medium">Path:</span>{' '}
                      <span className="font-mono text-xs">{model.file_path}</span>
                    </div>
                    {model.description && (
                      <div className="mt-3 text-gray-500 text-xs">
                        {model.description}
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                      Created: {new Date(model.created_at).toLocaleDateString()}
                    </span>
                    {model.updated_at && (
                      <span>
                        Updated:{' '}
                        {new Date(model.updated_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          About AI Models
        </h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>
            <strong>Detection Models:</strong> YOLO-based models that detect license
            plates in camera frames.
          </p>
          <p>
            <strong>OCR Models:</strong> CNN+CTC models that read text from detected
            plate regions.
          </p>
          <p className="mt-4 text-blue-700">
            Models are deployed and run on edge devices (Raspberry Pi + Hailo
            accelerator). They are configured via the edge worker service and model
            files (.hef format for Hailo).
          </p>
        </div>
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
