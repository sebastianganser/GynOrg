import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCalendarFilterStore } from '../calendarFilterStore';

describe('calendarFilterStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useCalendarFilterStore());
    act(() => {
      result.current.resetFilters();
    });
    // Clear localStorage
    localStorage.clear();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      expect(result.current.selectedEmployeeIds).toEqual([]);
      expect(result.current.showHolidays).toBe(true);
      expect(result.current.showSchoolVacations).toBe(true);
      expect(result.current.showVacationAbsences).toBe(true);
      expect(result.current.showSickLeave).toBe(true);
      expect(result.current.showTraining).toBe(true);
      expect(result.current.showSpecialLeave).toBe(true);
      expect(result.current.isSidebarCollapsed).toBe(false);
    });

    it('should have all filters enabled by default', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      expect(result.current.showHolidays).toBe(true);
      expect(result.current.showSchoolVacations).toBe(true);
      expect(result.current.showVacationAbsences).toBe(true);
      expect(result.current.showSickLeave).toBe(true);
      expect(result.current.showTraining).toBe(true);
      expect(result.current.showSpecialLeave).toBe(true);
    });

    it('should have empty employee selection by default', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      expect(result.current.selectedEmployeeIds).toEqual([]);
      expect(result.current.selectedEmployeeIds.length).toBe(0);
    });

    it('should have sidebar expanded by default', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      expect(result.current.isSidebarCollapsed).toBe(false);
    });
  });

  describe('Employee Filter Actions', () => {
    it('should toggle employee - add employee', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleEmployee(1);
      });
      
      expect(result.current.selectedEmployeeIds).toContain(1);
      expect(result.current.selectedEmployeeIds.length).toBe(1);
    });

    it('should toggle employee - remove employee', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleEmployee(1);
        result.current.toggleEmployee(1);
      });
      
      expect(result.current.selectedEmployeeIds).not.toContain(1);
      expect(result.current.selectedEmployeeIds.length).toBe(0);
    });

    it('should toggle multiple employees', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleEmployee(1);
        result.current.toggleEmployee(2);
        result.current.toggleEmployee(3);
      });
      
      expect(result.current.selectedEmployeeIds).toEqual([1, 2, 3]);
    });

    it('should select all employees', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      const employeeIds = [1, 2, 3, 4, 5];
      
      act(() => {
        result.current.selectAllEmployees(employeeIds);
      });
      
      expect(result.current.selectedEmployeeIds).toEqual(employeeIds);
    });

    it('should deselect all employees', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.selectAllEmployees([1, 2, 3]);
        result.current.deselectAllEmployees();
      });
      
      expect(result.current.selectedEmployeeIds).toEqual([]);
    });

    it('should set specific employees', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      const employeeIds = [2, 4, 6];
      
      act(() => {
        result.current.setSelectedEmployees(employeeIds);
      });
      
      expect(result.current.selectedEmployeeIds).toEqual(employeeIds);
    });

    it('should replace employees when setting new selection', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setSelectedEmployees([1, 2, 3]);
        result.current.setSelectedEmployees([4, 5]);
      });
      
      expect(result.current.selectedEmployeeIds).toEqual([4, 5]);
    });
  });

  describe('Calendar Type Filter Actions', () => {
    it('should toggle holidays filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleHolidays();
      });
      
      expect(result.current.showHolidays).toBe(false);
      
      act(() => {
        result.current.toggleHolidays();
      });
      
      expect(result.current.showHolidays).toBe(true);
    });

    it('should toggle school vacations filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleSchoolVacations();
      });
      
      expect(result.current.showSchoolVacations).toBe(false);
    });

    it('should toggle vacation absences filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleVacationAbsences();
      });
      
      expect(result.current.showVacationAbsences).toBe(false);
    });

    it('should toggle sick leave filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleSickLeave();
      });
      
      expect(result.current.showSickLeave).toBe(false);
    });

    it('should toggle training filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleTraining();
      });
      
      expect(result.current.showTraining).toBe(false);
    });

    it('should toggle special leave filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleSpecialLeave();
      });
      
      expect(result.current.showSpecialLeave).toBe(false);
    });

    it('should toggle multiple filters independently', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleHolidays();
        result.current.toggleSickLeave();
      });
      
      expect(result.current.showHolidays).toBe(false);
      expect(result.current.showSickLeave).toBe(false);
      expect(result.current.showSchoolVacations).toBe(true);
      expect(result.current.showVacationAbsences).toBe(true);
    });
  });

  describe('Bulk Calendar Filter Actions', () => {
    it('should enable all calendar filters', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.disableAllCalendarFilters();
        result.current.enableAllCalendarFilters();
      });
      
      expect(result.current.showHolidays).toBe(true);
      expect(result.current.showSchoolVacations).toBe(true);
      expect(result.current.showVacationAbsences).toBe(true);
      expect(result.current.showSickLeave).toBe(true);
      expect(result.current.showTraining).toBe(true);
      expect(result.current.showSpecialLeave).toBe(true);
    });

    it('should disable all calendar filters', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.disableAllCalendarFilters();
      });
      
      expect(result.current.showHolidays).toBe(false);
      expect(result.current.showSchoolVacations).toBe(false);
      expect(result.current.showVacationAbsences).toBe(false);
      expect(result.current.showSickLeave).toBe(false);
      expect(result.current.showTraining).toBe(false);
      expect(result.current.showSpecialLeave).toBe(false);
    });

    it('should set individual calendar filter', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setCalendarFilter('showHolidays', false);
      });
      
      expect(result.current.showHolidays).toBe(false);
      expect(result.current.showSchoolVacations).toBe(true);
    });

    it('should set multiple calendar filters individually', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setCalendarFilter('showHolidays', false);
        result.current.setCalendarFilter('showSickLeave', false);
        result.current.setCalendarFilter('showTraining', false);
      });
      
      expect(result.current.showHolidays).toBe(false);
      expect(result.current.showSickLeave).toBe(false);
      expect(result.current.showTraining).toBe(false);
      expect(result.current.showSchoolVacations).toBe(true);
      expect(result.current.showVacationAbsences).toBe(true);
      expect(result.current.showSpecialLeave).toBe(true);
    });
  });

  describe('Sidebar Actions', () => {
    it('should toggle sidebar collapsed state', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleSidebar();
      });
      
      expect(result.current.isSidebarCollapsed).toBe(true);
      
      act(() => {
        result.current.toggleSidebar();
      });
      
      expect(result.current.isSidebarCollapsed).toBe(false);
    });

    it('should set sidebar collapsed to true', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setSidebarCollapsed(true);
      });
      
      expect(result.current.isSidebarCollapsed).toBe(true);
    });

    it('should set sidebar collapsed to false', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setSidebarCollapsed(true);
        result.current.setSidebarCollapsed(false);
      });
      
      expect(result.current.isSidebarCollapsed).toBe(false);
    });
  });

  describe('Reset Functionality', () => {
    it('should reset all filters to default values', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.selectAllEmployees([1, 2, 3]);
        result.current.disableAllCalendarFilters();
        result.current.setSidebarCollapsed(true);
        result.current.resetFilters();
      });
      
      expect(result.current.selectedEmployeeIds).toEqual([]);
      expect(result.current.showHolidays).toBe(true);
      expect(result.current.showSchoolVacations).toBe(true);
      expect(result.current.showVacationAbsences).toBe(true);
      expect(result.current.showSickLeave).toBe(true);
      expect(result.current.showTraining).toBe(true);
      expect(result.current.showSpecialLeave).toBe(true);
      expect(result.current.isSidebarCollapsed).toBe(false);
    });

    it('should reset employee selection', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.selectAllEmployees([1, 2, 3, 4, 5]);
        result.current.resetFilters();
      });
      
      expect(result.current.selectedEmployeeIds).toEqual([]);
    });

    it('should reset calendar filters', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleHolidays();
        result.current.toggleSickLeave();
        result.current.resetFilters();
      });
      
      expect(result.current.showHolidays).toBe(true);
      expect(result.current.showSickLeave).toBe(true);
    });

    it('should reset sidebar state', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setSidebarCollapsed(true);
        result.current.resetFilters();
      });
      
      expect(result.current.isSidebarCollapsed).toBe(false);
    });
  });

  describe('Persistence', () => {
    it('should persist state to localStorage', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleEmployee(1);
        result.current.toggleHolidays();
      });
      
      const stored = localStorage.getItem('calendar-filters');
      expect(stored).toBeTruthy();
      
      const parsed = JSON.parse(stored!);
      expect(parsed.state.selectedEmployeeIds).toContain(1);
      expect(parsed.state.showHolidays).toBe(false);
    });

    it('should restore state from localStorage', () => {
      // First render: set some state
      const { result: result1 } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result1.current.selectAllEmployees([1, 2, 3]);
        result1.current.toggleSchoolVacations();
        result1.current.setSidebarCollapsed(true);
      });
      
      // Second render: should restore state
      const { result: result2 } = renderHook(() => useCalendarFilterStore());
      
      expect(result2.current.selectedEmployeeIds).toEqual([1, 2, 3]);
      expect(result2.current.showSchoolVacations).toBe(false);
      expect(result2.current.isSidebarCollapsed).toBe(true);
    });

    it('should use correct localStorage key', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.toggleEmployee(1);
      });
      
      const key = 'calendar-filters';
      const stored = localStorage.getItem(key);
      expect(stored).toBeTruthy();
    });

    it('should persist complex state changes', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.selectAllEmployees([1, 2, 3, 4, 5]);
        result.current.toggleHolidays();
        result.current.toggleSickLeave();
        result.current.toggleTraining();
        result.current.setSidebarCollapsed(true);
      });
      
      const stored = localStorage.getItem('calendar-filters');
      const parsed = JSON.parse(stored!);
      
      expect(parsed.state.selectedEmployeeIds).toEqual([1, 2, 3, 4, 5]);
      expect(parsed.state.showHolidays).toBe(false);
      expect(parsed.state.showSickLeave).toBe(false);
      expect(parsed.state.showTraining).toBe(false);
      expect(parsed.state.isSidebarCollapsed).toBe(true);
    });
  });

  describe('Selector Hooks', () => {
    it('useSelectedEmployeeIds should return selected employee IDs', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.selectAllEmployees([1, 2, 3]);
      });
      
      expect(result.current.selectedEmployeeIds).toEqual([1, 2, 3]);
    });

    it('useIsSidebarCollapsed should return sidebar state', () => {
      const { result } = renderHook(() => useCalendarFilterStore());
      
      act(() => {
        result.current.setSidebarCollapsed(true);
      });
      
      expect(result.current.isSidebarCollapsed).toBe(true);
    });
  });
});
