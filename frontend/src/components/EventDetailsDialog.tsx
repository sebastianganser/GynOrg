import type { CalendarEvent } from '../utils/calendarFilters';
import { getEventTypeLabel, getEventTypeColor } from '../utils/calendarFilters';

interface EventDetailsDialogProps {
  event: CalendarEvent | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * EventDetailsDialog Component
 * 
 * Displays detailed information about a calendar event in a modal dialog.
 * Shows event type, dates, description, and employee information.
 */
export function EventDetailsDialog({
  event,
  open,
  onOpenChange,
}: EventDetailsDialogProps) {
  if (!event) return null;

  const formatDate = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('de-DE', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDateShort = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('de-DE');
  };

  // Calculate duration in days
  const calculateDuration = () => {
    const start = new Date(event.start);
    const end = new Date(event.end);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays === 0 ? 1 : diffDays;
  };

  const duration = calculateDuration();

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50"
        onClick={() => onOpenChange(false)}
      />

      {/* Dialog */}
      <div className="relative z-50 w-full max-w-[500px] bg-card rounded-lg shadow-lg p-6 m-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: event.color || '#6b7280' }}
            />
            <h2 className="text-lg font-semibold">{event.title}</h2>
          </div>
          <button
            onClick={() => onOpenChange(false)}
            className="text-muted-foreground hover:text-foreground"
          >
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
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4">
          {/* Event Type */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-muted-foreground w-24">
              Typ:
            </span>
            <span
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              style={{
                backgroundColor: getEventTypeColor(event.type),
                color: 'white',
              }}
            >
              {getEventTypeLabel(event.type)}
            </span>
          </div>

          {/* Start Date */}
          <div className="flex items-start gap-2">
            <span className="text-sm font-medium text-muted-foreground w-24">
              Beginn:
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium">{formatDate(event.start)}</p>
              <p className="text-xs text-muted-foreground">
                {formatDateShort(event.start)}
              </p>
            </div>
          </div>

          {/* End Date */}
          <div className="flex items-start gap-2">
            <span className="text-sm font-medium text-muted-foreground w-24">
              Ende:
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium">{formatDate(event.end)}</p>
              <p className="text-xs text-muted-foreground">
                {formatDateShort(event.end)}
              </p>
            </div>
          </div>

          {/* Duration */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-muted-foreground w-24">
              Dauer:
            </span>
            <span className="text-sm">
              {duration} {duration === 1 ? 'Tag' : 'Tage'}
              {event.halfDayTime === 'AM' && ' (Vormittag)'}
              {event.halfDayTime === 'PM' && ' (Nachmittag)'}
            </span>
          </div>

          {/* Description */}
          {event.description && (
            <div className="flex items-start gap-2">
              <span className="text-sm font-medium text-muted-foreground w-24">
                Beschreibung:
              </span>
              <p className="text-sm flex-1">{event.description}</p>
            </div>
          )}

          {/* Employee ID (for debugging/admin) */}
          {event.employeeId && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground w-24">
                Mitarbeiter-ID:
              </span>
              <span className="text-sm font-mono">{event.employeeId}</span>
            </div>
          )}

          {/* All Day indicator */}
          {event.allDay && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground w-24">
                Ganztägig:
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded border text-xs">
                Ja
              </span>
            </div>
          )}
        </div>

        {/* Footer with event ID for reference */}
        <div className="border-t mt-4 pt-4">
          <p className="text-xs text-muted-foreground">
            Event-ID: {event.id}
          </p>
        </div>
      </div>
    </div>
  );
}
