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

// Algorithm to generate daily events for consolidated display
const generateDailyConsolidatedEvents = (holidays: Holiday[]) => {
  // 1. Map all holidays to their specific days
  const dayMap = new Map<string, Holiday[]>(); // "YYYY-MM-DD" -> Holidays[]

  holidays.forEach(h => {
    const start = moment(h.date);
    const end = h.end_date ? moment(h.end_date) : moment(h.date);

    // Iterate through every day of this holiday
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

  const dailyEvents: any[] = [];

  // 2. Process each day to group by vacation type
  dayMap.forEach((daysHolidays, dateStr) => {
    // Group by Vacation Type on this specific day
    const typeGroups = new Map<string, Set<string>>(); // TypeKey -> Set<StateCode>
    const typeProps = new Map<string, { type: SchoolVacationType | undefined, name: string }>();

    daysHolidays.forEach(h => {
      // Key: Use school_vacation_type if avail, else name
      const key = h.school_vacation_type || h.name;

      if (!typeGroups.has(key)) {
        typeGroups.set(key, new Set<string>());
        typeProps.set(key, { type: h.school_vacation_type, name: h.name });
      }

      if (h.federal_state_code) typeGroups.get(key)?.add(h.federal_state_code);
      else if (h.federal_state) typeGroups.get(key)?.add(h.federal_state);
      // else nationwide?
    });

    // 3. Create Event for this day and type
    typeGroups.forEach((states, key) => {
      const sortedStates = Array.from(states).sort().join(', ');
      const props = typeProps.get(key)!;

      const nameLabel = props.type
        ? getSchoolVacationTypeLabel(props.type)
        : props.name;

      const title = sortedStates ? `${nameLabel} (${sortedStates})` : nameLabel;
      const dateObj = moment(dateStr, 'YYYY-MM-DD').toDate();

      dailyEvents.push({
        id: `daily-${key}-${dateStr}`,
        title: title,
        start: dateObj,
        end: dateObj, // Same day start/end forces single day rendering
        allDay: true,
        resource: {
          name: props.name,
          school_vacation_type: props.type,
          consolidated: true
        },
        isConsolidated: true,
        holidayType: HolidayType.SCHOOL_VACATION
      });
    });
  });

  return dailyEvents;
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
    }).map((absence): CalendarAbsence => ({
      id: absence.id,
      title: absence.absence_type?.name || 'Abwesenheit',
      start: new Date(absence.start_date),
      end: new Date(absence.end_date),
      resource: absence,
      allDay: true
    }));
  }, [absences, absenceStatusFilter, selectedEmployeeIds, selectedAbsenceTypeIds]);

  // Filter and Process Holidays
  const calendarHolidays = useMemo(() => {
    const events: any[] = [];

    // 1. Public Holidays (Keep them separate for now, or consolidate too?)
    // Usually Public Holidays are 1 day and nationwide or state specific.
    if (showHolidays) {
      const publicHolidays = holidays?.filter(h => h.holiday_type === HolidayType.PUBLIC_HOLIDAY) || [];
      publicHolidays.forEach(h => {
        if (!h.is_nationwide && userFederalState && h.federal_state !== userFederalState) return;

        events.push({
          id: `holiday-${h.id}`,
          title: formatHolidayDisplayName(h),
          start: new Date(h.date),
          end: new Date(h.date), // Public holidays are usually 1 day
          resource: h,
          allDay: true,
          isHoliday: true,
          holidayType: HolidayType.PUBLIC_HOLIDAY
        });
      });
    }

    // 2. School Vacations - CONSOLIDATED
    if (showSchoolVacations) {
      const vacations = holidays?.filter(h => h.holiday_type === HolidayType.SCHOOL_VACATION) || [];
      // Filter filtering logic? The fetcher already filters by 'School Vacation Federal States' setting.
      // But if we want to honor 'userFederalState' strictly, useConsolidated logic needs input.
      // User requested "Easter (BY, ST)", implying we show ALL selected states.

      const consolidated = generateDailyConsolidatedEvents(vacations);
      events.push(...consolidated);
    }

    return events;
  }, [holidays, showHolidays, showSchoolVacations, userFederalState]);

  // Generate Spacers and Sort Events
  const allEvents = useMemo(() => {
    let events = [...filteredAbsences, ...calendarHolidays];
    const holidayDates = new Set(
      calendarHolidays
        .filter((e: any) => e.holidayType === HolidayType.PUBLIC_HOLIDAY)
        .map((e: any) => moment(e.start).format('YYYY-MM-DD'))
    );

    const spacers: any[] = [];
    const vacationDays = new Set<string>();

    calendarHolidays.filter((e: any) => e.holidayType === HolidayType.SCHOOL_VACATION).forEach((vacation: any) => {
      // Since we now have discrete daily events (generateDailyConsolidatedEvents), 
      // strict 1-day duration logic applies.
      const dateStr = moment(vacation.start).format('YYYY-MM-DD');

      // Check if this day has a public holiday
      if (!holidayDates.has(dateStr)) {
        // NO Public Holiday -> Insert Spacer to force School Vacation to Row 2
        spacers.push({
          id: `spacer-${dateStr}`,
          title: '',
          start: vacation.start,
          end: vacation.end,
          allDay: true,
          isSpacer: true
        });
      }
    });

    events = [...events, ...spacers];

    // Custom Sort via Start Time Offset
    // RBC sorts by Start Time Ascending.
    // We want: Spacer/Holiday (Row 1) < Vacation (Row 2) < Absence (Row 3)
    // So we give them slightly different times on the same day.
    // Note: They are allDay=true, so they still render as full bars.

    return events.map(e => {
      const start = new Date(e.start);
      // Reset to 00:00 first
      start.setHours(0, 0, 0, 0);

      if (e.isSpacer) {
        // Priority 1: Spacer (Row 1) logic handles no-holiday days.
        start.setMinutes(0);
      } else if (e.isHoliday && e.holidayType === HolidayType.PUBLIC_HOLIDAY) {
        // Priority 1: Public Holiday (Row 1)
        start.setMinutes(1);
      } else if (e.isConsolidated || (e.isHoliday && e.holidayType === HolidayType.SCHOOL_VACATION)) {
        // Priority 2: School Vacation (Row 2)
        start.setMinutes(10);
      } else {
        // Priority 3: Absences
        start.setMinutes(30);
      }

      return {
        ...e,
        start: start,
        end: e.end, // Duration doesn't matter much for equal days
        // Ensure title is clean (no prefix)
        title: e.resource?.displayTitle || e.title
      };
    }).sort((a, b) => {
      // Sort by time
      return a.start.getTime() - b.start.getTime();
    });

  }, [filteredAbsences, calendarHolidays]);

  // Styles
  const dayPropGetter = useCallback((calendarDate: Date) => {
    const day = calendarDate.getDay();
    const isWeekend = day === 0 || day === 6; // Sunday or Saturday
    const today = new Date();
    const isToday = moment(calendarDate).isSame(today, 'day');

    return {
      className: `${isWeekend ? 'bg-gray-50' : 'bg-white'} ${isToday ? 'bg-blue-50' : ''}`,
      style: {
        backgroundColor: isToday ? '#eff6ff' : isWeekend ? '#f9fafb' : undefined,
        minHeight: '180px'
      }
    };
  }, []);

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
    const color = absence.absence_type?.color || '#3b82f6';
    return {
      style: {
        ...style,
        backgroundColor: color,
        color: getTextColorForBackground(color),
      },
      title: event.title // Native tooltip
    };
  }, []);

  const handleNavigate = (newDate: Date) => setDate(newDate);
  const handleViewChange = (newView: View) => setView(newView);

  // Custom Date Header Component
  const CustomDateHeader = ({ label, date }: { label: string, date: Date }) => {
    const isToday = moment(date).isSame(moment(), 'day');
    const isMonday = moment(date).day() === 1;
    const kw = moment(date).isoWeek();
    const showCalendarWeeks = calendarSettings?.show_calendar_weeks ?? false;

    return (
      <div className="flex justify-between items-center p-1 w-full relative">
        {showCalendarWeeks && isMonday && (
          <span className="text-xs text-muted-foreground mr-1 min-w-[3ch]">
            KW{kw}
          </span>
        )}
        {!showCalendarWeeks && isMonday && (
          <span className="min-w-[3ch] mr-1"></span>
        )}
        <span
          className={`
            flex justify-center items-center w-7 h-7 rounded-full text-sm font-medium
            ${isToday ? 'bg-blue-600 text-white' : 'text-gray-700'}
            ${(!showCalendarWeeks || !isMonday) ? 'ml-auto' : ''}
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
    return (
      <div title={title} className="w-full h-full overflow-hidden text-ellipsis whitespace-nowrap px-1">
        {title}
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
