import { useCallback, useMemo } from 'react';
import { Calendar, momentLocalizer, View, Event } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/de';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import '../styles/team-calendar.css';
import type { CalendarEvent } from '../utils/calendarFilters';
import { getEventTypeLabel } from '../utils/calendarFilters';
import { getTextColorForBackground } from '../utils/colorUtils';
import { useHolidays } from '../hooks/useHolidays';
import { useCalendarSettings } from '../hooks/useCalendarSettings';
import { HolidayType, formatHolidayDisplayName } from '../types/holiday';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';

// Configure moment for German locale
moment.locale('de');
const localizer = momentLocalizer(moment);

/**
 * TeamCalendar Component Props
 */
interface TeamCalendarProps {
  events: CalendarEvent[];
  onEventClick?: (event: CalendarEvent) => void;
  defaultView?: View;
  className?: string;
  showCalendarWeeks?: boolean;
}

/**
 * Custom Event Component for react-big-calendar
 * Displays events with custom styling and color
 */
interface EventProps {
  event: CalendarEvent;
}

function CustomEvent({ event }: EventProps) {
  const bgColor = event.color || '#6b7280';
  const textColor = getTextColorForBackground(bgColor);
  const halfDayText = event.halfDayTime === 'AM' ? ' (Vormittag)' : event.halfDayTime === 'PM' ? ' (Nachmittag)' : '';
  const displayTitle = `${event.title}${halfDayText}`;

  return (
    <div
      className="rbc-event-content"
      style={{
        backgroundColor: bgColor,
        color: textColor,
        borderRadius: '4px',
        padding: '2px 4px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
      }}
      title={`${displayTitle} - ${getEventTypeLabel(event.type)}`}
    >
      <strong>{displayTitle}</strong>
    </div>
  );
}

/**
 * TeamCalendar Component
 * 
 * Displays a calendar view with filtered events from employees, holidays, and absences.
 * Uses react-big-calendar with German localization and custom styling.
 * 
 * Features:
 * - Month/Week/Day/Agenda views
 * - Color-coded events by employee or type
 * - Event tooltips with details
 * - Responsive design
 * - German localization
 */
export function TeamCalendar({
  events,
  onEventClick,
  defaultView = 'month',
  className = '',
  showCalendarWeeks = false,
}: TeamCalendarProps) {
  // We need to fetch holidays to render them in the headers
  const { data: calendarSettings } = useCalendarSettings();
  const { holidays } = useHolidays(new Date().getFullYear());
  const userFederalState = calendarSettings?.employer_federal_state;
  const { showHolidays } = useCalendarFilterStore();

  // Transform CalendarEvent to react-big-calendar Event format
  const calendarEvents = useMemo(() => {
    return events.map((event) => ({
      ...event,
      start: new Date(event.start),
      end: new Date(event.end),
      title: event.title,
      resource: event,
    }));
  }, [events]);

  // Handle event selection
  const handleSelectEvent = useCallback(
    (event: Event) => {
      if (onEventClick && event.resource) {
        onEventClick(event.resource as CalendarEvent);
      }
    },
    [onEventClick]
  );

  // Styles for day cells (e.g. weekends, holidays)
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
      className: `${isNonWorkingDay ? 'bg-muted/30' : 'bg-background'} ${isToday ? 'bg-primary/5' : ''}`,
      style: {
        backgroundColor: isToday ? 'hsl(var(--primary) / 0.05)' : isNonWorkingDay ? '#f9fafb' : undefined,
      }
    };
  }, [holidays, userFederalState, calendarEvents, showHolidays]);

  // Custom event style getter
  const eventStyleGetter = useCallback((event: Event) => {
    const calendarEvent = event.resource as CalendarEvent;
    const baseColor = calendarEvent.color || '#6b7280';
    
    let background = baseColor;
    if (calendarEvent.halfDayTime === 'AM') {
      background = `linear-gradient(135deg, ${baseColor} 50%, transparent 50%)`;
    } else if (calendarEvent.halfDayTime === 'PM') {
      background = `linear-gradient(135deg, transparent 50%, ${baseColor} 50%)`;
    }

    return {
      style: {
        background: background,
        borderRadius: '4px',
        opacity: 0.9,
        color: getTextColorForBackground(baseColor),
        border: calendarEvent.halfDayTime ? `1px solid ${baseColor}` : 'none',
        display: 'block',
        fontSize: '0.875rem',
        padding: '2px 4px',
      },
    };
  }, []);

  // German messages for calendar
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
    noEventsInRange: 'Keine Ereignisse in diesem Zeitraum.',
    showMore: (total: number) => `+ ${total} weitere`,
  };

  // German day and month names
  const formats = {
    dayFormat: 'dd DD',
    weekdayFormat: 'dddd',
    monthHeaderFormat: 'MMMM YYYY',
    dayHeaderFormat: 'dddd, DD. MMMM YYYY',
    dayRangeHeaderFormat: ({ start, end }: { start: Date; end: Date }) =>
      `${moment(start).format('DD. MMM')} - ${moment(end).format('DD. MMM YYYY')}`,
    agendaHeaderFormat: ({ start, end }: { start: Date; end: Date }) =>
      `${moment(start).format('DD. MMM')} - ${moment(end).format('DD. MMM YYYY')}`,
  };

  // Custom Date Header to show Week Number (KW) if needed
  const CustomDateHeader = ({ label, date }: { label: string, date: Date }) => {
    const isToday = moment(date).isSame(moment(), 'day');
    // Only show the KW on Mondays
    const isMonday = moment(date).day() === 1;
    const kw = moment(date).isoWeek();

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
            ${isToday ? 'bg-primary !text-primary-foreground !font-bold' : publicHoliday ? '' : 'text-foreground'}
          `}
        >
          {label}
        </span>
      </div>
    );
  };

  return (
    <div className={`team-calendar-wrapper ${className}`}>
      <Calendar
        localizer={localizer}
        events={calendarEvents}
        startAccessor="start"
        endAccessor="end"
        style={{ height: '100%', minHeight: '600px' }}
        defaultView={defaultView}
        views={['month', 'week', 'day', 'agenda']}
        messages={messages}
        formats={formats}
        onSelectEvent={handleSelectEvent}
        eventPropGetter={eventStyleGetter}
        dayPropGetter={dayPropGetter}
        components={{
          event: CustomEvent,
          month: {
            dateHeader: CustomDateHeader
          }
        }}
        popup
        selectable={false}
        tooltipAccessor={(event: Event) => {
          const calendarEvent = event.resource as CalendarEvent;
          return `${calendarEvent.title}\n${getEventTypeLabel(calendarEvent.type)}${calendarEvent.description ? `\n${calendarEvent.description}` : ''
            }`;
        }}
      />
    </div>
  );
}
