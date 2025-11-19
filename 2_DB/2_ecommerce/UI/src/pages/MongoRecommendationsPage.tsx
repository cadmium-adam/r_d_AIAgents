import React, { useEffect, useState } from 'react';
import {
  Text,
  Card,
  CardHeader,
  Badge,
  Spinner,
  Button,
  Table,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  Dropdown,
  Option,
  Field,
} from '@fluentui/react-components';
import {
  Target24Regular,
  Brain24Regular,
  Eye24Regular,
  Star24Filled,
  Payment24Regular,
  ArrowClockwise24Regular,
  Filter24Regular,
} from '@fluentui/react-icons';

interface Recommendation {
  _id: string;
  user_id: number;
  algorithm: string;
  products: Array<{
    product_id: number;
    score: number;
    reason: string;
  }>;
  page_type: string;
  user_segment: string;
  session_activity: string[];
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number;
  created_at: string;
  expires_at: string;
}

const MongoRecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [algorithmFilter, setAlgorithmFilter] = useState<string>('all');
  const [pageTypeFilter, setPageTypeFilter] = useState<string>('all');
  const [userFilter, setUserFilter] = useState<string>('all');

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8002/recommendations');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
      setError('Failed to load recommendations data');
    } finally {
      setLoading(false);
    }
  };

  const getAlgorithmIcon = (algorithm: string) => {
    switch (algorithm) {
      case 'collaborative':
        return <Target24Regular />;
      case 'content_based':
        return <Brain24Regular />;
      case 'hybrid':
        return <Star24Filled />;
      default:
        return <Brain24Regular />;
    }
  };

  const getAlgorithmColor = (algorithm: string) => {
    switch (algorithm) {
      case 'collaborative':
        return 'success';
      case 'content_based':
        return 'brand';
      case 'hybrid':
        return 'warning';
      default:
        return 'subtle';
    }
  };

  const getPageTypeColor = (pageType: string) => {
    switch (pageType) {
      case 'homepage':
        return 'brand';
      case 'product':
        return 'success';
      case 'cart':
        return 'warning';
      case 'checkout':
        return 'danger';
      default:
        return 'subtle';
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatPercentage = (value: number) => {
    if (isNaN(value) || value === null || value === undefined) {
      return '0.0%';
    }
    return `${(value * 100).toFixed(1)}%`;
  };

  const calculateConversionRate = (conversions: number, impressions: number) => {
    return impressions > 0 ? (conversions / impressions) * 100 : 0;
  };

  const filteredRecommendations = recommendations.filter(rec => {
    if (algorithmFilter !== 'all' && rec.algorithm !== algorithmFilter) {
      return false;
    }
    if (pageTypeFilter !== 'all' && rec.page_type !== pageTypeFilter) {
      return false;
    }
    if (userFilter !== 'all' && rec.user_id.toString() !== userFilter) {
      return false;
    }
    return true;
  });

  const uniqueUsers = [...new Set(recommendations.map(r => r.user_id))].sort((a, b) => a - b);
  const algorithms = [...new Set(recommendations.map(r => r.algorithm).filter(Boolean))];
  const pageTypes = [...new Set(recommendations.map(r => r.page_type).filter(Boolean))];

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Target24Regular style={{ fontSize: '32px', color: '#005571' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              AI Recommendations Data
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              MongoDB collection: recommendations - AI-generated product recommendations with performance tracking
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Target24Regular />
            MongoDB Recommendations Features
          </div>
          <div className="database-description">
            This collection showcases MongoDB's capability to store complex AI recommendation data with nested product arrays and performance metrics.
          </div>
          <ul className="feature-list">
            <li>Multi-algorithm recommendation storage (collaborative, content-based, hybrid, trending, seasonal)</li>
            <li>Nested product arrays with scores and reasoning</li>
            <li>Performance tracking with impressions, clicks, and conversions</li>
            <li>Context-aware recommendations by page type and user segment</li>
            <li>Session activity correlation for personalization</li>
            <li>TTL (Time To Live) support with expiration timestamps</li>
          </ul>
        </div>
      </div>

      {/* Recommendations Data */}
      <Card>
        <CardHeader
          header={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Target24Regular />
                <Text size={600} weight="semibold">Recommendation Campaigns</Text>
                <Badge appearance="tint" color="brand">MongoDB Collection</Badge>
              </div>
              <Button 
                appearance="secondary" 
                icon={<ArrowClockwise24Regular />}
                onClick={loadRecommendations}
                disabled={loading}
              >
                Refresh
              </Button>
            </div>
          }
        />
        <div style={{ padding: '0 16px 16px' }}>
          {loading ? (
            <div className="loading-container" style={{ padding: '40px' }}>
              <Spinner size="large" label="Loading recommendations data..." />
            </div>
          ) : error ? (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#d13438' }}>{error}</Text>
            </div>
          ) : recommendations.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#605e5c' }}>No recommendations data found</Text>
              <Text size={400} style={{ color: '#605e5c', marginTop: '8px', display: 'block' }}>
                AI-generated recommendations will appear here as they are created for users
              </Text>
            </div>
          ) : (
            <>
              {/* Filters */}
              <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'flex-end' }}>
                <Field label="Algorithm">
                  <Dropdown
                    value={algorithmFilter === 'all' ? 'All Algorithms' : algorithmFilter.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    onOptionSelect={(_, data) => setAlgorithmFilter(data.optionValue || 'all')}
                  >
                    <Option value="all">All Algorithms</Option>
                    {algorithms.map(algo => (
                      <Option key={algo} value={algo}>
                        {algo.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Option>
                    ))}
                  </Dropdown>
                </Field>
                
                <Field label="Page Type">
                  <Dropdown
                    value={pageTypeFilter === 'all' ? 'All Pages' : pageTypeFilter.replace(/\b\w/g, l => l.toUpperCase())}
                    onOptionSelect={(_, data) => setPageTypeFilter(data.optionValue || 'all')}
                  >
                    <Option value="all">All Pages</Option>
                    {pageTypes.map(type => (
                      <Option key={type} value={type}>
                        {type.replace(/\b\w/g, l => l.toUpperCase())}
                      </Option>
                    ))}
                  </Dropdown>
                </Field>

                <Field label="User">
                  <Dropdown
                    value={userFilter === 'all' ? 'All Users' : `User ${userFilter}`}
                    onOptionSelect={(_, data) => setUserFilter(data.optionValue || 'all')}
                  >
                    <Option value="all">All Users</Option>
                    {uniqueUsers.map(userId => (
                      <Option key={userId} value={userId.toString()}>
                        User {userId}
                      </Option>
                    ))}
                  </Dropdown>
                </Field>

                <Button 
                  appearance="secondary" 
                  icon={<Filter24Regular />}
                  onClick={() => {
                    setAlgorithmFilter('all');
                    setPageTypeFilter('all');
                    setUserFilter('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <Text size={400} style={{ color: '#605e5c' }}>
                  Showing {filteredRecommendations.length} of {recommendations.length} recommendation campaigns
                </Text>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>User & Context</TableHeaderCell>
                    <TableHeaderCell>Algorithm</TableHeaderCell>
                    <TableHeaderCell>Products</TableHeaderCell>
                    <TableHeaderCell>Performance</TableHeaderCell>
                    <TableHeaderCell>Engagement</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRecommendations.slice(0, 20).map((rec) => (
                    <TableRow key={rec._id}>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <Badge appearance="tint" color="informative">
                              User {rec.user_id}
                            </Badge>
                            <Badge 
                              appearance="tint" 
                              color={getPageTypeColor(rec.page_type)}
                              size="small"
                            >
                              {rec.page_type}
                            </Badge>
                          </div>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            Segment: {rec.user_segment}
                          </Text>
                          {rec.session_activity && rec.session_activity.length > 0 && (
                            <Text size={200} style={{ color: '#605e5c' }}>
                              Activity: {rec.session_activity.slice(0, 2).join(', ')}
                              {rec.session_activity.length > 2 && '...'}
                            </Text>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          {getAlgorithmIcon(rec.algorithm)}
                          <Badge 
                            appearance="tint" 
                            color={getAlgorithmColor(rec.algorithm)}
                          >
                            {rec.algorithm.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} weight="semibold" style={{ marginBottom: '4px', display: 'block' }}>
                            {rec.products?.length || 0} products
                          </Text>
                          {rec.products && rec.products.slice(0, 2).map((product, idx) => (
                            <div key={idx} style={{ marginBottom: '2px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Text size={200}>
                                  Product {product.product_id}
                                </Text>
                                <Badge appearance="tint" size="small" color="subtle">
                                  {product.score.toFixed(2)}
                                </Badge>
                              </div>
                              <Text size={200} style={{ color: '#605e5c', fontStyle: 'italic' }}>
                                {product.reason}
                              </Text>
                            </div>
                          ))}
                          {rec.products && rec.products.length > 2 && (
                            <Text size={200} style={{ color: '#605e5c' }}>
                              +{rec.products.length - 2} more...
                            </Text>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                            <Eye24Regular style={{ fontSize: '14px' }} />
                            <Text size={300}>
                              {rec.impressions} impressions
                            </Text>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                            <Star24Filled style={{ fontSize: '14px' }} />
                            <Text size={300}>
                              {rec.clicks} clicks
                            </Text>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Payment24Regular style={{ fontSize: '14px' }} />
                            <Text size={300}>
                              {rec.conversions} conversions
                            </Text>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} weight="semibold" style={{ color: '#0078d4', marginBottom: '4px', display: 'block' }}>
                            CTR: {formatPercentage(rec.ctr)}
                          </Text>
                          <Text size={300} style={{ color: '#0078d4' }}>
                            CVR: {formatPercentage(calculateConversionRate(rec.conversions, rec.impressions) / 100)}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            Created:
                          </Text>
                          <Text size={300} style={{ marginBottom: '4px', display: 'block' }}>
                            {formatDateTime(rec.created_at)}
                          </Text>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            Expires:
                          </Text>
                          <Text size={300}>
                            {formatDateTime(rec.expires_at)}
                          </Text>
                          {new Date(rec.expires_at) < new Date() && (
                            <Badge appearance="tint" color="danger" size="small" style={{ marginTop: '4px' }}>
                              Expired
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {filteredRecommendations.length > 20 && (
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Showing first 20 of {filteredRecommendations.length} filtered recommendations
                  </Text>
                </div>
              )}
            </>
          )}

          <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
            <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
              Recommendation Algorithm Types:
            </Text>
            <Text size={300} style={{ color: '#605e5c' }}>
              • <strong>Collaborative Filtering</strong>: Recommendations based on similar user behavior and preferences (uses embeddings)<br/>
              • <strong>Content-Based</strong>: Recommendations based on product features and user purchase history (uses embeddings)<br/>
              • <strong>Hybrid</strong>: Combined approach using both collaborative and content-based signals (uses embeddings)<br/>
              • <strong>Trending</strong>: Popular products across all users regardless of personal preferences (no embeddings)<br/>
              • <strong>Seasonal</strong>: Time-based recommendations for holidays, seasons, events (no embeddings)<br/><br/>
              <strong>Additional Features:</strong><br/>
              • Performance Tracking: Real-time metrics for impressions, clicks, CTR, and conversions<br/>
              • Context Awareness: Page-specific recommendations with user segmentation
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default MongoRecommendationsPage;