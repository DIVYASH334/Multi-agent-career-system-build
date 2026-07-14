import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

export default function App() {
  const [view, setView] = useState('login'); // login, register, dashboard
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Check localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      setView('dashboard');
    }
    setAuthLoading(false);
  }, []);

  const handleLoginSuccess = (newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    setView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setView('login');
  };

  if (authLoading) {
    return (
      <div className="app-container">
        <div className="gradient-bg"></div>
        <div className="loader-wrapper" style={{ minHeight: '100vh' }}>
          <div className="spinner"></div>
          <p>Loading application session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="gradient-bg"></div>

      {view === 'login' && (
        <Login 
          onLoginSuccess={handleLoginSuccess} 
          onNavigateToRegister={() => setView('register')} 
        />
      )}

      {view === 'register' && (
        <Register 
          onRegisterSuccess={() => setView('login')} 
          onNavigateToLogin={() => setView('login')} 
        />
      )}

      {view === 'dashboard' && (
        <Dashboard 
          token={token} 
          user={user} 
          onLogout={handleLogout} 
        />
      )}
    </div>
  );
}
