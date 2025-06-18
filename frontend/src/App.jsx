import React from 'react';
import { Routes, Route } from 'react-router-dom'; // Removed Link as Navbar handles it
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ScrapedProfilesPage from './pages/ScrapedProfilesPage'; // Import ScrapedProfilesPage
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <>
      <Navbar />
      <div className="container" style={{ padding: '1rem' }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          {/* Add a route for registration if you implement a separate registration page */}
          {/* <Route path="/register" element={<RegisterPage />} /> */}

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/scraped-profiles" element={<ScrapedProfilesPage />} /> {/* Added profiles route */}
            {/* Add other protected routes here, e.g.: */}
            {/* <Route path="/posts/:postId" element={<PostDetailPage />} /> */}
          </Route>

          {/* Catch-all for not found routes (optional) */}
          {/* <Route path="*" element={<div>Page Not Found</div>} /> */}
        </Routes>
      </div>
    </>
  );
}

export default App;
