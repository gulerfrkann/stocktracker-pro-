import api from './api';
import { 
  Product, 
  ProductCreate, 
  ProductUpdate, 
  ProductListResponse, 
  ProductFilters,
  ProductSnapshot,
  PriceHistoryData
} from '@/types';

export const productService = {
  // Get products with filtering and pagination
  getProducts: async (filters: ProductFilters = {}): Promise<ProductListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.skip) params.append('skip', filters.skip.toString());
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.site_id) params.append('site_id', filters.site_id.toString());
    if (filters.category) params.append('category', filters.category);
    if (filters.in_stock !== undefined) params.append('in_stock', filters.in_stock.toString());
    if (filters.search) params.append('search', filters.search);
    
    const response = await api.get(`/products?${params.toString()}`);
    return response.data;
  },

  // Get single product
  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  // Create new product
  createProduct: async (data: ProductCreate): Promise<Product> => {
    const response = await api.post('/products', data);
    return response.data;
  },

  // Update product
  updateProduct: async (id: number, data: ProductUpdate): Promise<Product> => {
    const response = await api.put(`/products/${id}`, data);
    return response.data;
  },

  // Delete product
  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`);
  },

  // Get product snapshots (price/stock history)
  getProductSnapshots: async (id: number, limit: number = 100): Promise<ProductSnapshot[]> => {
    const response = await api.get(`/products/${id}/snapshots?limit=${limit}`);
    return response.data;
  },

  // Trigger manual scrape
  triggerScrape: async (id: number): Promise<{ message: string; product_id: number }> => {
    const response = await api.post(`/products/${id}/scrape`);
    return response.data;
  },

  // Get price history for charts
  getPriceHistory: async (id: number, days: number = 30): Promise<PriceHistoryData> => {
    const response = await api.get(`/products/${id}/price-history?days=${days}`);
    return response.data;
  },

  // Bulk operations
  bulkDelete: async (ids: number[]): Promise<void> => {
    await api.post('/products/bulk-delete', { product_ids: ids });
  },

  bulkUpdateTracking: async (ids: number[], settings: Partial<Pick<Product, 'track_stock' | 'track_price' | 'check_interval'>>): Promise<void> => {
    await api.post('/products/bulk-update-tracking', { 
      product_ids: ids, 
      settings 
    });
  },

  // Import/Export
  exportProducts: async (filters: ProductFilters = {}): Promise<Blob> => {
    const params = new URLSearchParams();
    if (filters.site_id) params.append('site_id', filters.site_id.toString());
    if (filters.category) params.append('category', filters.category);
    if (filters.in_stock !== undefined) params.append('in_stock', filters.in_stock.toString());
    
    const response = await api.get(`/products/export?${params.toString()}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  importProducts: async (file: File): Promise<{ imported: number; errors: string[] }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/products/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};


