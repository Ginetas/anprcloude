'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Camera,
  MapPin,
  Box,
  Wifi,
  Share2,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useStore } from '@/lib/store';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  {
    name: 'Configuration',
    icon: Settings,
    children: [
      { name: 'Cameras', href: '/config/cameras', icon: Camera },
      { name: 'Zones', href: '/config/zones', icon: MapPin },
      { name: 'Models', href: '/config/models', icon: Box },
      { name: 'Sensors', href: '/config/sensors', icon: Wifi },
    ],
  },
  { name: 'Integrations', href: '/integrations', icon: Share2 },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useStore();

  return (
    <>
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col bg-gray-900 transition-all duration-300',
          sidebarOpen ? 'w-64' : 'w-20'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-gray-800">
          {sidebarOpen ? (
            <div className="flex items-center space-x-2">
              <Camera className="h-8 w-8 text-blue-500" />
              <span className="text-lg font-bold text-white">ANPR Engine</span>
            </div>
          ) : (
            <Camera className="h-8 w-8 text-blue-500 mx-auto" />
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {navigation.map((item) => (
            <div key={item.name}>
              {item.href ? (
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    pathname === item.href
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white',
                    !sidebarOpen && 'justify-center'
                  )}
                  title={!sidebarOpen ? item.name : undefined}
                >
                  <item.icon className={cn('h-5 w-5', sidebarOpen && 'mr-3')} />
                  {sidebarOpen && <span>{item.name}</span>}
                </Link>
              ) : (
                <>
                  {sidebarOpen && (
                    <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                      {item.name}
                    </div>
                  )}
                  {item.children?.map((child) => (
                    <Link
                      key={child.name}
                      href={child.href}
                      className={cn(
                        'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                        pathname === child.href
                          ? 'bg-gray-800 text-white'
                          : 'text-gray-300 hover:bg-gray-800 hover:text-white',
                        !sidebarOpen && 'justify-center'
                      )}
                      title={!sidebarOpen ? child.name : undefined}
                    >
                      <child.icon className={cn('h-5 w-5', sidebarOpen && 'mr-3')} />
                      {sidebarOpen && <span>{child.name}</span>}
                    </Link>
                  ))}
                </>
              )}
            </div>
          ))}
        </nav>

        {/* Toggle Button */}
        <div className="border-t border-gray-800 p-4">
          <button
            onClick={toggleSidebar}
            className="flex items-center justify-center w-full px-3 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
            title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {sidebarOpen ? (
              <>
                <ChevronLeft className="h-5 w-5 mr-3" />
                <span>Collapse</span>
              </>
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {/* Spacer */}
      <div className={cn('transition-all duration-300', sidebarOpen ? 'w-64' : 'w-20')} />
    </>
  );
}
