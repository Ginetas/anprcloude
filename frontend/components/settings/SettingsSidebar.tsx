/**
 * Settings Sidebar
 * Navigation sidebar for settings categories
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Settings,
  Cpu,
  Camera,
  Box,
  Eye,
  Video,
  Activity,
  Upload,
  Database,
  BarChart,
  Shield,
  Bell,
  Sliders,
} from 'lucide-react';

interface CategoryItem {
  id: string;
  name: string;
  icon: any;
  href: string;
  count?: number;
}

const categories: CategoryItem[] = [
  {
    id: 'overview',
    name: 'System Overview',
    icon: Activity,
    href: '/settings',
  },
  {
    id: 'hardware',
    name: 'Hardware',
    icon: Cpu,
    href: '/settings/hardware',
  },
  {
    id: 'cameras',
    name: 'Cameras',
    icon: Camera,
    href: '/settings/cameras',
  },
  {
    id: 'zones',
    name: 'Detection Zones',
    icon: Box,
    href: '/settings/zones',
  },
  {
    id: 'models',
    name: 'Detection Models',
    icon: Eye,
    href: '/settings/models',
  },
  {
    id: 'ocr',
    name: 'OCR',
    icon: Settings,
    href: '/settings/ocr',
  },
  {
    id: 'pipeline',
    name: 'Video Pipeline',
    icon: Video,
    href: '/settings/pipeline',
  },
  {
    id: 'tracking',
    name: 'Object Tracking',
    icon: Activity,
    href: '/settings/tracking',
  },
  {
    id: 'export',
    name: 'Data Export',
    icon: Upload,
    href: '/settings/export',
  },
  {
    id: 'storage',
    name: 'Storage & Database',
    icon: Database,
    href: '/settings/storage',
  },
  {
    id: 'monitoring',
    name: 'Monitoring',
    icon: BarChart,
    href: '/settings/monitoring',
  },
  {
    id: 'security',
    name: 'Security',
    icon: Shield,
    href: '/settings/security',
  },
  {
    id: 'notifications',
    name: 'Notifications',
    icon: Bell,
    href: '/settings/notifications',
  },
  {
    id: 'advanced',
    name: 'Advanced',
    icon: Sliders,
    href: '/settings/advanced',
  },
];

export default function SettingsSidebar() {
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCategories = categories.filter((category) =>
    category.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo/Brand */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">ANPR Settings</h2>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <input
          type="text"
          placeholder="Search settings..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Categories Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {filteredCategories.map((category) => {
            const Icon = category.icon;
            const isActive = pathname === category.href;

            return (
              <li key={category.id}>
                <Link
                  href={category.href}
                  className={`
                    flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors
                    ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span className="flex-1">{category.name}</span>
                  {category.count !== undefined && (
                    <span className="px-2 py-0.5 text-xs bg-gray-200 text-gray-600 rounded-full">
                      {category.count}
                    </span>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
        <p>ANPR Engine v1.0</p>
        <p>Powered by Claude</p>
      </div>
    </div>
  );
}
