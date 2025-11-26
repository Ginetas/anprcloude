/**
 * Settings Recommendations Component
 * Displays intelligent recommendations for settings optimization
 */

'use client';

import { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, AlertCircle, Check } from 'lucide-react';

interface Recommendation {
  id: string;
  setting_key: string;
  current_value: any;
  recommended_value: any;
  reason: string;
  impact: 'low' | 'medium' | 'high';
  category: string;
}

export default function SettingsRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([
    {
      id: '1',
      setting_key: 'hardware.type',
      current_value: 'cpu',
      recommended_value: 'gpu',
      reason: 'GPU detected, using GPU acceleration can improve performance by 3-5x',
      impact: 'high',
      category: 'hardware',
    },
    {
      id: '2',
      setting_key: 'camera.fps',
      current_value: 30,
      recommended_value: 15,
      reason: 'Lower FPS can reduce CPU usage without significant accuracy loss',
      impact: 'medium',
      category: 'camera',
    },
  ]);

  const [appliedRecommendations, setAppliedRecommendations] = useState<Set<string>>(
    new Set()
  );

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-red-600 bg-red-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const handleApply = (recId: string) => {
    // TODO: Implement apply recommendation
    setAppliedRecommendations((prev) => new Set(prev).add(recId));
    console.log('Applying recommendation:', recId);
  };

  const handleDismiss = (recId: string) => {
    setRecommendations((prev) => prev.filter((rec) => rec.id !== recId));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            Recommendations
          </h2>
          <span className="px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-700 rounded-full">
            {recommendations.length}
          </span>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="p-6">
        {recommendations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Check className="w-12 h-12 mx-auto mb-3 text-green-500" />
            <p className="text-sm font-medium">No recommendations</p>
            <p className="text-xs mt-1">
              Your settings are optimally configured
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp className="w-4 h-4 text-blue-500" />
                      <h4 className="text-sm font-semibold text-gray-900">
                        {rec.setting_key}
                      </h4>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded ${getImpactColor(
                          rec.impact
                        )}`}
                      >
                        {rec.impact.toUpperCase()} IMPACT
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{rec.reason}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-3 text-sm">
                  <div>
                    <span className="text-gray-500">Current:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {String(rec.current_value)}
                    </span>
                  </div>
                  <span className="text-gray-400">→</span>
                  <div>
                    <span className="text-gray-500">Recommended:</span>
                    <span className="ml-2 font-medium text-blue-600">
                      {String(rec.recommended_value)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-4">
                  {appliedRecommendations.has(rec.id) ? (
                    <div className="flex items-center gap-2 text-green-600 text-sm">
                      <Check className="w-4 h-4" />
                      <span>Applied</span>
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={() => handleApply(rec.id)}
                        className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                      >
                        Apply
                      </button>
                      <button
                        onClick={() => handleDismiss(rec.id)}
                        className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                      >
                        Dismiss
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
