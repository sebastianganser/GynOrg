import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Calendar Filter State Interface
 */
export interface CalendarFilters {
  // Employee filters
  selectedEmployeeIds: number[];

  // Calendar Holiday filters
  showHolidays: boolean;
  showSchoolVacations: boolean;

  // Absence Type filters
  selectedAbsenceTypeIds: number[];

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

  // Calendar Holiday filter actions
  toggleHolidays: () => void;
  toggleSchoolVacations: () => void;

  // Absence Type filter actions
  toggleAbsenceType: (id: number) => void;
  selectAllAbsenceTypes: (ids: number[]) => void;
  deselectAllAbsenceTypes: () => void;

  // Bulk calendar filter actions
  setCalendarFilter: (filterKey: keyof Omit<CalendarFilters, 'selectedEmployeeIds' | 'selectedAbsenceTypeIds' | 'isSidebarCollapsed'>, value: boolean) => void;
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
  selectedAbsenceTypeIds: [],
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

      // Absence Type filter actions
      toggleAbsenceType: (id) =>
        set((state) => ({
          selectedAbsenceTypeIds: state.selectedAbsenceTypeIds.includes(id)
            ? state.selectedAbsenceTypeIds.filter((typeId) => typeId !== id)
            : [...state.selectedAbsenceTypeIds, id],
        })),

      selectAllAbsenceTypes: (ids) =>
        set({ selectedAbsenceTypeIds: ids }),

      deselectAllAbsenceTypes: () =>
        set({ selectedAbsenceTypeIds: [] }),

      // Bulk calendar filter actions
      setCalendarFilter: (filterKey, value) =>
        set({ [filterKey]: value }),

      enableAllCalendarFilters: () =>
        set({
          showHolidays: true,
          showSchoolVacations: true,
        }),

      disableAllCalendarFilters: () =>
        set({
          showHolidays: false,
          showSchoolVacations: false,
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
        selectedAbsenceTypeIds: state.selectedAbsenceTypeIds,
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
    selectedAbsenceTypeIds: state.selectedAbsenceTypeIds,
  }));

export const useIsSidebarCollapsed = () =>
  useCalendarFilterStore((state) => state.isSidebarCollapsed);
