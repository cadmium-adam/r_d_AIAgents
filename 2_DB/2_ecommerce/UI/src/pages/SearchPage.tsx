import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Text,
  Button,
  Card,
  CardHeader,
  Input,
  Dropdown,
  Option,
  Badge,
  Spinner,
  Field,
  Checkbox,
} from '@fluentui/react-components';
import {
  Search24Regular,
  Filter24Regular,
  Star24Filled,
  Star24Regular,
  Timer24Regular,
  Target24Regular,
} from '@fluentui/react-icons';
import { elasticService } from '../services/api';
import { useApp } from '../components/AppProvider';
import type { SearchResponse, AutocompleteResponse } from '../types';

const SearchPage: React.FC = () => {
  const { state, setLoading, setError } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [autocomplete, setAutocomplete] = useState<AutocompleteResponse | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedBrand, setSelectedBrand] = useState<string>('all');
  const [priceRange, setPriceRange] = useState<{ min?: number; max?: number }>({});
  const [minRating, setMinRating] = useState<number | null>(null);
  const [inStockOnly, setInStockOnly] = useState(true);
  const [includeAggregations, setIncludeAggregations] = useState(true);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Load all products on mount
  useEffect(() => {
    performSearch('');
  }, []);

  // Re-search when filters or page change
  useEffect(() => {
    if (searchQuery.trim()) {
      performSearch(searchQuery);
    } else {
      performSearch('');
    }
  }, [selectedCategory, selectedBrand, priceRange.min, priceRange.max, minRating, inStockOnly, currentPage]);

  // Reset to page 1 when filters change (excluding currentPage)
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedCategory, selectedBrand, priceRange.min, priceRange.max, minRating, inStockOnly, searchQuery]);

  const performSearch = async (query: string = '') => {
    setLoading(true);
    setError(null);
    setShowAutocomplete(false);

    try {
      const results = await elasticService.searchProducts(query, {
        category: selectedCategory === 'all' ? undefined : selectedCategory,
        brand: selectedBrand === 'all' ? undefined : selectedBrand,
        min_price: priceRange.min,
        max_price: priceRange.max,
        min_rating: minRating || undefined,
        in_stock: inStockOnly,
        page: currentPage,
        size: pageSize,
        include_aggregations: includeAggregations,
        user_id: state.currentUser?.id,
      });

      setSearchResults(results);

      // Track search analytics only for actual searches
      if (query && state.currentUser) {
        await elasticService.trackSearchClick({
          query: query,
          results_count: results.total_hits,
          user_id: state.currentUser.id,
        });
      }
    } catch (error) {
      console.error('Search failed:', error);
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      // If search is empty, show all products
      await performSearch('');
    } else {
      await performSearch(searchQuery);
    }
  };

  const handleAutocomplete = async (query: string) => {
    if (query.length < 2) {
      setAutocomplete(null);
      setShowAutocomplete(false);
      return;
    }

    try {
      const suggestions = await elasticService.autocomplete(query);
      setAutocomplete(suggestions);
      setShowAutocomplete(true);
    } catch (error) {
      console.error('Autocomplete failed:', error);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        i <= rating ? (
          <Star24Filled key={i} style={{ color: '#ffb900', fontSize: '16px' }} />
        ) : (
          <Star24Regular key={i} style={{ color: '#d1d1d1', fontSize: '16px' }} />
        )
      );
    }
    return stars;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedBrand('all');
    setPriceRange({});
    setMinRating(null);
    setInStockOnly(true);
    setCurrentPage(1);
    // The useEffect will automatically trigger a new search showing all products
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Search24Regular style={{ fontSize: '32px', color: '#005571' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              Product Search
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Powered by Elasticsearch - Demonstrating full-text search, autocomplete, and real-time analytics
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Search24Regular />
            Elasticsearch Features Demonstrated
          </div>
          <div className="database-description">
            This page showcases Elasticsearch's search capabilities with advanced text analysis and real-time indexing.
          </div>
          <ul className="feature-list">
            <li>Full-text search with relevance scoring</li>
            <li>Faceted search with aggregations</li>
            <li>Fuzzy matching and typo tolerance</li>
            <li>Search event tracking (backend analytics)</li>
            <li>Multi-field boosting for search results</li>
            <li>Product filtering by category, brand, and price</li>
          </ul>
        </div>
      </div>

      {/* Search Interface */}
      <Card style={{ marginBottom: '24px' }}>
        <CardHeader
          header={
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Search24Regular />
              <Text size={500} weight="semibold">Search Products</Text>
            </div>
          }
        />
        <div style={{ padding: '0 16px 16px' }}>
          <div style={{ position: 'relative', marginBottom: '16px' }}>
            <Input
              size="large"
              placeholder="Search for products, brands, categories..."
              value={searchQuery}
              onChange={(_, data) => {
                setSearchQuery(data.value);
                handleAutocomplete(data.value);
              }}
              onKeyPress={handleKeyPress}
              contentAfter={
                <Button 
                  appearance="primary" 
                  onClick={handleSearch}
                >
                  {searchQuery.trim() ? 'Search' : 'Show All'}
                </Button>
              }
              style={{ width: '100%' }}
            />
            
            {/* Autocomplete Dropdown */}
            {showAutocomplete && autocomplete && (autocomplete.suggestions.length > 0 || autocomplete.products.length > 0) && (
              <Card
                style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  zIndex: 1000,
                  maxHeight: '300px',
                  overflowY: 'auto',
                  marginTop: '4px',
                }}
              >
                {autocomplete.suggestions.length > 0 && (
                  <div style={{ padding: '12px' }}>
                    <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '8px', display: 'block' }}>
                      Suggestions
                    </Text>
                    {autocomplete.suggestions.map((suggestion, index) => (
                      <div
                        key={index}
                        style={{
                          padding: '8px',
                          cursor: 'pointer',
                          borderRadius: '4px',
                          '&:hover': { backgroundColor: '#f3f2f1' }
                        }}
                        onClick={() => {
                          setSearchQuery(suggestion);
                          setShowAutocomplete(false);
                        }}
                      >
                        <Text size={300}>{suggestion}</Text>
                      </div>
                    ))}
                  </div>
                )}
                
                {autocomplete.products.length > 0 && (
                  <div style={{ padding: '12px', borderTop: '1px solid #e1e1e1' }}>
                    <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '8px', display: 'block' }}>
                      Products
                    </Text>
                    {autocomplete.products.slice(0, 3).map((product) => (
                      <div
                        key={product.id}
                        style={{
                          padding: '8px',
                          cursor: 'pointer',
                          borderRadius: '4px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                        onClick={() => {
                          setSearchQuery(product.name);
                          setShowAutocomplete(false);
                        }}
                      >
                        <div>
                          <Text size={300} weight="semibold">{product.name}</Text>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            {product.category}
                          </Text>
                        </div>
                        <Text size={300} weight="semibold" style={{ color: '#0078d4' }}>
                          {formatPrice(product.price)}
                        </Text>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            )}
          </div>

          {/* Advanced Filters */}
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <Field label="Category">
              <Dropdown
                placeholder="All Categories"
                value={selectedCategory === 'all' ? 'All Categories' : selectedCategory}
                onOptionSelect={(_, data) => setSelectedCategory(data.optionValue || 'all')}
              >
                <Option value="all">All Categories</Option>
                <Option value="Electronics">Electronics</Option>
                <Option value="Clothing">Clothing</Option>
                <Option value="Books">Books</Option>
                <Option value="Home & Garden">Home & Garden</Option>
                <Option value="Sports">Sports</Option>
              </Dropdown>
            </Field>

            <Field label="Brand">
              <Dropdown
                placeholder="All Brands"
                value={selectedBrand === 'all' ? 'All Brands' : selectedBrand}
                onOptionSelect={(_, data) => setSelectedBrand(data.optionValue || 'all')}
              >
                <Option value="all">All Brands</Option>
                <Option value="TechCorp">TechCorp</Option>
                <Option value="StyleBrand">StyleBrand</Option>
                <Option value="BookPublisher">BookPublisher</Option>
                <Option value="HomeMaker">HomeMaker</Option>
                <Option value="SportsCo">SportsCo</Option>
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

            <Field label="Min Rating">
              <Dropdown
                placeholder="Any Rating"
                value={minRating?.toString() || ''}
                onOptionSelect={(_, data) => setMinRating(data.optionValue ? parseInt(data.optionValue) : null)}
              >
                <Option value="">Any Rating</Option>
                <Option value="4">4+ Stars</Option>
                <Option value="3">3+ Stars</Option>
                <Option value="2">2+ Stars</Option>
              </Dropdown>
            </Field>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Checkbox
                label="In stock only"
                checked={inStockOnly}
                onChange={(_, data) => setInStockOnly(data.checked)}
              />
              <Checkbox
                label="Show aggregations"
                checked={includeAggregations}
                onChange={(_, data) => setIncludeAggregations(data.checked)}
              />
            </div>

            <Button appearance="secondary" onClick={clearFilters}>
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {/* Search Results */}
      {state.loading ? (
        <div className="loading-container">
          <Spinner size="large" label="Searching..." />
        </div>
      ) : state.error ? (
        <div className="error-container">
          <Text size={500} style={{ color: '#d13438' }}>{state.error}</Text>
        </div>
      ) : searchResults ? (
        <div>
          {/* Search Stats */}
          <Card style={{ marginBottom: '24px' }}>
            <div style={{ padding: '16px', display: 'flex', gap: '24px', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target24Regular />
                <Text size={400} weight="semibold">
                  {searchResults.total_hits} results found
                </Text>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Timer24Regular />
                <Text size={300} style={{ color: '#605e5c' }}>
                  Search took {searchResults.took}ms
                </Text>
              </div>
              <Text size={300} style={{ color: '#605e5c' }}>
                Query: "{searchResults.query}"
              </Text>
            </div>
          </Card>

          <div style={{ display: 'grid', gridTemplateColumns: includeAggregations && searchResults.aggregations ? '250px 1fr' : '1fr', gap: '24px' }}>
            {/* Facets/Aggregations */}
            {includeAggregations && searchResults.aggregations && (
              <div>
                <Card>
                  <CardHeader
                    header={
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Filter24Regular />
                        <Text size={500} weight="semibold">Refine Results</Text>
                      </div>
                    }
                  />
                  <div style={{ padding: '0 16px 16px' }}>
                    {Object.entries(searchResults.aggregations).map(([key, buckets]) => (
                      <div key={key} style={{ marginBottom: '16px' }}>
                        <Text size={400} weight="semibold" style={{ marginBottom: '8px', display: 'block', textTransform: 'capitalize' }}>
                          {key.replace('_', ' ')}
                        </Text>
                        {buckets.slice(0, 5).map((bucket) => (
                          <div key={bucket.key} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                            <Text size={300}>{bucket.key}</Text>
                            <Badge appearance="tint" size="small">{bucket.count}</Badge>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}

            {/* Results */}
            <div>
              {searchResults.results.length === 0 ? (
                <Card>
                  <div style={{ padding: '32px', textAlign: 'center' }}>
                    <Text size={500}>No products found</Text>
                    {searchResults.suggestions && searchResults.suggestions.length > 0 && (
                      <div style={{ marginTop: '16px' }}>
                        <Text size={400} style={{ marginBottom: '8px', display: 'block' }}>
                          Did you mean:
                        </Text>
                        {searchResults.suggestions.map((suggestion, index) => (
                          <Button
                            key={index}
                            appearance="secondary"
                            size="small"
                            style={{ margin: '0 4px 4px 0' }}
                            onClick={() => {
                              setSearchQuery(suggestion);
                              handleSearch();
                            }}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                </Card>
              ) : (
                <div className="product-grid">
                  {searchResults.results.map((product) => (
                    <Card key={product.id} className="product-card">
                      <div 
                        className="product-image"
                        style={{
                          backgroundImage: product.thumbnail_url ? `url(${product.thumbnail_url})` : 'none',
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          backgroundRepeat: 'no-repeat'
                        }}
                      >
                        {!product.thumbnail_url && <Search24Regular />}
                      </div>
                      <div className="product-info">
                        <Text className="product-name">{product.name}</Text>
                        <Text className="product-description">{product.description}</Text>
                        
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <Badge appearance="tint" color="brand">
                            {product.category}
                          </Badge>
                          <Text size={300} style={{ color: '#605e5c' }}>
                            {product.brand}
                          </Text>
                        </div>

                        <Text className="product-price">{formatPrice(product.price)}</Text>
                        
                        <div className="product-rating">
                          <div style={{ display: 'flex' }}>
                            {renderStars(Math.round(product.rating || 0))}
                          </div>
                          <Text size={300}>
                            {(product.rating || 0).toFixed(1)} ({product.review_count} reviews)
                          </Text>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <Badge 
                              appearance="tint" 
                              color={product.stock_quantity > 0 ? 'success' : 'danger'}
                              size="small"
                            >
                              {product.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}
                            </Badge>
                            <Badge appearance="tint" color="subtle" size="small">
                              Score: {product.score.toFixed(2)}
                            </Badge>
                          </div>
                          <Link to={`/products/${product.id}`} style={{ textDecoration: 'none' }}>
                            <Button
                              appearance="primary"
                              size="small"
                              onClick={() => {
                                // Track click
                                if (state.currentUser) {
                                  elasticService.trackSearchClick({
                                    query: searchResults.query,
                                    results_count: searchResults.total_hits,
                                    user_id: state.currentUser.id,
                                    clicked_product_id: product.id,
                                    clicked_position: searchResults.results.indexOf(product) + 1,
                                  });
                                }
                              }}
                            >
                              View Details
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}

              {/* Pagination */}
              {searchResults.results.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <Text size={400} style={{ color: '#605e5c' }}>
                      Showing {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, searchResults.total_hits)} of {searchResults.total_hits} results
                    </Text>
                    <Text size={300} style={{ color: '#605e5c' }}>
                      Page {currentPage} of {Math.ceil(searchResults.total_hits / pageSize)}
                    </Text>
                  </div>

                  {Math.ceil(searchResults.total_hits / pageSize) > 1 && (
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center' }}>
                      <Button
                        appearance="secondary"
                        disabled={currentPage === 1}
                        onClick={() => handlePageChange(currentPage - 1)}
                      >
                        Previous
                      </Button>

                      {Array.from({ length: Math.min(5, Math.ceil(searchResults.total_hits / pageSize)) }, (_, i) => {
                        const page = i + 1;
                        return (
                          <Button
                            key={page}
                            appearance={currentPage === page ? "primary" : "secondary"}
                            onClick={() => handlePageChange(page)}
                          >
                            {page}
                          </Button>
                        );
                      })}

                      {Math.ceil(searchResults.total_hits / pageSize) > 5 && currentPage < Math.ceil(searchResults.total_hits / pageSize) - 2 && (
                        <>
                          <Text>...</Text>
                          <Button
                            appearance="secondary"
                            onClick={() => handlePageChange(Math.ceil(searchResults.total_hits / pageSize))}
                          >
                            {Math.ceil(searchResults.total_hits / pageSize)}
                          </Button>
                        </>
                      )}

                      <Button
                        appearance="secondary"
                        disabled={currentPage === Math.ceil(searchResults.total_hits / pageSize)}
                        onClick={() => handlePageChange(currentPage + 1)}
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <Card>
          <div style={{ padding: '32px', textAlign: 'center' }}>
            <Search24Regular style={{ fontSize: '48px', color: '#605e5c', marginBottom: '16px' }} />
            <Text size={500} style={{ color: '#605e5c' }}>
              Enter a search term to find products
            </Text>
          </div>
        </Card>
      )}
    </div>
  );
};

export default SearchPage;