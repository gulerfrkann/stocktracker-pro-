import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { siteService } from '@/services/siteService';
import type { Site } from '@/types';

const Sites: React.FC = () => {
  const [sites, setSites] = useState<Site[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        setIsLoading(true);
        const data = await siteService.getSites();
        if (isMounted) setSites(data);
      } catch (e: any) {
        if (isMounted) setError(e?.response?.data?.detail || e?.message || 'Bir hata oluştu');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    })();
    return () => {
      isMounted = false;
    };
  }, []);

  const hasData = useMemo(() => (sites && sites.length > 0), [sites]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Siteler</h1>
        <Link to="/site-wizard" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          Yeni Site Ekle
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow">
        {isLoading ? (
          <div className="p-6 text-gray-600">Yükleniyor…</div>
        ) : error ? (
          <div className="p-6 text-red-600">{error}</div>
        ) : !hasData ? (
          <div className="p-6 text-gray-600">Kayıtlı site bulunamadı. Sağ üstten yeni site ekleyebilirsiniz.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ad</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Domain</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">JS</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gecikme (sn)</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Oluşturma</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sites.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{s.name}</td>
                    <td className="px-4 py-3 text-sm text-blue-600">{s.domain}</td>
                    <td className="px-4 py-3 text-sm">
                      {s.use_javascript ? (
                        <span className="inline-flex items-center rounded bg-yellow-100 px-2 py-0.5 text-yellow-800 text-xs">Playwright</span>
                      ) : (
                        <span className="inline-flex items-center rounded bg-green-100 px-2 py-0.5 text-green-800 text-xs">HTTP</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{Number(s.request_delay).toFixed(1)}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{new Date(s.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sites;
