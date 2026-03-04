import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { EventDetailsDialog } from '../EventDetailsDialog';
import type { CalendarEvent } from '../../utils/calendarFilters';

describe('EventDetailsDialog', () => {
  const mockEvent: CalendarEvent = {
    id: 'test-event-1',
    title: 'Test Event',
    start: new Date('2025-01-01'),
    end: new Date('2025-01-05'),
    type: 'absence',
    allDay: true,
    color: '#22c55e',
    description: 'Test description',
    employeeId: 1,
  };

  it('should not render when open is false', () => {
    const { container } = render(
      <EventDetailsDialog
        event={mockEvent}
        open={false}
        onOpenChange={vi.fn()}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('should not render when event is null', () => {
    const { container } = render(
      <EventDetailsDialog
        event={null}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('should render dialog when open is true and event exists', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Test Event')).toBeInTheDocument();
  });

  it('should display event type', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Typ:')).toBeInTheDocument();
    expect(screen.getByText('Abwesenheit')).toBeInTheDocument();
  });

  it('should display start and end dates', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Beginn:')).toBeInTheDocument();
    expect(screen.getByText('Ende:')).toBeInTheDocument();
  });

  it('should display duration', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Dauer:')).toBeInTheDocument();
    expect(screen.getByText(/Tage/)).toBeInTheDocument();
  });

  it('should display description when provided', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Beschreibung:')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('should not display description when not provided', () => {
    const eventWithoutDescription = { ...mockEvent, description: undefined };

    render(
      <EventDetailsDialog
        event={eventWithoutDescription}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.queryByText('Beschreibung:')).not.toBeInTheDocument();
  });

  it('should display employee ID when provided', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Mitarbeiter-ID:')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('should not display employee ID when not provided', () => {
    const eventWithoutEmployeeId = { ...mockEvent, employeeId: undefined };

    render(
      <EventDetailsDialog
        event={eventWithoutEmployeeId}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.queryByText('Mitarbeiter-ID:')).not.toBeInTheDocument();
  });

  it('should display all-day indicator when allDay is true', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Ganztägig:')).toBeInTheDocument();
    expect(screen.getByText('Ja')).toBeInTheDocument();
  });

  it('should not display all-day indicator when allDay is false', () => {
    const eventNotAllDay = { ...mockEvent, allDay: false };

    render(
      <EventDetailsDialog
        event={eventNotAllDay}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.queryByText('Ganztägig:')).not.toBeInTheDocument();
  });

  it('should display event ID in footer', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText(/Event-ID:/)).toBeInTheDocument();
    expect(screen.getByText(/test-event-1/)).toBeInTheDocument();
  });

  it('should call onOpenChange when close button is clicked', () => {
    const onOpenChange = vi.fn();

    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={onOpenChange}
      />
    );

    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('should call onOpenChange when backdrop is clicked', () => {
    const onOpenChange = vi.fn();

    const { container } = render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={onOpenChange}
      />
    );

    const backdrop = container.querySelector('.bg-black\\/50');
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(onOpenChange).toHaveBeenCalledWith(false);
    }
  });

  it('should handle different event types correctly', () => {
    const eventTypes: Array<{ type: CalendarEvent['type']; label: string }> = [
      { type: 'absence', label: 'Abwesenheit' },
      { type: 'holiday', label: 'Feiertag' },
      { type: 'school_vacation', label: 'Schulferien' },
    ];

    eventTypes.forEach(({ type, label }) => {
      const event = { ...mockEvent, type };
      const { unmount } = render(
        <EventDetailsDialog
          event={event}
          open={true}
          onOpenChange={vi.fn()}
        />
      );

      expect(screen.getByText(label)).toBeInTheDocument();
      unmount();
    });
  });

  it('should calculate duration correctly for single day event', () => {
    const singleDayEvent = {
      ...mockEvent,
      start: new Date('2025-01-01'),
      end: new Date('2025-01-01'),
    };

    render(
      <EventDetailsDialog
        event={singleDayEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('1 Tag')).toBeInTheDocument();
  });

  it('should calculate duration correctly for multi-day event', () => {
    render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText(/Tage/)).toBeInTheDocument();
  });

  it('should handle string dates correctly', () => {
    const stringDateEvent: CalendarEvent = {
      ...mockEvent,
      start: '2025-01-01',
      end: '2025-01-05',
    };

    render(
      <EventDetailsDialog
        event={stringDateEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    expect(screen.getByText('Test Event')).toBeInTheDocument();
  });

  it('should display color indicator', () => {
    const { container } = render(
      <EventDetailsDialog
        event={mockEvent}
        open={true}
        onOpenChange={vi.fn()}
      />
    );

    const colorIndicator = container.querySelector('[style*="background-color"]');
    expect(colorIndicator).toBeInTheDocument();
  });
});
