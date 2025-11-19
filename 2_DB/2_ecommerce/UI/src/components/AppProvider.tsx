import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { AppState, User, Cart } from '../types';
import { mssqlService } from '../services/api';

interface AppContextType {
  state: AppState;
  setCurrentUser: (user: User | null) => void;
  setCart: (cart: Cart | null) => void;
  setSearchQuery: (query: string) => void;
  setSelectedCategory: (category: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

type AppAction =
  | { type: 'SET_CURRENT_USER'; payload: User | null }
  | { type: 'SET_CART'; payload: Cart | null }
  | { type: 'SET_SEARCH_QUERY'; payload: string }
  | { type: 'SET_SELECTED_CATEGORY'; payload: string | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

const initialState: AppState = {
  currentUser: null,
  cart: null,
  searchQuery: '',
  selectedCategory: null,
  loading: false,
  error: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CURRENT_USER':
      return { ...state, currentUser: action.payload };
    case 'SET_CART':
      return { ...state, cart: action.payload };
    case 'SET_SEARCH_QUERY':
      return { ...state, searchQuery: action.payload };
    case 'SET_SELECTED_CATEGORY':
      return { ...state, selectedCategory: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Initialize with actual user from database (Erin Roberts - ID 1)
  useEffect(() => {
    const loadInitialUser = async () => {
      try {
        // Fetch users to get the first user with correct data
        const userData = await mssqlService.getUsers(1, 1);
        if (userData.users && userData.users.length > 0) {
          setCurrentUser(userData.users[0]);
        } else {
          // Fallback to hardcoded user if API fails
          const fallbackUser: User = {
            id: 1,
            username: 'erin3185',
            email: 'erin.roberts@hotmail.com',
            first_name: 'Erin',
            last_name: 'Roberts',
            is_active: false,
            is_premium: false,
            total_orders: 2, // Corrected value
            total_spent: 2075.54,
            average_order_value: 1037.77, // Corrected value
            created_at: '2025-05-03T23:43:21.039068Z',
            updated_at: '2025-06-19T09:51:33.137062Z',
          };
          setCurrentUser(fallbackUser);
        }
      } catch (error) {
        console.error('Failed to load initial user:', error);
        // Fallback to hardcoded user with corrected values
        const fallbackUser: User = {
          id: 1,
          username: 'erin3185',
          email: 'erin.roberts@hotmail.com',
          first_name: 'Erin',
          last_name: 'Roberts',
          is_active: false,
          is_premium: false,
          total_orders: 2, // Corrected value
          total_spent: 2075.54,
          average_order_value: 1037.77, // Corrected value
          created_at: '2025-05-03T23:43:21.039068Z',
          updated_at: '2025-06-19T09:51:33.137062Z',
        };
        setCurrentUser(fallbackUser);
      }
    };
    
    loadInitialUser();
  }, []);

  const setCurrentUser = (user: User | null) => {
    dispatch({ type: 'SET_CURRENT_USER', payload: user });
  };

  const setCart = (cart: Cart | null) => {
    dispatch({ type: 'SET_CART', payload: cart });
  };

  const setSearchQuery = (query: string) => {
    dispatch({ type: 'SET_SEARCH_QUERY', payload: query });
  };

  const setSelectedCategory = (category: string | null) => {
    dispatch({ type: 'SET_SELECTED_CATEGORY', payload: category });
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const contextValue: AppContextType = {
    state,
    setCurrentUser,
    setCart,
    setSearchQuery,
    setSelectedCategory,
    setLoading,
    setError,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}