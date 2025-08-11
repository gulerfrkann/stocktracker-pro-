export interface CreateTrendyolAccountPayload {
  platform: 'trendyol';
  name: string;
  credentials: {
    supplierId: number;
    apiKey: string;
    apiSecret: string;
    userAgent?: string;
  };
  webhook_enabled?: boolean;
}

export interface MarketplaceAccount {
  id: number;
  platform: string;
  name: string;
  last_synced_at?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

const API_BASE = '/api/v1/orders';

export async function listAccounts(): Promise<MarketplaceAccount[]> {
  const res = await fetch(`${API_BASE}/accounts`);
  if (!res.ok) return [];
  return res.json();
}

export async function createTrendyolAccount(payload: CreateTrendyolAccountPayload): Promise<MarketplaceAccount | null> {
  const res = await fetch(`${API_BASE}/accounts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function syncAccount(accountId: number, sinceISO?: string): Promise<number> {
  const res = await fetch(`${API_BASE}/accounts/${accountId}/sync${sinceISO ? `?since=${encodeURIComponent(sinceISO)}` : ''}`, {
    method: 'POST',
  });
  if (!res.ok) return 0;
  const data = await res.json();
  return data?.synced ?? 0;
}



