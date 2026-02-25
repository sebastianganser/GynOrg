import { describe, it, expect } from 'vitest';
import {
  filterEventsByEmployees,
  filterEventsByType,
  getEventTypeColor,
  applyColorMapping,
  applyCalendarFilters,
  createEmployeeColorMap,
  getEventTypeLabel,
  hasActiveFilters,
  getActiveFilterCount,
  type CalendarEvent,
  type CalendarEventType,
} from '../calendarFilters';
import type { CalendarFilters } from '../../stores/calendarFilterStore';

describe('calendarFilters', () => {
  // Test data
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
    {
      id: 6,
      title: 'Sonderurlaub - Erika Musterfrau',
      start: '2025-06-15',
      end: '2025-06-15',
      type: 'special_leave',
      employeeId: 2,
      allDay: true,
    },
  ];

  const mockEmployees = [
    { id: 1, calendar_color: '#3b82f6' }, // blue
    { id: 2, calendar_color: '#22c55e' }, // green
    { id: 3, calendar_color: '#f97316' }, // orange
  ];

  const defaultFilters: Omit<CalendarFilters, 'isSidebarCollapsed'> = {
    selectedEmployeeIds: [],
    showHolidays: true,
    showSchoolVacations: true,
    showVacationAbsences: true,
    showSickLeave: true,
    showTraining: true,
    showSpecialLeave: true,
  };

  describe('filterEventsByEmployees', () => {
    it('should return only non-employee events when no employees selected', () => {
      const result = filterEventsByEmployees(mockEvents, []);
      
      expect(result).toHaveLength(2);
      expect(result.every(e => !e.employeeId)).toBe(true);
      expect(result.map(e => e.type)).toEqual(['holiday', 'school_vacation']);
    });

    it('should filter events by selected employee IDs', () => {
      const result = filterEventsByEmployees(mockEvents, [1]);
      
      const employeeEvents = result.filter(e => e.employeeId);
      expect(employeeEvents.every(e => e.employeeId === 1)).toBe(true);
    });

    it('should include non-employee events regardless of selection', () => {
      const result = filterEventsByEmployees(mockEvents, [1]);
      
      const nonEmployeeEvents = result.filter(e => !e.employeeId);
      expect(nonEmployeeEvents).toHaveLength(2);
    });

    it('should filter multiple employees', () => {
      const result = filterEventsByEmployees(mockEvents, [1, 2]);
      
      expect(result).toHaveLength(6); // All events
    });

    it('should return empty array for empty input', () => {
      const result = filterEventsByEmployees([], [1, 2]);
      
      expect(result).toEqual([]);
    });

    it('should handle employee IDs that do not exist', () => {
      const result = filterEventsByEmployees(mockEvents, [999]);
      
      // Should only return non-employee events
      expect(result).toHaveLength(2);
      expect(result.every(e => !e.employeeId)).toBe(true);
    });
  });

  describe('filterEventsByType', () => {
    it('should filter out holidays when showHolidays is false', () => {
      const filters = { ...defaultFilters, showHolidays: false };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result.every(e => e.type !== 'holiday')).toBe(true);
      expect(result).toHaveLength(5);
    });

    it('should filter out school vacations when showSchoolVacations is false', () => {
      const filters = { ...defaultFilters, showSchoolVacations: false };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result.every(e => e.type !== 'school_vacation')).toBe(true);
      expect(result).toHaveLength(5);
    });

    it('should filter out vacation absences when showVacationAbsences is false', () => {
      const filters = { ...defaultFilters, showVacationAbsences: false };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result.every(e => e.type !== 'vacation')).toBe(true);
      expect(result).toHaveLength(5);
    });

    it('should filter out sick leave when showSickLeave is false', () => {
      const filters = { ...defaultFilters, showSickLeave: false };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result.every(e => e.type !== 'sick_leave')).toBe(true);
      expect(result).toHaveLength(5);
    });

    it('should filter out training when showTraining is false', () => {
      const filters = { ...defaultFilters, showTraining: false };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result.every(e => e.type !== 'training')).toBe(true);
      expect(result).toHaveLength(5);
    });

    it('should filter out special leave when showSpecialLeave is false', () => {
      const filters = { ...defaultFilters, showSpecialLeave: false };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result.every(e => e.type !== 'special_leave')).toBe(true);
      expect(result).toHaveLength(5);
    });

    it('should show all events when all filters are enabled', () => {
      const result = filterEventsByType(mockEvents, defaultFilters);
      
      expect(result).toHaveLength(6);
    });

    it('should filter multiple types simultaneously', () => {
      const filters = {
        ...defaultFilters,
        showHolidays: false,
        showSickLeave: false,
        showTraining: false,
      };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result).toHaveLength(3);
      expect(result.map(e => e.type)).toEqual(['school_vacation', 'vacation', 'special_leave']);
    });

    it('should return empty array when all filters are disabled', () => {
      const filters = {
        selectedEmployeeIds: [],
        showHolidays: false,
        showSchoolVacations: false,
        showVacationAbsences: false,
        showSickLeave: false,
        showTraining: false,
        showSpecialLeave: false,
      };
      const result = filterEventsByType(mockEvents, filters);
      
      expect(result).toEqual([]);
    });
  });

  describe('getEventTypeColor', () => {
    it('should return correct color for holiday', () => {
      expect(getEventTypeColor('holiday')).toBe('#ef4444');
    });

    it('should return correct color for school_vacation', () => {
      expect(getEventTypeColor('school_vacation')).toBe('#3b82f6');
    });

    it('should return correct color for vacation', () => {
      expect(getEventTypeColor('vacation')).toBe('#22c55e');
    });

    it('should return correct color for sick_leave', () => {
      expect(getEventTypeColor('sick_leave')).toBe('#f97316');
    });

    it('should return correct color for training', () => {
      expect(getEventTypeColor('training')).toBe('#a855f7');
    });

    it('should return correct color for special_leave', () => {
      expect(getEventTypeColor('special_leave')).toBe('#ec4899');
    });

    it('should return fallback color for unknown type', () => {
      expect(getEventTypeColor('unknown' as CalendarEventType)).toBe('#6b7280');
    });
  });

  describe('applyColorMapping', () => {
    it('should use employee color when available', () => {
      const colorMap = createEmployeeColorMap(mockEmployees);
      const events = [mockEvents[2]]; // Vacation event with employeeId: 1
      
      const result = applyColorMapping(events, colorMap);
      
      expect(result[0].color).toBe('#3b82f6'); // Employee 1's color
    });

    it('should use type-based color when no employee color', () => {
      const colorMap = new Map();
      const events = [mockEvents[0]]; // Holiday event without employeeId
      
      const result = applyColorMapping(events, colorMap);
      
      expect(result[0].color).toBe('#ef4444'); // Holiday color
    });

    it('should preserve existing color if set', () => {
      const colorMap = new Map();
      const events = [{ ...mockEvents[0], color: '#custom' }];
      
      const result = applyColorMapping(events, colorMap);
      
      expect(result[0].color).toBe('#custom');
    });

    it('should work with empty color map', () => {
      const colorMap = new Map();
      
      const result = applyColorMapping(mockEvents, colorMap);
      
      expect(result).toHaveLength(6);
      expect(result.every(e => e.color)).toBe(true);
    });

    it('should apply colors to all events', () => {
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyColorMapping(mockEvents, colorMap);
      
      expect(result.every(e => e.color)).toBe(true);
    });

    it('should not mutate original events', () => {
      const colorMap = createEmployeeColorMap(mockEmployees);
      const originalEvents = [...mockEvents];
      
      applyColorMapping(mockEvents, colorMap);
      
      expect(mockEvents).toEqual(originalEvents);
    });
  });

  describe('applyCalendarFilters', () => {
    it('should apply all filter steps in correct order', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [1],
        showSickLeave: false,
        isSidebarCollapsed: false,
      };
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyCalendarFilters(mockEvents, filters, colorMap);
      
      // Should filter by employee (1) and exclude sick_leave
      expect(result.every(e => !e.employeeId || e.employeeId === 1)).toBe(true);
      expect(result.every(e => e.type !== 'sick_leave')).toBe(true);
      expect(result.every(e => e.color)).toBe(true);
    });

    it('should apply employee filter first', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [1],
        isSidebarCollapsed: false,
      };
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyCalendarFilters(mockEvents, filters, colorMap);
      
      const employeeEvents = result.filter(e => e.employeeId);
      expect(employeeEvents.every(e => e.employeeId === 1)).toBe(true);
    });

    it('should apply type filter second', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [1, 2],
        showVacationAbsences: false,
        showTraining: false,
        isSidebarCollapsed: false,
      };
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyCalendarFilters(mockEvents, filters, colorMap);
      
      expect(result.every(e => e.type !== 'vacation' && e.type !== 'training')).toBe(true);
    });

    it('should apply color mapping last', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [1, 2],
        isSidebarCollapsed: false,
      };
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyCalendarFilters(mockEvents, filters, colorMap);
      
      expect(result.every(e => e.color)).toBe(true);
    });

    it('should handle empty events array', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        isSidebarCollapsed: false,
      };
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyCalendarFilters([], filters, colorMap);
      
      expect(result).toEqual([]);
    });

    it('should handle all filters disabled', () => {
      const filters: CalendarFilters = {
        selectedEmployeeIds: [],
        showHolidays: false,
        showSchoolVacations: false,
        showVacationAbsences: false,
        showSickLeave: false,
        showTraining: false,
        showSpecialLeave: false,
        isSidebarCollapsed: false,
      };
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      const result = applyCalendarFilters(mockEvents, filters, colorMap);
      
      expect(result).toEqual([]);
    });
  });

  describe('createEmployeeColorMap', () => {
    it('should create map from employee array', () => {
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      expect(colorMap.size).toBe(3);
      expect(colorMap.get(1)).toBe('#3b82f6');
      expect(colorMap.get(2)).toBe('#22c55e');
      expect(colorMap.get(3)).toBe('#f97316');
    });

    it('should work with empty array', () => {
      const colorMap = createEmployeeColorMap([]);
      
      expect(colorMap.size).toBe(0);
    });

    it('should handle duplicate IDs (last one wins)', () => {
      const employees = [
        { id: 1, calendar_color: '#first' },
        { id: 1, calendar_color: '#second' },
      ];
      
      const colorMap = createEmployeeColorMap(employees);
      
      expect(colorMap.get(1)).toBe('#second');
    });

    it('should return a Map instance', () => {
      const colorMap = createEmployeeColorMap(mockEmployees);
      
      expect(colorMap).toBeInstanceOf(Map);
    });
  });

  describe('getEventTypeLabel', () => {
    it('should return German label for holiday', () => {
      expect(getEventTypeLabel('holiday')).toBe('Feiertag');
    });

    it('should return German label for school_vacation', () => {
      expect(getEventTypeLabel('school_vacation')).toBe('Schulferien');
    });

    it('should return German label for vacation', () => {
      expect(getEventTypeLabel('vacation')).toBe('Urlaub');
    });

    it('should return German label for sick_leave', () => {
      expect(getEventTypeLabel('sick_leave')).toBe('Krankheit');
    });

    it('should return German label for training', () => {
      expect(getEventTypeLabel('training')).toBe('Fortbildung');
    });

    it('should return German label for special_leave', () => {
      expect(getEventTypeLabel('special_leave')).toBe('Sonderurlaub');
    });

    it('should return fallback for unknown type', () => {
      expect(getEventTypeLabel('unknown' as CalendarEventType)).toBe('Unbekannt');
    });
  });

  describe('hasActiveFilters', () => {
    it('should return false when all filters are enabled', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [1, 2, 3],
        isSidebarCollapsed: false,
      };
      
      expect(hasActiveFilters(filters)).toBe(false);
    });

    it('should return true when holidays filter is disabled', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        showHolidays: false,
        selectedEmployeeIds: [1],
        isSidebarCollapsed: false,
      };
      
      expect(hasActiveFilters(filters)).toBe(true);
    });

    it('should return true when no employees selected', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [],
        isSidebarCollapsed: false,
      };
      
      expect(hasActiveFilters(filters)).toBe(true);
    });

    it('should return true when any filter is disabled', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        showTraining: false,
        selectedEmployeeIds: [1],
        isSidebarCollapsed: false,
      };
      
      expect(hasActiveFilters(filters)).toBe(true);
    });

    it('should return true when multiple filters are disabled', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        showHolidays: false,
        showSickLeave: false,
        showTraining: false,
        selectedEmployeeIds: [],
        isSidebarCollapsed: false,
      };
      
      expect(hasActiveFilters(filters)).toBe(true);
    });
  });

  describe('getActiveFilterCount', () => {
    it('should return 0 when all filters are enabled', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        isSidebarCollapsed: false,
      };
      
      expect(getActiveFilterCount(filters)).toBe(0);
    });

    it('should count disabled filters correctly', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        showHolidays: false,
        showSickLeave: false,
        showTraining: false,
        isSidebarCollapsed: false,
      };
      
      expect(getActiveFilterCount(filters)).toBe(3);
    });

    it('should return 6 when all filters are disabled', () => {
      const filters: CalendarFilters = {
        selectedEmployeeIds: [],
        showHolidays: false,
        showSchoolVacations: false,
        showVacationAbsences: false,
        showSickLeave: false,
        showTraining: false,
        showSpecialLeave: false,
        isSidebarCollapsed: false,
      };
      
      expect(getActiveFilterCount(filters)).toBe(6);
    });

    it('should count each disabled filter once', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        showHolidays: false,
        isSidebarCollapsed: false,
      };
      
      expect(getActiveFilterCount(filters)).toBe(1);
    });

    it('should not count employee selection', () => {
      const filters: CalendarFilters = {
        ...defaultFilters,
        selectedEmployeeIds: [],
        isSidebarCollapsed: false,
      };
      
      // Employee selection is not counted in getActiveFilterCount
      expect(getActiveFilterCount(filters)).toBe(0);
    });
  });
});
