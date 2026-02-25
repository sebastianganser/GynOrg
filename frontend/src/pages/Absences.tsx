import React, { useState } from 'react';
import { AbsenceCalendar } from '../components/AbsenceCalendar';
import { CalendarSidebar } from '../components/CalendarSidebar';
import { CreateAbsenceForm } from '../components/CreateAbsenceForm';
import { useAbsenceManagement } from '../hooks/useAbsences';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import { Absence } from '../types/absence';
import { ErrorBoundary } from '../components/ErrorBoundary';

const Absences: React.FC = () => {
  const [selectedAbsence, setSelectedAbsence] = useState<Absence | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const { absences, isLoading, error } = useAbsenceManagement();

  const handleSelectEvent = (absence: Absence) => {
    setSelectedAbsence(absence);
    setShowCreateForm(false);
  };

  const handleSelectSlot = (slotInfo: { start: Date; end: Date }) => {
    setSelectedDate(slotInfo.start);
    setSelectedAbsence(null);
    setShowCreateForm(true);
  };

  const handleCreateAbsence = () => {
    setSelectedDate(new Date());
    setSelectedAbsence(null);
    setShowCreateForm(true);
  };

  const handleCloseForm = () => {
    setShowCreateForm(false);
    setSelectedDate(null);
    setSelectedAbsence(null);
  };

  const _handleFormSuccess = () => {
    setShowCreateForm(false);
    setSelectedDate(null);
    setSelectedAbsence(null);
  };

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800 mb-2">Fehler beim Laden der Abwesenheiten</h2>
          <p className="text-red-600">
            {error instanceof Error ? error.message : 'Ein unbekannter Fehler ist aufgetreten.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Calendar Sidebar */}
      <CalendarSidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Calendar and Side Panel */}
        <div className="flex-1 flex flex-col p-6">
          {/* Calendar Section */}
          <div className="flex-1">
                {isLoading ? (
                  <div className="flex items-center justify-center h-96 bg-white rounded-lg shadow border">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-gray-600">Lade Abwesenheiten...</span>
                  </div>
                ) : (
                  <ErrorBoundary>
                    <AbsenceCalendar
                      absences={absences || []}
                      onSelectEvent={handleSelectEvent}
                      onSelectSlot={handleSelectSlot}
                      onNewAbsence={handleCreateAbsence}
                    />
                  </ErrorBoundary>
                )}
              </div>

              {/* Side Panel */}
              <div className="space-y-6">
          {/* Create/Edit Form */}
          {showCreateForm && (
            <div className="bg-white rounded-lg shadow border">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedAbsence ? 'Abwesenheit bearbeiten' : 'Neue Abwesenheit'}
                </h2>
              </div>
              <div className="p-4">
                <CreateAbsenceForm
                  isOpen={showCreateForm}
                  onClose={handleCloseForm}
                  initialData={{
                    start_date: selectedDate || new Date(),
                    end_date: selectedDate || new Date()
                  }}
                />
              </div>
            </div>
          )}

          {/* Selected Absence Details */}
          {selectedAbsence && !showCreateForm && (
            <div className="bg-white rounded-lg shadow border">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Abwesenheitsdetails</h2>
              </div>
              <div className="p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Typ</label>
                  <p className="mt-1 text-sm text-gray-900">Abwesenheit</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Zeitraum</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {new Date(selectedAbsence.start_date).toLocaleDateString('de-DE')} - {new Date(selectedAbsence.end_date).toLocaleDateString('de-DE')}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    selectedAbsence.status === 'confirmed' 
                      ? 'bg-green-100 text-green-800'
                      : selectedAbsence.status === 'draft'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {selectedAbsence.status === 'confirmed' ? 'Bestätigt' : 
                     selectedAbsence.status === 'draft' ? 'Entwurf' : selectedAbsence.status}
                  </span>
                </div>
                {selectedAbsence.comment && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Kommentar</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedAbsence.comment}</p>
                  </div>
                )}
                <div className="flex gap-2 pt-4">
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors duration-200"
                  >
                    Bearbeiten
                  </button>
                  <button
                    onClick={() => setSelectedAbsence(null)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-2 rounded text-sm font-medium transition-colors duration-200"
                  >
                    Schließen
                  </button>
                </div>
              </div>
            </div>
          )}

              </div>
        </div>
      </div>
    </div>
  );
};

export default Absences;
