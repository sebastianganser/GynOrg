import React, { useState, useMemo, useCallback } from 'react';
import { Calendar, momentLocalizer, View, Views } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import { useHolidays } from '../hooks/useHolidays';
import { useEmployees } from '../hooks/useEmployees';
import { useCalendarSettings } from '../hooks/useCalendarSettings';
import { Absence, CalendarAbsence } from '../types/absence';
import { Holiday, HolidayType, getHolidayColor, getHolidayIcon, formatHolidayDisplayName, getSchoolVacationTypeLabel, SchoolVacationType } from '../types/holiday';
import { Employee } from '../types/employee';
import { getTextColorForBackground } from '../utils/colorUtils';

// Initialize moment localizer
moment.locale('de');
const localizer = momentLocalizer(moment);

// Override sortEvents to always place school vacations (marked with minute=1)
// above absences, regardless of event duration.
const originalSortEvents = (localizer as any).sortEvents;
(localizer as any).sortEvents = (args: any) => {
  const aMin = args.evtA.start?.getMinutes?.() ?? 0;
  const bMin = args.evtB.start?.getMinutes?.() ?? 0;
  const aIsVac = aMin === 1;
  const bIsVac = bMin === 1;
  // If one is a vacation and the other isn't, vacation wins (goes first = negative)
  if (aIsVac && !bIsVac) return -1;
  if (!aIsVac && bIsVac) return 1;
  // Otherwise fall back to default RBC sort
  return originalSortEvents(args);
};

interface AbsenceCalendarProps {
  absences: Absence[];
  onSelectEvent: (event: any) => void;
  onSelectSlot: (slotInfo: { start: Date; end: Date }) => void;
  onNewAbsence: (start: Date, end: Date) => void;
  filters?: any;
  onFiltersChange?: (filters: any) => void;
  loading?: boolean;
  userFederalState?: string;
}

type ExtendedView = View | 'year';

// Algorithm to generate multi-day span events for consolidated display
// RBC renders multi-day events above single-day events, so we must
// create proper multi-day spans to compete with multi-day absences.
const generateDailyConsolidatedEvents = (holidays: Holiday[]) => {
  // 1. Map all holidays to their specific days
  const dayMap = new Map<string, Holiday[]>(); // "YYYY-MM-DD" -> Holidays[]

  holidays.forEach(h => {
    const start = moment(h.date);
    const end = h.end_date ? moment(h.end_date) : moment(h.date);

    let current = start.clone();
    while (current.isSameOrBefore(end, 'day')) {
      const dateStr = current.format('YYYY-MM-DD');
      if (!dayMap.has(dateStr)) {
        dayMap.set(dateStr, []);
      }
      dayMap.get(dateStr)?.push(h);
      current.add(1, 'day');
    }
  });

  // 2. Build daily type info
  const dailyTypeInfo = new Map<string, Map<string, { states: Set<string>, type: SchoolVacationType | undefined, name: string }>>();

  dayMap.forEach((daysHolidays, dateStr) => {
    const typeGroups = new Map<string, { states: Set<string>, type: SchoolVacationType | undefined, name: string }>();

    daysHolidays.forEach(h => {
      const key = h.school_vacation_type || h.name;

      if (!typeGroups.has(key)) {
        typeGroups.set(key, { states: new Set<string>(), type: h.school_vacation_type, name: h.name });
      }

      const group = typeGroups.get(key)!;
      if (h.federal_state_code) group.states.add(h.federal_state_code);
      else if (h.federal_state) group.states.add(h.federal_state);
    });

    dailyTypeInfo.set(dateStr, typeGroups);
  });

  // 3. Merge consecutive days of the same type into multi-day spans
  const sortedDates = Array.from(dailyTypeInfo.keys()).sort();
  const spans: any[] = [];
  const activeSpans = new Map<string, { startDate: string, endDate: string, states: string, title: string, props: any }>();

  sortedDates.forEach(dateStr => {
    const typeGroups = dailyTypeInfo.get(dateStr)!;
    const currentKeys = new Set<string>();

    typeGroups.forEach((info, key) => {
      currentKeys.add(key);
      const sortedStates = Array.from(info.states).sort().join(', ');
      const nameLabel = info.type ? getSchoolVacationTypeLabel(info.type) : info.name;
      const title = sortedStates ? `${nameLabel} (${sortedStates})` : nameLabel;
      const spanKey = `${key}::${sortedStates}`;

      const existing = activeSpans.get(spanKey);
      if (existing) {
        // Check if this date is consecutive (next day)
        const prevEnd = moment(existing.endDate, 'YYYY-MM-DD');
        const currDate = moment(dateStr, 'YYYY-MM-DD');
        if (currDate.diff(prevEnd, 'days') <= 1) {
          // Extend the span
          existing.endDate = dateStr;
        } else {
          // Gap found - finalize old span, start new one
          spans.push({ ...existing });
          activeSpans.set(spanKey, { startDate: dateStr, endDate: dateStr, states: sortedStates, title, props: { name: info.name, type: info.type } });
        }
      } else {
        activeSpans.set(spanKey, { startDate: dateStr, endDate: dateStr, states: sortedStates, title, props: { name: info.name, type: info.type } });
      }
    });

    // Close spans for types not present on this day
    activeSpans.forEach((span, spanKey) => {
      const typeKey = spanKey.split('::')[0];
      if (!currentKeys.has(typeKey)) {
        spans.push({ ...span });
        activeSpans.delete(spanKey);
      }
    });
  });

  // Finalize remaining spans
  activeSpans.forEach(span => spans.push({ ...span }));

  // 4. Convert spans to calendar events
  return spans.map(span => {
    // Set minute=1 as marker so our custom sortEvents recognizes school vacations
    const startDate = moment(span.startDate, 'YYYY-MM-DD').minute(1).toDate();
    // Add 1 day to end for RBC exclusive end-date handling
    const endDate = moment(span.endDate, 'YYYY-MM-DD').add(1, 'day').toDate();

    return {
      id: `vacation-${span.props.type || span.props.name}-${span.startDate}`,
      title: span.title,
      start: startDate,
      end: endDate,
      allDay: true,
      resource: {
        name: span.props.name,
        school_vacation_type: span.props.type,
        consolidated: true
      },
      isConsolidated: true,
      holidayType: HolidayType.SCHOOL_VACATION
    };
  });
};

