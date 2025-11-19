import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Text,
  Button,
  Card,
  CardHeader,
  Dropdown,
  Option,
  Badge,
  Spinner,
  Field,
  Input,
} from '@fluentui/react-components';
import {
  Sparkle24Regular,
  Search24Regular,
  Target24Regular,
  Brain24Regular,
} from '@fluentui/react-icons';
import { qdrantService, mssqlService } from '../services/api';
import { useApp } from '../components/AppProvider';
import type { SimilarProductsResponse, RecommendationResponse, SemanticSearchResponse, Product } from '../types';

const RecommendationsPage: React.FC = () => {
  const { state, setLoading, setError } = useApp();
  const [activeTab, setActiveTab] = useState<'similar' | 'personalized' | 'semantic'>('personalized');
  const [similarProducts, setSimilarProducts] = useState<SimilarProductsResponse | null>(null);
  const [personalizedRecs, setPersonalizedRecs] = useState<RecommendationResponse | null>(null);
  const [semanticResults, setSemanticResults] = useState<SemanticSearchResponse | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  
  // Form states
  const [selectedProductId, setSelectedProductId] = useState<string>('1');
  const [algorithm, setAlgorithm] = useState<string>('hybrid');
  const [semanticQuery, setSemanticQuery] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [priceRange, setPriceRange] = useState<{ min?: number; max?: number }>({});

  useEffect(() => {
    if (state.currentUser && activeTab === 'personalized') {
      loadPersonalizedRecommendations();
    }
  }, [state.currentUser, activeTab]);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const productData = await mssqlService.getProducts(1, 100); // Get first 100 products
      setProducts(productData.products);
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  const loadSimilarProducts = async () => {
    if (!selectedProductId) return;

    setLoading(true);
    setError(null);
    
    try {
      const results = await qdrantService.getSimilarProducts(parseInt(selectedProductId), {
        limit: 12,
        category_filter: categoryFilter || undefined,
        min_price: priceRange.min,
        max_price: priceRange.max,
      });
      setSimilarProducts(results);
    } catch (error) {
      console.error('Failed to load similar products:', error);
      setError('Failed to load similar products');
    } finally {
      setLoading(false);
    }
  };

  const loadPersonalizedRecommendations = async () => {
    if (!state.currentUser) return;

    setLoading(true);
    setError(null);
    
    try {
      const results = await qdrantService.getPersonalizedRecommendations(state.currentUser.id, {
        algorithm,
        limit: 12,
        category_filter: categoryFilter || undefined,
        min_price: priceRange.min,
        max_price: priceRange.max,
      });
      setPersonalizedRecs(results);
    } catch (error) {
      console.error('Failed to load personalized recommendations:', error);
      setError('Failed to load personalized recommendations');
    } finally {
      setLoading(false);
    }
  };

  const performSemanticSearch = async () => {
    if (!semanticQuery.trim()) return;

    setLoading(true);
    setError(null);
    
    try {
      const results = await qdrantService.semanticSearch(semanticQuery, {
        limit: 12,
        category_filter: categoryFilter || undefined,
        min_price: priceRange.min,
        max_price: priceRange.max,
      });
      setSemanticResults(results);
    } catch (error) {
      console.error('Failed to perform semantic search:', error);
      setError('Failed to perform semantic search');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const clearFilters = () => {
    setCategoryFilter('');
    setPriceRange({});
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Brain24Regular style={{ fontSize: '32px', color: '#dc382d' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              AI-Powered Recommendations
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Powered by Qdrant Vector Database - Demonstrating similarity search, embeddings, and semantic understanding
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Brain24Regular />
            Qdrant Vector Database Features
          </div>
          <div className="database-description">
            This page showcases advanced AI capabilities using vector embeddings for semantic understanding and similarity matching.
          </div>
          <ul className="feature-list">
            <li>Vector similarity search using embeddings</li>
            <li>Personalized recommendations based on user preferences</li>
            <li>Semantic search understanding natural language intent</li>
            <li>Real-time similarity scoring and ranking</li>
            <li>High-dimensional vector operations and filtering</li>
            <li>Machine learning model integration</li>
          </ul>
        </div>
      </div>

      {/* Tab Navigation */}
      <Card style={{ marginBottom: '24px' }}>
        <div style={{ padding: '16px', display: 'flex', gap: '12px', borderBottom: '1px solid #e1e1e1' }}>
          <Button
            appearance={activeTab === 'personalized' ? 'primary' : 'secondary'}
            onClick={() => setActiveTab('personalized')}
            icon={<Sparkle24Regular />}
          >
            Personalized for You
          </Button>
          <Button
            appearance={activeTab === 'similar' ? 'primary' : 'secondary'}
            onClick={() => setActiveTab('similar')}
            icon={<Target24Regular />}
          >
            Similar Products
          </Button>
          <Button
            appearance={activeTab === 'semantic' ? 'primary' : 'secondary'}
            onClick={() => setActiveTab('semantic')}
            icon={<Search24Regular />}
          >
            Semantic Search
          </Button>
        </div>

        {/* Filters */}
        <div style={{ padding: '16px' }}>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <Field label="Category Filter">
              <Dropdown
                placeholder="All Categories"
                value={categoryFilter || 'All Categories'}
                onOptionSelect={(_, data) => setCategoryFilter(data.optionValue || '')}
              >
                <Option value="">All Categories</Option>
                <Option value="Electronics">Electronics</Option>
                <Option value="Clothing">Clothing</Option>
                <Option value="Books">Books</Option>
                <Option value="Home & Garden">Home & Garden</Option>
                <Option value="Sports">Sports</Option>
              </Dropdown>
            </Field>

            <Field label="Min Price">
              <Input
                type="number"
                placeholder="$0"
                value={priceRange.min?.toString() || ''}
                onChange={(_, data) => setPriceRange(prev => ({ ...prev, min: data.value ? parseFloat(data.value) : undefined }))}
              />
            </Field>

            <Field label="Max Price">
              <Input
                type="number"
                placeholder="$1000"
                value={priceRange.max?.toString() || ''}
                onChange={(_, data) => setPriceRange(prev => ({ ...prev, max: data.value ? parseFloat(data.value) : undefined }))}
              />
            </Field>

            {/* Tab-specific controls */}
            {activeTab === 'similar' && (
              <Field label="Select Product">
                <Dropdown
                  placeholder="Choose a product..."
                  value={products.find(p => p.id.toString() === selectedProductId)?.name || 'Choose a product...'}
                  onOptionSelect={(_, data) => setSelectedProductId(data.optionValue || '1')}
                  style={{ minWidth: '200px' }}
                >
                  {products.map((product) => (
                    <Option key={product.id} value={product.id.toString()}>
                      {product.name}
                    </Option>
                  ))}
                </Dropdown>
              </Field>
            )}

            {activeTab === 'personalized' && (
              <Field label="Algorithm">
                <Dropdown
                  value={algorithm}
                  onOptionSelect={(_, data) => setAlgorithm(data.optionValue || 'hybrid')}
                >
                  <Option value="hybrid">Hybrid</Option>
                  <Option value="category_based">Category Based</Option>
                  <Option value="price_based">Price Based</Option>
                </Dropdown>
              </Field>
            )}

            {activeTab === 'semantic' && (
              <Field label="Semantic Query">
                <Input
                  placeholder="Describe what you're looking for..."
                  value={semanticQuery}
                  onChange={(_, data) => setSemanticQuery(data.value)}
                  style={{ minWidth: '250px' }}
                />
              </Field>
            )}

            <div style={{ display: 'flex', gap: '8px' }}>
              {activeTab === 'similar' && (
                <Button appearance="primary" onClick={loadSimilarProducts}>
                  Find Similar
                </Button>
              )}
              {activeTab === 'personalized' && (
                <Button appearance="primary" onClick={loadPersonalizedRecommendations}>
                  Get Recommendations
                </Button>
              )}
              {activeTab === 'semantic' && (
                <Button appearance="primary" onClick={performSemanticSearch}>
                  Semantic Search
                </Button>
              )}
              <Button appearance="secondary" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Results */}
      {state.loading ? (
        <div className="loading-container">
          <Spinner size="large" label="Processing with AI..." />
        </div>
      ) : state.error ? (
        <div className="error-container">
          <Text size={500} style={{ color: '#d13438' }}>{state.error}</Text>
        </div>
      ) : (
        <div>
          {/* Personalized Recommendations */}
          {activeTab === 'personalized' && personalizedRecs && (
            <div>
              <Card style={{ marginBottom: '24px' }}>
                <CardHeader
                  header={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Text size={600} weight="semibold">
                        Personalized Recommendations
                      </Text>
                      <Badge appearance="tint" color="important">
                        Algorithm: {personalizedRecs.algorithm_used}
                      </Badge>
                    </div>
                  }
                />
                <div style={{ padding: '0 16px 16px' }}>
                  <Text size={400} style={{ color: '#605e5c' }}>
                    Based on your preferences and purchase history
                  </Text>
                </div>
              </Card>

              <div className="product-grid">
                {personalizedRecs.recommendations.map((product) => (
                  <Card key={product.id} className="product-card">
                    <div className="product-image">
                      {product.thumbnail_url ? (
                        <img
                          src={product.thumbnail_url}
                          alt={product.name}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement!.innerHTML = '<div style="color: #605e5c; font-size: 24px; display: flex; align-items: center; justify-content: center; height: 100%;">✨</div>';
                          }}
                        />
                      ) : (
                        <Sparkle24Regular />
                      )}
                    </div>
                    <div className="product-info">
                      <Text className="product-name">{product.name}</Text>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <Badge appearance="tint" color="brand">
                          {product.category}
                        </Badge>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          {product.brand}
                        </Text>
                      </div>

                      <Text className="product-price">{formatPrice(product.price)}</Text>
                      
                      <div style={{ marginBottom: '12px' }}>
                        <Badge appearance="tint" color="success" size="small">
                          Similarity: {(product.similarity_score * 100).toFixed(1)}%
                        </Badge>
                        <Text size={300} style={{ color: '#605e5c', marginTop: '4px', display: 'block' }}>
                          {product.recommendation_reason}
                        </Text>
                      </div>

                      <Link to={`/products/${product.id}`} style={{ textDecoration: 'none', width: '100%' }}>
                        <Button appearance="primary" size="small" style={{ width: '100%' }}>
                          View Product
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Similar Products */}
          {activeTab === 'similar' && similarProducts && (
            <div>
              <Card style={{ marginBottom: '24px' }}>
                <CardHeader
                  header={
                    <Text size={600} weight="semibold">
                      Products Similar to {products.find(p => p.id === similarProducts.product_id)?.name || `#${similarProducts.product_id}`}
                    </Text>
                  }
                />
                <div style={{ padding: '0 16px 16px' }}>
                  <Text size={400} style={{ color: '#605e5c' }}>
                    Found {similarProducts.similar_products.length} similar products using vector similarity
                  </Text>
                </div>
              </Card>

              <div className="product-grid">
                {similarProducts.similar_products.map((product, index) => (
                  <Card key={product.id} className="product-card">
                    <div className="product-image">
                      {product.thumbnail_url ? (
                        <img
                          src={product.thumbnail_url}
                          alt={product.name}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement!.innerHTML = '<div style="color: #605e5c; font-size: 24px; display: flex; align-items: center; justify-content: center; height: 100%;">🎯</div>';
                          }}
                        />
                      ) : (
                        <Target24Regular />
                      )}
                    </div>
                    <div className="product-info">
                      <Text className="product-name">{product.name}</Text>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <Badge appearance="tint" color="brand">
                          {product.category}
                        </Badge>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          {product.brand}
                        </Text>
                      </div>

                      <Text className="product-price">{formatPrice(product.price)}</Text>
                      
                      <div style={{ marginBottom: '12px' }}>
                        <Badge appearance="tint" color="important" size="small">
                          Similarity: {(similarProducts.similarity_scores[index] * 100).toFixed(1)}%
                        </Badge>
                        <Badge 
                          appearance="tint" 
                          color={product.in_stock ? 'success' : 'danger'}
                          size="small"
                          style={{ marginLeft: '8px' }}
                        >
                          {product.in_stock ? 'In Stock' : 'Out of Stock'}
                        </Badge>
                      </div>

                      <Link to={`/products/${product.id}`} style={{ textDecoration: 'none', width: '100%' }}>
                        <Button appearance="primary" size="small" style={{ width: '100%' }}>
                          View Product
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Semantic Search Results */}
          {activeTab === 'semantic' && semanticResults && (
            <div>
              <Card style={{ marginBottom: '24px' }}>
                <CardHeader
                  header={
                    <Text size={600} weight="semibold">
                      Semantic Search Results
                    </Text>
                  }
                />
                <div style={{ padding: '0 16px 16px' }}>
                  <Text size={400} style={{ color: '#605e5c' }}>
                    Found {semanticResults.results.length} products matching "{semanticResults.query}" using semantic understanding
                  </Text>
                </div>
              </Card>

              <div className="product-grid">
                {semanticResults.results.map((product, index) => (
                  <Card key={product.id} className="product-card">
                    <div className="product-image">
                      {product.thumbnail_url ? (
                        <img
                          src={product.thumbnail_url}
                          alt={product.name}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement!.innerHTML = '<div style="color: #605e5c; font-size: 24px; display: flex; align-items: center; justify-content: center; height: 100%;">🔍</div>';
                          }}
                        />
                      ) : (
                        <Search24Regular />
                      )}
                    </div>
                    <div className="product-info">
                      <Text className="product-name">{product.name}</Text>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <Badge appearance="tint" color="brand">
                          {product.category}
                        </Badge>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          {product.brand}
                        </Text>
                      </div>

                      <Text className="product-price">{formatPrice(product.price)}</Text>
                      
                      <div style={{ marginBottom: '12px' }}>
                        <Badge appearance="tint" color="warning" size="small">
                          Relevance: {(semanticResults.similarity_scores[index] * 100).toFixed(1)}%
                        </Badge>
                        <Badge 
                          appearance="tint" 
                          color={product.in_stock ? 'success' : 'danger'}
                          size="small"
                          style={{ marginLeft: '8px' }}
                        >
                          {product.in_stock ? 'In Stock' : 'Out of Stock'}
                        </Badge>
                      </div>

                      <Link to={`/products/${product.id}`} style={{ textDecoration: 'none', width: '100%' }}>
                        <Button appearance="primary" size="small" style={{ width: '100%' }}>
                          View Product
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {((activeTab === 'personalized' && !personalizedRecs) ||
            (activeTab === 'similar' && !similarProducts) ||
            (activeTab === 'semantic' && !semanticResults)) && (
            <Card>
              <div style={{ padding: '32px', textAlign: 'center' }}>
                <Brain24Regular style={{ fontSize: '48px', color: '#605e5c', marginBottom: '16px' }} />
                <Text size={500} style={{ marginBottom: '16px', display: 'block' }}>
                  {activeTab === 'personalized' && 'Get personalized recommendations'}
                  {activeTab === 'similar' && 'Find products similar to any item'}
                  {activeTab === 'semantic' && 'Search using natural language'}
                </Text>
                <Text size={400} style={{ color: '#605e5c' }}>
                  {activeTab === 'personalized' && 'Click "Get Recommendations" to see products tailored to your preferences'}
                  {activeTab === 'similar' && 'Enter a product ID and click "Find Similar" to discover related items'}
                  {activeTab === 'semantic' && 'Describe what you\'re looking for in natural language'}
                </Text>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;