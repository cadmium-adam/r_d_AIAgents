import React from 'react';
import {
  Text,
  Card,
  CardHeader,
} from '@fluentui/react-components';
import {
  Database24Regular,
  ChartMultiple24Regular,
} from '@fluentui/react-icons';

const AdminPage: React.FC = () => {

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <ChartMultiple24Regular style={{ fontSize: '32px', color: '#0078d4' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              Admin Dashboard
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              System analytics, performance metrics, and administrative insights from the multi-database platform
            </Text>
          </div>
        </div>
      </div>

      {/* Database Overview */}
      <Card style={{ marginBottom: '32px' }}>
        <CardHeader
          header={
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Database24Regular />
              <Text size={600} weight="semibold">System Overview</Text>
            </div>
          }
        />
        <div style={{ padding: '0 16px 16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
              <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                55
              </Text>
              <Text size={300} style={{ color: '#605e5c' }}>
                Products (MSSQL)
              </Text>
            </div>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
              <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                8
              </Text>
              <Text size={300} style={{ color: '#605e5c' }}>
                Users (MSSQL)
              </Text>
            </div>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
              <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                53
              </Text>
              <Text size={300} style={{ color: '#605e5c' }}>
                Orders (MSSQL)
              </Text>
            </div>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid #e1e1e1', borderRadius: '8px' }}>
              <Text size={500} weight="semibold" style={{ display: 'block', color: '#0078d4' }}>
                202
              </Text>
              <Text size={300} style={{ color: '#605e5c' }}>
                Reviews (MongoDB)
              </Text>
            </div>
          </div>
        </div>
      </Card>

    </div>
  );
};

export default AdminPage;