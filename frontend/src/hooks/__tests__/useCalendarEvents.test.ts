import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useCalendarEvents } from '../useCalendarEvents';
import * as useAbsencesModule from '../useAbsences';
import * as useHolidaysModule from '../useHolidays';
import type { Absence } from '../../types/absence';
import type { Holiday, HolidayType } from '../../types/holiday';

// Mock the hooks
vi.mock('../useAbsences');
vi.mock('../useHolidays');

describe('useCalendarEvents', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return empty events when no data is available', () => {
    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: [],
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.events).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should transform absences to calendar events', () => {
    const mockAbsences: Absence[] = [
      {
        id: 1,
        employee_id: 1,
        absence_type_id: 1,
        start_date: '2025-01-01',
        end_date: '2025-01-05',
        comment: 'Test vacation',
        status: 'APPROVED' as any,
        duration_days: 5,
        is_active: true,
        created_at: '2025-01-01',
        updated_at: '2025-01-01',
        absence_type: {
          id: 1,
          name: 'Urlaub',
          category: 'VACATION' as any,
          color: '#22c55e',
          is_paid: true,
          requires_approval: true,
          active: true,
        },
      },
    ];

    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: mockAbsences,
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: [],
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0]).toMatchObject({
      id: 'absence-1',
      title: 'Urlaub',
      type: 'vacation',
      employeeId: 1,
      allDay: true,
    });
  });

  it('should transform holidays to calendar events', () => {
    const mockHolidays: Holiday[] = [
      {
        id: 1,
        name: 'Neujahr',
        date: '2025-01-01',
        federal_state: 'DE',
        is_nationwide: true,
        year: 2025,
        notes: '',
        holiday_type: 'PUBLIC_HOLIDAY' as HolidayType,
        data_source: 'MANUAL' as any,
        created_at: '2025-01-01',
      },
    ];

    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: mockHolidays,
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0]).toMatchObject({
      id: 'holiday-1',
      title: 'Neujahr',
      type: 'holiday',
      allDay: true,
    });
  });

  it('should distinguish between public holidays and school vacations', () => {
    const mockHolidays: Holiday[] = [
      {
        id: 1,
        name: 'Neujahr',
        date: '2025-01-01',
        federal_state: 'DE',
        is_nationwide: true,
        year: 2025,
        notes: '',
        holiday_type: 'PUBLIC_HOLIDAY' as HolidayType,
        data_source: 'MANUAL' as any,
        created_at: '2025-01-01',
      },
      {
        id: 2,
        name: 'Winterferien',
        date: '2025-02-01',
        federal_state: 'ST',
        is_nationwide: false,
        year: 2025,
        notes: '',
        holiday_type: 'SCHOOL_VACATION' as HolidayType,
        school_vacation_type: 'WINTER' as any,
        data_source: 'MEHR_SCHULFERIEN_API' as any,
        created_at: '2025-01-01',
      },
    ];

    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: mockHolidays,
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.events).toHaveLength(2);
    expect(result.current.events[0].type).toBe('holiday');
    expect(result.current.events[1].type).toBe('school_vacation');
  });

  it('should calculate correct statistics', () => {
    const mockAbsences: Absence[] = [
      {
        id: 1,
        employee_id: 1,
        absence_type_id: 1,
        start_date: '2025-01-01',
        end_date: '2025-01-05',
        status: 'APPROVED' as any,
        duration_days: 5,
        is_active: true,
        created_at: '2025-01-01',
        updated_at: '2025-01-01',
        absence_type: {
          id: 1,
          name: 'Urlaub',
          category: 'VACATION' as any,
          color: '#22c55e',
          is_paid: true,
          requires_approval: true,
          active: true,
        },
      },
    ];

    const mockHolidays: Holiday[] = [
      {
        id: 1,
        name: 'Neujahr',
        date: '2025-01-01',
        federal_state: 'DE',
        is_nationwide: true,
        year: 2025,
        notes: '',
        holiday_type: 'PUBLIC_HOLIDAY' as HolidayType,
        data_source: 'MANUAL' as any,
        created_at: '2025-01-01',
      },
      {
        id: 2,
        name: 'Winterferien',
        date: '2025-02-01',
        federal_state: 'ST',
        is_nationwide: false,
        year: 2025,
        notes: '',
        holiday_type: 'SCHOOL_VACATION' as HolidayType,
        data_source: 'MEHR_SCHULFERIEN_API' as any,
        created_at: '2025-01-01',
      },
    ];

    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: mockAbsences,
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: mockHolidays,
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.stats).toEqual({
      total: 3,
      absences: 1,
      holidays: 1,
      schoolVacations: 1,
    });
  });

  it('should handle loading state', () => {
    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: [],
      isLoading: true,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: [],
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.isLoading).toBe(true);
  });

  it('should handle error state', () => {
    const mockError = new Error('Failed to load absences');

    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: [],
      isLoading: false,
      error: mockError,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: [],
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.error).toBe(mockError);
  });

  it('should map different absence types correctly', () => {
    const mockAbsences: Absence[] = [
      {
        id: 1,
        employee_id: 1,
        absence_type_id: 1,
        start_date: '2025-01-01',
        end_date: '2025-01-05',
        status: 'APPROVED' as any,
        duration_days: 5,
        is_active: true,
        created_at: '2025-01-01',
        updated_at: '2025-01-01',
        absence_type: {
          id: 1,
          name: 'Krankheit',
          category: 'SICK_LEAVE' as any,
          color: '#f97316',
          is_paid: true,
          requires_approval: false,
          active: true,
        },
      },
      {
        id: 2,
        employee_id: 1,
        absence_type_id: 2,
        start_date: '2025-02-01',
        end_date: '2025-02-03',
        status: 'APPROVED' as any,
        duration_days: 3,
        is_active: true,
        created_at: '2025-01-01',
        updated_at: '2025-01-01',
        absence_type: {
          id: 2,
          name: 'Fortbildung',
          category: 'TRAINING' as any,
          color: '#a855f7',
          is_paid: true,
          requires_approval: true,
          active: true,
        },
      },
    ];

    vi.spyOn(useAbsencesModule, 'useAbsences').mockReturnValue({
      data: mockAbsences,
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useHolidaysModule, 'useHolidays').mockReturnValue({
      holidays: [],
      loading: false,
      error: null,
    } as any);

    const { result } = renderHook(() => useCalendarEvents());

    expect(result.current.events).toHaveLength(2);
    expect(result.current.events[0].type).toBe('sick_leave');
    expect(result.current.events[1].type).toBe('training');
  });
});
