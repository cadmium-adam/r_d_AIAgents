import React, { useEffect, useState } from 'react';
import {
  Text,
  Card,
  CardHeader,
  Badge,
  Spinner,
  Button,
  Dropdown,
  Option,
} from '@fluentui/react-components';
import {
  Person24Regular,
  PersonSwap24Regular,
} from '@fluentui/react-icons';
import { mssqlService } from '../services/api';
import { useApp } from '../components/AppProvider';
import type { User } from '../types';

const UserSelectionPage: React.FC = () => {
  const { state, setCurrentUser, setError } = useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const userData = await mssqlService.getUsers(1, 50); // Get first 50 users
      setUsers(userData.users); // Extract users array from response
    } catch (error) {
      console.error('Failed to load users:', error);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleUserChange = (userId: string) => {
    const selectedUser = users.find(user => user.id.toString() === userId);
    if (selectedUser) {
      setCurrentUser(selectedUser);
      console.log('Switched to user:', selectedUser);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <PersonSwap24Regular style={{ fontSize: '32px', color: '#0078d4' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              User Selection
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Switch between different users to test the multi-database e-commerce system
            </Text>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <Spinner size="large" label="Loading users..." />
        </div>
      ) : (
        <div>
          {/* Current User Display */}
          <Card style={{ marginBottom: '32px' }}>
            <CardHeader
              header={
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Person24Regular />
                  <Text size={600} weight="semibold">Current User</Text>
                </div>
              }
            />
            <div style={{ padding: '0 16px 16px' }}>
              {state.currentUser ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', alignItems: 'center' }}>
                  <div>
                    <Text size={500} weight="semibold" style={{ display: 'block', marginBottom: '8px' }}>
                      {state.currentUser.first_name} {state.currentUser.last_name}
                    </Text>
                    <Text size={400} style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
                      ID: {state.currentUser.id} • {state.currentUser.email}
                    </Text>
                    <Text size={400} style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
                      Username: {state.currentUser.username}
                    </Text>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                      <Badge appearance="tint" color={state.currentUser.is_premium ? 'brand' : 'subtle'}>
                        {state.currentUser.is_premium ? 'Premium' : 'Standard'}
                      </Badge>
                      <Badge appearance="tint" color={state.currentUser.is_active ? 'success' : 'danger'}>
                        {state.currentUser.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                        <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                          {state.currentUser.total_orders}
                        </Text>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          Total Orders
                        </Text>
                      </div>
                      <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                        <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                          {formatCurrency(state.currentUser.total_spent)}
                        </Text>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          Total Spent
                        </Text>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <Text size={400} style={{ color: '#605e5c' }}>
                  No user selected
                </Text>
              )}
            </div>
          </Card>

          {/* User Selection */}
          <Card>
            <CardHeader
              header={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <PersonSwap24Regular />
                    <Text size={600} weight="semibold">Switch User</Text>
                  </div>
                  <Button appearance="secondary" onClick={loadUsers}>
                    Refresh Users
                  </Button>
                </div>
              }
            />
            <div style={{ padding: '0 16px 16px' }}>
              <div style={{ marginBottom: '16px' }}>
                <Text size={400} style={{ color: '#605e5c', marginBottom: '8px', display: 'block' }}>
                  Select a user to test different scenarios:
                </Text>
                <Dropdown
                  placeholder="Select a user..."
                  value={state.currentUser?.id.toString()}
                  onOptionSelect={(_, data) => handleUserChange(data.optionValue || '')}
                  style={{ width: '100%', maxWidth: '400px' }}
                >
                  {users.map((user) => (
                    <Option key={user.id} value={user.id.toString()}>
                      {user.first_name} {user.last_name} (ID: {user.id}) - {user.email}
                    </Option>
                  ))}
                </Dropdown>
              </div>

              {/* Users List Preview */}
              <div>
                <Text size={400} weight="semibold" style={{ marginBottom: '12px', display: 'block' }}>
                  Available Users ({users.length})
                </Text>
                <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
                  {users.slice(0, 10).map((user) => (
                    <div
                      key={user.id}
                      style={{
                        padding: '12px 16px',
                        borderBottom: '1px solid #f3f2f1',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        cursor: 'pointer',
                        backgroundColor: state.currentUser?.id === user.id ? '#f3f2f1' : 'transparent'
                      }}
                      onClick={() => handleUserChange(user.id.toString())}
                    >
                      <div>
                        <Text size={400} weight="semibold" style={{ display: 'block' }}>
                          {user.first_name} {user.last_name}
                        </Text>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          ID: {user.id} • {user.username} • {user.email}
                        </Text>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <Text size={300} style={{ color: '#605e5c' }}>
                          {user.total_orders} orders
                        </Text>
                        {user.is_premium && (
                          <Badge appearance="tint" color="brand" size="small">
                            Premium
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                  {users.length > 10 && (
                    <div style={{ padding: '12px 16px', textAlign: 'center', backgroundColor: '#f9f9f9' }}>
                      <Text size={300} style={{ color: '#605e5c' }}>
                        ... and {users.length - 10} more users
                      </Text>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default UserSelectionPage;