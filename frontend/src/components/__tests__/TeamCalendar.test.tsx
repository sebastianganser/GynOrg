import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TeamCalendar } from '../TeamCalendar';
import type { CalendarEvent } from '../../utils/calendarFilters';

// Mock react-big-calendar
vi.mock('react-big-calendar', () => ({
  Calendar: ({ events, onSelectEvent }: any) => (
    <div data-testid="mock-calendar">
      {events.map((event: any) => (
        <div
          key={event.id}
          data-testid={`event-${event.id}`}
          onClick={() => onSelectEvent(event)}
        >
          {event.title}
        </div>
      ))}
    </div>
  ),
  momentLocalizer: () => ({}),
}));

// Mock moment
vi.mock('moment', () => ({
  default: {
    locale: vi.fn(),
  },
}));

describe('TeamCalendar', () => {
  const mockEvents: CalendarEvent[] = [
    {
      id: 'event-1',
      title: 'Test Event 1',
      start: new Date('2025-01-01'),
      end: new Date('2025-01-05'),
      type: 'absence',
      allDay: true,
      color: '#22c55e',
    },
    {
      id: 'event-2',
      title: 'Test Event 2',
      start: new Date('2025-01-10'),
      end: new Date('2025-01-12'),
      type: 'holiday',
      allDay: true,
      color: '#ef4444',
    },
  ];

  it('should render calendar with events', () => {
    render(<TeamCalendar events={mockEvents} />);

    expect(screen.getByTestId('mock-calendar')).toBeInTheDocument();
    expect(screen.getByTestId('event-event-1')).toBeInTheDocument();
    expect(screen.getByTestId('event-event-2')).toBeInTheDocument();
  });

  it('should display event titles', () => {
    render(<TeamCalendar events={mockEvents} />);

    expect(screen.getByText('Test Event 1')).toBeInTheDocument();
    expect(screen.getByText('Test Event 2')).toBeInTheDocument();
  });

  it('should call onEventClick when event is clicked', () => {
    const onEventClick = vi.fn();
    render(<TeamCalendar events={mockEvents} onEventClick={onEventClick} />);

    const event = screen.getByTestId('event-event-1');
    fireEvent.click(event);

    expect(onEventClick).toHaveBeenCalledTimes(1);
    expect(onEventClick).toHaveBeenCalledWith(
      expect.objectContaining({
        id: 'event-1',
        title: 'Test Event 1',
      })
    );
  });

  it('should render with empty events array', () => {
    render(<TeamCalendar events={[]} />);

    expect(screen.getByTestId('mock-calendar')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <TeamCalendar events={mockEvents} className="custom-class" />
    );

    const wrapper = container.querySelector('.team-calendar-wrapper');
    expect(wrapper).toHaveClass('custom-class');
  });

  it('should handle events with different types', () => {
    const diverseEvents: CalendarEvent[] = [
      {
        id: 'vacation-1',
        title: 'Vacation',
        start: new Date('2025-01-01'),
        end: new Date('2025-01-05'),
        type: 'absence',
        allDay: true,
        color: '#22c55e',
      },
      {
        id: 'sick-1',
        title: 'Sick Leave',
        start: new Date('2025-01-10'),
        end: new Date('2025-01-12'),
        type: 'absence',
        allDay: true,
        color: '#f97316',
      },
      {
        id: 'training-1',
        title: 'Training',
        start: new Date('2025-01-15'),
        end: new Date('2025-01-16'),
        type: 'absence',
        allDay: true,
        color: '#a855f7',
      },
    ];

    render(<TeamCalendar events={diverseEvents} />);

    expect(screen.getByText('Vacation')).toBeInTheDocument();
    expect(screen.getByText('Sick Leave')).toBeInTheDocument();
    expect(screen.getByText('Training')).toBeInTheDocument();
  });

  it('should handle events with employee IDs', () => {
    const employeeEvents: CalendarEvent[] = [
      {
        id: 'emp-event-1',
        title: 'Employee 1 Vacation',
        start: new Date('2025-01-01'),
        end: new Date('2025-01-05'),
        type: 'absence',
        employeeId: 1,
        allDay: true,
        color: '#22c55e',
      },
      {
        id: 'emp-event-2',
        title: 'Employee 2 Vacation',
        start: new Date('2025-01-10'),
        end: new Date('2025-01-12'),
        type: 'absence',
        employeeId: 2,
        allDay: true,
        color: '#3b82f6',
      },
    ];

    render(<TeamCalendar events={employeeEvents} />);

    expect(screen.getByText('Employee 1 Vacation')).toBeInTheDocument();
    expect(screen.getByText('Employee 2 Vacation')).toBeInTheDocument();
  });

  it('should handle events with descriptions', () => {
    const eventsWithDescriptions: CalendarEvent[] = [
      {
        id: 'desc-event-1',
        title: 'Event with Description',
        start: new Date('2025-01-01'),
        end: new Date('2025-01-05'),
        type: 'absence',
        allDay: true,
        color: '#22c55e',
        description: 'This is a test description',
      },
    ];

    render(<TeamCalendar events={eventsWithDescriptions} />);

    expect(screen.getByText('Event with Description')).toBeInTheDocument();
  });

  it('should not call onEventClick when not provided', () => {
    render(<TeamCalendar events={mockEvents} />);

    const event = screen.getByTestId('event-event-1');
    // Should not throw error
    expect(() => fireEvent.click(event)).not.toThrow();
  });

  it('should handle date conversion correctly', () => {
    const stringDateEvents: CalendarEvent[] = [
      {
        id: 'string-date-1',
        title: 'String Date Event',
        start: '2025-01-01',
        end: '2025-01-05',
        type: 'absence',
        allDay: true,
        color: '#22c55e',
      },
    ];

    render(<TeamCalendar events={stringDateEvents} />);

    expect(screen.getByText('String Date Event')).toBeInTheDocument();
  });
});
