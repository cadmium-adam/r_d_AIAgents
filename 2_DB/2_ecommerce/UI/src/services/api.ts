import axios from 'axios';
import type {
  AutocompleteResponse,
  Cart,
  DatabaseStatus,
  Order,
  PaginationInfo,
  PopularSearch,
  Product,
  RecommendationResponse,
  Review,
  SearchResponse,
  SemanticSearchResponse,
  SimilarProductsResponse,
  User,
  UserSession
} from '../types';

// Create axios instances for each database API
const mssqlApi = axios.create({ baseURL: '/api/mssql' });
const mongoApi = axios.create({ baseURL: '/api/mongodb' });
const elasticApi = axios.create({ baseURL: '/api/elasticsearch' });
const qdrantApi = axios.create({ baseURL: '/api/qdrant' });

// MSSQL API Services
export const mssqlService = {
  // Products
  getProducts: async (page = 1, pageSize = 20, category?: string): Promise<{ products: Product[]; pagination: PaginationInfo }> => {
    const params = new URLSearchParams({ page: page.toString(), page_size: pageSize.toString() });
    if (category) params.append('category', category);
    
    const response = await mssqlApi.get(`/products?${params}`);
    return {
      products: response.data.products,
      pagination: response.data.pagination
    };
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await mssqlApi.get(`/products/${id}`);
    return response.data;
  },

  getCategories: async (): Promise<string[]> => {
    const response = await mssqlApi.get('/categories');
    return response.data.map((cat: any) => cat.name);
  },

  // Users
  getUsers: async (page = 1, limit = 20): Promise<{ users: User[]; total: number }> => {
    const response = await mssqlApi.get(`/users?page=${page}&limit=${limit}`);
    return response.data;
  },

  getUser: async (id: number): Promise<User> => {
    const response = await mssqlApi.get(`/users/${id}`);
    return response.data;
  },

  // Orders
  getUserOrders: async (userId: number): Promise<Order[]> => {
    const response = await mssqlApi.get(`/users/${userId}/orders`);
    return response.data;
  },

  getOrder: async (orderId: number): Promise<Order> => {
    const response = await mssqlApi.get(`/orders/${orderId}`);
    return response.data;
  },

  createOrder: async (orderData: {
    user_id: number;
    items: Array<{ product_id: number; quantity: number; unit_price: number }>;
    shipping_address: string;
    payment_method: string;
  }): Promise<Order> => {
    const response = await mssqlApi.post('/orders', orderData);
    return response.data;
  },

  // Analytics
  getSalesAnalytics: async (): Promise<any> => {
    const response = await mssqlApi.get('/analytics/sales');
    return response.data;
  },

  getInventoryStatus: async (): Promise<any> => {
    const response = await mssqlApi.get('/analytics/inventory');
    return response.data;
  },

  // Health
  healthCheck: async (): Promise<DatabaseStatus> => {
    try {
      const response = await mssqlApi.get('/health');
      return { name: 'MSSQL', status: 'healthy', details: response.data };
    } catch (error) {
      return { name: 'MSSQL', status: 'error', details: error };
    }
  }
};

// MongoDB API Services
export const mongoService = {
  // Reviews
  getProductReviews: async (productId: number, page = 1, limit = 10): Promise<Review[]> => {
    const response = await mongoApi.get(`/reviews/product/${productId}?skip=${(page - 1) * limit}&limit=${limit}`);
    return response.data;
  },

  createReview: async (review: {
    product_id: number;
    user_id: number;
    order_id: number;
    rating: number;
    title: string;
    comment: string;
  }): Promise<Review> => {
    const response = await mongoApi.post('/reviews', review);
    return response.data;
  },

  markReviewHelpful: async (reviewId: string): Promise<void> => {
    await mongoApi.post(`/reviews/${reviewId}/helpful`);
  },

  // Shopping Cart
  getCart: async (userId: number): Promise<Cart> => {
    const response = await mongoApi.get(`/cart/${userId}`);
    return response.data;
  },

  addToCart: async (userId: number, item: { product_id: number; quantity: number }): Promise<void> => {
    await mongoApi.post(`/cart/${userId}/add`, item);
  },

  removeFromCart: async (userId: number, productId: number): Promise<void> => {
    await mongoApi.delete(`/cart/${userId}/item/${productId}`);
  },

  // User Sessions
  getUserSession: async (userId: number): Promise<UserSession> => {
    const response = await mongoApi.get(`/users/${userId}/session`);
    return response.data;
  },

  trackBehavior: async (userId: number, event: {
    event_type: string;
    product_id?: number;
    search_query?: string;
    filters?: Record<string, any>;
  }): Promise<void> => {
    await mongoApi.post(`/users/${userId}/behavior`, event);
  },

  // Recommendations
  getUserRecommendations: async (userId: number, algorithm?: string): Promise<any[]> => {
    const params = algorithm ? `?algorithm=${algorithm}` : '';
    const response = await mongoApi.get(`/recommendations/${userId}${params}`);
    return response.data;
  },

  getTrendingProducts: async (limit = 10): Promise<any> => {
    const response = await mongoApi.get(`/recommendations/trending?limit=${limit}`);
    return response.data;
  },

  // Analytics
  getRealTimeAnalytics: async (): Promise<any> => {
    const response = await mongoApi.get('/analytics/realtime');
    return response.data;
  },

  // Health
  healthCheck: async (): Promise<DatabaseStatus> => {
    try {
      const response = await mongoApi.get('/health');
      return { name: 'MongoDB', status: 'healthy', details: response.data };
    } catch (error) {
      return { name: 'MongoDB', status: 'error', details: error };
    }
  }
};

