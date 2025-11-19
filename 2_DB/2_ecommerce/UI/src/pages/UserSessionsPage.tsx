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
  Globe24Regular,
  Clock24Regular,
  Desktop24Regular,
  Phone24Regular,
  Tablet24Regular,
  ArrowClockwise24Regular,
} from '@fluentui/react-icons';

interface UserSession {
  _id: string;
  session_id: string;
  user_id: number;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  pages_viewed: Array<{
    url: string;
    timestamp: string;
    time_spent_seconds: number;
  }>;
  device_info: {
    type: string;
    os: string;
    browser: string;
    screen_resolution: string;
  };
  location: {
    country: string;
    city: string;
    ip_address: string;
  };
  referrer: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const UserSessionsPage: React.FC = () => {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8003/user-sessions?size=100');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load user sessions:', error);
      setError('Failed to load user sessions data');
    } finally {
      setLoading(false);
    }
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType?.toLowerCase()) {
      case 'mobile':
        return <Phone24Regular />;
      case 'tablet':
        return <Tablet24Regular />;
      default:
        return <Desktop24Regular />;
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${Math.round(minutes)}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = Math.round(minutes % 60);
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Globe24Regular style={{ fontSize: '32px', color: '#005571' }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              User Sessions
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              Elasticsearch index: user_sessions - Tracking user browsing sessions and behavior patterns
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Globe24Regular />
            Elasticsearch User Sessions Features
          </div>
          <div className="database-description">
            This index demonstrates Elasticsearch's strength in storing and searching time-series session data with complex nested documents.
          </div>
          <ul className="feature-list">
            <li>Time-series optimized storage for session tracking</li>
            <li>Fast searching and filtering of sessions by user, device, or location</li>
            <li>Nested documents for device info, location, and page views</li>
            <li>Aggregation capabilities for session analytics</li>
            <li>Geolocation data with geo-point support</li>
            <li>Efficient date range queries for time-based analysis</li>
          </ul>
        </div>
      </div>

      {/* Sessions Data */}
      <Card>
        <CardHeader
          header={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Globe24Regular />
                <Text size={600} weight="semibold">User Sessions Data</Text>
                <Badge appearance="tint" color="success">Elasticsearch Index</Badge>
              </div>
              <Button 
                appearance="secondary" 
                icon={<ArrowClockwise24Regular />}
                onClick={loadSessions}
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
              <Spinner size="large" label="Loading user sessions..." />
            </div>
          ) : error ? (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#d13438' }}>{error}</Text>
            </div>
          ) : sessions.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <Text size={500} style={{ color: '#605e5c' }}>No user sessions found</Text>
              <Text size={400} style={{ color: '#605e5c', marginTop: '8px', display: 'block' }}>
                Sessions will appear here as users browse the application
              </Text>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '16px' }}>
                <Text size={400} style={{ color: '#605e5c' }}>
                  Found {sessions.length} user sessions with detailed tracking data
                </Text>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>Session ID</TableHeaderCell>
                    <TableHeaderCell>User</TableHeaderCell>
                    <TableHeaderCell>Device</TableHeaderCell>
                    <TableHeaderCell>Duration</TableHeaderCell>
                    <TableHeaderCell>Pages</TableHeaderCell>
                    <TableHeaderCell>Location</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>Started</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.slice(0, 20).map((session) => (
                    <TableRow key={session._id}>
                      <TableCell>
                        <Text size={300} style={{ fontFamily: 'monospace' }}>
                          {session.session_id.substring(0, 12)}...
                        </Text>
                      </TableCell>
                      <TableCell>
                        <Badge appearance="tint" color="informative">
                          User {session.user_id}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          {getDeviceIcon(session.device_info?.type)}
                          <div>
                            <Text size={300} weight="semibold">
                              {session.device_info?.type || 'Unknown'}
                            </Text>
                            <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                              {session.device_info?.os} • {session.device_info?.browser}
                            </Text>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock24Regular style={{ fontSize: '14px' }} />
                          <Text size={300}>
                            {formatDuration(session.duration_minutes)}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge appearance="tint" color="subtle">
                          {session.pages_viewed?.length || 0} pages
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <Text size={300} weight="semibold">
                            {session.location?.city || 'Unknown'}
                          </Text>
                          <Text size={200} style={{ color: '#605e5c', display: 'block' }}>
                            {session.location?.country || 'Unknown Country'}
                          </Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          appearance="tint" 
                          color={session.is_active ? 'success' : 'subtle'}
                        >
                          {session.is_active ? 'Active' : 'Ended'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Text size={300}>
                          {formatDateTime(session.start_time)}
                        </Text>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {sessions.length > 20 && (
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                  <Text size={300} style={{ color: '#605e5c' }}>
                    Showing first 20 of {sessions.length} sessions
                  </Text>
                </div>
              )}
            </>
          )}

          <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
            <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
              Schema Highlights:
            </Text>
            <Text size={300} style={{ color: '#605e5c' }}>
              • <strong>Nested Documents</strong>: Device info, location, and page views stored as embedded documents<br/>
              • <strong>Array Fields</strong>: pages_viewed stores multiple page visits with timestamps<br/>
              • <strong>Flexible Schema</strong>: Can easily add new fields without schema migrations<br/>
              • <strong>Real-time Updates</strong>: Session state and duration updated as users browse
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default UserSessionsPage;