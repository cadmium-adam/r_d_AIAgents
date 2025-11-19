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
  Person24Regular,
  Eye24Regular,
  Cart24Regular,
  Payment24Regular,
  Search24Regular,
  ArrowClockwise24Regular,
  Filter24Regular,
} from '@fluentui/react-icons';

interface UserBehavior {
  _id: string;
  user_id: number;
  session_id: string;
  event_type: string;
  timestamp: string;
  page_url: string;
  device_info: {
    type: string;
    os: string;
    browser: string;
  };
  product_id?: number;
  search_query?: string;
  filters?: {
    category?: string;
    price_range?: string;
    brand?: string;
  };
  order_total?: number;
  items_count?: number;
}

const UserBehaviorPage: React.FC = () => {
  const [behaviors, setBehaviors] = useState<UserBehavior[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  const [userFilter, setUserFilter] = useState<string>('all');

  useEffect(() => {
    loadBehaviors();
  }, []);

  const loadBehaviors = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8003/user-behavior?size=100');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setBehaviors(data.behaviors || []);
    } catch (error) {
      console.error('Failed to load user behavior:', error);
      setError('Failed to load user behavior data');
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'page_view':
        return <Eye24Regular />;
      case 'product_view':
        return <Person24Regular />;
      case 'add_to_cart':
        return <Cart24Regular />;
      case 'purchase':
        return <Payment24Regular />;
      case 'search':
        return <Search24Regular />;
      default:
        return <Person24Regular />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'page_view':
        return 'subtle';
      case 'product_view':
        return 'informative';
      case 'add_to_cart':
        return 'warning';
      case 'purchase':
        return 'success';
      case 'search':
        return 'brand';
      default:
        return 'subtle';
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const filteredBehaviors = behaviors.filter(behavior => {
    if (eventTypeFilter !== 'all' && behavior.event_type !== eventTypeFilter) {
      return false;
    }
    if (userFilter !== 'all' && behavior.user_id.toString() !== userFilter) {
      return false;
    }
    return true;
  });

  const uniqueUsers = [...new Set(behaviors.map(b => b.user_id))].sort((a, b) => a - b);
  const eventTypes = [...new Set(behaviors.map(b => b.event_type))];

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Person24Regular style={{ fontSize: '32px', color: '#005571' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              User Behavior Tracking
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Elasticsearch index: user_behavior - Detailed user interaction events and behavioral analytics
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Person24Regular />
            Elasticsearch User Behavior Features
          </div>
          <div className="database-description">
            This index captures granular user interactions, showcasing Elasticsearch's strength in real-time event search and behavioral analytics.
          </div>
          <ul className="feature-list">
            <li>Real-time event searching and filtering capabilities</li>
            <li>Aggregation support for behavioral analytics</li>
            <li>Time-based queries for user journey analysis</li>
            <li>Full-text search on user queries and interactions</li>
            <li>Device and context filtering for segmentation</li>
            <li>High-performance event stream processing</li>
          </ul>
        </div>
      </div>

      {/* Behavior Data */}
      <Card>
        <CardHeader
          header={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Person24Regular />
                <Text size={600} weight="semibold">User Behavior Events</Text>
                <Badge appearance="tint" color="success">Elasticsearch Index</Badge>
              </div>
              <Button 
                appearance="secondary" 
                icon={<ArrowClockwise24Regular />}
                onClick={loadBehaviors}
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
              <Spinner size="large" label="Loading user behavior data..." />
            </div>
          ) : error ? (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#d13438' }}>{error}</Text>
            </div>
          ) : behaviors.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#605e5c' }}>No user behavior data found</Text>
              <Text size={400} style={{ color: '#605e5c', marginTop: '8px', display: 'block' }}>
                Behavior events will appear here as users interact with the application
              </Text>
            </div>
          ) : (
            <>
              {/* Filters */}
              <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'flex-end' }}>
                <Field label="Event Type">
                  <Dropdown
                    value={eventTypeFilter === 'all' ? 'All Events' : eventTypeFilter.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    onOptionSelect={(_, data) => setEventTypeFilter(data.optionValue || 'all')}
                  >
                    <Option value="all">All Events</Option>
                    {eventTypes.map(type => (
                      <Option key={type} value={type}>
                        {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
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
                    setEventTypeFilter('all');
                    setUserFilter('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <Text size={400} style={{ color: '#605e5c' }}>
                  Showing {filteredBehaviors.length} of {behaviors.length} behavior events
                </Text>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>Event</TableHeaderCell>
                    <TableHeaderCell>User</TableHeaderCell>
                    <TableHeaderCell>Timestamp</TableHeaderCell>
                    <TableHeaderCell>Page/Context</TableHeaderCell>
                    <TableHeaderCell>Device</TableHeaderCell>
                    <TableHeaderCell>Details</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredBehaviors.slice(0, 50).map((behavior) => (
                    <TableRow key={behavior._id}>
                      <TableCell>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          {getEventIcon(behavior.event_type)}
                          <Badge 
                            appearance="tint" 
                            color={getEventColor(behavior.event_type)}
                          >
                            {behavior.event_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge appearance="tint" color="informative">
                          User {behavior.user_id}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Text size={300}>
                          {formatDateTime(behavior.timestamp)}
                        </Text>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} weight="semibold">
                            {behavior.page_url?.split('/').pop() || 'Unknown'}
                          </Text>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            {behavior.page_url}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300}>
                            {behavior.device_info?.type || 'Unknown'}
                          </Text>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            {behavior.device_info?.browser}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          {behavior.search_query && (
                            <Text size={300} style={{ display: 'block' }}>
                              🔍 "{behavior.search_query}"
                            </Text>
                          )}
                          {behavior.product_id && (
                            <Text size={300} style={{ display: 'block' }}>
                              📦 Product {behavior.product_id}
                            </Text>
                          )}
                          {behavior.order_total && (
                            <Text size={300} style={{ display: 'block', color: '#0078d4' }}>
                              💰 {formatCurrency(behavior.order_total)}
                            </Text>
                          )}
                          {behavior.items_count && (
                            <Text size={300} style={{ display: 'block' }}>
                              🛒 {behavior.items_count} items
                            </Text>
                          )}
                          {behavior.filters && (
                            <div>
                              {behavior.filters.category && (
                                <Badge appearance="tint" size="small" style={{ margin: '2px' }}>
                                  {behavior.filters.category}
                                </Badge>
                              )}
                              {behavior.filters.brand && (
                                <Badge appearance="tint" size="small" style={{ margin: '2px' }}>
                                  {behavior.filters.brand}
                                </Badge>
                              )}
                              {behavior.filters.price_range && (
                                <Badge appearance="tint" size="small" style={{ margin: '2px' }}>
                                  {behavior.filters.price_range}
                                </Badge>
                              )}
                            </div>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {filteredBehaviors.length > 50 && (
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Showing first 50 of {filteredBehaviors.length} filtered events
                  </Text>
                </div>
              )}
            </>
          )}

          <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
            <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
              Event Types & Use Cases:
            </Text>
            <Text size={300} style={{ color: '#605e5c' }}>
              • <strong>page_view</strong>: General navigation tracking for analytics<br/>
              • <strong>product_view</strong>: Product interest and engagement measurement<br/>
              • <strong>add_to_cart</strong>: Purchase intent tracking and conversion funnel analysis<br/>
              • <strong>search</strong>: Query analysis and search optimization<br/>
              • <strong>purchase</strong>: Conversion tracking with order value and item count
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default UserBehaviorPage;