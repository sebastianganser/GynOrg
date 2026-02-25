import { useMemo } from 'react';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import type { CalendarFilters } from '../stores/calendarFilterStore';
import { useShallow } from 'zustand/react/shallow';
import {
  applyCalendarFilters,
  createEmployeeColorMap,
  type CalendarEvent,
} from '../utils/calendarFilters';

/**
 * Hook to get filtered calendar events based on current filter settings
 * 
 * @param events - Raw calendar events
 * @param employees - Employee data with calendar colors
 * @returns Filtered and colored calendar events
 */
export function useFilteredCalendarEvents(
  events: CalendarEvent[],
  employees: Array<{ id: number; calendar_color: string }>
) {
  // Use a SINGLE selector with SHALLOW equality check
  // This ensures React detects changes in the object properties and triggers re-renders
  const filters: CalendarFilters = useCalendarFilterStore(
    useShallow((state): CalendarFilters => ({
      selectedEmployeeIds: state.selectedEmployeeIds,
      showHolidays: state.showHolidays,
      showSchoolVacations: state.showSchoolVacations,
      showVacationAbsences: state.showVacationAbsences,
      showSickLeave: state.showSickLeave,
      showTraining: state.showTraining,
      showSpecialLeave: state.showSpecialLeave,
      isSidebarCollapsed: state.isSidebarCollapsed,
    }))
  ) as CalendarFilters;

  // Create employee color map (with safety check)
  const employeeColorMap = useMemo(
    () => createEmployeeColorMap(employees || []),
    [employees]
  );

  // Apply all filters (with safety check)
  const filteredEvents = useMemo(() => {
    console.log('[useFilteredCalendarEvents] Filtering with:', {
      showHolidays: filters.showHolidays,
      totalEvents: events?.length || 0,
    });

    const filtered = applyCalendarFilters(events || [], filters, employeeColorMap);

    console.log('[useFilteredCalendarEvents] Filtered result:', {
      filteredCount: filtered.length,
      holidayEvents: filtered.filter(e => e.type === 'holiday').length,
    });

    return filtered;
  }, [events, filters, employeeColorMap]);

  return {
    filteredEvents,
    filters,
    totalEvents: (events || []).length,
    filteredCount: filteredEvents.length,
  };
}
