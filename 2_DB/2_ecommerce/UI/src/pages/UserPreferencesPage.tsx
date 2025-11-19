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
  Brain24Regular,
  Person24Regular,
  Target24Regular,
  ArrowClockwise24Regular,
  Filter24Regular,
} from '@fluentui/react-icons';
import { qdrantService } from '../services/api';
import { useApp } from '../components/AppProvider';

interface UserPreference {
  user_id: number;
  email: string;
  preferences: {
    categories: string[];
    brands: string[];
    price_range: string;
  };
  purchase_history: {
    total_orders: number;
    total_spent: number;
    avg_order_value: number;
  };
  demographics: {
    age_group: string;
    location: string;
  };
  top_category: string;
  similarity_score?: number;
}

const UserPreferencesPage: React.FC = () => {
  const { state } = useApp();
  const [preferences, setPreferences] = useState<UserPreference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>('all');

  useEffect(() => {
    loadUserPreferences();
  }, []);

  const loadUserPreferences = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch from Qdrant API through service
      const collectionsData = await qdrantService.getCollectionsInfo();
      
      // Since we don't have a direct endpoint, we'll create mock data based on the current user
      const mockPreferences: UserPreference[] = [
        {
          user_id: 1,
          email: 'john.smith@email.com',
          preferences: {
            categories: ['Electronics', 'Gaming'],
            brands: ['TechCorp', 'GameMaster'],
            price_range: '$500-$2000'
          },
          purchase_history: {
            total_orders: 15,
            total_spent: 12750.00,
            avg_order_value: 850.00
          },
          demographics: {
            age_group: '25-34',
            location: 'San Francisco, CA'
          },
          top_category: 'Electronics'
        },
        {
          user_id: 2,
          email: 'sarah.wilson@email.com',
          preferences: {
            categories: ['Clothing', 'Beauty'],
            brands: ['FashionBrand', 'BeautyLux'],
            price_range: '$50-$500'
          },
          purchase_history: {
            total_orders: 8,
            total_spent: 2400.00,
            avg_order_value: 300.00
          },
          demographics: {
            age_group: '30-39',
            location: 'New York, NY'
          },
          top_category: 'Clothing'
        },
        {
          user_id: 3,
          email: 'mike.johnson@email.com',
          preferences: {
            categories: ['Sports', 'Outdoor'],
            brands: ['SportsPro', 'OutdoorGear'],
            price_range: '$100-$1000'
          },
          purchase_history: {
            total_orders: 22,
            total_spent: 8900.00,
            avg_order_value: 404.55
          },
          demographics: {
            age_group: '28-35',
            location: 'Denver, CO'
          },
          top_category: 'Sports'
        }
      ];
      
      setPreferences(mockPreferences);
    } catch (error) {
      console.error('Failed to load user preferences:', error);
      setError('Failed to load user preference embeddings');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getAgeGroupColor = (ageGroup: string) => {
    switch (ageGroup) {
      case '18-24':
        return 'success';
      case '25-34':
        return 'informative';
      case '30-39':
        return 'warning';
      case '40+':
        return 'important';
      default:
        return 'subtle';
    }
  };

  const filteredPreferences = preferences.filter(pref => {
    if (categoryFilter !== 'all' && !pref.preferences.categories.includes(categoryFilter)) {
      return false;
    }
    if (ageGroupFilter !== 'all' && pref.demographics.age_group !== ageGroupFilter) {
      return false;
    }
    return true;
  });

  const uniqueCategories = [...new Set(preferences.flatMap(p => p.preferences.categories))];
  const uniqueAgeGroups = [...new Set(preferences.map(p => p.demographics.age_group))];

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Brain24Regular style={{ fontSize: '32px', color: '#dc382d' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              User Preference Embeddings
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Qdrant collection: user_preference_embeddings - AI-generated user preference vectors for personalized recommendations
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Brain24Regular />
            Qdrant User Preference Features
          </div>
          <div className="database-description">
            This collection demonstrates how user preferences are converted into high-dimensional vectors for AI-powered personalization.
          </div>
          <ul className="feature-list">
            <li>384-dimensional preference vectors using all-MiniLM-L6-v2 model</li>
            <li>Cosine similarity matching for user-to-user recommendations</li>
            <li>Purchase history and behavioral data integration</li>
            <li>Demographic and location-based preference modeling</li>
            <li>Real-time preference updates based on user interactions</li>
            <li>Vector clustering for user segmentation and targeting</li>
          </ul>
        </div>
      </div>

      {/* User Preferences Data */}
      <Card>
        <CardHeader
          header={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Person24Regular />
                <Text size={600} weight="semibold">User Preference Vectors</Text>
                <Badge appearance="tint" color="danger">Qdrant Collection</Badge>
              </div>
              <Button 
                appearance="secondary" 
                icon={<ArrowClockwise24Regular />}
                onClick={loadUserPreferences}
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
              <Spinner size="large" label="Loading user preference embeddings..." />
            </div>
          ) : error ? (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#d13438' }}>{error}</Text>
            </div>
          ) : preferences.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#605e5c' }}>No user preference data found</Text>
              <Text size={400} style={{ color: '#605e5c', marginTop: '8px', display: 'block' }}>
                User preference vectors will be generated as users interact with the system
              </Text>
            </div>
          ) : (
            <>
              {/* Filters */}
              <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'flex-end' }}>
                <Field label="Category Preference">
                  <Dropdown
                    value={categoryFilter === 'all' ? 'All Categories' : categoryFilter}
                    onOptionSelect={(_, data) => setCategoryFilter(data.optionValue || 'all')}
                  >
                    <Option value="all">All Categories</Option>
                    {uniqueCategories.map(category => (
                      <Option key={category} value={category}>
                        {category}
                      </Option>
                    ))}
                  </Dropdown>
                </Field>
                
                <Field label="Age Group">
                  <Dropdown
                    value={ageGroupFilter === 'all' ? 'All Ages' : ageGroupFilter}
                    onOptionSelect={(_, data) => setAgeGroupFilter(data.optionValue || 'all')}
                  >
                    <Option value="all">All Ages</Option>
                    {uniqueAgeGroups.map(ageGroup => (
                      <Option key={ageGroup} value={ageGroup}>
                        {ageGroup}
                      </Option>
                    ))}
                  </Dropdown>
                </Field>

                <Button 
                  appearance="secondary" 
                  icon={<Filter24Regular />}
                  onClick={() => {
                    setCategoryFilter('all');
                    setAgeGroupFilter('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <Text size={400} style={{ color: '#605e5c' }}>
                  Showing {filteredPreferences.length} of {preferences.length} user preference profiles
                </Text>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>User Profile</TableHeaderCell>
                    <TableHeaderCell>Preferences</TableHeaderCell>
                    <TableHeaderCell>Purchase History</TableHeaderCell>
                    <TableHeaderCell>Demographics</TableHeaderCell>
                    <TableHeaderCell>Vector Insights</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPreferences.map((userPref) => (
                    <TableRow key={userPref.user_id}>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <Person24Regular style={{ fontSize: '16px' }} />
                            <Text size={300} weight="semibold">
                              User {userPref.user_id}
                            </Text>
                          </div>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            {userPref.email}
                          </Text>
                          <Badge 
                            appearance="tint" 
                            color="brand"
                            size="small"
                            style={{ marginTop: '4px' }}
                          >
                            Top: {userPref.top_category}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} weight="semibold" style={{ marginBottom: '4px', display: 'block' }}>
                            Categories:
                          </Text>
                          <div style={{ marginBottom: '8px' }}>
                            {userPref.preferences.categories.map((category, idx) => (
                              <Badge 
                                key={idx}
                                appearance="tint" 
                                size="small" 
                                style={{ margin: '2px' }}
                              >
                                {category}
                              </Badge>
                            ))}
                          </div>
                          <Text size={300} weight="semibold" style={{ marginBottom: '4px', display: 'block' }}>
                            Brands:
                          </Text>
                          <div style={{ marginBottom: '8px' }}>
                            {userPref.preferences.brands.map((brand, idx) => (
                              <Badge 
                                key={idx}
                                appearance="tint" 
                                color="warning"
                                size="small" 
                                style={{ margin: '2px' }}
                              >
                                {brand}
                              </Badge>
                            ))}
                          </div>
                          <Text size={200} style={{ color: '#605e5c' }}>
                            Price Range: {userPref.preferences.price_range}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} style={{ display: 'block', marginBottom: '4px' }}>
                            📦 {userPref.purchase_history.total_orders} orders
                          </Text>
                          <Text size={300} style={{ display: 'block', marginBottom: '4px' }}>
                            💰 {formatCurrency(userPref.purchase_history.total_spent)} total
                          </Text>
                          <Text size={300} style={{ display: 'block', color: '#0078d4' }}>
                            📊 {formatCurrency(userPref.purchase_history.avg_order_value)} avg
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <Badge 
                              appearance="tint" 
                              color={getAgeGroupColor(userPref.demographics.age_group)}
                              size="small"
                            >
                              {userPref.demographics.age_group}
                            </Badge>
                          </div>
                          <Text size={300} style={{ display: 'block' }}>
                            📍 {userPref.demographics.location}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={200} style={{ color: '#605e5c', display: 'block', marginBottom: '4px' }}>
                            Vector Dimensions:
                          </Text>
                          <Badge appearance="tint" color="success" size="small">
                            384D Embedding
                          </Badge>
                          <Text size={200} style={{ color: '#605e5c', display: 'block', marginTop: '4px' }}>
                            Model: all-MiniLM-L6-v2
                          </Text>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            Distance: Cosine Similarity
                          </Text>
                          {state.currentUser && userPref.user_id === state.currentUser.id && (
                            <Badge 
                              appearance="tint" 
                              color="important" 
                              size="small"
                              style={{ marginTop: '4px' }}
                            >
                              Current User
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          )}

          <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
            <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
              Vector Embedding Process:
            </Text>
            <Text size={300} style={{ color: '#605e5c' }}>
              • <strong>Data Collection</strong>: User interactions, purchases, browsing history, and explicit preferences<br/>
              • <strong>Feature Engineering</strong>: Combine categorical, numerical, and textual user data<br/>
              • <strong>Embedding Generation</strong>: Transform user profile into 384-dimensional vector using SentenceTransformers<br/>
              • <strong>Similarity Matching</strong>: Use cosine distance to find users with similar preferences<br/>
              • <strong>Personalization</strong>: Generate recommendations based on similar users' purchase patterns
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default UserPreferencesPage;