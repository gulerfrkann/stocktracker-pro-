import React from 'react';
import {
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

interface Alert {
  id: number;
  product: string;
  type: 'price_drop' | 'price_rise' | 'stock_out' | 'stock_in';
  message: string;
  time: string;
  severity: 'high' | 'medium' | 'low';
}

interface AlertsListProps {
  alerts: Alert[];
}

const alertIcons = {
  price_drop: ExclamationTriangleIcon,
  price_rise: ExclamationTriangleIcon,
  stock_out: ExclamationTriangleIcon,
  stock_in: CheckCircleIcon,
};

const alertColors = {
  high: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: 'text-red-600',
    text: 'text-red-800',
  },
  medium: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    icon: 'text-yellow-600',
    text: 'text-yellow-800',
  },
  low: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: 'text-blue-600',
    text: 'text-blue-800',
  },
};

export default function AlertsList({ alerts }: AlertsListProps) {
  return (
    <div className="space-y-3">
      {alerts.map((alert) => {
        const Icon = alertIcons[alert.type];
        const colors = alertColors[alert.severity];
        
        return (
          <div
            key={alert.id}
            className={`
              p-3 rounded-lg border transition-all duration-200 hover:shadow-sm
              ${colors.bg} ${colors.border}
            `}
          >
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <Icon className={`h-5 w-5 ${colors.icon}`} aria-hidden="true" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <div className="text-sm font-medium text-gray-900 truncate">
                  {alert.product}
                </div>
                <div className={`text-sm ${colors.text} mt-1`}>
                  {alert.message}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {alert.time}
                </div>
              </div>
            </div>
          </div>
        );
      })}
      
      {alerts.length === 0 && (
        <div className="text-center py-6">
          <InformationCircleIcon className="mx-auto h-8 w-8 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">
            Henüz uyarı bulunmuyor
          </p>
        </div>
      )}
      
      <div className="mt-4">
        <button className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium py-2 border border-primary-200 rounded-md hover:bg-primary-50 transition-colors duration-200">
          Tüm uyarıları görüntüle
        </button>
      </div>
    </div>
  );
}


