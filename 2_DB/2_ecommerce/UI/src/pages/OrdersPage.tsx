import React, { useEffect, useState } from 'react';
import {
  Text,
  Card,
  CardHeader,
  Badge,
  Spinner,
  Button,
} from '@fluentui/react-components';
import {
  Receipt24Regular,
  Cart24Regular,
  Calendar24Regular,
  Money24Regular,
} from '@fluentui/react-icons';
import { mssqlService } from '../services/api';
import { useApp } from '../components/AppProvider';
import type { Order } from '../types';

const OrdersPage: React.FC = () => {
  const { state, setLoading, setError } = useApp();
  const [orders, setOrders] = useState<Order[]>([]);
  const [localLoading, setLocalLoading] = useState(true);

  useEffect(() => {
    if (state.currentUser) {
      loadOrders();
    }
  }, [state.currentUser]);

  const loadOrders = async () => {
    if (!state.currentUser) return;

    setLocalLoading(true);
    try {
      const orderData = await mssqlService.getUserOrders(state.currentUser.id);
      setOrders(orderData);
    } catch (error) {
      console.error('Failed to load orders:', error);
      setError('Failed to load orders');
    } finally {
      setLocalLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'warning';
      case 'processing': return 'brand';
      case 'shipped': return 'informative';
      case 'delivered': return 'success';
      case 'cancelled': return 'danger';
      default: return 'subtle';
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Receipt24Regular style={{ fontSize: '32px', color: '#0078d4' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              Order History
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Powered by MSSQL - Demonstrating ACID transactions, relational data integrity, and complex queries
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Receipt24Regular />
            MSSQL Features Demonstrated
          </div>
          <div className="database-description">
            This page showcases MSSQL's strength in handling transactional data with guaranteed consistency.
          </div>
          <ul className="feature-list">
            <li>ACID transaction guarantees for financial data</li>
            <li>Complex relational joins between orders and products</li>
            <li>Foreign key constraints ensuring data integrity</li>
            <li>Advanced aggregations for order calculations</li>
            <li>Structured financial and business reporting</li>
            <li>Optimized queries with proper indexing</li>
          </ul>
        </div>
      </div>

      {localLoading ? (
        <div className="loading-container">
          <Spinner size="large" label="Loading orders..." />
        </div>
      ) : state.error ? (
        <div className="error-container">
          <Text size={500} style={{ color: '#d13438' }}>{state.error}</Text>
        </div>
      ) : !state.currentUser ? (
        <Card>
          <div style={{ padding: '32px', textAlign: 'center' }}>
            <Text size={500}>Please select a user to view orders</Text>
          </div>
        </Card>
      ) : orders.length === 0 ? (
        <Card>
          <div style={{ padding: '32px', textAlign: 'center' }}>
            <Receipt24Regular style={{ fontSize: '48px', color: '#605e5c', marginBottom: '16px' }} />
            <Text size={500} style={{ marginBottom: '16px', display: 'block' }}>
              No orders found
            </Text>
            <Text size={400} style={{ color: '#605e5c', marginBottom: '24px', display: 'block' }}>
              This user hasn't placed any orders yet
            </Text>
            <Button appearance="primary">
              Browse Products
            </Button>
          </div>
        </Card>
      ) : (
        <div>
          {/* User Order Summary */}
          <Card style={{ marginBottom: '24px' }}>
            <CardHeader
              header={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text size={600} weight="semibold">
                    Orders for {state.currentUser.first_name} {state.currentUser.last_name}
                  </Text>
                  <Badge appearance="tint" color="brand">
                    MSSQL Transactional Data
                  </Badge>
                </div>
              }
            />
            <div style={{ padding: '0 16px 16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px' }}>
                <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                  <Cart24Regular style={{ fontSize: '24px', color: '#0078d4', marginBottom: '8px' }} />
                  <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                    {orders.length}
                  </Text>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Total Orders
                  </Text>
                </div>
                <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                  <Money24Regular style={{ fontSize: '24px', color: '#107c10', marginBottom: '8px' }} />
                  <Text size={500} weight="semibold" style={{ display: 'block', color: '#107c10' }}>
                    {formatPrice(orders.reduce((sum, order) => sum + (order.total_amount || 0), 0))}
                  </Text>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Total Value
                  </Text>
                </div>
                <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                  <Calendar24Regular style={{ fontSize: '24px', color: '#8764b8', marginBottom: '8px' }} />
                  <Text size={500} weight="semibold" style={{ display: 'block', color: '#8764b8' }}>
                    {formatPrice(orders.reduce((sum, order) => sum + (order.total_amount || 0), 0) / orders.length)}
                  </Text>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Average Order
                  </Text>
                </div>
                <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                  <Receipt24Regular style={{ fontSize: '24px', color: '#d83b01', marginBottom: '8px' }} />
                  <Text size={500} weight="semibold" style={{ display: 'block', color: '#d83b01' }}>
                    {orders.reduce((sum, order) => sum + (order.items?.length || 0), 0)}
                  </Text>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Total Items
                  </Text>
                </div>
              </div>
            </div>
          </Card>

          {/* Orders List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {orders.map((order) => (
              <Card key={order.id}>
                <CardHeader
                  header={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Text size={500} weight="semibold">
                          Order #{order.id}
                        </Text>
                        <Text size={300} style={{ color: '#605e5c', marginLeft: '8px' }}>
                          {formatDate(order.order_date)}
                        </Text>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <Badge appearance="tint" color={getStatusColor(order.status)}>
                          {order.status}
                        </Badge>
                        <Text size={500} weight="semibold" style={{ color: '#0078d4' }}>
                          {formatPrice(order.total_amount || 0)}
                        </Text>
                      </div>
                    </div>
                  }
                />
                <div style={{ padding: '0 16px 16px' }}>
                  {/* Order Details */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                    <div>
                      <Text size={400} weight="semibold" style={{ marginBottom: '8px', display: 'block' }}>
                        Order Details
                      </Text>
                      <Text size={300} style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
                        Payment: {order.payment_method || 'Credit Card'}
                      </Text>
                      <Text size={300} style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
                        Items: {order.items?.length || 0}
                      </Text>
                      <Text size={300} style={{ color: '#605e5c', display: 'block' }}>
                        Shipping: {order.shipping_address || 'Standard shipping'}
                      </Text>
                    </div>
                    <div>
                      <Text size={400} weight="semibold" style={{ marginBottom: '8px', display: 'block' }}>
                        Pricing Breakdown
                      </Text>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <Text size={300} style={{ color: '#605e5c' }}>Subtotal:</Text>
                        <Text size={300}>{formatPrice(order.subtotal || 0)}</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <Text size={300} style={{ color: '#605e5c' }}>Tax:</Text>
                        <Text size={300}>{formatPrice(order.tax_amount || 0)}</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <Text size={300} style={{ color: '#605e5c' }}>Shipping:</Text>
                        <Text size={300}>{formatPrice(order.shipping_cost || 0)}</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #e1e1e1', paddingTop: '4px' }}>
                        <Text size={300} weight="semibold">Total:</Text>
                        <Text size={300} weight="semibold">{formatPrice(order.total_amount || 0)}</Text>
                      </div>
                    </div>
                  </div>

                  {/* Order Items */}
                  {order.items && order.items.length > 0 && (
                  <div>
                    <Text size={400} weight="semibold" style={{ marginBottom: '12px', display: 'block' }}>
                      Order Items
                    </Text>
                    <div style={{ border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                      {order.items.map((item, index) => (
                        <div
                          key={index}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '12px 16px',
                            borderBottom: index < order.items.length - 1 ? '1px solid #f3f2f1' : 'none'
                          }}
                        >
                          <div>
                            <Text size={400} weight="semibold" style={{ display: 'block' }}>
                              {item.product_name}
                            </Text>
                            <Text size={300} style={{ color: '#605e5c' }}>
                              Product ID: {item.product_id}
                            </Text>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <Text size={400} weight="semibold" style={{ display: 'block' }}>
                              {formatPrice(item.total_price)}
                            </Text>
                            <Text size={300} style={{ color: '#605e5c' }}>
                              {item.quantity} × {formatPrice(item.unit_price)}
                            </Text>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrdersPage;