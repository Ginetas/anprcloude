/**
 * Settings Layout
 * Provides the layout structure for the settings dashboard
 */

'use client';

import { ReactNode } from 'react';
import SettingsSidebar from '@/components/settings/SettingsSidebar';
import SettingsHeader from '@/components/settings/SettingsHeader';

interface SettingsLayoutProps {
  children: ReactNode;
}

export default function SettingsLayout({ children }: SettingsLayoutProps) {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <SettingsSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <SettingsHeader />

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
