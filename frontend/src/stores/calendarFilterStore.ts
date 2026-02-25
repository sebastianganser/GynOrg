import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Calendar Filter State Interface
 */
export interface CalendarFilters {
  // Employee filters
  selectedEmployeeIds: number[];
  
  // Calendar type filters
  showHolidays: boolean;
  showSchoolVacations: boolean;
  showVacationAbsences: boolean;
  showSickLeave: boolean;
  showTraining: boolean;
  showSpecialLeave: boolean;
  
  // Sidebar state
  isSidebarCollapsed: boolean;
}

/**
 * Calendar Filter Store Actions
 */
interface CalendarFilterActions {
  // Employee filter actions
  toggleEmployee: (employeeId: number) => void;
  selectAllEmployees: (employeeIds: number[]) => void;
  deselectAllEmployees: () => void;
  setSelectedEmployees: (employeeIds: number[]) => void;
  
  // Calendar filter actions
  toggleHolidays: () => void;
  toggleSchoolVacations: () => void;
  toggleVacationAbsences: () => void;
  toggleSickLeave: () => void;
  toggleTraining: () => void;
  toggleSpecialLeave: () => void;
  
  // Bulk calendar filter actions
  setCalendarFilter: (filterKey: keyof Omit<CalendarFilters, 'selectedEmployeeIds' | 'isSidebarCollapsed'>, value: boolean) => void;
  enableAllCalendarFilters: () => void;
  disableAllCalendarFilters: () => void;
  
  // Sidebar actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Reset action
  resetFilters: () => void;
}

/**
 * Combined Store Type
 */
type CalendarFilterStore = CalendarFilters & CalendarFilterActions;

/**
 * Default filter state
 */
const defaultFilters: CalendarFilters = {
  selectedEmployeeIds: [],
  showHolidays: true,
  showSchoolVacations: true,
  showVacationAbsences: true,
  showSickLeave: true,
  showTraining: true,
  showSpecialLeave: true,
  isSidebarCollapsed: false,
};

/**
 * Calendar Filter Store with localStorage persistence
 */
export const useCalendarFilterStore = create<CalendarFilterStore>()(
  persist(
    (set, get) => ({
      // Initial state
      ...defaultFilters,

      // Employee filter actions
      toggleEmployee: (employeeId) =>
        set((state) => ({
          selectedEmployeeIds: state.selectedEmployeeIds.includes(employeeId)
            ? state.selectedEmployeeIds.filter((id) => id !== employeeId)
            : [...state.selectedEmployeeIds, employeeId],
        })),

      selectAllEmployees: (employeeIds) =>
        set({ selectedEmployeeIds: employeeIds }),

      deselectAllEmployees: () =>
        set({ selectedEmployeeIds: [] }),

      setSelectedEmployees: (employeeIds) =>
        set({ selectedEmployeeIds: employeeIds }),

      // Calendar filter actions
      toggleHolidays: () =>
        set((state) => {
          console.log('[CalendarFilterStore] toggleHolidays:', !state.showHolidays);
          return { showHolidays: !state.showHolidays };
        }),

      toggleSchoolVacations: () =>
        set((state) => ({ showSchoolVacations: !state.showSchoolVacations })),

      toggleVacationAbsences: () =>
        set((state) => ({ showVacationAbsences: !state.showVacationAbsences })),

      toggleSickLeave: () =>
        set((state) => ({ showSickLeave: !state.showSickLeave })),

      toggleTraining: () =>
        set((state) => ({ showTraining: !state.showTraining })),

      toggleSpecialLeave: () =>
        set((state) => ({ showSpecialLeave: !state.showSpecialLeave })),

      // Bulk calendar filter actions
      setCalendarFilter: (filterKey, value) =>
        set({ [filterKey]: value }),

      enableAllCalendarFilters: () =>
        set({
          showHolidays: true,
          showSchoolVacations: true,
          showVacationAbsences: true,
          showSickLeave: true,
          showTraining: true,
          showSpecialLeave: true,
        }),

      disableAllCalendarFilters: () =>
        set({
          showHolidays: false,
          showSchoolVacations: false,
          showVacationAbsences: false,
          showSickLeave: false,
          showTraining: false,
          showSpecialLeave: false,
        }),

      // Sidebar actions
      toggleSidebar: () =>
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

      setSidebarCollapsed: (collapsed) =>
        set({ isSidebarCollapsed: collapsed }),

      // Reset action
      resetFilters: () =>
        set(defaultFilters),
    }),
    {
      name: 'calendar-filter-storage', // EXPLICIT localStorage key
      version: 1,
      // Explicitly define what to persist
      partialize: (state) => ({
        selectedEmployeeIds: state.selectedEmployeeIds,
        showHolidays: state.showHolidays,
        showSchoolVacations: state.showSchoolVacations,
        showVacationAbsences: state.showVacationAbsences,
        showSickLeave: state.showSickLeave,
        showTraining: state.showTraining,
        showSpecialLeave: state.showSpecialLeave,
        isSidebarCollapsed: state.isSidebarCollapsed,
      }),
    }
  )
);

/**
 * Selector hooks for optimized re-renders
 */
export const useSelectedEmployeeIds = () =>
  useCalendarFilterStore((state) => state.selectedEmployeeIds);

export const useCalendarFilters = () =>
  useCalendarFilterStore((state) => ({
    showHolidays: state.showHolidays,
    showSchoolVacations: state.showSchoolVacations,
    showVacationAbsences: state.showVacationAbsences,
    showSickLeave: state.showSickLeave,
    showTraining: state.showTraining,
    showSpecialLeave: state.showSpecialLeave,
  }));

export const useIsSidebarCollapsed = () =>
  useCalendarFilterStore((state) => state.isSidebarCollapsed);
