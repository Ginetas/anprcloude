/**
 * Settings Header
 * Top header with breadcrumbs, quick actions, and system status
 */

'use client';

import { usePathname } from 'next/navigation';
import { Save, Download, Upload, History, RefreshCw } from 'lucide-react';

export default function SettingsHeader() {
  const pathname = usePathname();

  // Generate breadcrumbs from pathname
  const generateBreadcrumbs = () => {
    const paths = pathname.split('/').filter(Boolean);
    return paths.map((path, index) => ({
      name: path.charAt(0).toUpperCase() + path.slice(1),
      href: '/' + paths.slice(0, index + 1).join('/'),
      isLast: index === paths.length - 1,
    }));
  };

  const breadcrumbs = generateBreadcrumbs();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Breadcrumbs */}
        <nav className="flex" aria-label="Breadcrumb">
          <ol className="flex items-center space-x-2">
            {breadcrumbs.map((breadcrumb, index) => (
              <li key={breadcrumb.href} className="flex items-center">
                {index > 0 && (
                  <span className="mx-2 text-gray-400">/</span>
                )}
                <a
                  href={breadcrumb.href}
                  className={`text-sm font-medium ${
                    breadcrumb.isLast
                      ? 'text-gray-900'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {breadcrumb.name}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          <button
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            title="View History"
          >
            <History className="w-4 h-4" />
            History
          </button>

          <button
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            title="Export Settings"
          >
            <Download className="w-4 h-4" />
            Export
          </button>

          <button
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            title="Import Settings"
          >
            <Upload className="w-4 h-4" />
            Import
          </button>

          <button
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
            title="Save All Changes"
          >
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>
      </div>
    </header>
  );
}
