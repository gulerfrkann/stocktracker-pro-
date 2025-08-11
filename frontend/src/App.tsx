import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import Layout from '@/components/layout/Layout';
import Dashboard from '@/pages/Dashboard';
import Products from '@/pages/Products';
import Sites from '@/pages/Sites';
import SiteWizard from '@/pages/SiteWizard';
import Alerts from '@/pages/Alerts';
import Jobs from '@/pages/Jobs';
import UserPreferences from '@/pages/UserPreferences';
import Reports from '@/pages/Reports';
import Settings from '@/pages/Settings';
import Orders from '@/pages/Orders';

function App() {
  return (
    <Layout>
      <Routes>
        {/* Ana sayfa - Dashboard'a yönlendir */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* Ana sayfalar */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/sites" element={<Sites />} />
        <Route path="/site-wizard" element={<SiteWizard />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/preferences" element={<UserPreferences />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        
        {/* 404 sayfası */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;

