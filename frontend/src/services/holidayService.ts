import { API_BASE_URL } from './config';
import { 
  Holiday, 
  HolidayFilter, 
  HolidayImportResult, 
  HolidayDisplayFilter,
  HolidayType,
  getHolidayColor,
  getHolidayTextColor,
  formatHolidayDisplayName
} from '../types/holiday';

class HolidayService {
  private baseUrl = `${API_BASE_URL}/holidays`;

  async getHolidays(filter?: HolidayFilter): Promise<Holiday[]> {
    const params = new URLSearchParams();
    
    if (filter?.year) params.append('year', filter.year.toString());
    if (filter?.month) params.append('month', filter.month.toString());
    if (filter?.federal_state) params.append('federal_state', filter.federal_state);
    if (filter?.include_nationwide !== undefined) {
      params.append('include_nationwide', filter.include_nationwide.toString());
    }
    if (filter?.holiday_type) params.append('holiday_type', filter.holiday_type);
    if (filter?.school_vacation_type) params.append('school_vacation_type', filter.school_vacation_type);
    if (filter?.data_source) params.append('data_source', filter.data_source);

    const url = params.toString() ? `${this.baseUrl}?${params}` : this.baseUrl;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async getUpcomingHolidays(federal_state?: string, days: number = 30): Promise<Holiday[]> {
    const params = new URLSearchParams();
    
    if (federal_state) params.append('federal_state', federal_state);
    params.append('days', days.toString());

    const response = await fetch(`${this.baseUrl}/upcoming?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async checkHoliday(date: string, federal_state?: string): Promise<{
    is_holiday: boolean;
    holiday?: Holiday;
    message: string;
  }> {
    const params = new URLSearchParams();
    if (federal_state) params.append('federal_state', federal_state);

    const url = params.toString() 
      ? `${this.baseUrl}/check/${date}?${params}`
      : `${this.baseUrl}/check/${date}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async importHolidaysForYear(year: number, federal_states?: string[]): Promise<HolidayImportResult> {
    const body = federal_states ? { federal_states } : undefined;
    
    const response = await fetch(`${this.baseUrl}/import/${year}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!response.ok) {
      if (response.status === 422) {
        // 422 Unprocessable Entity - wahrscheinlich Duplikate
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`422: ${errorData.detail || 'Feiertage bereits vorhanden'}`);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async importCurrentYearHolidays(): Promise<HolidayImportResult> {
    const response = await fetch(`${this.baseUrl}/import/current-year`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      if (response.status === 422) {
        // 422 Unprocessable Entity - wahrscheinlich Duplikate
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`422: ${errorData.detail || 'Feiertage bereits vorhanden'}`);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async importNextYearHolidays(): Promise<HolidayImportResult> {
    const response = await fetch(`${this.baseUrl}/import/next-year`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      if (response.status === 422) {
        // 422 Unprocessable Entity - wahrscheinlich Duplikate
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`422: ${errorData.detail || 'Feiertage bereits vorhanden'}`);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async deleteHolidaysForYear(year: number): Promise<{
    year: number;
    deleted_count: number;
    message: string;
  }> {
    const response = await fetch(`${this.baseUrl}/year/${year}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async getFederalStates(): Promise<Array<{ code: string; name: string }>> {
    const response = await fetch(`${this.baseUrl}/federal-states`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async getAvailableYears(): Promise<{
    years: number[];
    count: number;
    current_year: number;
  }> {
    const response = await fetch(`${this.baseUrl}/years`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async getStatistics(year?: number): Promise<{
    year: number;
    total_holidays: number;
    nationwide_holidays: number;
    state_specific_holidays: number;
    holidays_by_state: Record<string, number>;
  }> {
    const params = year ? `?year=${year}` : '';
    
    const response = await fetch(`${this.baseUrl}/statistics${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  // Frontend-Filter für Holiday-Anzeige
  filterHolidaysForDisplay(holidays: Holiday[], displayFilter: HolidayDisplayFilter, userFederalState?: string): Holiday[] {
    return holidays.filter(holiday => {
      // Filter nach Holiday-Typ
      if (!displayFilter.showPublicHolidays && holiday.holiday_type === HolidayType.PUBLIC_HOLIDAY) {
        return false;
      }
      if (!displayFilter.showSchoolVacations && holiday.holiday_type === HolidayType.SCHOOL_VACATION) {
        return false;
      }

      // Filter nach Bundesland
      if (displayFilter.showOnlyMyState && userFederalState) {
        // Zeige nur Feiertage/Ferien für das Benutzer-Bundesland oder bundesweite
        if (!holiday.is_nationwide && holiday.federal_state !== userFederalState) {
          return false;
        }
      }

      // Filter nach ausgewählten Bundesländern
      if (displayFilter.selectedFederalStates.length > 0) {
        if (!holiday.is_nationwide && 
            holiday.federal_state && 
            !displayFilter.selectedFederalStates.includes(holiday.federal_state)) {
          return false;
        }
      }

      return true;
    });
  }

  // Hilfsmethoden für die Kalenderintegration
  formatHolidayForCalendar(holiday: Holiday) {
    return {
      id: `holiday-${holiday.id}`,
      title: formatHolidayDisplayName(holiday),
      start: new Date(holiday.date),
      end: new Date(holiday.date),
      allDay: true,
      resource: {
        type: 'holiday',
        holidayType: holiday.holiday_type,
        schoolVacationType: holiday.school_vacation_type,
        isNationwide: holiday.is_nationwide,
        federalState: holiday.federal_state,
        notes: holiday.notes,
        originalHoliday: holiday
      }
    };
  }

  getHolidayColor(holiday: Holiday): string {
    return getHolidayColor(holiday);
  }

  getHolidayTextColor(holiday: Holiday): string {
    return getHolidayTextColor(holiday);
  }

  // Neue Hilfsmethoden für Schulferien
  async getSchoolVacations(year: number, federalState?: string): Promise<Holiday[]> {
    return this.getHolidays({
      year,
      holiday_type: HolidayType.SCHOOL_VACATION,
      federal_state: federalState
    });
  }

  async getPublicHolidays(year: number, federalState?: string): Promise<Holiday[]> {
    return this.getHolidays({
      year,
      holiday_type: HolidayType.PUBLIC_HOLIDAY,
      federal_state: federalState
    });
  }
}

export const holidayService = new HolidayService();

// Re-export types for convenience
export type { 
  Holiday, 
  HolidayFilter, 
  HolidayImportResult,
  HolidayDisplayFilter,
  GroupedHoliday
} from '../types/holiday';

export { 
  HolidayType, 
  SchoolVacationType, 
  DataSource 
} from '../types/holiday';
