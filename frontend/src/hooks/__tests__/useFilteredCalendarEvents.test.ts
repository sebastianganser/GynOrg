import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useFilteredCalendarEvents } from '../useFilteredCalendarEvents';
import { useCalendarFilterStore } from '../../stores/calendarFilterStore';
import type { CalendarEvent } from '../../utils/calendarFilters';

describe('useFilteredCalendarEvents', () => {
  const mockEvents: CalendarEvent[] = [
    {
      id: 1,
      title: 'Weihnachten',
      start: '2025-12-25',
      end: '2025-12-25',
      type: 'holiday',
      allDay: true,
    },
    {
      id: 2,
      title: 'Winterferien',
      start: '2025-02-01',
      end: '2025-02-14',
      type: 'school_vacation',
      allDay: true,
    },
    {
      id: 3,
      title: 'Urlaub - Max Mustermann',
      start: '2025-07-01',
      end: '2025-07-14',
      type: 'vacation',
      employeeId: 1,
      allDay: true,
    },
    {
      id: 4,
      title: 'Krankheit - Erika Musterfrau',
      start: '2025-03-10',
      end: '2025-03-12',
      type: 'sick_leave',
      employeeId: 2,
      allDay: true,
    },
    {
      id: 5,
      title: 'Fortbildung - Max Mustermann',
      start: '2025-05-20',
      end: '2025-05-21',
      type: 'training',
      employeeId: 1,
      allDay: true,
    },
  ];

  const mockEmployees = [
    { id: 1, calendar_color: '#3b82f6' },
    { id: 2, calendar_color: '#22c55e' },
    { id: 3, calendar_color: '#f97316' },
  ];

  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useCalendarFilterStore());
    act(() => {
      result.current.resetFilters();
    });
    localStorage.clear();
  });

  describe('Basic Functionality', () => {
    it('should return filtered events', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      expect(result.current.filteredEvents).toBeDefined();
      expect(Array.isArray(result.current.filteredEvents)).toBe(true);
    });

    it('should return filter state', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      expect(result.current.filters).toBeDefined();
      expect(result.current.filters.showHolidays).toBeDefined();
      expect(result.current.filters.selectedEmployeeIds).toBeDefined();
    });

    it('should return event counts', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      expect(result.current.totalEvents).toBe(5);
      expect(result.current.filteredCount).toBeDefined();
      expect(typeof result.current.filteredCount).toBe('number');
    });

    it('should handle empty events array', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents([], mockEmployees)
      );

      expect(result.current.filteredEvents).toEqual([]);
      expect(result.current.totalEvents).toBe(0);
      expect(result.current.filteredCount).toBe(0);
    });

    it('should handle empty employees array', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, [])
      );

      expect(result.current.filteredEvents).toBeDefined();
      expect(Array.isArray(result.current.filteredEvents)).toBe(true);
    });
  });

  describe('Store Integration', () => {
    it('should read filters from store', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      expect(hookResult.current.filters.showHolidays).toBe(
        storeResult.current.showHolidays
      );
      expect(hookResult.current.filters.selectedEmployeeIds).toEqual(
        storeResult.current.selectedEmployeeIds
      );
    });

    it('should react to store changes', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      const initialCount = hookResult.current.filteredCount;

      act(() => {
        storeResult.current.toggleHolidays();
      });

      rerender();

      expect(hookResult.current.filters.showHolidays).toBe(false);
      expect(hookResult.current.filteredCount).not.toBe(initialCount);
    });

    it('should update when employee filter changes', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1]);
      });

      rerender();

      expect(hookResult.current.filters.selectedEmployeeIds).toEqual([1]);
      const employeeEvents = hookResult.current.filteredEvents.filter(
        (e) => e.employeeId
      );
      expect(employeeEvents.every((e) => e.employeeId === 1)).toBe(true);
    });

    it('should update when calendar type filter changes', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.toggleSickLeave();
      });

      rerender();

      expect(hookResult.current.filters.showSickLeave).toBe(false);
      expect(
        hookResult.current.filteredEvents.every((e) => e.type !== 'sick_leave')
      ).toBe(true);
    });
  });

  describe('Color Mapping', () => {
    it('should apply employee colors to events', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1, 2]);
      });

      rerender();

      const employeeEvents = hookResult.current.filteredEvents.filter(
        (e) => e.employeeId
      );
      expect(employeeEvents.every((e) => e.color)).toBe(true);
    });

    it('should create employee color map', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      // Events should have colors applied
      expect(result.current.filteredEvents.every((e) => e.color)).toBe(true);
    });

    it('should use employee color for employee events', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1]);
      });

      rerender();

      const employeeEvent = hookResult.current.filteredEvents.find(
        (e) => e.employeeId === 1
      );
      expect(employeeEvent?.color).toBe('#3b82f6'); // Employee 1's color
    });

    it('should use type color for non-employee events', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      const holidayEvent = result.current.filteredEvents.find(
        (e) => e.type === 'holiday'
      );
      expect(holidayEvent?.color).toBe('#ef4444'); // Holiday color
    });
  });

  describe('Filtering Logic', () => {
    it('should filter by employee selection', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1]);
      });

      rerender();

      const employeeEvents = hookResult.current.filteredEvents.filter(
        (e) => e.employeeId
      );
      expect(employeeEvents.every((e) => e.employeeId === 1)).toBe(true);
    });

    it('should filter by calendar type', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.toggleVacationAbsences();
      });

      rerender();

      expect(
        hookResult.current.filteredEvents.every((e) => e.type !== 'vacation')
      ).toBe(true);
    });

    it('should apply multiple filters simultaneously', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1]);
        storeResult.current.toggleTraining();
      });

      rerender();

      const employeeEvents = hookResult.current.filteredEvents.filter(
        (e) => e.employeeId
      );
      expect(employeeEvents.every((e) => e.employeeId === 1)).toBe(true);
      expect(
        hookResult.current.filteredEvents.every((e) => e.type !== 'training')
      ).toBe(true);
    });

    it('should show only non-employee events when no employees selected', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      // Default: no employees selected
      const employeeEvents = result.current.filteredEvents.filter(
        (e) => e.employeeId
      );
      expect(employeeEvents).toHaveLength(0);
    });

    it('should show all events when all filters enabled and employees selected', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1, 2, 3]);
      });

      rerender();

      expect(hookResult.current.filteredCount).toBe(5);
    });
  });

  describe('Memoization', () => {
    it('should memoize employee color map', () => {
      const { result, rerender } = renderHook(
        ({ events, employees }) => useFilteredCalendarEvents(events, employees),
        {
          initialProps: { events: mockEvents, employees: mockEmployees },
        }
      );

      const firstResult = result.current.filteredEvents;

      // Rerender with same employees
      rerender({ events: mockEvents, employees: mockEmployees });

      // Should use memoized color map (same reference)
      expect(result.current.filteredEvents).toBe(firstResult);
    });

    it('should recalculate when employees change', () => {
      const { result, rerender } = renderHook(
        ({ events, employees }) => useFilteredCalendarEvents(events, employees),
        {
          initialProps: { events: mockEvents, employees: mockEmployees },
        }
      );

      const firstResult = result.current.filteredEvents;

      // Rerender with different employees
      const newEmployees = [
        { id: 1, calendar_color: '#ff0000' },
        { id: 2, calendar_color: '#00ff00' },
      ];
      rerender({ events: mockEvents, employees: newEmployees });

      // Should recalculate (different reference)
      expect(result.current.filteredEvents).not.toBe(firstResult);
    });

    it('should recalculate when events change', () => {
      const { result, rerender } = renderHook(
        ({ events, employees }) => useFilteredCalendarEvents(events, employees),
        {
          initialProps: { events: mockEvents, employees: mockEmployees },
        }
      );

      const firstResult = result.current.filteredEvents;

      // Rerender with different events
      const newEvents = [...mockEvents, {
        id: 6,
        title: 'New Event',
        start: '2025-08-01',
        end: '2025-08-01',
        type: 'vacation' as const,
        employeeId: 1,
        allDay: true,
      }];
      rerender({ events: newEvents, employees: mockEmployees });

      // Should recalculate
      expect(result.current.filteredEvents).not.toBe(firstResult);
      expect(result.current.totalEvents).toBe(6);
    });

    it('should recalculate when filters change', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      const firstResult = hookResult.current.filteredEvents;

      act(() => {
        storeResult.current.toggleHolidays();
      });

      rerender();

      // Should recalculate due to filter change
      expect(hookResult.current.filteredEvents).not.toBe(firstResult);
    });
  });

  describe('Event Counts', () => {
    it('should calculate total events correctly', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      expect(result.current.totalEvents).toBe(5);
    });

    it('should calculate filtered count correctly', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.selectAllEmployees([1, 2]);
      });

      rerender();

      expect(hookResult.current.filteredCount).toBe(5); // All events
    });

    it('should update filtered count when filters change', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      const initialCount = hookResult.current.filteredCount;

      act(() => {
        storeResult.current.toggleHolidays();
      });

      rerender();

      expect(hookResult.current.filteredCount).not.toBe(initialCount);
      expect(hookResult.current.filteredCount).toBe(initialCount - 1);
    });

    it('should handle zero filtered events', () => {
      const { result: storeResult } = renderHook(() => useCalendarFilterStore());
      const { result: hookResult, rerender } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, mockEmployees)
      );

      act(() => {
        storeResult.current.disableAllCalendarFilters();
      });

      rerender();

      expect(hookResult.current.filteredCount).toBe(0);
      expect(hookResult.current.filteredEvents).toEqual([]);
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined events', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(undefined as any, mockEmployees)
      );

      // Should not crash
      expect(result.current).toBeDefined();
    });

    it('should handle undefined employees', () => {
      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, undefined as any)
      );

      // Should not crash
      expect(result.current).toBeDefined();
    });

    it('should handle events without required fields', () => {
      const invalidEvents = [
        { id: 1, title: 'Test' } as any,
      ];

      const { result } = renderHook(() =>
        useFilteredCalendarEvents(invalidEvents, mockEmployees)
      );

      // Should not crash
      expect(result.current).toBeDefined();
    });

    it('should handle employees without calendar_color', () => {
      const invalidEmployees = [
        { id: 1 } as any,
      ];

      const { result } = renderHook(() =>
        useFilteredCalendarEvents(mockEvents, invalidEmployees)
      );

      // Should not crash
      expect(result.current).toBeDefined();
    });
  });
});
