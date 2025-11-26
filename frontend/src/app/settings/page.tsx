/**
 * Settings Dashboard - Main Page
 * Shows system overview and quick settings
 */

'use client';

import SystemOverview from '@/components/settings/SystemOverview';
import QuickSettings from '@/components/settings/QuickSettings';
import SettingsRecommendations from '@/components/settings/SettingsRecommendations';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Manage all ANPR system settings and configurations
        </p>
      </div>

      {/* System Overview */}
      <SystemOverview />

      {/* Quick Settings & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QuickSettings />
        <SettingsRecommendations />
      </div>
    </div>
  );
}
