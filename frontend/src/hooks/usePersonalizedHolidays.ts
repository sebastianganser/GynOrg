import { useState, useEffect, useCallback, useMemo } from 'react';
import { personalizedHolidayService, type PersonalizedHoliday, type HolidayFilterOptions } from '../services/personalizedHolidayService';
import { useFederalStateSwitcher } from '../components/FederalStateSwitcher';
import { useEmployeePreferences } from './useEmployeePreferences';
import type { SchoolVacationType } from '../types/holiday';

export interface UsePersonalizedHolidaysOptions {
  employeeId?: number;
  autoLoadEmployeePreferences?: boolean;
  initialFederalStates?: string[];
  initialVacationTypes?: SchoolVacationType[];
  dateRange?: {
    startDate: string;
    endDate: string;
  };
}

export interface UsePersonalizedHolidaysReturn {
  // Data
  holidays: PersonalizedHoliday[];
  filteredHolidays: PersonalizedHoliday[];
  
  // Loading states
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  
  // Federal state management
  activeFederalStates: string[];
  primaryFederalState: string;
  additionalFederalStates: string[];
  childrenFederalStates: string[];
  
  // Filter management
  activeVacationTypes: SchoolVacationType[];
  activeRelevanceLevels: ('primary' | 'additional' | 'children' | 'all')[];
  showOnlyRelevant: boolean;
  
  // Actions
  handleStateToggle: (stateCode: string) => void;
  handlePrimaryStateChange: (stateCode: string) => void;
  toggleVacationType: (vacationType: SchoolVacationType) => void;
  toggleRelevanceLevel: (level: 'primary' | 'additional' | 'children' | 'all') => void;
  setShowOnlyRelevant: (show: boolean) => void;
  refreshHolidays: () => Promise<void>;
  clearCache: () => void;
  
  // Utility functions
  getHolidaysForDate: (date: string) => PersonalizedHoliday[];
  getUpcomingHolidays: (daysAhead?: number) => PersonalizedHoliday[];
  getHolidayStats: () => {
    totalHolidays: number;
    relevantHolidays: number;
    byRelevanceLevel: Record<string, number>;
    byVacationType: Record<string, number>;
    byFederalState: Record<string, number>;
  };
}

export const usePersonalizedHolidays = (
  options: UsePersonalizedHolidaysOptions = {}
): UsePersonalizedHolidaysReturn => {
  const {
    employeeId,
    autoLoadEmployeePreferences = true,
    initialFederalStates: _initialFederalStates = [],
    initialVacationTypes = [],
    dateRange
  } = options;

  // State management
  const [holidays, setHolidays] = useState<PersonalizedHoliday[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [activeVacationTypes, setActiveVacationTypes] = useState<SchoolVacationType[]>(initialVacationTypes);
  const [activeRelevanceLevels, setActiveRelevanceLevels] = useState<('primary' | 'additional' | 'children' | 'all')[]>(['primary', 'additional', 'children']);
  const [showOnlyRelevant, setShowOnlyRelevant] = useState(true);

  // Employee preferences hook
  const employeePreferencesQuery = useEmployeePreferences(employeeId || 0);
  const employeePreferences = employeePreferencesQuery.data;
  const preferencesLoading = employeePreferencesQuery.isLoading;

  // Federal state switcher hook
  const {
    primaryFederalState,
    additionalFederalStates,
    childrenFederalStates,
    activeFederalStates,
    handleStateToggle,
    handlePrimaryStateChange,
    setPrimaryFederalState,
    setAdditionalFederalStates,
    setChildrenFederalStates
  } = useFederalStateSwitcher(
    employeePreferences?.primary_federal_state,
    employeePreferences?.additional_federal_states || [],
    employeePreferences?.children_federal_states || []
  );

  // Update federal states when employee preferences change
  useEffect(() => {
    if (employeePreferences && autoLoadEmployeePreferences) {
      setPrimaryFederalState(employeePreferences.primary_federal_state);
      setAdditionalFederalStates(employeePreferences.additional_federal_states || []);
      setChildrenFederalStates(employeePreferences.children_federal_states || []);
      
      // Update vacation types if specified in preferences
      if (employeePreferences.relevant_vacation_types?.length) {
        setActiveVacationTypes(employeePreferences.relevant_vacation_types as SchoolVacationType[]);
      }
    }
  }, [employeePreferences, autoLoadEmployeePreferences, setPrimaryFederalState, setAdditionalFederalStates, setChildrenFederalStates]);

  // Load holidays function
  const loadHolidays = useCallback(async (refresh = false) => {
    if (refresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const filterOptions: HolidayFilterOptions = {
        federalStates: activeFederalStates.length > 0 ? activeFederalStates : undefined,
        vacationTypes: activeVacationTypes.length > 0 ? activeVacationTypes : undefined,
        startDate: dateRange?.startDate,
        endDate: dateRange?.endDate,
        relevanceLevels: activeRelevanceLevels.length > 0 ? activeRelevanceLevels : undefined
      };

      const personalizedHolidays = await personalizedHolidayService.getPersonalizedHolidays(
        employeeId,
        filterOptions
      );

      setHolidays(personalizedHolidays);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load holidays';
      setError(errorMessage);
      console.error('Error loading personalized holidays:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [employeeId, activeFederalStates, activeVacationTypes, activeRelevanceLevels, dateRange]);

  // Load holidays when dependencies change
  useEffect(() => {
    if (!preferencesLoading) {
      loadHolidays();
    }
  }, [loadHolidays, preferencesLoading]);

  // Filter holidays based on current settings
  const filteredHolidays = useMemo(() => {
    let filtered = holidays;

    // Filter by relevance if enabled
    if (showOnlyRelevant) {
      filtered = filtered.filter(holiday => holiday.isRelevant);
    }

    // Additional client-side filtering can be added here
    return filtered;
  }, [holidays, showOnlyRelevant]);

  // Vacation type toggle
  const toggleVacationType = useCallback((vacationType: SchoolVacationType) => {
    setActiveVacationTypes(prev => {
      if (prev.includes(vacationType)) {
        return prev.filter(type => type !== vacationType);
      } else {
        return [...prev, vacationType];
      }
    });
  }, []);

  // Relevance level toggle
  const toggleRelevanceLevel = useCallback((level: 'primary' | 'additional' | 'children' | 'all') => {
    setActiveRelevanceLevels(prev => {
      if (prev.includes(level)) {
        return prev.filter(l => l !== level);
      } else {
        return [...prev, level];
      }
    });
  }, []);

  // Refresh holidays
  const refreshHolidays = useCallback(async () => {
    await loadHolidays(true);
  }, [loadHolidays]);

  // Clear cache
  const clearCache = useCallback(() => {
    if (employeeId) {
      personalizedHolidayService.clearEmployeeCache(employeeId);
    } else {
      personalizedHolidayService.clearCache();
    }
  }, [employeeId]);

  // Get holidays for specific date
  const getHolidaysForDate = useCallback((date: string) => {
    return filteredHolidays.filter(holiday => holiday.date === date);
  }, [filteredHolidays]);

  // Get upcoming holidays
  const getUpcomingHolidays = useCallback((daysAhead: number = 30) => {
    const today = new Date();
    const futureDate = new Date(today.getTime() + daysAhead * 24 * 60 * 60 * 1000);
    
    return filteredHolidays.filter(holiday => {
      const holidayDate = new Date(holiday.date);
      return holidayDate >= today && holidayDate <= futureDate;
    });
  }, [filteredHolidays]);

  // Get holiday statistics
  const getHolidayStats = useCallback(() => {
    const stats = {
      totalHolidays: filteredHolidays.length,
      relevantHolidays: filteredHolidays.filter(h => h.isRelevant).length,
      byRelevanceLevel: {} as Record<string, number>,
      byVacationType: {} as Record<string, number>,
      byFederalState: {} as Record<string, number>
    };

    filteredHolidays.forEach(holiday => {
      // Count by relevance level
      stats.byRelevanceLevel[holiday.relevanceLevel] = 
        (stats.byRelevanceLevel[holiday.relevanceLevel] || 0) + 1;

      // Count by vacation type (only if defined)
      if (holiday.vacation_type) {
        stats.byVacationType[holiday.vacation_type] = 
          (stats.byVacationType[holiday.vacation_type] || 0) + 1;
      }

      // Count by federal state (only if defined)
      if (holiday.federal_state) {
        stats.byFederalState[holiday.federal_state] = 
          (stats.byFederalState[holiday.federal_state] || 0) + 1;
      }
    });

    return stats;
  }, [filteredHolidays]);

  return {
    // Data
    holidays,
    filteredHolidays,
    
    // Loading states
    isLoading: isLoading || preferencesLoading,
    isRefreshing,
    error,
    
    // Federal state management
    activeFederalStates,
    primaryFederalState,
    additionalFederalStates,
    childrenFederalStates,
    
    // Filter management
    activeVacationTypes,
    activeRelevanceLevels,
    showOnlyRelevant,
    
    // Actions
    handleStateToggle,
    handlePrimaryStateChange,
    toggleVacationType,
    toggleRelevanceLevel,
    setShowOnlyRelevant,
    refreshHolidays,
    clearCache,
    
    // Utility functions
    getHolidaysForDate,
    getUpcomingHolidays,
    getHolidayStats
  };
};

// Specialized hooks for common use cases

// Hook for calendar integration
export const useCalendarHolidays = (
  employeeId?: number,
  currentMonth?: Date
) => {
  const startDate = currentMonth 
    ? new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).toISOString().split('T')[0]
    : undefined;
  const endDate = currentMonth 
    ? new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).toISOString().split('T')[0]
    : undefined;

  return usePersonalizedHolidays({
    employeeId,
    dateRange: startDate && endDate ? { startDate, endDate } : undefined,
    autoLoadEmployeePreferences: true
  });
};

// Hook for upcoming holidays widget
export const useUpcomingHolidays = (
  employeeId?: number,
  daysAhead: number = 30
) => {
  const startDate = new Date().toISOString().split('T')[0];
  const endDate = new Date(Date.now() + daysAhead * 24 * 60 * 60 * 1000)
    .toISOString().split('T')[0];

  return usePersonalizedHolidays({
    employeeId,
    dateRange: { startDate, endDate },
    autoLoadEmployeePreferences: true
  });
};

// Hook for federal state comparison
export const useFederalStateComparison = (
  federalStates: string[],
  dateRange?: { startDate: string; endDate: string }
) => {
  return usePersonalizedHolidays({
    initialFederalStates: federalStates,
    dateRange,
    autoLoadEmployeePreferences: false
  });
};
