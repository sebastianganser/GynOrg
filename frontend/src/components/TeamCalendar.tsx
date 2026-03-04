import { useCallback, useMemo } from 'react';
import { Calendar, momentLocalizer, View, Event } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/de';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import '../styles/team-calendar.css';
import type { CalendarEvent } from '../utils/calendarFilters';
import { getEventTypeLabel } from '../utils/calendarFilters';
import { getTextColorForBackground } from '../utils/colorUtils';

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
      title={`${event.title} - ${getEventTypeLabel(event.type)}`}
    >
      <strong>{event.title}</strong>
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

  // Custom event style getter
  const eventStyleGetter = useCallback((event: Event) => {
    const calendarEvent = event.resource as CalendarEvent;
    const bgColor = calendarEvent.color || '#6b7280';
    return {
      style: {
        backgroundColor: bgColor,
        borderRadius: '4px',
        opacity: 0.9,
        color: getTextColorForBackground(bgColor),
        border: 'none',
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
            ${isToday ? 'bg-primary text-primary-foreground' : 'text-foreground'}
            ${(!showCalendarWeeks || !isMonday) ? 'ml-auto' : ''}
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
