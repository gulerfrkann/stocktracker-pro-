import api from './api';
import { Site, SiteCreate, SiteAnalysisRequest, SiteAnalysisResponse, SiteTestRequest, SiteTestResponse } from '@/types';

export const siteService = {
  // Get all sites
  getSites: async (): Promise<Site[]> => {
    const response = await api.get('/sites');
    return response.data;
  },

  // Get single site
  getSite: async (id: number): Promise<Site> => {
    const response = await api.get(`/sites/${id}`);
    return response.data;
  },

  // Create new site
  createSite: async (data: SiteCreate): Promise<Site> => {
    const response = await api.post('/sites', data);
    return response.data;
  },

  // Update site
  updateSite: async (id: number, data: Partial<SiteCreate>): Promise<Site> => {
    const response = await api.put(`/sites/${id}`, data);
    return response.data;
  },

  // Site Wizard functions
  analyzeSite: async (data: SiteAnalysisRequest): Promise<SiteAnalysisResponse> => {
    const response = await api.post('/site-wizard/analyze-site', data);
    return response.data;
  },

  testConfiguration: async (data: SiteTestRequest): Promise<SiteTestResponse> => {
    const response = await api.post('/site-wizard/test-configuration', data);
    return response.data;
  },

  createSiteFromWizard: async (config: any): Promise<{ message: string; site_id: number; domain: string }> => {
    const response = await api.post('/site-wizard/create-site', config);
    return response.data;
  },

  getSupportedSites: async (): Promise<{
    total_sites: number;
    predefined_sites: number;
    dynamic_sites: number;
    sites: Array<{
      domain: string;
      name: string;
      type: 'predefined' | 'dynamic';
      parser_available: boolean;
    }>;
  }> => {
    const response = await api.get('/site-wizard/supported-sites');
    return response.data;
  },
};


