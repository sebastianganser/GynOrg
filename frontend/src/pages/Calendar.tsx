import { useState } from 'react';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import { CalendarSidebar } from '../components/CalendarSidebar';
import { TeamCalendar } from '../components/TeamCalendar';
import { EventDetailsDialog } from '../components/EventDetailsDialog';
import { useCalendarEvents } from '../hooks/useCalendarEvents';
import { useFilteredCalendarEvents } from '../hooks/useFilteredCalendarEvents';
import { useEmployeesForCalendar } from '../hooks/useEmployeesForCalendar';
import { useCalendarSettings } from '../hooks/useCalendarSettings';
import type { CalendarEvent } from '../utils/calendarFilters';

/**
 * Calendar Page - Desktop-Only Layout
 * 
 * Features:
 * - Fixed Grid Layout (Sidebar 250px + Calendar flex-1)
 * - Integrated filter management via Zustand
 * - No mobile responsiveness (desktop-only)
 */
export default function Calendar() {
  const isSidebarCollapsed = useCalendarFilterStore((state) => state.isSidebarCollapsed);
  const toggleSidebar = useCalendarFilterStore((state) => state.toggleSidebar);

  // Event details dialog state
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Load all calendar events
  const { events, isLoading: eventsLoading, error: eventsError } = useCalendarEvents();

  // Load employees for color mapping
  const { data: employees, isLoading: employeesLoading } = useEmployeesForCalendar(true);

  // Load calendar settings
  const { data: calendarSettings } = useCalendarSettings();

  // Apply filters to events
  const { filteredEvents } = useFilteredCalendarEvents(
    events,
    employees || []
  );

  // Combined loading state
  const isLoading = eventsLoading || employeesLoading;

  // Handle event click
  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
    setIsDialogOpen(true);
  };

  return (
    <div className="flex h-full">
      {/* Calendar Sidebar - Fixed width, collapsible */}
      <CalendarSidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={toggleSidebar}
      />

      {/* Main Calendar Area */}
      <div className="flex-1 flex flex-col bg-background">
        {/* Calendar Header */}
        <div className="border-b bg-card">
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-2xl font-semibold">Team-Kalender</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Übersicht aller Abwesenheiten und Termine
              </p>
            </div>

            {/* Calendar Controls (Placeholder for now) */}
            <div className="flex items-center gap-2">
              <button className="px-4 py-2 text-sm border rounded-md hover:bg-accent">
                Heute
              </button>
              <div className="flex items-center gap-1">
                <button className="p-2 hover:bg-accent rounded-md">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="15 18 9 12 15 6" />
                  </svg>
                </button>
                <span className="px-4 py-2 text-sm font-medium min-w-[120px] text-center">
                  Dezember 2025
                </span>
                <button className="p-2 hover:bg-accent rounded-md">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="9 18 15 12 9 6" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Calendar Content Area */}
        <div className="flex-1 overflow-auto p-6">
          {/* Loading State */}
          {isLoading && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-2">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="text-sm text-muted-foreground">
                  Lade Kalender-Daten...
                </p>
              </div>
            </div>
          )}

          {/* Error State */}
          {eventsError && !isLoading && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mx-auto text-destructive"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <p className="text-lg font-medium text-destructive">
                  Fehler beim Laden der Kalender-Daten
                </p>
                <p className="text-sm text-muted-foreground">
                  {eventsError.toString()}
                </p>
              </div>
            </div>
          )}

          {/* Calendar Component */}
          {!isLoading && !eventsError && (
            <div className="h-full">
              <TeamCalendar
                events={filteredEvents}
                onEventClick={handleEventClick}
                showCalendarWeeks={calendarSettings?.show_calendar_weeks}
              />
            </div>
          )}
        </div>
      </div>

      {/* Event Details Dialog */}
      <EventDetailsDialog
        event={selectedEvent}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
      />
    </div>
  );
}
