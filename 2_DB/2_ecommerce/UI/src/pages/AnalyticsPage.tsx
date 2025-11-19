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
} from '@fluentui/react-components';
import {
  ChartMultiple24Regular,
  Calendar24Regular,
  People24Regular,
  ShoppingBag24Regular,
  Money24Regular,
  ArrowClockwise24Regular,
  ArrowUp24Regular,
} from '@fluentui/react-icons';

interface MongoAnalytics {
  _id: string;
  date: string;
  metric_type: string;
  unique_visitors: number;
  returning_visitors: number;
  new_visitors: number;
  page_views: number;
  sessions: number;
  bounce_rate: number;
  avg_session_duration: number;
  conversion_rate: number;
  revenue: number;
  orders: number;
  avg_order_value: number;
  top_products: Array<{
    product_id: number;
    name: string;
    views: number;
    sales: number;
  }>;
  top_categories: Array<{
    category: string;
    views: number;
    sales: number;
  }>;
  traffic_sources: {
    direct: number;
    search: number;
    social: number;
    referral: number;
  };
  device_breakdown: {
    desktop: number;
    mobile: number;
    tablet: number;
  };
}

const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<MongoAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8003/analytics?size=100');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setAnalytics(data.analytics || []);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setError('Failed to load analytics data');
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

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${Math.round(minutes)}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = Math.round(minutes % 60);
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getMetricTypeColor = (metricType: string) => {
    switch (metricType) {
      case 'daily':
        return 'success';
      case 'weekly':
        return 'warning';
      case 'monthly':
        return 'brand';
      default:
        return 'subtle';
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <ChartMultiple24Regular style={{ fontSize: '32px', color: '#005571' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              Analytics Dashboard
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Elasticsearch index: analytics - Daily aggregated metrics and business intelligence data
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <ChartMultiple24Regular />
            Elasticsearch Analytics Features
          </div>
          <div className="database-description">
            This index demonstrates Elasticsearch's powerful aggregation and time-series capabilities for analytics and business metrics.
          </div>
          <ul className="feature-list">
            <li>Time-series optimized storage with date histograms</li>
            <li>Fast aggregations for real-time dashboard queries</li>
            <li>Nested documents for top products and categories</li>
            <li>Multi-dimensional analytics with sub-aggregations</li>
            <li>Efficient date range queries and filtering</li>
            <li>Built-in support for percentiles and statistical analysis</li>
          </ul>
        </div>
      </div>

      {/* Analytics Data */}
      <Card>
        <CardHeader
          header={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <ChartMultiple24Regular />
                <Text size={600} weight="semibold">Analytics Metrics</Text>
                <Badge appearance="tint" color="success">Elasticsearch Index</Badge>
              </div>
              <Button 
                appearance="secondary" 
                icon={<ArrowClockwise24Regular />}
                onClick={loadAnalytics}
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
              <Spinner size="large" label="Loading analytics data..." />
            </div>
          ) : error ? (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#d13438' }}>{error}</Text>
            </div>
          ) : analytics.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#605e5c' }}>No analytics data found</Text>
              <Text size={400} style={{ color: '#605e5c', marginTop: '8px', display: 'block' }}>
                Analytics data will be aggregated and stored here for business intelligence
              </Text>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '16px' }}>
                <Text size={400} style={{ color: '#605e5c' }}>
                  Found {analytics.length} analytics records with comprehensive business metrics
                </Text>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>Date</TableHeaderCell>
                    <TableHeaderCell>Type</TableHeaderCell>
                    <TableHeaderCell>Visitors</TableHeaderCell>
                    <TableHeaderCell>Engagement</TableHeaderCell>
                    <TableHeaderCell>Conversions</TableHeaderCell>
                    <TableHeaderCell>Revenue</TableHeaderCell>
                    <TableHeaderCell>Top Performance</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {analytics.slice(0, 20).map((record) => (
                    <TableRow key={record._id}>
                      <TableCell>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <Calendar24Regular style={{ fontSize: '16px' }} />
                          <Text size={300} weight="semibold">
                            {formatDate(record.date)}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          appearance="tint" 
                          color={getMetricTypeColor(record.metric_type)}
                        >
                          {record.metric_type.charAt(0).toUpperCase() + record.metric_type.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                            <People24Regular style={{ fontSize: '14px' }} />
                            <Text size={300} weight="semibold">
                              {record.unique_visitors.toLocaleString()}
                            </Text>
                            <Text size={200} style={{ color: '#605e5c' }}>unique</Text>
                          </div>
                          <Text size={200} style={{ color: '#605e5c' }}>
                            {record.new_visitors} new • {record.returning_visitors} returning
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} style={{ display: 'block' }}>
                            📄 {record.page_views.toLocaleString()} views
                          </Text>
                          <Text size={300} style={{ display: 'block' }}>
                            🎯 {formatPercentage(record.bounce_rate)} bounce
                          </Text>
                          <Text size={200} style={{ color: '#605e5c' }}>
                            ⏱️ {formatDuration(record.avg_session_duration)} avg
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                            <ArrowUp24Regular style={{ fontSize: '14px', color: '#0078d4' }} />
                            <Text size={300} weight="semibold" style={{ color: '#0078d4' }}>
                              {formatPercentage(record.conversion_rate)}
                            </Text>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <ShoppingBag24Regular style={{ fontSize: '14px' }} />
                            <Text size={300}>
                              {record.orders} orders
                            </Text>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                            <Money24Regular style={{ fontSize: '14px', color: '#0078d4' }} />
                            <Text size={300} weight="semibold" style={{ color: '#0078d4' }}>
                              {formatCurrency(record.revenue)}
                            </Text>
                          </div>
                          <Text size={200} style={{ color: '#605e5c' }}>
                            AOV: {formatCurrency(record.avg_order_value)}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          {record.top_products && record.top_products.length > 0 && (
                            <div style={{ marginBottom: '4px' }}>
                              <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                                Top Product:
                              </Text>
                              <Text size={300} weight="semibold">
                                {record.top_products[0].name}
                              </Text>
                              <Text size={200} style={{ color: '#605e5c' }}>
                                {record.top_products[0].views} views • {record.top_products[0].sales} sales
                              </Text>
                            </div>
                          )}
                          {record.top_categories && record.top_categories.length > 0 && (
                            <div>
                              <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                                Top Category:
                              </Text>
                              <Badge appearance="tint" size="small">
                                {record.top_categories[0].category}
                              </Badge>
                            </div>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {analytics.length > 20 && (
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Showing first 20 of {analytics.length} analytics records
                  </Text>
                </div>
              )}

              {/* Sample Traffic Sources and Device Breakdown */}
              {analytics.length > 0 && analytics[0].traffic_sources && (
                <div style={{ marginTop: '24px' }}>
                  <Text size={500} weight="semibold" style={{ marginBottom: '16px', display: 'block' }}>
                    Sample Data Structures
                  </Text>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <Card>
                      <CardHeader header={<Text size={400} weight="semibold">Traffic Sources</Text>} />
                      <div style={{ padding: '0 16px 16px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Direct:</Text>
                            <Text size={300} weight="semibold">{analytics[0].traffic_sources.direct}%</Text>
                          </div>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Search:</Text>
                            <Text size={300} weight="semibold">{analytics[0].traffic_sources.search}%</Text>
                          </div>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Social:</Text>
                            <Text size={300} weight="semibold">{analytics[0].traffic_sources.social}%</Text>
                          </div>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Referral:</Text>
                            <Text size={300} weight="semibold">{analytics[0].traffic_sources.referral}%</Text>
                          </div>
                        </div>
                      </div>
                    </Card>

                    <Card>
                      <CardHeader header={<Text size={400} weight="semibold">Device Breakdown</Text>} />
                      <div style={{ padding: '0 16px 16px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Desktop:</Text>
                            <Text size={300} weight="semibold">{analytics[0].device_breakdown.desktop}%</Text>
                          </div>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Mobile:</Text>
                            <Text size={300} weight="semibold">{analytics[0].device_breakdown.mobile}%</Text>
                          </div>
                          <div>
                            <Text size={300} style={{ color: '#605e5c' }}>Tablet:</Text>
                            <Text size={300} weight="semibold">{analytics[0].device_breakdown.tablet}%</Text>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
              )}
            </>
          )}

          <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
            <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
              Analytics Schema Benefits:
            </Text>
            <Text size={300} style={{ color: '#605e5c' }}>
              • <strong>Time-Series Storage</strong>: Efficient storage of historical metrics by date and period<br/>
              • <strong>Aggregated Data</strong>: Pre-computed metrics for fast dashboard queries<br/>
              • <strong>Nested Arrays</strong>: Top products and categories with performance metrics<br/>
              • <strong>Embedded Objects</strong>: Traffic sources and device data stored as subdocuments<br/>
              • <strong>Flexible Metrics</strong>: Easy to add new KPIs without schema changes
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AnalyticsPage;