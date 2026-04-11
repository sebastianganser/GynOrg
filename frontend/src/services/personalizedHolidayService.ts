import { holidayService } from './holidayService';
import { employeePreferencesService } from './employeePreferencesService';
import type { Holiday, SchoolVacationType } from '../types/holiday';
import type { EmployeeSchoolHolidayPreferences } from './employeePreferencesService';

export interface PersonalizedHoliday extends Holiday {
  federalState: string;
  relevanceLevel: 'primary' | 'additional' | 'children' | 'all';
  color: string;
  isRelevant: boolean;
  start_date?: string;
  end_date?: string;
  vacation_type?: SchoolVacationType;
}

export interface HolidayFilterOptions {
  federalStates?: string[];
  vacationTypes?: SchoolVacationType[];
  startDate?: string;
  endDate?: string;
  relevanceLevels?: ('primary' | 'additional' | 'children' | 'all')[];
}

class PersonalizedHolidayService {
  private cache = new Map<string, PersonalizedHoliday[]>();
  private cacheExpiry = new Map<string, number>();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  // Color scheme for federal states (consistent with FederalStateSwitcher)
  private getStateColor(stateCode: string): string {
    const colors = {
      'Baden-Württemberg': '#FF6B6B',
      'Bayern': '#4ECDC4',
      'Berlin': '#45B7D1',
      'Brandenburg': '#96CEB4',
      'Bremen': '#FFEAA7',
      'Hamburg': '#DDA0DD',
      'Hessen': '#98D8C8',
      'Mecklenburg-Vorpommern': '#F7DC6F',
      'Niedersachsen': '#BB8FCE',
      'Nordrhein-Westfalen': '#85C1E9',
      'Rheinland-Pfalz': '#F8C471',
      'Saarland': '#82E0AA',
      'Sachsen': '#F1948A',
      'Sachsen-Anhalt': '#85C1E9',
      'Schleswig-Holstein': '#D7BDE2',
      'Thüringen': '#A9DFBF'
    };
    return colors[stateCode as keyof typeof colors] || '#95A5A6';
  }

  // Determine relevance level based on employee preferences
  private getRelevanceLevel(
    federalState: string,
    preferences?: EmployeeSchoolHolidayPreferences
  ): 'primary' | 'additional' | 'children' | 'all' {
    if (!preferences) return 'all';

    if (federalState === preferences.primary_federal_state) {
      return 'primary';
    }

    if (preferences.additional_federal_states?.includes(federalState)) {
      return 'additional';
    }

    if (preferences.children_federal_states?.includes(federalState)) {
      return 'children';
    }

    return 'all';
  }

  // Check if holiday is relevant based on preferences
  private isHolidayRelevant(
    holiday: Holiday,
    preferences?: EmployeeSchoolHolidayPreferences
  ): boolean {
    if (!preferences) return true;

    // Check federal state relevance
    const relevantStates = [
      preferences.primary_federal_state,
      ...(preferences.additional_federal_states || []),
      ...(preferences.children_federal_states || [])
    ];

    if (holiday.federal_state && !relevantStates.includes(holiday.federal_state)) {
      return preferences.show_all_states || false;
    }

    // Check vacation type relevance
    if (preferences.relevant_vacation_types?.length && holiday.school_vacation_type) {
      return preferences.relevant_vacation_types.includes(holiday.school_vacation_type);
    }

    return true;
  }

  // Convert Holiday to PersonalizedHoliday
  private personalizeHoliday(
    holiday: Holiday,
    preferences?: EmployeeSchoolHolidayPreferences
  ): PersonalizedHoliday {
    const federalState = holiday.federal_state || '';
    const relevanceLevel = this.getRelevanceLevel(federalState, preferences);
    const isRelevant = this.isHolidayRelevant(holiday, preferences);
    const color = this.getStateColor(federalState);

    return {
      ...holiday,
      federalState,
      relevanceLevel,
      color,
      isRelevant
    };
  }

  // Get cache key for employee preferences
  private getCacheKey(employeeId?: number, options?: HolidayFilterOptions): string {
    const optionsKey = options ? JSON.stringify(options) : 'default';
    return `${employeeId || 'anonymous'}-${optionsKey}`;
  }

  // Check if cache is valid
  private isCacheValid(key: string): boolean {
    const expiry = this.cacheExpiry.get(key);
    return expiry ? Date.now() < expiry : false;
  }

