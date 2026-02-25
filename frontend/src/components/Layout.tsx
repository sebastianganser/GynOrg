import React, { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { CalendarSettingsModal } from './CalendarSettingsModal';
import Employees from '../pages/Employees';
import Absences from '../pages/Absences';

interface LayoutProps {
  onLogout: () => void;
  username: string;
}

export const Layout: React.FC<LayoutProps> = ({ onLogout, username }) => {
  const [currentPage, setCurrentPage] = useState('employees');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userPreference, setUserPreference] = useState<boolean | null>(null);
  const [isCalendarSettingsOpen, setIsCalendarSettingsOpen] = useState(false);

  // Responsive sidebar behavior
  useEffect(() => {
    // Load user preference from localStorage
    const savedPreference = localStorage.getItem('sidebar-collapsed');
    if (savedPreference !== null) {
      const preference = JSON.parse(savedPreference);
      setUserPreference(preference);
      setIsCollapsed(preference);
    }

    const handleResize = () => {
      const isMobile = window.innerWidth < 768; // md breakpoint
      
      // If user has no preference, auto-collapse based on screen size
      if (userPreference === null) {
        setIsCollapsed(isMobile);
      }
    };

    // Initial check
    handleResize();

    // Add resize listener
    window.addEventListener('resize', handleResize);
    
    return () => window.removeEventListener('resize', handleResize);
  }, [userPreference]);

  const handleSidebarToggle = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    setUserPreference(newCollapsed);
    localStorage.setItem('sidebar-collapsed', JSON.stringify(newCollapsed));
  };

  const getPageTitle = (page: string): string => {
    switch (page) {
      case 'employees':
        return 'Mitarbeiter';
      case 'absences':
        return 'Abwesenheiten';
      case 'settings':
        return 'Einstellungen';
      default:
        return 'GynOrg';
    }
  };

  const renderPageContent = () => {
    switch (currentPage) {
      case 'employees':
        return <Employees />;
      case 'absences':
        return <Absences />;
      case 'settings':
        return (
          <div className="p-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Einstellungen</h2>
              <div className="space-y-4">
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Kalender</h3>
                  <p className="text-gray-600 mb-4">
                    Passen Sie die Anzeige von Feiertagen und anderen Kalendereinstellungen an.
                  </p>
                  <button
                    onClick={() => setIsCalendarSettingsOpen(true)}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Kalender anpassen
                  </button>
                </div>
                
                <div className="pt-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Weitere Einstellungen</h3>
                  <p className="text-gray-600">
                    Zusätzliche Systemeinstellungen werden hier implementiert.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return <Employees />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Skip Link für Accessibility */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:bg-blue-600 focus:text-white focus:p-2 focus:z-50 focus:rounded"
      >
        Zum Hauptinhalt springen
      </a>
      
      <Sidebar 
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onLogout={onLogout}
        isCollapsed={isCollapsed}
        onToggle={handleSidebarToggle}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header 
          title={getPageTitle(currentPage)}
          username={username}
        />
        
        <main id="main-content" className="flex-1 overflow-auto">
          {renderPageContent()}
        </main>
      </div>

      {/* Kalendereinstellungen Modal */}
      <CalendarSettingsModal
        isOpen={isCalendarSettingsOpen}
        onClose={() => setIsCalendarSettingsOpen(false)}
      />
    </div>
  );
};
