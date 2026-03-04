import type { CalendarFilters } from '../stores/calendarFilterStore';

/**
 * Calendar Event Type
 * Represents different types of calendar events
 */
export type CalendarEventType =
  | 'holiday'
  | 'school_vacation'
  | 'vacation' // Keeping vacation as fallback or generic if needed, better to use 'absence'
  | 'absence';

/**
 * Calendar Event Interface
 * Base structure for all calendar events
 */
export interface CalendarEvent {
  id: string | number;
  title: string;
  start: Date | string;
  end: Date | string;
  type: CalendarEventType;
  employeeId?: number;
  absenceTypeId?: number;
  color?: string;
  allDay?: boolean;
  description?: string;
}

/**
 * Filter events by selected employee IDs
 * 
 * @param events - Array of calendar events
 * @param selectedEmployeeIds - Array of selected employee IDs
 * @returns Filtered events that belong to selected employees or have no employee association
 */
export function filterEventsByEmployees(
  events: CalendarEvent[],
  selectedEmployeeIds: number[]
): CalendarEvent[] {
  // If no employees selected, show ALL events
  // This handles the case when employees haven't loaded yet
  if (selectedEmployeeIds.length === 0) {
    return events;
  }

  // Filter events: keep non-employee events AND selected employee events
  return events.filter((event) => {
    // Keep events without employeeId (holidays, school vacations)
    // These were already filtered by type filter
    if (!event.employeeId) {
      return true;
    }

    // For employee events: only keep if employee is selected
    return selectedEmployeeIds.includes(event.employeeId);
  });
}

/**
 * Filter events by calendar type filters
 * 
 * @param events - Array of calendar events
 * @param filters - Calendar filter settings
 * @returns Filtered events based on enabled calendar types
 */
export function filterEventsByType(
  events: CalendarEvent[],
  filters: Omit<CalendarFilters, 'selectedEmployeeIds' | 'isSidebarCollapsed'>
): CalendarEvent[] {
  console.log('[filterEventsByType] Input:', {
    totalEvents: events.length,
    showHolidays: filters.showHolidays,
    holidayEvents: events.filter(e => e.type === 'holiday').length,
  });

  const filtered = events.filter((event) => {
    switch (event.type) {
      case 'holiday':
        return filters.showHolidays;
      case 'school_vacation':
        return filters.showSchoolVacations;
      case 'absence':
      case 'vacation':
        // If we have selected IDs, only show if it matches
        if (event.absenceTypeId !== undefined && filters.selectedAbsenceTypeIds.length > 0) {
          return filters.selectedAbsenceTypeIds.includes(event.absenceTypeId);
        }
        return true;
      default:
        return true;
    }
  });

  console.log('[filterEventsByType] Output:', {
    filteredEvents: filtered.length,
    holidayEvents: filtered.filter(e => e.type === 'holiday').length,
  });

  return filtered;
}

/**
 * Get default color for event type
 * 
 * @param type - Calendar event type
 * @returns Hex color code
 */
export function getEventTypeColor(type: CalendarEventType): string {
  const colorMap: Record<CalendarEventType, string> = {
    holiday: '#ef4444', // red-500
    school_vacation: '#3b82f6', // blue-500
    vacation: '#22c55e', // green-500
    absence: '#6b7280', // generic gray
  };

  return colorMap[type] || '#6b7280'; // gray-500 as fallback
}

/**
 * Apply color mapping to events
 * Uses employee calendar color if available, otherwise uses type-based color
 * 
 * @param events - Array of calendar events
 * @param employeeColorMap - Map of employee IDs to their calendar colors
 * @returns Events with applied colors
 */
export function applyColorMapping(
  events: CalendarEvent[],
  employeeColorMap: Map<number, string>
): CalendarEvent[] {
  return events.map((event) => {
    // Use employee color if available
    if (event.employeeId && employeeColorMap.has(event.employeeId)) {
      return {
        ...event,
        color: employeeColorMap.get(event.employeeId),
      };
    }

    // Use existing color or type-based color
    return {
      ...event,
      color: event.color || getEventTypeColor(event.type),
    };
  });
}

/**
 * Apply all filters to calendar events
 * Combines employee filtering, type filtering, and color mapping
 * 
 * @param events - Array of calendar events
 * @param filters - Complete calendar filter settings
 * @param employeeColorMap - Map of employee IDs to their calendar colors
 * @returns Fully filtered and colored events
 */
export function applyCalendarFilters(
  events: CalendarEvent[],
  filters: CalendarFilters,
  employeeColorMap: Map<number, string>
): CalendarEvent[] {
  // Step 1: Filter by calendar types FIRST (important for holidays/school vacations)
  let filteredEvents = filterEventsByType(events, {
    showHolidays: filters.showHolidays,
    showSchoolVacations: filters.showSchoolVacations,
    selectedAbsenceTypeIds: filters.selectedAbsenceTypeIds,
  });

  // Step 2: Filter by employees
  filteredEvents = filterEventsByEmployees(filteredEvents, filters.selectedEmployeeIds);

  // Step 3: Apply color mapping
  filteredEvents = applyColorMapping(filteredEvents, employeeColorMap);

  return filteredEvents;
}

/**
 * Create employee color map from employee data
 * 
 * @param employees - Array of employees with calendar colors
 * @returns Map of employee IDs to colors
 */
export function createEmployeeColorMap(
  employees: Array<{ id: number; calendar_color: string }>
): Map<number, string> {
  const colorMap = new Map<number, string>();

  employees.forEach((employee) => {
    colorMap.set(employee.id, employee.calendar_color);
  });

  return colorMap;
}

/**
 * Get event type label in German
 * 
 * @param type - Calendar event type
 * @returns German label for the event type
 */
export function getEventTypeLabel(type: CalendarEventType): string {
  const labelMap: Record<CalendarEventType, string> = {
    holiday: 'Feiertag',
    school_vacation: 'Schulferien',
    vacation: 'Urlaub',
    absence: 'Abwesenheit',
  };

  return labelMap[type] || 'Unbekannt';
}

/**
 * Check if any filters are active
 * 
 * @param filters - Calendar filter settings
 * @returns True if any filter is disabled
 */
export function hasActiveFilters(filters: CalendarFilters): boolean {
  return (
    !filters.showHolidays ||
    !filters.showSchoolVacations ||
    filters.selectedAbsenceTypeIds.length > 0 || // Actually, should only trigger if it's not all
    filters.selectedEmployeeIds.length === 0
  );
}

/**
 * Get count of active filters
 * 
 * @param filters - Calendar filter settings
 * @returns Number of disabled filters
 */
export function getActiveFilterCount(filters: CalendarFilters): number {
  let count = 0;

  if (!filters.showHolidays) count++;
  if (!filters.showSchoolVacations) count++;
  if (filters.selectedAbsenceTypeIds.length > 0) count++;

  return count;
}
