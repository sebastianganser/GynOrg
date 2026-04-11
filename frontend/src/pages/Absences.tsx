import React, { useState } from 'react';
import { AbsenceCalendar } from '../components/AbsenceCalendar';
import { CalendarSidebar } from '../components/CalendarSidebar';
import { CreateAbsenceForm } from '../components/CreateAbsenceForm';
import { EditAbsenceForm } from '../components/EditAbsenceForm';
import { useAbsenceManagement } from '../hooks/useAbsences';
import { useEmployees } from '../hooks/useEmployees';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import { Absence } from '../types/absence';
import { ErrorBoundary } from '../components/ErrorBoundary';

const Absences: React.FC = () => {
  const [selectedAbsence, setSelectedAbsence] = useState<Absence | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const { absences, absenceTypes, isLoading, error, approveAbsence, deleteAbsence } = useAbsenceManagement();
  const { data: employees } = useEmployees(false);

  const enrichedAbsences = React.useMemo(() => {
    if (!absences) return [];
    return absences.map(absence => ({
      ...absence,
      absence_type: absenceTypes?.find(t => t.id === absence.absence_type_id) || absence.absence_type
    }));
  }, [absences, absenceTypes]);

  const handleSelectEvent = (event: any) => {
    if (event && event.resource && 'employee_id' in event.resource) {
      setSelectedAbsence(event.resource as Absence);
      setShowCreateForm(false);
    } else {
      setSelectedAbsence(null);
    }
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
        selectedAbsence={selectedAbsence}
        employees={employees}
        onApproveAbsence={(id) => approveAbsence(id, { onSuccess: () => setSelectedAbsence(null) })}
        onDeleteAbsence={(id) => deleteAbsence(id, { onSuccess: () => setSelectedAbsence(null) })}
        onEditAbsence={() => setShowCreateForm(true)}
        onCloseDetails={() => setSelectedAbsence(null)}
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
                  absences={enrichedAbsences}
                  onSelectEvent={handleSelectEvent}
                  onSelectSlot={handleSelectSlot}
                  onNewAbsence={handleCreateAbsence}
                />
              </ErrorBoundary>
            )}
          </div>

          {/* Create/Edit Form Modal */}
          {showCreateForm && (
            selectedAbsence ? (
              <EditAbsenceForm
                isOpen={showCreateForm}
                onClose={handleCloseForm}
                absence={selectedAbsence}
              />
            ) : (
              <CreateAbsenceForm
                isOpen={showCreateForm}
                onClose={handleCloseForm}
                initialData={{
                  start_date: selectedDate || new Date(),
                  end_date: selectedDate || new Date()
                }}
              />
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default Absences;
