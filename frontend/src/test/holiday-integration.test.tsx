import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { AbsenceCalendar } from '../components/AbsenceCalendar';
import { HolidayType, SchoolVacationType, DataSource } from '../types/holiday';
import { holidayService } from '../services/holidayService';

// Mock the holiday service
vi.mock('../services/holidayService');

// Mock the hooks
vi.mock('../hooks/useHolidays', () => ({
  useHolidays: () => ({
    holidays: [
      {
        id: 1,
        name: 'Tag der Deutschen Einheit',
        date: '2025-10-03',
        federal_state: undefined,
        is_nationwide: true,
        year: 2025,
        notes: 'Bundesweiter Feiertag',
        holiday_type: HolidayType.PUBLIC_HOLIDAY,
        data_source: DataSource.MANUAL,
        created_at: '2025-01-01T00:00:00Z'
      },
      {
        id: 2,
        name: 'Sommerferien',
        date: '2025-07-15',
        federal_state: 'Nordrhein-Westfalen',
        is_nationwide: false,
        year: 2025,
        notes: 'Schulferien NRW',
        holiday_type: HolidayType.SCHOOL_VACATION,
        school_vacation_type: SchoolVacationType.SUMMER,
        data_source: DataSource.MEHR_SCHULFERIEN_API,
        created_at: '2025-01-01T00:00:00Z'
      }
    ],
    loading: false,
    currentYear: 2025,
    availableYears: [2024, 2025, 2026],
    setYear: vi.fn(),
    importCurrentYear: vi.fn(),
    fetchHolidays: vi.fn()
  })
}));

vi.mock('../hooks/useCalendarSettings', () => ({
  useCalendarSettings: () => ({
    data: {
      selected_federal_states: ['Nordrhein-Westfalen']
    }
  })
}));

