import React from 'react';
import { Link } from 'react-router-dom';
import {
  PlusIcon,
  PlayIcon,
  ArrowDownTrayIcon,
  CogIcon,
  GlobeAltIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

const actions = [
  {
    name: 'Ürün Ekle',
    description: 'Yeni ürün takibine başla',
    href: '/products?action=create',
    icon: PlusIcon,
    color: 'bg-blue-500 hover:bg-blue-600',
  },
  {
    name: 'Site Ekle',
    description: 'Yeni e-ticaret sitesi ekle',
    href: '/site-wizard',
    icon: GlobeAltIcon,
    color: 'bg-green-500 hover:bg-green-600',
  },
  {
    name: 'Tarama Başlat',
    description: 'Manuel veri taraması',
    href: '/jobs?action=create',
    icon: PlayIcon,
    color: 'bg-purple-500 hover:bg-purple-600',
  },
  {
    name: 'Rapor Al',
    description: 'Excel raporu indir',
    href: '/reports',
    icon: ArrowDownTrayIcon,
    color: 'bg-yellow-500 hover:bg-yellow-600',
  },
  {
    name: 'Tercihler',
    description: 'Veri çekme ayarları',
    href: '/preferences',
    icon: CogIcon,
    color: 'bg-gray-500 hover:bg-gray-600',
  },
  {
    name: 'Analitik',
    description: 'Detaylı raporlar',
    href: '/reports',
    icon: ChartBarIcon,
    color: 'bg-indigo-500 hover:bg-indigo-600',
  },
];

export default function QuickActions() {
  return (
    <div className="grid grid-cols-2 gap-3">
      {actions.map((action) => (
        <Link
          key={action.name}
          to={action.href}
          className="group relative rounded-lg p-4 bg-gray-50 hover:bg-white hover:shadow-md transition-all duration-200 border border-gray-200 hover:border-gray-300"
        >
          <div className="flex items-center">
            <div className={`
              flex h-8 w-8 items-center justify-center rounded-lg text-white transition-colors duration-200
              ${action.color}
            `}>
              <action.icon className="h-4 w-4" aria-hidden="true" />
            </div>
            <div className="ml-3 min-w-0 flex-1">
              <div className="text-sm font-medium text-gray-900 group-hover:text-gray-700">
                {action.name}
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {action.description}
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
