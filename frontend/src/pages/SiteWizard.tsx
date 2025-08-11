import React, { useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { siteService } from '@/services/siteService';
import {
  SiteAnalysisResponse,
  SiteTestResponse,
} from '@/types';

type Step = 1 | 2 | 3;

interface NewSiteConfigForm {
  name: string;
  domain: string;
  use_javascript: boolean;
  requires_proxy: boolean;
  request_delay: number;
  selectors: Record<string, string>;
  headers?: Record<string, string>;
}

const defaultSelectors: Record<string, string> = {
  price: '',
  currency: '',
  stock_status: '',
  stock_quantity: '',
  product_name: '',
};

const SiteWizard: React.FC = () => {
  const [step, setStep] = useState<Step>(1);

  // Step 1
  const [inputUrl, setInputUrl] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysis, setAnalysis] = useState<SiteAnalysisResponse | null>(null);

  // Step 2 (config)
  const [config, setConfig] = useState<NewSiteConfigForm>({
    name: '',
    domain: '',
    use_javascript: true,
    requires_proxy: false,
    request_delay: 2.0,
    selectors: { ...defaultSelectors },
  });

  // Step 3 (test)
  const [testUrl, setTestUrl] = useState<string>('');
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<SiteTestResponse | null>(null);
  const [isCreating, setIsCreating] = useState<boolean>(false);

  const canProceedToConfig = useMemo(() => Boolean(analysis), [analysis]);
  const canProceedToTest = useMemo(() => {
    return (
      config.name.trim().length > 0 &&
      config.domain.trim().length > 0 &&
      config.request_delay >= 0.5 &&
      config.request_delay <= 10
    );
  }, [config]);

  async function handleAnalyze() {
    if (!inputUrl) {
      toast.error('Lütfen bir URL girin');
      return;
    }
    setIsAnalyzing(true);
    setAnalysis(null);
    try {
      const data = await siteService.analyzeSite({ url: inputUrl });
      setAnalysis(data);

      // Fill config from analysis
      const suggested = data.suggested_config || {};
      const suggestedSelectors = data.suggested_selectors || {};

      const selectors: Record<string, string> = { ...defaultSelectors };
      Object.entries(suggestedSelectors).forEach(([key, arr]) => {
        if (Array.isArray(arr) && arr.length > 0) selectors[key] = arr[0] as string;
      });

      setConfig({
        name: String(suggested.name || data.site_name || ''),
        domain: String(data.domain || ''),
        use_javascript: Boolean(suggested.use_javascript ?? data.requires_javascript ?? true),
        requires_proxy: Boolean(suggested.requires_proxy ?? false),
        request_delay: Number(suggested.request_delay ?? 2.0),
        selectors,
      });

      toast.success('Analiz tamamlandı');
      setStep(2);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Analiz başarısız';
      toast.error(String(msg));
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleTest() {
    if (!testUrl) {
      toast.error('Test için bir ürün sayfası URL’si girin');
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await siteService.testConfiguration({
        domain: config.domain,
        test_url: testUrl,
        config: {
          name: config.name,
          domain: config.domain,
          use_javascript: config.use_javascript,
          requires_proxy: config.requires_proxy,
          request_delay: config.request_delay,
          selectors: config.selectors,
        },
      });
      setTestResult(res);
      if (res.test_successful) toast.success('Test başarılı');
      else toast('Test tamamlandı, önerileri inceleyin', { icon: 'ℹ️' });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Test başarısız';
      toast.error(String(msg));
    } finally {
      setIsTesting(false);
    }
  }

  async function handleCreate() {
    setIsCreating(true);
    try {
      const payload = {
        name: config.name,
        domain: config.domain,
        use_javascript: config.use_javascript,
        requires_proxy: config.requires_proxy,
        request_delay: config.request_delay,
        selectors: config.selectors,
      };
      const res = await siteService.createSiteFromWizard(payload);
      toast.success(`Site eklendi: ${res.domain}`);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Site oluşturulamadı';
      toast.error(String(msg));
    } finally {
      setIsCreating(false);
    }
  }

  function handleSelectorKeyChange(oldKey: string, newKey: string) {
    const trimmed = newKey.trim();
    if (!trimmed) {
      toast.error('Alan adı boş olamaz');
      return;
    }
    if (trimmed !== oldKey && Object.prototype.hasOwnProperty.call(config.selectors, trimmed)) {
      toast.error('Bu alan adı zaten var');
      return;
    }
    setConfig((prev) => {
      const nextSelectors: Record<string, string> = {};
      Object.entries(prev.selectors).forEach(([k, v]) => {
        if (k === oldKey) nextSelectors[trimmed] = v;
        else nextSelectors[k] = v;
      });
      return { ...prev, selectors: nextSelectors };
    });
  }

  function handleSelectorValueChange(key: string, value: string) {
    setConfig((prev) => ({
      ...prev,
      selectors: { ...prev.selectors, [key]: value },
    }));
  }

  function handleSelectorRemove(key: string) {
    setConfig((prev) => {
      const entries = Object.entries(prev.selectors).filter(([k]) => k !== key);
      const nextSelectors = Object.fromEntries(entries);
      return { ...prev, selectors: nextSelectors };
    });
  }

  function handleSelectorAdd() {
    setConfig((prev) => {
      let idx = 1;
      let newKey = `field_${idx}`;
      const existing = new Set(Object.keys(prev.selectors));
      while (existing.has(newKey)) {
        idx += 1;
        newKey = `field_${idx}`;
      }
      return {
        ...prev,
        selectors: { ...prev.selectors, [newKey]: '' },
      };
    });
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Site Ekleme Sihirbazı</h1>
      </div>

      {/* Steps indicator */}
      <div className="bg-white rounded-lg shadow p-4 flex items-center gap-3 text-sm">
        <div className={`px-2 py-1 rounded ${step === 1 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
          1. Site Analizi
        </div>
        <div className={`px-2 py-1 rounded ${step === 2 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
          2. Yapılandırma
        </div>
        <div className={`px-2 py-1 rounded ${step === 3 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
          3. Test & Kaydet
        </div>
      </div>

      {/* Step 1: Analyze */}
      {step === 1 && (
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <label className="block text-sm font-medium text-gray-700">Site URL</label>
          <input
            type="url"
            placeholder="https://www.ornek-site.com/urun/123"
            className="w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
          />
          <div className="flex items-center gap-3">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !inputUrl}
              className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
            >
              {isAnalyzing ? 'Analiz ediliyor...' : 'Analiz Et'}
            </button>
            {canProceedToConfig && (
              <button
                onClick={() => setStep(2)}
                className="px-4 py-2 rounded bg-gray-100 text-gray-800"
              >
                Yapılandırmaya Geç
              </button>
            )}
          </div>
          {analysis && (
            <div className="mt-4 text-sm text-gray-700">
              <div><span className="font-medium">Domain:</span> {analysis.domain}</div>
              <div><span className="font-medium">Önerilen İsim:</span> {analysis.site_name}</div>
              <div><span className="font-medium">JS Gerekli mi:</span> {analysis.requires_javascript ? 'Evet' : 'Hayır'}</div>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Configure */}
      {step === 2 && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Site Adı</label>
              <input
                type="text"
                className="w-full rounded border border-gray-300 px-3 py-2"
                value={config.name}
                onChange={(e) => setConfig({ ...config, name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Domain</label>
              <input
                type="text"
                className="w-full rounded border border-gray-300 px-3 py-2"
                value={config.domain}
                onChange={(e) => setConfig({ ...config, domain: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">İstek Gecikmesi (sn)</label>
              <input
                type="number"
                min={0.5}
                max={10}
                step={0.5}
                className="w-full rounded border border-gray-300 px-3 py-2"
                value={config.request_delay}
                onChange={(e) => setConfig({ ...config, request_delay: Number(e.target.value) })}
              />
            </div>
            <div className="flex items-center gap-6 mt-6">
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.use_javascript}
                  onChange={(e) => setConfig({ ...config, use_javascript: e.target.checked })}
                />
                <span className="text-sm text-gray-700">JavaScript kullan</span>
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.requires_proxy}
                  onChange={(e) => setConfig({ ...config, requires_proxy: e.target.checked })}
                />
                <span className="text-sm text-gray-700">Proxy gerekli</span>
              </label>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-900">Seçiciler (CSS)</h2>
              <button
                type="button"
                onClick={handleSelectorAdd}
                className="px-3 py-1.5 rounded bg-green-600 text-white text-sm"
              >Yeni Alan Ekle</button>
            </div>
            <div className="space-y-3">
              {Object.entries(config.selectors).map(([key, value]) => (
                <div key={key} className="grid grid-cols-1 md:grid-cols-12 gap-2 items-center">
                  <div className="md:col-span-3">
                    <label className="block text-[11px] font-medium text-gray-600">Alan Adı</label>
                    <input
                      type="text"
                      className="w-full rounded border border-gray-300 px-3 py-2"
                      defaultValue={key}
                      onBlur={(e) => {
                        const newKey = e.target.value;
                        if (newKey !== key) handleSelectorKeyChange(key, newKey);
                        else e.target.value = key; // keep in sync if unchanged
                      }}
                    />
                  </div>
                  <div className="md:col-span-8">
                    <label className="block text-[11px] font-medium text-gray-600">CSS Selector</label>
                    <input
                      type="text"
                      className="w-full rounded border border-gray-300 px-3 py-2"
                      value={value}
                      onChange={(e) => handleSelectorValueChange(key, e.target.value)}
                    />
                  </div>
                  <div className="md:col-span-1 flex md:justify-end">
                    <button
                      type="button"
                      onClick={() => handleSelectorRemove(key)}
                      className="px-3 py-2 rounded bg-red-50 text-red-700 text-sm border border-red-200"
                    >Sil</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <button onClick={() => setStep(1)} className="px-4 py-2 rounded bg-gray-100 text-gray-800">Geri</button>
            <button
              onClick={() => setStep(3)}
              disabled={!canProceedToTest}
              className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
            >
              Test Aşamasına Geç
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Test & Create */}
      {step === 3 && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Test Ürün URL</label>
            <input
              type="url"
              placeholder="https://{domain}/urun/..."
              className="w-full rounded border border-gray-300 px-3 py-2"
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
            />
            <div className="flex items-center gap-3">
              <button
                onClick={handleTest}
                disabled={isTesting || !testUrl}
                className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
              >
                {isTesting ? 'Test ediliyor...' : 'Konfigürasyonu Test Et'}
              </button>
              <button onClick={() => setStep(2)} className="px-4 py-2 rounded bg-gray-100 text-gray-800">Geri</button>
            </div>
          </div>

          {testResult && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border rounded p-3">
                <div className="text-sm font-medium text-gray-900 mb-2">Sonuç</div>
                <div className={`inline-flex items-center px-2 py-1 rounded text-xs ${testResult.test_successful ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {testResult.test_successful ? 'Başarılı' : 'Başarısız'}
                </div>
                <pre className="mt-3 text-xs bg-gray-50 p-2 rounded overflow-auto max-h-48">
{JSON.stringify(testResult.extracted_data, null, 2)}
                </pre>
              </div>
              <div className="border rounded p-3">
                <div className="text-sm font-medium text-gray-900 mb-2">Öneriler / Sorunlar</div>
                {testResult.issues?.length ? (
                  <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                    {testResult.issues.map((i, idx) => (
                      <li key={idx}>{i}</li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-gray-600">Sorun raporlanmadı.</div>
                )}
                {!!testResult.suggestions?.length && (
                  <div className="mt-3">
                    <div className="text-sm font-medium text-gray-900 mb-1">Öneriler</div>
                    <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                      {testResult.suggestions.map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <button onClick={() => setStep(2)} className="px-4 py-2 rounded bg-gray-100 text-gray-800">Geri</button>
            <button
              onClick={handleCreate}
              disabled={isCreating}
              className="px-4 py-2 rounded bg-green-600 text-white disabled:opacity-50"
            >
              {isCreating ? 'Kaydediliyor...' : 'Siteyi Oluştur'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SiteWizard;
