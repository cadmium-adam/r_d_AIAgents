// API Response Types

// Pagination Types
export interface PaginationInfo {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// MSSQL Types
export interface Product {
  id: number;
  name: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  stock_quantity: number;
  rating: number;
  review_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  main_image_url?: string;
  thumbnail_url?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_premium: boolean;
  total_orders: number;
  total_spent: number;
  average_order_value: number;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: number;
  user_id: number;
  status: string;
  total_amount: number;
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  payment_method: string;
  shipping_address: string;
  order_date: string;
  items: OrderItem[];
}

export interface OrderItem {
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

// MongoDB Types
export interface Review {
  id: string;
  product_id: number;
  product_name: string;
  product_category: string;
  user_id: number;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  pros: string[];
  cons: string[];
  helpful_votes: number;
  total_votes: number;
  unhelpful_votes: number;
  helpfulness_ratio: number;
  verified_purchase: boolean;
  early_reviewer: boolean;
  vine_customer: boolean;
  device_used: string;
  review_language: string;
  contains_media: boolean;
  photos: string[];
  sentiment_score: number;
  moderation: {
    status: string;
    flagged_reasons: string[];
    moderator_notes: string;
  };
  engagement: {
    replies: Array<{
      author: string;
      message: string;
      timestamp: string;
    }>;
    shares: number;
  };
  created_at: string;
  updated_at: string;
}

export interface CartItem {
  product_id: number;
  product_name: string;
  product_image?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Cart {
  user_id: number;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  estimated_total: number;
}

export interface UserSession {
  session_id: string;
  user_id: number;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  pages_viewed: Array<{
    page_type: string;
    url: string;
    timestamp: string;
    time_spent_seconds: number;
  }>;
  device_info: {
    user_agent: string;
    device_type: string;
    browser: string;
    os: string;
  };
  location: {
    ip_address: string;
    country: string;
    city: string;
  };
  referrer: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Elasticsearch Types
export interface SearchResult {
  id: number;
  name: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  rating: number;
  review_count: number;
  stock_quantity: number;
  score: number;
  main_image_url?: string;
  thumbnail_url?: string;
}

export interface SearchResponse {
  query: string;
  total_hits: number;
  took: number;
  results: SearchResult[];
  aggregations?: Record<string, Array<{ key: string; count: number }>>;
  suggestions?: string[];
}

export interface AutocompleteResponse {
  suggestions: string[];
  products: Array<{
    id: number;
    name: string;
    price: number;
    category: string;
  }>;
}

export interface PopularSearch {
  query: string;
  search_count: number;
  trending_score: number;
  suggestions: string[];
}

// Qdrant Types
export interface SimilarProduct {
  id: number;
  name: string;
  category: string;
  brand: string;
  price: number;
  rating: number;
  in_stock: boolean;
  thumbnail_url?: string;
}

export interface SimilarProductsResponse {
  product_id: number;
  similar_products: SimilarProduct[];
  similarity_scores: number[];
}

export interface RecommendationProduct {
  id: number;
  name: string;
  category: string;
  brand: string;
  price: number;
  rating: number;
  similarity_score: number;
  recommendation_reason: string;
  thumbnail_url?: string;
}

export interface RecommendationResponse {
  user_id: number;
  recommendations: RecommendationProduct[];
  algorithm_used: string;
}

export interface SemanticSearchResponse {
  query: string;
  results: SimilarProduct[];
  similarity_scores: number[];
}

// UI State Types
export interface AppState {
  currentUser: User | null;
  cart: Cart | null;
  searchQuery: string;
  selectedCategory: string | null;
  loading: boolean;
  error: string | null;
}

export interface DatabaseStatus {
  name: string;
  status: 'healthy' | 'error' | 'loading';
  response_time?: number;
  details?: any;
}