import React from 'react';
import StatsCard from '@/components/dashboard/StatsCard';
import RecentActivity from '@/components/dashboard/RecentActivity';
import PriceChart from '@/components/dashboard/PriceChart';
import AlertsList from '@/components/dashboard/AlertsList';
import QuickActions from '@/components/dashboard/QuickActions';

const Dashboard: React.FC = () => {
  const stats = [
    { name: 'Toplam Ürün', value: '1,234', change: '+12%', changeType: 'increase' as const },
    { name: 'Aktif Siteler', value: '45', change: '+3', changeType: 'increase' as const },
    { name: 'Bugünkü İşler', value: '23', change: '-5%', changeType: 'decrease' as const },
    { name: 'Uyarılar', value: '8', change: '+2', changeType: 'increase' as const },
  ];

  const recentActivity = [
    { id: 1, type: 'info', action: 'Yeni ürün eklendi', product: 'iPhone 15 Pro', message: 'Ürün havuza alındı', time: '2 saat önce', icon: 'info', iconColor: 'text-blue-500' },
  ];

  const alerts = [
    { id: 1, product: 'iPhone 15 Pro', type: 'price_drop' as const, message: 'Fiyat %15 düştü', time: '2 saat önce', severity: 'medium' as const },
    { id: 2, product: 'MacBook Air M2', type: 'stock_out' as const, message: 'Stok tükendi', time: '5 saat önce', severity: 'high' as const },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <QuickActions />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <StatsCard key={stat.name} {...stat} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Fiyat Trendi</h3>
          <PriceChart />
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Son Aktiviteler</h3>
          <RecentActivity activities={recentActivity as any} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Son Uyarılar</h3>
        </div>
        <div className="p-6">
          <AlertsList alerts={alerts as any} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
