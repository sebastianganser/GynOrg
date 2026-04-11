import { useMemo } from 'react';
import { useAbsences } from './useAbsences';
import { useEmployees } from './useEmployees';
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

  // Parse date strings as local midnight to avoid UTC timezone shift
  const parseLocalDate = (dateStr: string): Date => {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d);
  };

  return {
    id: `absence-${absence.id}`,
    title: absenceTypeName,
    start: parseLocalDate(absence.start_date as unknown as string),
    end: parseLocalDate(absence.end_date as unknown as string),
    type: mapAbsenceTypeToEventType(),
    employeeId: absence.employee_id,
    absenceTypeId: absence.absence_type_id,
    allDay: !absence.half_day_time,
    description: absence.comment || undefined,
    halfDayTime: absence.half_day_time || null,
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

  // Fetch employees for initials
  const { data: employees } = useEmployees(false);

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
      const absenceEvents = absences.map(absence => {
        const event = transformAbsenceToEvent(absence);
        const employee = employees?.find(e => e.id === absence.employee_id);
        const initials = employee?.initials || (employee ? `${employee.first_name?.[0] || ''}${employee.last_name?.[0] || ''}` : '');
        event.color = employee?.calendar_color || '#3b82f6';
        
        let displaySuffix = '';
        if (initials || absence.comment) {
          const parts = [];
          if (initials) parts.push(initials);
          if (absence.comment) parts.push(absence.comment);
          displaySuffix = ` (${parts.join(' - ')})`;
        }
        
        event.title = `${event.title}${displaySuffix}`;
        return event;
      });
      allEvents.push(...absenceEvents);
    }

    // Add holiday events (Exclude PUBLIC_HOLIDAYs, as they are rendered in the cell header now)
    if (holidays && Array.isArray(holidays)) {
      const holidayEvents = holidays
        .filter(h => h.holiday_type !== 'PUBLIC_HOLIDAY')
        .map(h => transformHolidayToEvent(h, settings));
      allEvents.push(...holidayEvents);
    }

    return allEvents;
  }, [absences, holidays, settings, employees]);

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
