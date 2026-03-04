import { useMemo } from 'react';
import { useAbsences } from './useAbsences';
import { useHolidays } from './useHolidays';
import type { CalendarEvent, CalendarEventType } from '../utils/calendarFilters';
import type { Absence } from '../types/absence';
import type { Holiday } from '../types/holiday';
import { useCalendarSettings } from './useCalendarSettings';
import type { CalendarSettings } from '../types/calendarSettings';

/**
 * Map absence type to calendar event type
 */
function mapAbsenceTypeToEventType(): CalendarEventType {
  return 'absence';
}

/**
 * Transform absence to calendar event
 */
function transformAbsenceToEvent(absence: Absence): CalendarEvent {
  // Get absence type name from the nested absence_type object
  const absenceTypeName = absence.absence_type?.name || 'Urlaub';

  return {
    id: `absence-${absence.id}`,
    title: absenceTypeName,
    start: new Date(absence.start_date),
    end: new Date(absence.end_date),
    type: mapAbsenceTypeToEventType(),
    employeeId: absence.employee_id,
    absenceTypeId: absence.absence_type_id,
    color: absence.absence_type?.color || undefined,
    allDay: true,
    description: absence.comment || undefined,
  };
}

/**
 * Transform holiday to calendar event
 */
function transformHolidayToEvent(holiday: Holiday, settings?: CalendarSettings): CalendarEvent {
  // Determine if it's a school vacation or public holiday
  const isSchoolVacation = holiday.holiday_type === 'SCHOOL_VACATION';

  return {
    id: `holiday-${holiday.id}`,
    title: holiday.name,
    start: new Date(holiday.date),
    end: new Date(holiday.date),
    type: isSchoolVacation ? 'school_vacation' : 'holiday',
    color: isSchoolVacation ? settings?.school_vacation_color : settings?.holiday_color,
    allDay: true,
    description: holiday.federal_state_code
      ? `Bundesland: ${holiday.federal_state_code}`
      : undefined,
  };
}

/**
 * Hook to load and combine all calendar events
 * 
 * Fetches data from:
 * - Absences (vacation, sick leave, training, special leave)
 * - Holidays (public holidays)
 * - School Vacations (from holidays with type SCHULFERIEN)
 * 
 * @returns Combined calendar events with loading and error states
 */
export function useCalendarEvents() {
  // Fetch absences
  const {
    data: absences,
    isLoading: absencesLoading,
    error: absencesError,
  } = useAbsences();

  // Fetch holidays for current year
  const currentYear = new Date().getFullYear();
  const {
    holidays,
    loading: holidaysLoading,
    error: holidaysError,
  } = useHolidays(currentYear);

  // Fetch calendar settings for colors
  const { data: settings } = useCalendarSettings();

  // Combine loading states
  const isLoading = absencesLoading || holidaysLoading;

  // Combine error states
  const error = absencesError || holidaysError;

  // Transform and combine all events
  const events = useMemo(() => {
    const allEvents: CalendarEvent[] = [];

    // Add absence events
    if (absences && Array.isArray(absences)) {
      const absenceEvents = absences.map(transformAbsenceToEvent);
      allEvents.push(...absenceEvents);
    }

    // Add holiday events
    if (holidays && Array.isArray(holidays)) {
      const holidayEvents = holidays.map(h => transformHolidayToEvent(h, settings));
      allEvents.push(...holidayEvents);
    }

    return allEvents;
  }, [absences, holidays, settings]);

  // Calculate statistics
  const stats = useMemo(() => {
    const absenceCount = absences?.length || 0;
    const holidayCount = holidays?.filter((h: Holiday) => h.holiday_type === 'PUBLIC_HOLIDAY').length || 0;
    const schoolVacationCount = holidays?.filter((h: Holiday) => h.holiday_type === 'SCHOOL_VACATION').length || 0;

    return {
      total: events.length,
      absences: absenceCount,
      holidays: holidayCount,
      schoolVacations: schoolVacationCount,
    };
  }, [events, absences, holidays]);

  return {
    events,
    isLoading,
    error,
    stats,
  };
}
