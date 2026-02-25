import { useState, useEffect, useRef, useCallback } from 'react';
import { holidayService, Holiday, HolidayFilter, HolidayType } from '../services/holidayService';
import { useCalendarSettings } from './useCalendarSettings';

// Cache-Interface für Jahr-basiertes Caching
interface HolidayCache {
  [cacheKey: string]: {
    holidays: Holiday[];
    timestamp: number;
  };
}

// Erweiterte Hook-Signatur mit Jahr-Parameter
export const useHolidays = (year?: number, additionalFilter?: Omit<HolidayFilter, 'year'>) => {
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentYear, setCurrentYear] = useState<number>(year || new Date().getFullYear());
  const [availableYears, setAvailableYears] = useState<number[]>([]);

  // Jahr-basiertes Caching mit useRef für Persistenz zwischen Renders
  const cacheRef = useRef<HolidayCache>({});
  const CACHE_DURATION = 5 * 60 * 1000; // 5 Minuten Cache

  // Lade Kalendereinstellungen
  const { data: calendarSettings } = useCalendarSettings();

  // Cache-Key generieren basierend auf Jahr und Kalendereinstellungen
  const generateCacheKey = useCallback((targetYear: number, settings?: any) => {
    const federalStates = settings?.selected_federal_states?.join(',') || '';
    const showNationwide = settings?.show_nationwide_holidays || false;
    return `${targetYear}-${federalStates}-${showNationwide}`;
  }, []);

  // Prüfe Cache für gegebenes Jahr
  const getCachedHolidays = useCallback((targetYear: number) => {
    const cacheKey = generateCacheKey(targetYear, calendarSettings);
    const cached = cacheRef.current[cacheKey];

    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.holidays;
    }
    return null;
  }, [generateCacheKey, calendarSettings]);

  // Speichere Holidays im Cache
  const setCachedHolidays = useCallback((targetYear: number, holidays: Holiday[]) => {
    const cacheKey = generateCacheKey(targetYear, calendarSettings);
    cacheRef.current[cacheKey] = {
      holidays,
      timestamp: Date.now()
    };
  }, [generateCacheKey, calendarSettings]);

  const fetchHolidays = async (targetYear?: number, newFilter?: Omit<HolidayFilter, 'year'>) => {
    const yearToFetch = targetYear || currentYear;

    // Prüfe Cache zuerst
    const cachedHolidays = getCachedHolidays(yearToFetch);
    if (cachedHolidays) {
      setHolidays(cachedHolidays);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Kombiniere Filter mit Jahr und zusätzlichen Filtern
      const effectiveFilter: HolidayFilter = {
        year: yearToFetch,
        ...additionalFilter,
        ...newFilter,
      };

      // Verwende Kalendereinstellungen wenn verfügbar und keine expliziten Filter gesetzt sind
      if (calendarSettings && !effectiveFilter.federal_state && effectiveFilter.include_nationwide === undefined) {
        // Sammle alle Feiertage für die ausgewählten Bundesländer
        const allHolidays: Holiday[] = [];
        const processedIds = new Set<number>();

        const safePush = (newHolidays: Holiday[]) => {
          newHolidays.forEach(h => {
            if (!processedIds.has(h.id)) {
              allHolidays.push(h);
              processedIds.add(h.id);
            }
          });
        };

        // 1. Bundesweite Feiertage laden (wenn aktiviert)
        if (calendarSettings.show_nationwide_holidays) {
          const nationwideFilter = {
            ...effectiveFilter,
            federal_state: undefined,
            include_nationwide: true,
          };
          const nationwideHolidays = await holidayService.getHolidays(nationwideFilter);
          safePush(nationwideHolidays.filter(h => h.is_nationwide));
        }

        // 2. Bundeslandspezifische Feiertage (Public Holidays) laden
        if (calendarSettings.selected_federal_states) {
          for (const stateCode of calendarSettings.selected_federal_states) {
            const stateFilter = {
              ...effectiveFilter,
              federal_state: stateCode,
              include_nationwide: false,
              holiday_type: HolidayType.PUBLIC_HOLIDAY
            };
            const stateHolidays = await holidayService.getHolidays(stateFilter);
            safePush(stateHolidays);
          }
        }

        // 3. Schulferien laden
        if (calendarSettings.school_holiday_federal_states) {
          for (const stateCode of calendarSettings.school_holiday_federal_states) {
            const stateFilter = {
              ...effectiveFilter,
              federal_state: stateCode,
              include_nationwide: false,
              holiday_type: HolidayType.SCHOOL_VACATION
            };
            const schoolHolidays = await holidayService.getHolidays(stateFilter);
            safePush(schoolHolidays);
          }
        }

        // Nach Datum sortieren
        allHolidays.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        setHolidays(allHolidays);
        setCachedHolidays(yearToFetch, allHolidays);
      } else {
        // Fallback: Verwende ursprüngliche Logik oder lade alle Feiertage wenn keine spezifischen Filter
        if (!effectiveFilter.federal_state && effectiveFilter.include_nationwide === undefined) {
          // Lade alle Feiertage (bundesweit + alle Bundesländer)
          const allFilter = {
            ...effectiveFilter,
            include_nationwide: true,
          };
          const data = await holidayService.getHolidays(allFilter);
          setHolidays(data);
          setCachedHolidays(yearToFetch, data);
        } else {
          // Verwende spezifische Filter
          const data = await holidayService.getHolidays(effectiveFilter);
          setHolidays(data);
          setCachedHolidays(yearToFetch, data);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Laden der Feiertage');
    } finally {
      setLoading(false);
    }
  };

  // Lade verfügbare Jahre beim ersten Laden
  const fetchAvailableYears = useCallback(async () => {
    try {
      const response = await holidayService.getAvailableYears();
      setAvailableYears(response.years);
    } catch (err) {
      console.warn('Fehler beim Laden der verfügbaren Jahre:', err);
    }
  }, []);

  // Jahr-Wechsel-Funktion
  const setYear = useCallback((newYear: number) => {
    setCurrentYear(newYear);
    fetchHolidays(newYear);
  }, []);

  // Aktualisiere currentYear wenn year-Parameter sich ändert
  useEffect(() => {
    if (year !== undefined && year !== currentYear) {
      setCurrentYear(year);
    }
  }, [year, currentYear]);

  // Lade Feiertage wenn sich relevante Parameter ändern
  useEffect(() => {
    fetchHolidays(currentYear);
  }, [
    currentYear,
    additionalFilter?.month,
    additionalFilter?.federal_state,
    additionalFilter?.include_nationwide,
    calendarSettings?.selected_federal_states,
    calendarSettings?.show_nationwide_holidays
  ]);

  // Lade verfügbare Jahre beim ersten Mount
  useEffect(() => {
    fetchAvailableYears();
  }, [fetchAvailableYears]);

  const importCurrentYear = async () => {
    setLoading(true);
    setError(null);

    try {
      await holidayService.importCurrentYearHolidays();
      await fetchHolidays(); // Reload holidays after import
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Fehler beim Importieren der Feiertage';
      // Bei 422-Fehler (Duplikate) nicht als Fehler behandeln
      if (errorMessage.includes('422') || errorMessage.includes('already exists')) {
        console.log('Feiertage bereits vorhanden, Import übersprungen');
        await fetchHolidays(); // Trotzdem neu laden
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const importNextYear = async () => {
    setLoading(true);
    setError(null);

    try {
      await holidayService.importNextYearHolidays();
      await fetchHolidays(); // Reload holidays after import
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Fehler beim Importieren der Feiertage';
      // Bei 422-Fehler (Duplikate) nicht als Fehler behandeln
      if (errorMessage.includes('422') || errorMessage.includes('already exists')) {
        console.log('Feiertage bereits vorhanden, Import übersprungen');
        await fetchHolidays(); // Trotzdem neu laden
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const checkHoliday = async (date: string, federal_state?: string) => {
    try {
      return await holidayService.checkHoliday(date, federal_state);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Prüfen des Feiertags');
      return { is_holiday: false, message: 'Fehler beim Prüfen' };
    }
  };

  return {
    holidays,
    loading,
    error,
    currentYear,
    availableYears,
    setYear,
    fetchHolidays,
    importCurrentYear,
    importNextYear,
    checkHoliday,
    refetch: fetchHolidays
  };
};

// Rückwärtskompatibilitäts-Wrapper für die alte API
export const useHolidaysLegacy = (filter?: HolidayFilter) => {
  const year = filter?.year;
  const additionalFilter = filter ? { ...filter, year: undefined } : undefined;

  const result = useHolidays(year, additionalFilter as Omit<HolidayFilter, 'year'>);

  // Rückgabe im alten Format für Kompatibilität
  return {
    holidays: result.holidays,
    loading: result.loading,
    error: result.error,
    fetchHolidays: (newFilter?: HolidayFilter) => {
      const newYear = newFilter?.year;
      const newAdditionalFilter = newFilter ? { ...newFilter, year: undefined } : undefined;
      return result.fetchHolidays(newYear, newAdditionalFilter as Omit<HolidayFilter, 'year'>);
    },
    importCurrentYear: result.importCurrentYear,
    importNextYear: result.importNextYear,
    checkHoliday: result.checkHoliday,
    refetch: result.refetch
  };
};

export const useUpcomingHolidays = (federal_state?: string, days: number = 30) => {
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Lade Kalendereinstellungen
  const { data: calendarSettings } = useCalendarSettings();

  useEffect(() => {
    const fetchUpcomingHolidays = async () => {
      setLoading(true);
      setError(null);

      try {
        // Wenn kein spezifisches Bundesland angegeben ist, verwende Kalendereinstellungen
        if (!federal_state && calendarSettings && calendarSettings.selected_federal_states.length > 0) {
          // Verwende das erste ausgewählte Bundesland für upcoming holidays
          const primaryState = calendarSettings.selected_federal_states[0];
          const data = await holidayService.getUpcomingHolidays(primaryState, days);
          setHolidays(data);
        } else {
          const data = await holidayService.getUpcomingHolidays(federal_state, days);
          setHolidays(data);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Fehler beim Laden der kommenden Feiertage');
      } finally {
        setLoading(false);
      }
    };

    if (calendarSettings || federal_state) {
      fetchUpcomingHolidays();
    }
  }, [federal_state, days, calendarSettings?.selected_federal_states]);

  return { holidays, loading, error };
};
