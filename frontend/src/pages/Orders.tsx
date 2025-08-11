import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createTrendyolAccount, listAccounts, syncAccount } from '@/services/ordersService';

interface OrderItem {
  id: number;
  sku?: string;
  product_name: string;
  quantity: number;
  unit_price?: number;
  line_total?: number;
  currency: string;
}

interface Order {
  id: number;
  external_order_id: string;
  buyer_name?: string;
  total_amount?: number;
  currency: string;
  order_status?: string;
  placed_at?: string;
  items: OrderItem[];
}

const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [creating, setCreating] = useState<boolean>(false);
  const [accounts, setAccounts] = useState<{ id: number; name: string }[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const apiBase = useMemo(() => '/api/v1', []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/orders?limit=50`);
      if (!res.ok) {
        setOrders([]);
        return;
      }
      const data = await res.json();
      setOrders(Array.isArray(data) ? data : []);
    } catch (e) {
      // noop
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    listAccounts().then((acs) => setAccounts(acs.map(a => ({ id: a.id, name: a.name }))));
    // Subscribe SSE
    const es = new EventSource(`${apiBase}/orders/events/stream`);
    es.onmessage = () => {
      // On any event, refresh list
      fetchOrders();
    };
    es.onerror = () => {
      es.close();
    };
    eventSourceRef.current = es;
    return () => {
      es.close();
    };
  }, [apiBase]);

  return (
    <div className="p-6">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-xl font-semibold">Siparişler</h2>
        <div className="flex items-center gap-2">
          <button
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            onClick={fetchOrders}
            disabled={loading}
          >
            Yenile
          </button>
          <button
            className="rounded bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
            disabled={creating}
            onClick={async () => {
              const apiKey = prompt('Trendyol API Key');
              const apiSecret = prompt('Trendyol API Secret');
              const supplierIdStr = prompt('SupplierId (örn: 954256)');
              if (!apiKey || !apiSecret || !supplierIdStr) return;
              const supplierId = Number(supplierIdStr);
              setCreating(true);
              const created = await createTrendyolAccount({
                platform: 'trendyol',
                name: `Trendyol ${supplierId}`,
                credentials: { supplierId, apiKey, apiSecret, userAgent: 'YourAppName/1.0' },
                webhook_enabled: false,
              });
              await listAccounts().then((acs) => setAccounts(acs.map(a => ({ id: a.id, name: a.name }))));
              setCreating(false);
              if (created) alert('Hesap eklendi');
            }}
          >
            Trendyol Hesap Ekle
          </button>
          {accounts.length > 0 && (
            <button
              className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
              onClick={async () => {
                const selected = accounts[0];
                const since = prompt('Since ISO (boş bırakılabilir)', '');
                const synced = await syncAccount(selected.id, since || undefined);
                alert(`Senkronize edilen sipariş: ${synced}`);
                fetchOrders();
              }}
            >
              İlk Hesabı Senkronize Et
            </button>
          )}
        </div>
      </div>

      <div className="overflow-hidden rounded border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">#</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Sipariş</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Müşteri</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Tutar</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Durum</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Tarih</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {orders.map((o) => (
              <tr key={o.id}>
                <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">{o.id}</td>
                <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-900">{o.external_order_id}</td>
                <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">{o.buyer_name || '-'}</td>
                <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">{o.total_amount ?? '-'} {o.currency}</td>
                <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">{o.order_status || '-'}</td>
                <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">{o.placed_at ? new Date(o.placed_at).toLocaleString() : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Orders;


