import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';
import { ChartBarIcon } from '@heroicons/react/24/outline';

interface StatsCardProps {
  name: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease';
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  color?: 'blue' | 'green' | 'yellow' | 'purple' | 'red';
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-500',
    lightBg: 'bg-blue-50',
    text: 'text-blue-600',
    ring: 'ring-blue-500/20',
  },
  green: {
    bg: 'bg-green-500',
    lightBg: 'bg-green-50',
    text: 'text-green-600',
    ring: 'ring-green-500/20',
  },
  yellow: {
    bg: 'bg-yellow-500',
    lightBg: 'bg-yellow-50',
    text: 'text-yellow-600',
    ring: 'ring-yellow-500/20',
  },
  purple: {
    bg: 'bg-purple-500',
    lightBg: 'bg-purple-50',
    text: 'text-purple-600',
    ring: 'ring-purple-500/20',
  },
  red: {
    bg: 'bg-red-500',
    lightBg: 'bg-red-50',
    text: 'text-red-600',
    ring: 'ring-red-500/20',
  },
} as const;

export default function StatsCard({
  name,
  value,
  change,
  changeType,
  icon: Icon = ChartBarIcon,
  color = 'blue',
}: StatsCardProps) {
  const colors = colorClasses[color];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div
            className={`inline-flex items-center justify-center p-3 rounded-lg ${colors.lightBg} ${colors.ring} ring-4`}
          >
            <Icon className={`h-6 w-6 ${colors.text}`} aria-hidden="true" />
          </div>
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{name}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value}</div>
              <div className="ml-2 flex items-baseline text-sm font-semibold">
                {changeType === 'increase' ? (
                  <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={changeType === 'increase' ? 'text-green-600' : 'text-red-600'}>
                  {change}
                </span>
                <span className="ml-1 text-gray-500">bu ay</span>
              </div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
  );
}
