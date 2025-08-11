import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';

export default function PriceChart() {
  // Mock data - gerçek veriler API'den gelecek
  const data = [
    { date: '1 Ağu', avgPrice: 14500, products: 120 },
    { date: '2 Ağu', avgPrice: 14300, products: 125 },
    { date: '3 Ağu', avgPrice: 14800, products: 128 },
    { date: '4 Ağu', avgPrice: 14200, products: 132 },
    { date: '5 Ağu', avgPrice: 13900, products: 135 },
    { date: '6 Ağu', avgPrice: 14100, products: 140 },
    { date: '7 Ağu', avgPrice: 13800, products: 142 },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{label}</p>
          <p className="text-sm text-primary-600">
            Ortalama Fiyat: {payload[0].value.toLocaleString('tr-TR')} ₺
          </p>
          <p className="text-sm text-gray-500">
            Ürün Sayısı: {payload[0].payload.products}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="date" 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#6b7280' }}
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            domain={['dataMin - 200', 'dataMax + 200']}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="avgPrice"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#priceGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
      
      <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-primary-500 rounded-full mr-2"></div>
            <span>Ortalama Fiyat</span>
          </div>
        </div>
        <div>
          Son 7 gün
        </div>
      </div>
    </div>
  );
}


