import React, { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { CalendarSettingsModal } from './CalendarSettingsModal';
import { JobPositionModal } from './JobPositionModal';
import { AbsenceTypeModal } from './AbsenceTypeModal';
import { StationModal } from './StationModal';
import { SystemSettingsManager } from './SystemSettingsManager';
import { useSystemSettings } from '../hooks/useSystemSettings';
import Employees from '../pages/Employees';
import Absences from '../pages/Absences';
import Auslastung from '../pages/Auslastung';
import Rechnungen from '../pages/Rechnungen';
import RechnungWizard from '../pages/RechnungWizard';
import PraxisEinstellungenForm from './PraxisEinstellungenForm';
import GoaeUpdateManager from './GoaeUpdateManager';

interface LayoutProps {
  onLogout: () => void;
  username: string;
}

export const Layout: React.FC<LayoutProps> = ({ onLogout, username }) => {
  const [currentPage, setCurrentPage] = useState(() => {
    return localStorage.getItem('last-active-page') || 'employees';
  });
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userPreference, setUserPreference] = useState<boolean | null>(null);
  const [editRechnungId, setEditRechnungId] = useState<number | undefined>(undefined);
  const [isCalendarSettingsOpen, setIsCalendarSettingsOpen] = useState(false);
  const [isJobPositionModalOpen, setIsJobPositionModalOpen] = useState(false);
  const [isAbsenceTypeModalOpen, setIsAbsenceTypeModalOpen] = useState(false);
  const [isStationModalOpen, setIsStationModalOpen] = useState(false);

  // Persist current page
  useEffect(() => {
    localStorage.setItem('last-active-page', currentPage);
  }, [currentPage]);

  // Global Idle Timeout for Auto-Logout
  const { settings } = useSystemSettings();

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    const minutes = settings?.auto_logout_minutes || 30;

    const resetTimer = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        onLogout();
        window.location.reload();
      }, minutes * 60 * 1000);
    };

    const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'wheel'];

    events.forEach((eventName) => {
      document.addEventListener(eventName, resetTimer, { passive: true });
    });

    // Start initial timer
    resetTimer();

    return () => {
      clearTimeout(timeoutId);
      events.forEach((eventName) => {
        document.removeEventListener(eventName, resetTimer);
      });
    };
  }, [settings?.auto_logout_minutes, onLogout]);

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
      case 'auslastung':
        return 'Belegungsstatistik';
      case 'rechnungen':
        return 'Privatrechnungen';
      case 'rechnung-wizard':
        return 'Neue Rechnung';
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
      case 'auslastung':
        return <Auslastung />;
      case 'rechnungen':
        return (
          <Rechnungen
            onNavigateToWizard={() => { setEditRechnungId(undefined); setCurrentPage('rechnung-wizard'); }}
            onEditRechnung={(id) => { setEditRechnungId(id); setCurrentPage('rechnung-wizard'); }}
          />
        );
      case 'rechnung-wizard':
        return (
          <RechnungWizard
            onComplete={() => { setEditRechnungId(undefined); setCurrentPage('rechnungen'); }}
            onCancel={() => { setEditRechnungId(undefined); setCurrentPage('rechnungen'); }}
            onNavigateToPatienten={() => setCurrentPage('patienten')}
            editRechnungId={editRechnungId}
          />
        );
      case 'settings':
        return (
          <div className="p-6 max-w-7xl mx-auto space-y-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Einstellungen</h2>

            {/* Modul: Mitarbeiter */}
            <section className="space-y-4">
              <div className="border-b border-gray-200 pb-2">
                <h3 className="text-xl font-semibold text-gray-800">Modul: Mitarbeiter</h3>
                <p className="text-sm text-gray-500">Einstellungen für Mitarbeiter und Personal</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-lg font-medium text-gray-900 mb-2">Mitarbeiter-Positionen</h4>
                <p className="text-gray-600 mb-4">
                  Verwalten Sie hier die Liste der verfügbaren Job-Positionen für Mitarbeiter.
                </p>
                <button
                  onClick={() => setIsJobPositionModalOpen(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Positionen anpassen
                </button>
              </div>
            </section>

            {/* Modul: Abwesenheiten */}
            <section className="space-y-4">
              <div className="border-b border-gray-200 pb-2 mt-8">
                <h3 className="text-xl font-semibold text-gray-800">Modul: Abwesenheiten</h3>
                <p className="text-sm text-gray-500">Einstellungen für Urlaube, Krankheit und Kalender</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-lg font-medium text-gray-900 mb-2">Kalender</h4>
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

              <div className="bg-white rounded-lg shadow p-6 mt-4">
                <h4 className="text-lg font-medium text-gray-900 mb-2">Abwesenheitstypen</h4>
                <p className="text-gray-600 mb-4">
                  Verwalten Sie hier die Liste der verfügbaren Kategorien für Abwesenheiten.
                </p>
                <button
                  onClick={() => setIsAbsenceTypeModalOpen(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Abwesenheitstypen anpassen
                </button>
              </div>
            </section>

            {/* Modul: Belegungsstatistik */}
            <section className="space-y-4">
              <div className="border-b border-gray-200 pb-2 mt-8">
                <h3 className="text-xl font-semibold text-gray-800">Modul: Belegungsstatistik</h3>
                <p className="text-sm text-gray-500">Zukünftige Einstellungen für Statistiken</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-lg font-medium text-gray-900 mb-2">Stations-Stammdaten</h4>
                <p className="text-gray-600 mb-4">
                  Verwalten Sie die Stationen und deren historisierte Bettenkapazitäten.
                </p>
                <button
                  onClick={() => setIsStationModalOpen(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  Stationen anpassen
                </button>
              </div>
            </section>

            {/* Modul: Rechnungslegung */}
            <section className="space-y-4">
              <div className="border-b border-gray-200 pb-2 mt-8">
                <h3 className="text-xl font-semibold text-gray-800">Modul: Rechnungslegung</h3>
                <p className="text-sm text-gray-500">Praxisdaten, Bankverbindung und Abrechnungseinstellungen für GOÄ-Rechnungen</p>
              </div>
              <PraxisEinstellungenForm />
              <GoaeUpdateManager />
            </section>

            {/* Modul: Grundeinstellungen */}
            <section className="space-y-4">
              <div className="border-b border-gray-200 pb-2 mt-8">
                <h3 className="text-xl font-semibold text-gray-800">Modul: Grundeinstellungen</h3>
                <p className="text-sm text-gray-500">Globale Systemeinstellungen der Applikation</p>
              </div>
              <SystemSettingsManager />
            </section>
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
      
      {/* Mitarbeiter-Positionen Modal */}
      <JobPositionModal
        isOpen={isJobPositionModalOpen}
        onClose={() => setIsJobPositionModalOpen(false)}
      />
      
      {/* Abwesenheitstypen Modal */}
      <AbsenceTypeModal
        isOpen={isAbsenceTypeModalOpen}
        onClose={() => setIsAbsenceTypeModalOpen(false)}
      />

      {/* Stationen Modal */}
      <StationModal
        isOpen={isStationModalOpen}
        onClose={() => setIsStationModalOpen(false)}
      />
    </div>
  );
};