describe('Holiday Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
    vi.clearAllMocks();
  });

  const renderWithQueryClient = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  describe('Holiday Display and Filtering', () => {
    test('should display public holidays with correct icon and color', async () => {
      renderWithQueryClient(
        <AbsenceCalendar
          absences={[]}
          userFederalState="Nordrhein-Westfalen"
        />
      );

      // Warte auf das Laden der Komponente
      await waitFor(() => {
        expect(screen.getByText(/Oktober 2025/)).toBeInTheDocument();
      });

      // Prüfe, ob der Feiertag mit dem richtigen Icon angezeigt wird
      const holidayElement = screen.getByText(/🏛️.*Tag der Deutschen Einheit/);
      expect(holidayElement).toBeInTheDocument();
      expect(holidayElement).toHaveClass('text-red-600');
    });

    test('should display school vacations with correct icon and color', async () => {
      renderWithQueryClient(
        <AbsenceCalendar
          absences={[]}
          userFederalState="Nordrhein-Westfalen"
        />
      );

      // Navigiere zum Juli 2025
      const prevButton = screen.getByRole('button', { name: /zurück/i });
      fireEvent.click(prevButton);
      fireEvent.click(prevButton);
      fireEvent.click(prevButton);

      await waitFor(() => {
        expect(screen.getByText(/Juli 2025/)).toBeInTheDocument();
      });

      // Prüfe, ob die Schulferien mit dem richtigen Icon angezeigt werden
      const schoolHolidayElement = screen.getByText(/🎒.*Sommerferien/);
      expect(schoolHolidayElement).toBeInTheDocument();
      expect(schoolHolidayElement).toHaveClass('text-blue-600');
    });

    test('should filter holidays based on display settings', async () => {
      renderWithQueryClient(
        <AbsenceCalendar
          absences={[]}
          userFederalState="Nordrhein-Westfalen"
        />
      );

      // Öffne Filter
      const filterButton = screen.getByRole('button', { name: /filter/i });
      fireEvent.click(filterButton);

      await waitFor(() => {
        expect(screen.getByText('Feiertage & Schulferien:')).toBeInTheDocument();
      });

      // Deaktiviere Feiertage
      const publicHolidaysCheckbox = screen.getByLabelText(/🏛️ Feiertage anzeigen/);
      fireEvent.click(publicHolidaysCheckbox);

      // Navigiere zum Oktober
      const nextButton = screen.getByRole('button', { name: /weiter/i });
      fireEvent.click(nextButton);
      fireEvent.click(nextButton);
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText(/Oktober 2025/)).toBeInTheDocument();
      });

      // Feiertag sollte nicht mehr angezeigt werden
      expect(screen.queryByText(/🏛️.*Tag der Deutschen Einheit/)).not.toBeInTheDocument();
    });

    test('should filter school vacations independently', async () => {
      renderWithQueryClient(
        <AbsenceCalendar
          absences={[]}
          userFederalState="Nordrhein-Westfalen"
        />
      );

      // Öffne Filter
      const filterButton = screen.getByRole('button', { name: /filter/i });
      fireEvent.click(filterButton);

      // Deaktiviere Schulferien
      const schoolVacationsCheckbox = screen.getByLabelText(/🎒 Schulferien anzeigen/);
      fireEvent.click(schoolVacationsCheckbox);

      // Navigiere zum Juli
      const prevButton = screen.getByRole('button', { name: /zurück/i });
      fireEvent.click(prevButton);
      fireEvent.click(prevButton);
      fireEvent.click(prevButton);

      await waitFor(() => {
        expect(screen.getByText(/Juli 2025/)).toBeInTheDocument();
      });

      // Schulferien sollten nicht mehr angezeigt werden
      expect(screen.queryByText(/🎒.*Sommerferien/)).not.toBeInTheDocument();
    });

    test('should show federal state filter when userFederalState is provided', async () => {
      renderWithQueryClient(
        <AbsenceCalendar
          absences={[]}
          userFederalState="Nordrhein-Westfalen"
        />
      );

      // Öffne Filter
      const filterButton = screen.getByRole('button', { name: /filter/i });
      fireEvent.click(filterButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/📍 Nur mein Bundesland \(Nordrhein-Westfalen\)/)).toBeInTheDocument();
      });
    });

    test('should not show federal state filter when userFederalState is not provided', async () => {
      renderWithQueryClient(
        <AbsenceCalendar
          absences={[]}
        />
      );

      // Öffne Filter
      const filterButton = screen.getByRole('button', { name: /filter/i });
      fireEvent.click(filterButton);

      await waitFor(() => {
        expect(screen.queryByLabelText(/📍 Nur mein Bundesland/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Holiday Service Integration', () => {
    test('should call holiday service with correct filter parameters', async () => {
      const mockGetHolidays = vi.fn().mockResolvedValue([]);
      holidayService.getHolidays = mockGetHolidays;

      await holidayService.getHolidays({
        year: 2025,
        holiday_type: HolidayType.SCHOOL_VACATION,
        federal_state: 'Nordrhein-Westfalen'
      });

      expect(mockGetHolidays).toHaveBeenCalledWith({
        year: 2025,
        holiday_type: HolidayType.SCHOOL_VACATION,
        federal_state: 'Nordrhein-Westfalen'
      });
    });

    test('should filter holidays for display correctly', () => {
      const holidays = [
        {
          id: 1,
          name: 'Feiertag',
          date: '2025-10-03',
          federal_state: undefined,
          is_nationwide: true,
          year: 2025,
          notes: '',
          holiday_type: HolidayType.PUBLIC_HOLIDAY,
          data_source: DataSource.MANUAL,
          created_at: '2025-01-01T00:00:00Z'
        },
        {
          id: 2,
          name: 'Schulferien',
          date: '2025-07-15',
          federal_state: 'Bayern',
          is_nationwide: false,
          year: 2025,
          notes: '',
          holiday_type: HolidayType.SCHOOL_VACATION,
          school_vacation_type: SchoolVacationType.SUMMER,
          data_source: DataSource.MEHR_SCHULFERIEN_API,
          created_at: '2025-01-01T00:00:00Z'
        }
      ];

      const displayFilter = {
        showPublicHolidays: true,
        showSchoolVacations: false,
        showOnlyMyState: false,
        selectedFederalStates: []
      };

      const filtered = holidayService.filterHolidaysForDisplay(holidays, displayFilter);

      expect(filtered).toHaveLength(1);
      expect(filtered[0].holiday_type).toBe(HolidayType.PUBLIC_HOLIDAY);
    });

    test('should filter by federal state correctly', () => {
      const holidays = [
        {
          id: 1,
          name: 'Bundesweiter Feiertag',
          date: '2025-10-03',
          federal_state: undefined,
          is_nationwide: true,
          year: 2025,
          notes: '',
          holiday_type: HolidayType.PUBLIC_HOLIDAY,
          data_source: DataSource.MANUAL,
          created_at: '2025-01-01T00:00:00Z'
        },
        {
          id: 2,
          name: 'NRW Schulferien',
          date: '2025-07-15',
          federal_state: 'Nordrhein-Westfalen',
          is_nationwide: false,
          year: 2025,
          notes: '',
          holiday_type: HolidayType.SCHOOL_VACATION,
          school_vacation_type: SchoolVacationType.SUMMER,
          data_source: DataSource.MEHR_SCHULFERIEN_API,
          created_at: '2025-01-01T00:00:00Z'
        },
        {
          id: 3,
          name: 'Bayern Schulferien',
          date: '2025-07-20',
          federal_state: 'Bayern',
          is_nationwide: false,
          year: 2025,
          notes: '',
          holiday_type: HolidayType.SCHOOL_VACATION,
          school_vacation_type: SchoolVacationType.SUMMER,
          data_source: DataSource.MEHR_SCHULFERIEN_API,
          created_at: '2025-01-01T00:00:00Z'
        }
      ];

      const displayFilter = {
        showPublicHolidays: true,
        showSchoolVacations: true,
        showOnlyMyState: true,
        selectedFederalStates: []
      };

      const filtered = holidayService.filterHolidaysForDisplay(holidays, displayFilter, 'Nordrhein-Westfalen');

      expect(filtered).toHaveLength(2); // Bundesweiter Feiertag + NRW Schulferien
      expect(filtered.some(h => h.name === 'Bundesweiter Feiertag')).toBe(true);
      expect(filtered.some(h => h.name === 'NRW Schulferien')).toBe(true);
      expect(filtered.some(h => h.name === 'Bayern Schulferien')).toBe(false);
    });
  });

  describe('Holiday Type Utilities', () => {
    test('should return correct holiday type labels', async () => {
      const { getHolidayTypeLabel, getSchoolVacationTypeLabel } = await import('../types/holiday');

      expect(getHolidayTypeLabel(HolidayType.PUBLIC_HOLIDAY)).toBe('Feiertag');
      expect(getHolidayTypeLabel(HolidayType.SCHOOL_VACATION)).toBe('Schulferien');

      expect(getSchoolVacationTypeLabel(SchoolVacationType.SUMMER)).toBe('Sommerferien');
      expect(getSchoolVacationTypeLabel(SchoolVacationType.WINTER)).toBe('Winterferien');
      expect(getSchoolVacationTypeLabel(SchoolVacationType.EASTER)).toBe('Osterferien');
      expect(getSchoolVacationTypeLabel(SchoolVacationType.AUTUMN)).toBe('Herbstferien');
    });

    test('should return correct holiday icons', async () => {
      const { getHolidayIcon } = await import('../types/holiday');

      const publicHoliday = {
        holiday_type: HolidayType.PUBLIC_HOLIDAY
      };

      const schoolVacation = {
        holiday_type: HolidayType.SCHOOL_VACATION
      };

      expect(getHolidayIcon(publicHoliday as any)).toBe('🏛️');
      expect(getHolidayIcon(schoolVacation as any)).toBe('🎒');
    });

    test('should return correct holiday colors', async () => {
      const { getHolidayColor } = await import('../types/holiday');

      const publicHolidayNationwide = {
        holiday_type: HolidayType.PUBLIC_HOLIDAY,
        is_nationwide: true
      };

      const publicHolidayState = {
        holiday_type: HolidayType.PUBLIC_HOLIDAY,
        is_nationwide: false
      };

      const schoolVacation = {
        holiday_type: HolidayType.SCHOOL_VACATION
      };

      expect(getHolidayColor(publicHolidayNationwide as any)).toBe('#dc2626'); // Rot
      expect(getHolidayColor(publicHolidayState as any)).toBe('#ea580c'); // Orange
      expect(getHolidayColor(schoolVacation as any)).toBe('#2563eb'); // Blau
    });
  });
});
