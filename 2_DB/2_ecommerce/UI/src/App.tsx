import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppProvider } from './components/AppProvider';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import ProductsPage from './pages/ProductsPage';
import SearchPage from './pages/SearchPage';
import CartPage from './pages/CartPage';
import RecommendationsPage from './pages/RecommendationsPage';
import AdminPage from './pages/AdminPage';
import OrdersPage from './pages/OrdersPage';
import ProductDetailPage from './pages/ProductDetailPage';
import UserSelectionPage from './pages/UserSelectionPage';
import UserSessionsPage from './pages/UserSessionsPage';
import UserBehaviorPage from './pages/UserBehaviorPage';
import AnalyticsPage from './pages/AnalyticsPage';
import MongoRecommendationsPage from './pages/MongoRecommendationsPage';
import UserPreferencesPage from './pages/UserPreferencesPage';
import VectorStatusPage from './pages/VectorStatusPage';
import SearchAnalyticsPage from './pages/SearchAnalyticsPage';

function App() {
  return (
    <AppProvider>
      <div className="app-container">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/user-selection" element={<UserSelectionPage />} />
            <Route path="/user-sessions" element={<UserSessionsPage />} />
            <Route path="/user-behavior" element={<UserBehaviorPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/mongo-recommendations" element={<MongoRecommendationsPage />} />
            <Route path="/user-preferences" element={<UserPreferencesPage />} />
            <Route path="/vector-status" element={<VectorStatusPage />} />
            <Route path="/search-analytics" element={<SearchAnalyticsPage />} />
          </Routes>
        </main>
      </div>
    </AppProvider>
  );
}

export default App;