'use client';

import { useEffect } from 'react';
import { Activity, Camera, Hash, TrendingUp } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function StatsCards() {
  const { stats, setStats, setLoading, setError } = useStore();

  useEffect(() => {
    const fetchStats = async () => {
      setLoading('stats', true);
      try {
        const data = await api.getStats();
        setStats(data);
        setError('stats', null);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        setError('stats', (error as Error).message);
      } finally {
        setLoading('stats', false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000);

    return () => clearInterval(interval);
  }, [setStats, setLoading, setError]);

  if (!stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-3/4"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Detections',
      value: stats.total_detections.toLocaleString(),
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Today',
      value: stats.detections_today.toLocaleString(),
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'This Hour',
      value: stats.detections_this_hour.toLocaleString(),
      icon: Camera,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Unique Plates',
      value: stats.unique_plates.toLocaleString(),
      icon: Hash,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statCards.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            <div className={`p-2 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            {stat.title === 'Today' && (
              <p className="text-xs text-muted-foreground mt-1">
                Avg. Confidence: {(stats.avg_confidence * 100).toFixed(1)}%
              </p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
