/**
 * Quick Settings Component
 * Displays frequently accessed settings for quick editing
 */

'use client';

import { useState } from 'react';
import { Settings, Save } from 'lucide-react';

interface QuickSetting {
  id: string;
  label: string;
  value: any;
  type: 'toggle' | 'select' | 'number';
  options?: string[];
}

export default function QuickSettings() {
  const [settings, setSettings] = useState<QuickSetting[]>([
    {
      id: 'ocr_enabled',
      label: 'OCR Enabled',
      value: true,
      type: 'toggle',
    },
    {
      id: 'detection_enabled',
      label: 'Detection Enabled',
      value: true,
      type: 'toggle',
    },
    {
      id: 'log_level',
      label: 'Log Level',
      value: 'INFO',
      type: 'select',
      options: ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    },
    {
      id: 'max_workers',
      label: 'Max Workers',
      value: 4,
      type: 'number',
    },
  ]);

  const handleChange = (id: string, value: any) => {
    setSettings((prev) =>
      prev.map((setting) =>
        setting.id === id ? { ...setting, value } : setting
      )
    );
  };

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving settings:', settings);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Quick Settings</h2>
        </div>
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          <Save className="w-4 h-4" />
          Save
        </button>
      </div>

      {/* Settings List */}
      <div className="p-6 space-y-4">
        {settings.map((setting) => (
          <div key={setting.id} className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              {setting.label}
            </label>

            {setting.type === 'toggle' && (
              <button
                onClick={() => handleChange(setting.id, !setting.value)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  setting.value ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    setting.value ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            )}

            {setting.type === 'select' && (
              <select
                value={setting.value}
                onChange={(e) => handleChange(setting.id, e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {setting.options?.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            )}

            {setting.type === 'number' && (
              <input
                type="number"
                value={setting.value}
                onChange={(e) =>
                  handleChange(setting.id, parseInt(e.target.value))
                }
                className="w-20 px-3 py-1.5 border border-gray-300 rounded-md text-sm text-right focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
