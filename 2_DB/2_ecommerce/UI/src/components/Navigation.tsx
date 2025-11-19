import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Toolbar,
  ToolbarGroup,
  Text,
  Avatar,
  Badge,
  Button,
  Menu,
  MenuTrigger,
  MenuPopover,
  MenuList,
  MenuItem,
  MenuDivider,
  Dropdown,
  Option,
} from '@fluentui/react-components';
import {
  Home24Regular,
  ShoppingBag24Regular,
  Search24Regular,
  Cart24Regular,
  Sparkle24Regular,
  Database24Regular,
  Receipt24Regular,
  PersonSwap24Regular,
  ChevronDown24Regular,
  Globe24Regular,
  Person24Regular,
  ChartMultiple24Regular,
  Target24Regular,
  Brain24Regular,
} from '@fluentui/react-icons';
import { useApp } from './AppProvider';
import { mssqlService } from '../services/api';
import type { User } from '../types';

const Navigation: React.FC = () => {
  const location = useLocation();
  const { state, setCurrentUser, setError } = useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const userData = await mssqlService.getUsers(1, 100);
      setUsers(userData.users);
    } catch (error) {
      console.error('Failed to load users:', error);
      setError('Failed to load users');
    }
  };

  const handleUserChange = (userId: string) => {
    const selectedUser = users.find(user => user.id.toString() === userId);
    if (selectedUser) {
      setCurrentUser(selectedUser);
      setShowUserMenu(false);
    }
  };

  const navItems = [
    { path: '/', label: 'Home', icon: <Home24Regular /> },
    { path: '/products', label: 'Products', icon: <ShoppingBag24Regular /> },
    { path: '/search', label: 'Search', icon: <Search24Regular /> },
    { path: '/cart', label: 'Cart', icon: <Cart24Regular /> },
    { path: '/recommendations', label: 'AI Recommendations', icon: <Sparkle24Regular /> },
    { path: '/orders', label: 'Orders', icon: <Receipt24Regular /> },
  ];

  const mongoNavItems = [
    { path: '/mongo-recommendations', label: 'Recommendations Data', icon: <Target24Regular /> },
  ];

  const elasticsearchNavItems = [
    { path: '/user-sessions', label: 'User Sessions', icon: <Globe24Regular /> },
    { path: '/user-behavior', label: 'User Behavior', icon: <Person24Regular /> },
    { path: '/analytics', label: 'Analytics Dashboard', icon: <ChartMultiple24Regular /> },
    { path: '/search-analytics', label: 'Search Analytics', icon: <Search24Regular /> },
  ];

  const qdrantNavItems = [
    { path: '/user-preferences', label: 'User Preferences', icon: <Person24Regular /> },
    { path: '/vector-status', label: 'Vector Database Status', icon: <Database24Regular /> },
  ];


  return (
    <Toolbar style={{ padding: '12px 20px', borderBottom: '1px solid #e1e1e1', backgroundColor: '#ffffff' }}>
      <ToolbarGroup>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Database24Regular style={{ fontSize: '24px', color: '#0078d4' }} />
          <Text size={600} weight="semibold" style={{ color: '#323130' }}>
            Multi-DB E-commerce Demo
          </Text>
        </div>
      </ToolbarGroup>

      <ToolbarGroup style={{ flex: 1, justifyContent: 'center' }}>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{ textDecoration: 'none' }}
            >
              <Button
                appearance={location.pathname === item.path ? 'primary' : 'subtle'}
                icon={item.icon}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  minWidth: 'auto'
                }}
              >
                {item.label}
                {item.path === '/cart' && state.cart && state.cart.total_items > 0 && (
                  <Badge
                    appearance="filled"
                    color="important"
                    size="small"
                    style={{ marginLeft: '4px' }}
                  >
                    {state.cart.total_items}
                  </Badge>
                )}
              </Button>
            </Link>
          ))}
          
          {/* MongoDB Data Dropdown */}
          <Menu positioning="below-start">
            <MenuTrigger>
              <Button
                appearance="subtle"
                icon={<Database24Regular />}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  minWidth: 'auto'
                }}
              >
                MongoDB Data
                <ChevronDown24Regular style={{ fontSize: '16px' }} />
              </Button>
            </MenuTrigger>
            <MenuPopover>
              <MenuList>
                {mongoNavItems.map((item) => (
                  <MenuItem key={item.path}>
                    <Link
                      to={item.path}
                      style={{
                        textDecoration: 'none',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '100%'
                      }}
                    >
                      {item.icon}
                      <div>
                        <Text size={300} weight="semibold" style={{ display: 'block' }}>
                          {item.label}
                        </Text>
                        <Text size={200} style={{ color: '#605e5c' }}>
                          {item.path === '/mongo-recommendations' && 'AI recommendation campaigns'}
                        </Text>
                      </div>
                    </Link>
                  </MenuItem>
                ))}
              </MenuList>
            </MenuPopover>
          </Menu>

          {/* Elasticsearch Data Dropdown */}
          <Menu positioning="below-start">
            <MenuTrigger>
              <Button
                appearance="subtle"
                icon={<Search24Regular />}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  minWidth: 'auto'
                }}
              >
                Elasticsearch Data
                <ChevronDown24Regular style={{ fontSize: '16px' }} />
              </Button>
            </MenuTrigger>
            <MenuPopover>
              <MenuList>
                {elasticsearchNavItems.map((item) => (
                  <MenuItem key={item.path}>
                    <Link
                      to={item.path}
                      style={{
                        textDecoration: 'none',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '100%'
                      }}
                    >
                      {item.icon}
                      <div>
                        <Text size={300} weight="semibold" style={{ display: 'block' }}>
                          {item.label}
                        </Text>
                        <Text size={200} style={{ color: '#605e5c' }}>
                          {item.path === '/user-sessions' && 'Browsing sessions & device tracking'}
                          {item.path === '/user-behavior' && 'Event-driven interaction analytics'}
                          {item.path === '/analytics' && 'Aggregated business metrics'}
                          {item.path === '/search-analytics' && 'Real-time search performance & trends'}
                        </Text>
                      </div>
                    </Link>
                  </MenuItem>
                ))}
              </MenuList>
            </MenuPopover>
          </Menu>

          {/* Qdrant Vector Data Dropdown */}
          <Menu positioning="below-start">
            <MenuTrigger>
              <Button
                appearance="subtle"
                icon={<Brain24Regular />}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  minWidth: 'auto'
                }}
              >
                Qdrant Vector Data
                <ChevronDown24Regular style={{ fontSize: '16px' }} />
              </Button>
            </MenuTrigger>
            <MenuPopover>
              <MenuList>
                {qdrantNavItems.map((item) => (
                  <MenuItem key={item.path}>
                    <Link
                      to={item.path}
                      style={{
                        textDecoration: 'none',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '100%'
                      }}
                    >
                      {item.icon}
                      <div>
                        <Text size={300} weight="semibold" style={{ display: 'block' }}>
                          {item.label}
                        </Text>
                        <Text size={200} style={{ color: '#605e5c' }}>
                          {item.path === '/user-preferences' && 'AI user preference vectors & embeddings'}
                          {item.path === '/vector-status' && 'Collection health & performance metrics'}
                        </Text>
                      </div>
                    </Link>
                  </MenuItem>
                ))}
              </MenuList>
            </MenuPopover>
          </Menu>
        </div>
      </ToolbarGroup>

      <ToolbarGroup>
        {state.currentUser ? (
          <Menu positioning="below-end">
            <MenuTrigger>
              <Button
                appearance="subtle"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '8px 12px',
                  height: 'auto'
                }}
              >
                <div style={{ textAlign: 'right' }}>
                  <Text size={300} weight="semibold" style={{ display: 'block' }}>
                    {state.currentUser.email}
                  </Text>
                  <Text size={200} style={{ color: '#605e5c' }}>
                    {state.currentUser.is_premium ? 'Premium Member' : 'Standard Member'}
                  </Text>
                </div>
                <Avatar
                  name={`${state.currentUser.first_name} ${state.currentUser.last_name}`}
                  color="colorful"
                  size={32}
                />
                <ChevronDown24Regular style={{ fontSize: '16px', color: '#605e5c' }} />
              </Button>
            </MenuTrigger>
            <MenuPopover>
              <MenuList>
                <MenuItem>
                  <div style={{ padding: '8px 0' }}>
                    <Text size={400} weight="semibold" style={{ display: 'block' }}>
                      {state.currentUser.first_name} {state.currentUser.last_name}
                    </Text>
                    <Text size={300} style={{ color: '#605e5c' }}>
                      ID: {state.currentUser.id} • {state.currentUser.total_orders} orders
                    </Text>
                  </div>
                </MenuItem>
                <MenuDivider />
                <MenuItem>
                  <PersonSwap24Regular style={{ marginRight: '8px' }} />
                  Switch User
                </MenuItem>
                <MenuDivider />
                {users.map((user) => (
                  <MenuItem
                    key={user.id}
                    onClick={() => handleUserChange(user.id.toString())}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                      <div>
                        <Text size={300} weight="semibold" style={{ display: 'block' }}>
                          {user.first_name} {user.last_name}
                        </Text>
                        <Text size={200} style={{ color: '#605e5c' }}>
                          {user.email}
                        </Text>
                      </div>
                      {user.is_premium && (
                        <Badge appearance="tint" color="brand" size="small">
                          Premium
                        </Badge>
                      )}
                    </div>
                  </MenuItem>
                ))}
              </MenuList>
            </MenuPopover>
          </Menu>
        ) : (
          <Button appearance="primary">
            Sign In
          </Button>
        )}
      </ToolbarGroup>
    </Toolbar>
  );
};

export default Navigation;