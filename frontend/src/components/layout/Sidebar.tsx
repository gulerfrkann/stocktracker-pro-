import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  CubeIcon,
  GlobeAltIcon,
  PlusCircleIcon,
  BellIcon,
  ShoppingCartIcon,
  PlayIcon,
  UserIcon,
  ChartBarIcon,
  CogIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Ürünler', href: '/products', icon: CubeIcon },
  { name: 'Siteler', href: '/sites', icon: GlobeAltIcon },
  { name: 'Site Ekle', href: '/site-wizard', icon: PlusCircleIcon },
  { name: 'Uyarılar', href: '/alerts', icon: BellIcon },
  { name: 'Siparişler', href: '/orders', icon: ShoppingCartIcon },
  { name: 'İşler', href: '/jobs', icon: PlayIcon },
  { name: 'Tercihler', href: '/preferences', icon: UserIcon },
  { name: 'Raporlar', href: '/reports', icon: ChartBarIcon },
  { name: 'Ayarlar', href: '/settings', icon: CogIcon },
];

const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="flex h-16 items-center justify-center border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">StockTracker Pro</h1>
      </div>
      <nav className="mt-8">
        <div className="space-y-1 px-3">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  isActive
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <item.icon
                  className={`mr-3 h-5 w-5 flex-shrink-0 ${
                    isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;