export const AbsenceCalendar: React.FC<AbsenceCalendarProps> = ({
  absences,
  onSelectEvent,
  onSelectSlot,
  onNewAbsence,
  loading = false,
  userFederalState
}) => {
  const [view, setView] = useState<ExtendedView>(Views.MONTH);
  const [date, setDate] = useState(new Date());

  // Local filter state for Absences (Status/Type) - keeping simple for now
  const [absenceStatusFilter, setAbsenceStatusFilter] = useState<string>('');
  const [absenceTypeFilter, setAbsenceTypeFilter] = useState<string>('');

  // Global store for Holiday filters
  const { showHolidays, showSchoolVacations, selectedEmployeeIds, selectedAbsenceTypeIds } = useCalendarFilterStore();

  const { data: calendarSettings } = useCalendarSettings();
  const { data: employees } = useEmployees(false);

  // Holidays
  const { holidays } = useHolidays(date.getFullYear());

  // Filter and Process Absences
  const filteredAbsences = useMemo(() => {
    return absences.filter(absence => {
      // 1. Filter by Employee
      if (selectedEmployeeIds.length > 0 && !selectedEmployeeIds.includes(absence.employee_id)) {
        return false;
      }

      // 2. Filter by Absence Type
      if (selectedAbsenceTypeIds.length > 0 && !selectedAbsenceTypeIds.includes(absence.absence_type_id)) {
        return false;
      }

      // 3. Optional status filter (local state)
      if (absenceStatusFilter && absence.status !== absenceStatusFilter) return false;

      return true;
    }).map((absence): CalendarAbsence => {
      const employee = employees?.find(e => e.id === absence.employee_id);
      const initials = employee?.initials || (employee ? `${employee.first_name?.[0] || ''}${employee.last_name?.[0] || ''}` : '');
      const typeName = absence.absence_type?.name || 'Abwesenheit';
      
      let displaySuffix = '';
      if (initials || absence.comment) {
        const parts = [];
        if (initials) parts.push(initials);
        if (absence.comment) parts.push(absence.comment);
        displaySuffix = ` (${parts.join(' - ')})`;
      }

      // Parse date strings as local midnight to avoid UTC timezone shift
      const parseLocalDate = (dateStr: string): Date => {
        const [y, m, d] = dateStr.split('-').map(Number);
        return new Date(y, m - 1, d);
      };

      // react-big-calendar treats allDay end dates as exclusive,
      // so add 1 day to include the last day visually
      const endDate = parseLocalDate(absence.end_date as unknown as string);
      endDate.setDate(endDate.getDate() + 1);

      return {
        id: absence.id,
        title: `${typeName}${displaySuffix}`,
        start: parseLocalDate(absence.start_date as unknown as string),
        end: endDate,
        resource: absence,
        allDay: true,
        color: employee?.calendar_color || '#3b82f6'
      };
    });
  }, [absences, absenceStatusFilter, selectedEmployeeIds, selectedAbsenceTypeIds, employees]);

  // Filter and Process Holidays
  const calendarHolidays = useMemo(() => {
    const events: any[] = [];

    // 1. Public Holidays
    // NOTE: Public Holidays are no longer added as blocks to the grid. 
    // They are rendered directly in the CustomDateHeader.

    // 2. School Vacations - CONSOLIDATED
    if (showSchoolVacations) {
      const vacations = holidays?.filter(h => h.holiday_type === HolidayType.SCHOOL_VACATION) || [];
      const consolidated = generateDailyConsolidatedEvents(vacations);
      events.push(...consolidated);
    }

    return events;
  }, [holidays, showSchoolVacations]);

  // Generate All Events - holidays FIRST so they render above absences
  const allEvents = useMemo(() => {
    return [...calendarHolidays, ...filteredAbsences];
  }, [filteredAbsences, calendarHolidays]);

  // Styles
  const dayPropGetter = useCallback((calendarDate: Date) => {
    const day = calendarDate.getDay();
    const isWeekend = day === 0 || day === 6; // Sunday or Saturday
    const today = new Date();
    const isToday = moment(calendarDate).isSame(today, 'day');

    const dateStr = moment(calendarDate).format('YYYY-MM-DD');
    const isPublicHoliday = showHolidays && holidays?.some(h => 
      h.holiday_type === HolidayType.PUBLIC_HOLIDAY && 
      moment(h.date).format('YYYY-MM-DD') === dateStr &&
      (h.is_nationwide || !userFederalState || h.federal_state === userFederalState)
    );

    const isNonWorkingDay = isWeekend || isPublicHoliday;

    return {
      className: `${isNonWorkingDay ? 'bg-gray-50' : 'bg-white'} ${isToday ? 'bg-blue-50' : ''}`,
      style: {
        backgroundColor: isToday ? '#eff6ff' : isNonWorkingDay ? '#f9fafb' : undefined,
        minHeight: '180px'
      }
    };
  }, [holidays, userFederalState, showHolidays]);

  const eventPropGetter = useCallback((event: any) => {
    // Default opacity for text
    const style: any = {
      borderRadius: '4px',
      border: 'none',
      fontSize: '0.85rem',
      marginBottom: '2px',
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    };

    if (event.isSpacer) {
      return {
        style: {
          ...style,
          backgroundColor: 'transparent',
          color: 'transparent',
          height: '24px',
          pointerEvents: 'none' as 'none'
        }
      };
    }

    if (event.isHoliday || event.isConsolidated) {
      const holiday = event.resource as Holiday;
      const bgColor = getHolidayColor(holiday);
      return {
        style: {
          ...style,
          backgroundColor: bgColor,
          color: getTextColorForBackground(bgColor),
        },
        title: event.title // Native tooltip
      };
    }

    // Absence styling
    const absence = event.resource as Absence;
    const employee = employees?.find(e => e.id === absence.employee_id);
    const color = employee?.calendar_color || '#3b82f6';
    const isPending = absence.status === 'pending';
    
    let background: string = color;
    if (absence.half_day_time === 'AM') {
      background = `linear-gradient(135deg, ${color} 50%, transparent 50%)`;
    } else if (absence.half_day_time === 'PM') {
      background = `linear-gradient(135deg, transparent 50%, ${color} 50%)`;
    }

    return {
      style: {
        ...style,
        background: background,
        opacity: isPending ? 0.5 : 1,
        color: getTextColorForBackground(color),
        border: absence.half_day_time ? `1px solid ${color}` : 'none',
      },
      title: event.title // Native tooltip
    };
  }, [employees]);

  const handleNavigate = (newDate: Date) => setDate(newDate);
  const handleViewChange = (newView: View) => setView(newView);

  // Custom Date Header Component
  const CustomDateHeader = ({ label, date }: { label: string, date: Date }) => {
    const isToday = moment(date).isSame(moment(), 'day');
    const isMonday = moment(date).day() === 1;
    const kw = moment(date).isoWeek();
    const showCalendarWeeks = calendarSettings?.show_calendar_weeks ?? false;

    // FIND PUBLIC HOLIDAY
    const dateStr = moment(date).format('YYYY-MM-DD');
    const publicHoliday = showHolidays ? holidays?.find(h => 
      h.holiday_type === HolidayType.PUBLIC_HOLIDAY && 
      moment(h.date).format('YYYY-MM-DD') === dateStr &&
      (h.is_nationwide || !userFederalState || h.federal_state === userFederalState)
    ) : null;
    const formatName = publicHoliday ? formatHolidayDisplayName(publicHoliday) : null;

    return (
      <div className="flex justify-between items-center p-1 w-full relative">
        <div className="flex items-center min-w-0 flex-1 overflow-hidden mr-1 gap-1.5">
           {showCalendarWeeks && isMonday && (
             <span className="text-xs text-muted-foreground flex-shrink-0">
               KW{kw}
             </span>
           )}
           {formatName && (
             <span className="text-xs font-bold text-black truncate" title={formatName}>
               {formatName}
             </span>
           )}
        </div>
        
        <span
          className={`
            flex flex-shrink-0 justify-center items-center w-7 h-7 rounded-full text-sm 
            ${publicHoliday ? 'font-bold text-black' : 'font-medium'}
            ${isToday ? 'bg-blue-600 !text-white !font-bold' : publicHoliday ? '' : 'text-gray-700'}
          `}
        >
          {label}
        </span>
      </div>
    );
  };

  // Custom Event Component for refined rendering
  // Uses event.resource.displayTitle to show the clean title without prefix
  const CustomEvent = ({ event }: any) => {
    const title = event.resource?.displayTitle || event.title;
    const halfDayText = event.halfDayTime === 'AM' ? ' (Vormittag)' : event.halfDayTime === 'PM' ? ' (Nachmittag)' : '';
    const displayTitle = `${title}${halfDayText}`;
    return (
      <div title={displayTitle} className="w-full h-full overflow-hidden text-ellipsis whitespace-nowrap px-1">
        {displayTitle}
      </div>
    )
  }

  const messages = {
    allDay: 'Ganztägig',
    previous: 'Zurück',
    next: 'Weiter',
    today: 'Heute',
    month: 'Monat',
    week: 'Woche',
    day: 'Tag',
    agenda: 'Agenda',
    date: 'Datum',
    time: 'Zeit',
    event: 'Ereignis',
    work_week: 'Arbeitswoche',
    showMore: (total: number) => `+${total} mehr`,
    noEventsInRange: 'Keine Ereignisse in diesem Zeitraum.'
  };

  if (loading) {
    return <div className="p-10 text-center">Lade Kalender...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden h-full flex flex-col">
      {/* Calendar */}
      <div className="flex-1 p-4 min-h-0">
        <Calendar
          localizer={localizer}
          events={allEvents}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          date={date}
          onNavigate={handleNavigate}
          view={view as View}
          onView={handleViewChange}
          onSelectEvent={onSelectEvent}
          onSelectSlot={onSelectSlot}
          selectable
          dayPropGetter={dayPropGetter}
          eventPropGetter={eventPropGetter}
          components={{
            month: {
              dateHeader: CustomDateHeader,
              event: CustomEvent
            }
          }}
          messages={messages}
          formats={{
            monthHeaderFormat: 'MMMM YYYY',
            weekdayFormat: (date, culture, localizer) =>
              localizer?.format(date, 'dd', culture) || ''
          }}
          culture="de"
        />
      </div>
    </div>
  );
};
