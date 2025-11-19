import React, { useEffect, useState } from 'react';
import {
  Text,
  Button,
  Card,
  CardHeader,
  Badge,
  Spinner,
} from '@fluentui/react-components';
import {
  Database24Regular,
  Server24Regular,
  Search24Regular,
  Brain24Regular,
  ChevronRight24Regular,
  Sparkle24Regular,
  Star24Filled,
  Star24Regular,
  Cart24Regular,
} from '@fluentui/react-icons';
import { Link } from 'react-router-dom';
import { healthService, qdrantService } from '../services/api';
import { useApp } from '../components/AppProvider';
import type { DatabaseStatus, RecommendationResponse } from '../types';

const HomePage: React.FC = () => {
  const { state } = useApp();
  const [databaseStatuses, setDatabaseStatuses] = useState<DatabaseStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [personalizedRecs, setPersonalizedRecs] = useState<RecommendationResponse | null>(null);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const checkDatabases = async () => {
      try {
        const statuses = await healthService.checkAllDatabases();
        setDatabaseStatuses(statuses);
      } catch (error) {
        console.error('Failed to check database statuses:', error);
      } finally {
        setLoading(false);
      }
    };

    checkDatabases();
  }, []);

  useEffect(() => {
    if (state.currentUser) {
      loadPersonalizedRecommendations();
    }
  }, [state.currentUser]);

  const loadPersonalizedRecommendations = async () => {
    if (!state.currentUser) return;
    
    setLoadingRecs(true);
    try {
      const recommendations = await qdrantService.getPersonalizedRecommendations(state.currentUser.id, {
        algorithm: 'hybrid',
        limit: 6,
      });
      setPersonalizedRecs(recommendations);
    } catch (error) {
      console.error('Failed to load personalized recommendations:', error);
      // Don't show error for recommendations failure on homepage
    } finally {
      setLoadingRecs(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'error': return 'danger';
      default: return 'warning';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✓';
      case 'error': return '✗';
      default: return '⚠';
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        i <= rating ? (
          <Star24Filled key={i} style={{ color: '#ffc83d', fontSize: '16px' }} />
        ) : (
          <Star24Regular key={i} style={{ color: '#d1d1d1', fontSize: '16px' }} />
        )
      );
    }
    return stars;
  };

  const databaseInfo = [
    {
      name: 'MSSQL',
      icon: <Database24Regular />,
      description: 'Core Business Data & Transactions',
      features: ['Product catalog', 'User accounts', 'Orders & payments', 'Financial reporting'],
      path: '/products',
      color: '#0078d4'
    },
    {
      name: 'MongoDB',
      icon: <Server24Regular />,
      description: 'Flexible Schema & Real-time Data',
      features: ['User sessions', 'Product reviews', 'Shopping cart', 'Real-time analytics'],
      path: '/cart',
      color: '#47a248'
    },
    {
      name: 'Elasticsearch',
      icon: <Search24Regular />,
      description: 'Search & Discovery',
      features: ['Product search', 'Autocomplete', 'Search analytics', 'Faceted navigation'],
      path: '/search',
      color: '#005571'
    },
    {
      name: 'Qdrant',
      icon: <Brain24Regular />,
      description: 'AI-Powered Features',
      features: ['Product similarity', 'Personalized recommendations', 'Semantic search'],
      path: '/recommendations',
      color: '#dc382d'
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '48px', padding: '40px 0' }}>
        <Text as="h1" size={900} weight="semibold" style={{ marginBottom: '16px' }}>
          Multi-Database E-commerce Platform
        </Text>
        <Text size={500} style={{ color: '#605e5c', maxWidth: '800px', margin: '0 auto', display: 'block' }}>
          Discover how different database technologies work together in a real-world e-commerce scenario.
          Each database serves specific use cases where it excels.
        </Text>
      </div>

      {/* Database Status */}
      <Card style={{ marginBottom: '32px' }}>
        <CardHeader
          header={
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Server24Regular />
              <Text size={600} weight="semibold">Database Status</Text>
            </div>
          }
        />
        <div style={{ padding: '0 16px 16px' }}>
          {loading ? (
            <div className="loading-container">
              <Spinner label="Checking database connections..." />
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {databaseStatuses.map((db) => (
                <div
                  key={db.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px',
                    border: '1px solid #e1e1e1',
                    borderRadius: '6px',
                    backgroundColor: '#fafafa'
                  }}
                >
                  <span style={{ fontSize: '18px' }}>{getStatusIcon(db.status)}</span>
                  <div style={{ flex: 1 }}>
                    <Text weight="semibold">{db.name}</Text>
                    <Badge appearance="tint" color={getStatusColor(db.status)} style={{ marginLeft: '8px' }}>
                      {db.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Personalized Recommendations */}
      {state.currentUser && (
        <Card style={{ marginBottom: '32px' }}>
          <CardHeader
            header={
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Sparkle24Regular style={{ color: '#dc382d', fontSize: '24px' }} />
                <div>
                  <Text size={600} weight="semibold">Recommended for You</Text>
                  <Text size={300} style={{ color: '#605e5c', display: 'block' }}>
                    Powered by AI vector embeddings - personalized just for {state.currentUser.first_name}
                  </Text>
                </div>
                <Badge appearance="tint" color="danger">Qdrant AI</Badge>
              </div>
            }
          />
          <div style={{ padding: '0 16px 16px' }}>
            {loadingRecs ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                <Spinner size="medium" label="Generating personalized recommendations..." />
              </div>
            ) : personalizedRecs && personalizedRecs.recommendations.length > 0 ? (
              <>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', 
                  gap: '16px',
                  marginBottom: '16px'
                }}>
                  {personalizedRecs.recommendations.map((product) => (
                    <Card key={product.id} style={{ cursor: 'pointer', transition: 'all 0.2s' }}>
                      <Link to={`/products/${product.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                        <div style={{ position: 'relative' }}>
                          <div style={{ 
                            height: '100px', 
                            backgroundColor: '#f3f2f1', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            marginBottom: '8px'
                          }}>
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
                                  e.currentTarget.parentElement!.innerHTML = '<div style="color: #605e5c; font-size: 20px;">✨</div>';
                                }}
                              />
                            ) : (
                              <Sparkle24Regular style={{ fontSize: '24px', color: '#605e5c' }} />
                            )}
                          </div>
                          <Badge 
                            appearance="tint" 
                            color="success" 
                            size="small"
                            style={{ 
                              position: 'absolute', 
                              top: '4px', 
                              right: '4px',
                              backgroundColor: 'rgba(255, 255, 255, 0.9)'
                            }}
                          >
                            {(product.similarity_score * 100).toFixed(0)}% match
                          </Badge>
                        </div>
                        <div style={{ padding: '8px' }}>
                          <Text size={300} weight="semibold" style={{ 
                            marginBottom: '4px', 
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}>
                            {product.name}
                          </Text>
                          
                          <Text size={300} weight="semibold" style={{ color: '#0078d4', marginBottom: '4px', display: 'block' }}>
                            {formatPrice(product.price)}
                          </Text>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                            {renderStars(product.rating)}
                          </div>

                          <Text size={200} style={{ 
                            color: '#605e5c',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}>
                            {product.recommendation_reason}
                          </Text>
                        </div>
                      </Link>
                    </Card>
                  ))}
                </div>
                <div style={{ textAlign: 'center' }}>
                  <Link to="/recommendations" style={{ textDecoration: 'none' }}>
                    <Button 
                      appearance="secondary" 
                      icon={<ChevronRight24Regular />}
                      iconPosition="after"
                    >
                      View All AI Recommendations
                    </Button>
                  </Link>
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#605e5c' }}>
                <Brain24Regular style={{ fontSize: '48px', marginBottom: '16px' }} />
                <Text size={400}>Building your personalized recommendations</Text>
                <Text size={300} style={{ marginTop: '8px', display: 'block' }}>
                  Browse some products to help our AI learn your preferences
                </Text>
                <Link to="/products" style={{ textDecoration: 'none' }}>
                  <Button 
                    appearance="primary" 
                    style={{ marginTop: '16px' }}
                    icon={<ChevronRight24Regular />}
                    iconPosition="after"
                  >
                    Explore Products
                  </Button>
                </Link>
              </div>
            )}

            <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
              <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
                How AI Personalization Works:
              </Text>
              <Text size={300} style={{ color: '#605e5c' }}>
                • <strong>Vector Embeddings</strong>: Your preferences are converted to high-dimensional vectors<br/>
                • <strong>Similarity Matching</strong>: AI finds products that match your unique preference profile<br/>
                • <strong>Real-time Learning</strong>: Recommendations improve as you browse and purchase
              </Text>
            </div>
          </div>
        </Card>
      )}

      {/* Database Architecture */}
      <div style={{ marginBottom: '32px' }}>
        <Text as="h2" size={700} weight="semibold" style={{ marginBottom: '24px' }}>
          Database Architecture
        </Text>
        <div className="grid-container grid-2-cols">
          {databaseInfo.map((db) => (
            <Card key={db.name} style={{ height: '100%' }}>
              <CardHeader
                header={
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ color: db.color, fontSize: '24px' }}>
                      {db.icon}
                    </div>
                    <div>
                      <Text size={600} weight="semibold">{db.name}</Text>
                      <Text size={300} style={{ color: '#605e5c', display: 'block' }}>
                        {db.description}
                      </Text>
                    </div>
                  </div>
                }
              />
              <div style={{ padding: '0 16px 16px' }}>
                <ul className="feature-list">
                  {db.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
                <Link to={db.path} style={{ textDecoration: 'none' }}>
                  <Button
                    appearance="primary"
                    icon={<ChevronRight24Regular />}
                    iconPosition="after"
                    style={{
                      marginTop: '12px',
                      backgroundColor: db.color,
                      borderColor: db.color
                    }}
                  >
                    Explore {db.name}
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>

    </div>
  );
};

export default HomePage;