// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

// Product Types
export interface Product {
  id: number;
  name: string;
  sku?: string;
  url: string;
  site_id: number;
  barcode?: string;
  manufacturer_code?: string;
  category?: string;
  tags?: string[];
  
  // Current values
  current_price?: number;
  current_currency: string;
  is_in_stock?: boolean;
  stock_quantity?: number;
  last_checked?: string;
  
  // Tracking settings
  min_price_threshold?: number;
  max_price_threshold?: number;
  track_stock: boolean;
  track_price: boolean;
  check_interval: number;
  
  // Metadata
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ProductCreate {
  name: string;
  sku?: string;
  url: string;
  site_id: number;
  barcode?: string;
  manufacturer_code?: string;
  category?: string;
  tags?: string[];
  min_price_threshold?: number;
  max_price_threshold?: number;
  track_stock?: boolean;
  track_price?: boolean;
  check_interval?: number;
}

export interface ProductUpdate extends Partial<ProductCreate> {}

export interface ProductSnapshot {
  id: number;
  product_id: number;
  price?: number;
  currency: string;
  is_in_stock?: boolean;
  stock_quantity?: number;
  page_title?: string;
  availability_text?: string;
  scrape_duration_ms?: number;
  http_status_code?: number;
  error_message?: string;
  created_at: string;
}

// Site Types
export interface Site {
  id: number;
  name: string;
  domain: string;
  base_url: string;
  request_delay: number;
  use_javascript: boolean;
  requires_proxy: boolean;
  selectors?: Record<string, any>;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface SiteCreate {
  name: string;
  domain: string;
  base_url: string;
  request_delay?: number;
  use_javascript?: boolean;
  requires_proxy?: boolean;
  selectors?: Record<string, any>;
}

// Alert Types
export interface Alert {
  id: number;
  alert_uuid: string;
  product_id: number;
  alert_type: 'stock_out' | 'stock_in' | 'price_drop' | 'price_rise';
  condition_value?: number;
  triggered_at?: string;
  trigger_value?: number;
  is_sent: boolean;
  sent_at?: string;
  notification_channels?: string[];
  message?: string;
  created_at: string;
}

// Job Types
export interface ScrapingJob {
  id: number;
  job_uuid: string;
  job_type: string;
  product_ids: number[];
  scheduled_at?: string;
  started_at?: string;
  completed_at?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  total_products: number;
  successful_scrapes: number;
  failed_scrapes: number;
  error_message?: string;
  retry_count: number;
  max_retries: number;
  avg_scrape_time_ms?: number;
  created_at: string;
}

// Custom Field Types
export interface CustomField {
  id: number;
  field_uuid: string;
  field_name: string;
  field_label: string;
  field_type: 'text' | 'number' | 'boolean' | 'price' | 'date';
  description?: string;
  is_required: boolean;
  default_value?: string;
  validation_rules?: Record<string, any>;
  display_order: number;
  is_searchable: boolean;
  is_exportable: boolean;
  is_global: boolean;
  created_by: string;
  created_at: string;
}

export interface CustomFieldCreate {
  field_name: string;
  field_label: string;
  field_type: 'text' | 'number' | 'boolean' | 'price' | 'date';
  description?: string;
  is_required?: boolean;
  default_value?: string;
  validation_rules?: Record<string, any>;
  display_order?: number;
  is_searchable?: boolean;
  is_exportable?: boolean;
  is_global?: boolean;
}

export interface UserPreferences {
  id: number;
  user_id: string;
  site_id: number;
  
  // Standard field preferences
  extract_price: boolean;
  extract_stock_status: boolean;
  extract_stock_quantity: boolean;
  extract_product_name: boolean;
  extract_description: boolean;
  extract_images: boolean;
  extract_reviews: boolean;
  extract_rating: boolean;
  extract_brand: boolean;
  extract_model: boolean;
  extract_category: boolean;
  
  // Custom field preferences
  enabled_custom_fields?: string[];
  custom_selectors?: Record<string, string>;
  
  created_at: string;
  updated_at: string;
}

export interface FieldMapping {
  id: number;
  field_id: number;
  site_id: number;
  user_id: string;
  css_selector: string;
  attribute: string;
  regex_pattern?: string;
  preprocessing_rules?: Record<string, any>;
  is_tested: boolean;
  test_url?: string;
  test_result?: string;
  last_tested?: string;
  created_at: string;
}

// Dashboard Types
export interface DashboardStats {
  total_products: number;
  active_products: number;
  total_sites: number;
  pending_alerts: number;
  running_jobs: number;
  success_rate: number;
  avg_response_time: number;
}

export interface PriceChange {
  product_id: number;
  product_name: string;
  old_price: number;
  new_price: number;
  change_percent: number;
  changed_at: string;
}

// Filter and Pagination Types
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ProductFilters extends PaginationParams {
  site_id?: number;
  category?: string;
  in_stock?: boolean;
  search?: string;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  skip: number;
  limit: number;
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface PriceHistoryData {
  product_id: number;
  product_name: string;
  currency: string;
  days: number;
  data_points: number;
  price_history: {
    timestamp: string;
    price?: number;
    is_in_stock: boolean;
    currency: string;
  }[];
}

// Site Wizard Types
export interface SiteAnalysisRequest {
  url: string;
}

export interface SiteAnalysisResponse {
  domain: string;
  site_name: string;
  suggested_config: Record<string, any>;
  suggested_selectors: Record<string, string[]>;
  requires_javascript: boolean;
  analysis_successful: boolean;
}

export interface SiteTestRequest {
  domain: string;
  test_url: string;
  config: {
    name: string;
    domain: string;
    use_javascript: boolean;
    requires_proxy: boolean;
    request_delay: number;
    selectors: Record<string, string>;
  };
}

export interface SiteTestResponse {
  test_successful: boolean;
  extracted_data: Record<string, any>;
  response_time_ms?: number;
  issues: string[];
  suggestions: string[];
  http_status_code?: number;
}

// Error Types
export interface ApiError {
  message: string;
  detail?: string;
  status_code: number;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

// Form Types
export interface FormError {
  field: string;
  message: string;
}

export interface FormState<T = any> {
  data: T;
  errors: FormError[];
  isSubmitting: boolean;
}

// Theme Types
export type ThemeMode = 'light' | 'dark' | 'system';

// Navigation Types
export interface NavItem {
  name: string;
  href: string;
  icon: any;
  badge?: number;
  children?: NavItem[];
}