// Elasticsearch API Services
export const elasticService = {
  // Search
  searchProducts: async (
    query: string,
    options: {
      category?: string;
      brand?: string;
      min_price?: number;
      max_price?: number;
      min_rating?: number;
      in_stock?: boolean;
      page?: number;
      size?: number;
      include_aggregations?: boolean;
      user_id?: number;
    } = {}
  ): Promise<SearchResponse> => {
    const params = new URLSearchParams({ q: query });
    
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await elasticApi.get(`/search?${params}`);
    return response.data;
  },

  autocomplete: async (query: string, size = 5): Promise<AutocompleteResponse> => {
    const response = await elasticApi.get(`/autocomplete?q=${encodeURIComponent(query)}&size=${size}`);
    return response.data;
  },

  // Analytics
  trackSearchClick: async (analytics: {
    query: string;
    results_count: number;
    user_id?: number;
    clicked_product_id?: number;
    clicked_position?: number;
    filters_applied?: Record<string, any>;
  }): Promise<void> => {
    await elasticApi.post('/analytics/search', analytics);
  },

  getPopularSearches: async (limit = 10, timeRange = '7d'): Promise<PopularSearch[]> => {
    const response = await elasticApi.get(`/analytics/popular-searches?limit=${limit}&time_range=${timeRange}`);
    return response.data;
  },

  getSearchPerformance: async (): Promise<any> => {
    const response = await elasticApi.get('/analytics/search-performance');
    return response.data;
  },

  // Index Management
  indexProduct: async (product: {
    id: number;
    name: string;
    description: string;
    category: string;
    brand: string;
    price: number;
    stock_quantity: number;
    rating?: number;
    review_count?: number;
    is_active?: boolean;
  }): Promise<void> => {
    await elasticApi.post('/products/index', product);
  },

  removeProductFromIndex: async (productId: number): Promise<void> => {
    await elasticApi.delete(`/products/${productId}`);
  },

  // Health
  healthCheck: async (): Promise<DatabaseStatus> => {
    try {
      const response = await elasticApi.get('/health');
      return { name: 'Elasticsearch', status: 'healthy', details: response.data };
    } catch (error) {
      return { name: 'Elasticsearch', status: 'error', details: error };
    }
  }
};

// Qdrant API Services
export const qdrantService = {
  // Similarity Search
  getSimilarProducts: async (
    productId: number,
    options: {
      limit?: number;
      category_filter?: string;
      min_price?: number;
      max_price?: number;
    } = {}
  ): Promise<SimilarProductsResponse> => {
    const params = new URLSearchParams();
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await qdrantApi.get(`/similar/${productId}?${params}`);
    return response.data;
  },

  // Personalized Recommendations
  getPersonalizedRecommendations: async (
    userId: number,
    options: {
      algorithm?: string;
      limit?: number;
      category_filter?: string;
      min_price?: number;
      max_price?: number;
    } = {}
  ): Promise<RecommendationResponse> => {
    const response = await qdrantApi.post(`/recommendations/${userId}`, options);
    return response.data;
  },

  // Semantic Search
  semanticSearch: async (
    query: string,
    options: {
      limit?: number;
      category_filter?: string;
      min_price?: number;
      max_price?: number;
    } = {}
  ): Promise<SemanticSearchResponse> => {
    const requestBody = { query, ...options };
    const response = await qdrantApi.post('/search/semantic', requestBody);
    return response.data;
  },

  // Status
  getStatus: async (): Promise<any> => {
    const response = await qdrantApi.get('/status');
    return response.data;
  },

  getCollectionsInfo: async (): Promise<any> => {
    const response = await qdrantApi.get('/collections/info');
    return response.data;
  },

  // Health
  healthCheck: async (): Promise<DatabaseStatus> => {
    try {
      const response = await qdrantApi.get('/health');
      return { name: 'Qdrant', status: 'healthy', details: response.data };
    } catch (error) {
      return { name: 'Qdrant', status: 'error', details: error };
    }
  }
};

// Combined Health Check
export const healthService = {
  checkAllDatabases: async (): Promise<DatabaseStatus[]> => {
    const checks = await Promise.allSettled([
      mssqlService.healthCheck(),
      mongoService.healthCheck(),
      elasticService.healthCheck(),
      qdrantService.healthCheck()
    ]);

    return checks.map((result, index) => {
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        const names = ['MSSQL', 'MongoDB', 'Elasticsearch', 'Qdrant'];
        return { 
          name: names[index], 
          status: 'error' as const, 
          details: result.reason 
        };
      }
    });
  }
};