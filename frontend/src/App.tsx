import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginForm } from './components/LoginForm';
import { Layout } from './components/Layout';
import { authService } from './services/authService';

const queryClient = new QueryClient();

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      // Check if user is already authenticated on app load
      const isValid = await authService.verifyToken();
      setIsAuthenticated(isValid);
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-lg">Laden...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Desktop Split-Screen Layout */}
        <div className="flex min-h-screen">
          {/* Left Panel - Login Form (40% width) */}
          <div className="flex-1 lg:w-2/5 bg-white flex flex-col justify-center px-8 xl:px-12">
            <div className="mx-auto w-full max-w-sm">
              <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">GynOrg</h1>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Willkommen zurück</h2>
                <p className="text-gray-600">Melden Sie sich an, um auf die Abwesenheitsplanung zuzugreifen</p>
              </div>
              <LoginForm onLoginSuccess={handleLoginSuccess} />
            </div>
          </div>

          {/* Right Panel - Branding/Info (60% width) */}
          <div className="flex-1 lg:w-3/5 bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 flex flex-col justify-center items-center px-8 xl:px-12 text-white">
            <div className="max-w-md text-center">
              <div className="mb-8">
                <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold mb-4">Effiziente Abwesenheitsplanung</h3>
                <p className="text-xl text-white/90 mb-6">
                  Verwalten Sie Urlaube, Krankheitstage und Abwesenheiten mit unserem intuitiven Planungstool.
                </p>
              </div>
              <div className="space-y-4 text-left">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                  <span className="text-white/90">Übersichtliche Kalenderansicht</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                  <span className="text-white/90">Automatische Konfliktprüfung</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                  <span className="text-white/90">Einfache Mitarbeiterverwaltung</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Layout onLogout={handleLogout} username="MGanser" />
    </QueryClientProvider>
  );
}

export default App;