  // Get holidays for employee with personalization
  async getPersonalizedHolidays(
    employeeId?: number,
    options?: HolidayFilterOptions
  ): Promise<PersonalizedHoliday[]> {
    const cacheKey = this.getCacheKey(employeeId, options);

    // Check cache first
    if (this.isCacheValid(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (cached) {
        return cached;
      }
    }

    try {
      // Get employee preferences if employeeId provided
      let preferences: EmployeeSchoolHolidayPreferences | undefined;
      if (employeeId) {
        try {
          preferences = await employeePreferencesService.getEmployeePreferences(employeeId);
        } catch (error) {
          console.warn('Could not load employee preferences, using defaults:', error);
        }
      }

      // Determine which federal states to load
      let federalStatesToLoad: string[] = [];
      
      if (options?.federalStates?.length) {
        federalStatesToLoad = options.federalStates;
      } else if (preferences) {
        federalStatesToLoad = [
          preferences.primary_federal_state,
          ...(preferences.additional_federal_states || []),
          ...(preferences.children_federal_states || [])
        ];
        
        // If show_all_states is enabled, we might need all states
        if (preferences.show_all_states) {
          // We'll load all states, but this could be optimized
          federalStatesToLoad = []; // Empty array means load all
        }
      }

      // Get holidays from holiday service
      const holidays = await holidayService.getHolidays({
        federal_state: federalStatesToLoad.length ? federalStatesToLoad[0] : undefined,
        start_date: options?.startDate,
        end_date: options?.endDate
      });

      // Personalize holidays
      let personalizedHolidays = holidays.map(holiday => 
        this.personalizeHoliday(holiday, preferences)
      );

      // Apply additional filters
      if (options?.vacationTypes?.length) {
        personalizedHolidays = personalizedHolidays.filter(holiday =>
          holiday.vacation_type && options.vacationTypes!.includes(holiday.vacation_type)
        );
      }

      if (options?.relevanceLevels?.length) {
        personalizedHolidays = personalizedHolidays.filter(holiday =>
          options.relevanceLevels!.includes(holiday.relevanceLevel)
        );
      }

      // Sort by relevance and date
      personalizedHolidays.sort((a, b) => {
        // Primary relevance first
        const relevanceOrder = { primary: 0, additional: 1, children: 2, all: 3 };
        const relevanceDiff = relevanceOrder[a.relevanceLevel] - relevanceOrder[b.relevanceLevel];
        
        if (relevanceDiff !== 0) return relevanceDiff;
        
        // Then by date (use date field from Holiday interface)
        return new Date(a.date).getTime() - new Date(b.date).getTime();
      });

      // Cache the result
      this.cache.set(cacheKey, personalizedHolidays);
      this.cacheExpiry.set(cacheKey, Date.now() + this.CACHE_DURATION);

      return personalizedHolidays;
    } catch (error) {
      console.error('Error getting personalized holidays:', error);
      throw error;
    }
  }

  // Get holidays for specific federal states
  async getHolidaysForStates(
    federalStates: string[],
    options?: Omit<HolidayFilterOptions, 'federalStates'>
  ): Promise<PersonalizedHoliday[]> {
    return this.getPersonalizedHolidays(undefined, {
      ...options,
      federalStates
    });
  }

  // Get holidays for date range
  async getHolidaysForDateRange(
    startDate: string,
    endDate: string,
    employeeId?: number
  ): Promise<PersonalizedHoliday[]> {
    return this.getPersonalizedHolidays(employeeId, {
      startDate,
      endDate
    });
  }

  // Get upcoming holidays for employee
  async getUpcomingHolidays(
    employeeId?: number,
    daysAhead: number = 30
  ): Promise<PersonalizedHoliday[]> {
    const startDate = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + daysAhead * 24 * 60 * 60 * 1000)
      .toISOString().split('T')[0];

    const holidays = await this.getPersonalizedHolidays(employeeId, {
      startDate,
      endDate
    });

    return holidays.filter(holiday => holiday.isRelevant);
  }

  // Get holiday statistics for employee
  async getHolidayStats(employeeId?: number): Promise<{
    totalHolidays: number;
    relevantHolidays: number;
    byRelevanceLevel: Record<string, number>;
    byVacationType: Record<string, number>;
    byFederalState: Record<string, number>;
  }> {
    const holidays = await this.getPersonalizedHolidays(employeeId);

    const stats = {
      totalHolidays: holidays.length,
      relevantHolidays: holidays.filter(h => h.isRelevant).length,
      byRelevanceLevel: {} as Record<string, number>,
      byVacationType: {} as Record<string, number>,
      byFederalState: {} as Record<string, number>
    };

    holidays.forEach(holiday => {
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
  }

  // Clear cache
  clearCache(): void {
    this.cache.clear();
    this.cacheExpiry.clear();
  }

  // Clear cache for specific employee
  clearEmployeeCache(employeeId: number): void {
    const keysToDelete: string[] = [];
    
    this.cache.forEach((_, key) => {
      if (key.startsWith(`${employeeId}-`)) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => {
      this.cache.delete(key);
      this.cacheExpiry.delete(key);
    });
  }
}

export const personalizedHolidayService = new PersonalizedHolidayService();
