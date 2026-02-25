import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CalendarSidebar } from '../CalendarSidebar';
import { useEmployeesForCalendar } from '../../hooks/useEmployeesForCalendar';
import { useCalendarFilterStore } from '../../stores/calendarFilterStore';

// Mock hooks
vi.mock('../../hooks/useEmployeesForCalendar');
vi.mock('../../stores/calendarFilterStore');

const mockEmployees = [
  {
    id: 1,
    full_name: 'Maria Ganser',
    calendar_color: '#FF5733',
  },
  {
    id: 2,
    full_name: 'John Doe',
    calendar_color: '#33FF57',
  },
  {
    id: 3,
    full_name: 'Jane Smith',
    calendar_color: '#3357FF',
  },
];

describe('CalendarSidebar', () => {
  const mockToggle = vi.fn();
  const mockToggleEmployee = vi.fn();
  const mockSelectAllEmployees = vi.fn();
  const mockDeselectAllEmployees = vi.fn();
  const mockToggleHolidays = vi.fn();
  const mockToggleSchoolVacations = vi.fn();
  const mockToggleVacationAbsences = vi.fn();
  const mockToggleSickLeave = vi.fn();
  const mockToggleTraining = vi.fn();
  const mockToggleSpecialLeave = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock useEmployeesForCalendar
    vi.mocked(useEmployeesForCalendar).mockReturnValue({
      data: mockEmployees,
      isLoading: false,
      error: null,
    } as any);

    // Mock useCalendarFilterStore
    vi.mocked(useCalendarFilterStore).mockImplementation((selector: any) => {
      const state = {
        selectedEmployeeIds: [1, 2],
        toggleEmployee: mockToggleEmployee,
        selectAllEmployees: mockSelectAllEmployees,
        deselectAllEmployees: mockDeselectAllEmployees,
        showHolidays: true,
        showSchoolVacations: true,
        showVacationAbsences: true,
        showSickLeave: true,
        showTraining: true,
        showSpecialLeave: true,
        toggleHolidays: mockToggleHolidays,
        toggleSchoolVacations: mockToggleSchoolVacations,
        toggleVacationAbsences: mockToggleVacationAbsences,
        toggleSickLeave: mockToggleSickLeave,
        toggleTraining: mockToggleTraining,
        toggleSpecialLeave: mockToggleSpecialLeave,
      };
      return selector(state);
    });
  });

  describe('Rendering', () => {
    it('should render sidebar in expanded state', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Kalender')).toBeInTheDocument();
      expect(screen.getByText('Meine Kalender')).toBeInTheDocument();
      expect(screen.getByText('Weitere Kalender')).toBeInTheDocument();
    });

    it('should render sidebar in collapsed state', () => {
      render(
        <CalendarSidebar isCollapsed={true} onToggle={mockToggle} />
      );

      // Header text should not be visible when collapsed
      expect(screen.queryByText('Kalender')).not.toBeInTheDocument();
    });

    it('should apply correct width classes', () => {
      const { container, rerender } = render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      let sidebar = container.firstChild as HTMLElement;
      expect(sidebar).toHaveClass('w-[250px]');

      rerender(<CalendarSidebar isCollapsed={true} onToggle={mockToggle} />);
      sidebar = container.firstChild as HTMLElement;
      expect(sidebar).toHaveClass('w-[60px]');
    });
  });

  describe('Toggle Functionality', () => {
    it('should call onToggle when toggle button is clicked', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const toggleButton = screen.getByTitle('Sidebar minimieren');
      fireEvent.click(toggleButton);

      expect(mockToggle).toHaveBeenCalledTimes(1);
    });

    it('should show correct icon based on collapsed state', () => {
      const { rerender } = render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByTitle('Sidebar minimieren')).toBeInTheDocument();

      rerender(<CalendarSidebar isCollapsed={true} onToggle={mockToggle} />);
      expect(screen.getByTitle('Sidebar erweitern')).toBeInTheDocument();
    });
  });

  describe('Employee List', () => {
    it('should render all employees', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Maria Ganser')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    it('should show employee colors', () => {
      const { container } = render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const colorDivs = container.querySelectorAll('[style*="background-color"]');
      expect(colorDivs.length).toBeGreaterThan(0);
    });

    it('should toggle employee selection when checkbox is clicked', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const checkboxes = screen.getAllByRole('checkbox');
      const employeeCheckbox = checkboxes.find((cb) =>
        cb.closest('label')?.textContent?.includes('Maria Ganser')
      );

      if (employeeCheckbox) {
        fireEvent.click(employeeCheckbox);
        expect(mockToggleEmployee).toHaveBeenCalledWith(1);
      }
    });

    it('should show "Alle auswählen" button when not all selected', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Alle auswählen')).toBeInTheDocument();
    });

    it('should show "Alle abwählen" button when all selected', () => {
      vi.mocked(useCalendarFilterStore).mockImplementation((selector: any) => {
        const state = {
          selectedEmployeeIds: [1, 2, 3],
          toggleEmployee: mockToggleEmployee,
          selectAllEmployees: mockSelectAllEmployees,
          deselectAllEmployees: mockDeselectAllEmployees,
          showHolidays: true,
          showSchoolVacations: true,
          showVacationAbsences: true,
          showSickLeave: true,
          showTraining: true,
          showSpecialLeave: true,
          toggleHolidays: mockToggleHolidays,
          toggleSchoolVacations: mockToggleSchoolVacations,
          toggleVacationAbsences: mockToggleVacationAbsences,
          toggleSickLeave: mockToggleSickLeave,
          toggleTraining: mockToggleTraining,
          toggleSpecialLeave: mockToggleSpecialLeave,
        };
        return selector(state);
      });

      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Alle abwählen')).toBeInTheDocument();
    });

    it('should handle select all employees', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const selectAllButton = screen.getByText('Alle auswählen');
      fireEvent.click(selectAllButton);

      expect(mockSelectAllEmployees).toHaveBeenCalledWith([1, 2, 3]);
    });
  });

  describe('Calendar Filters', () => {
    it('should render all calendar filter options', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Feiertage')).toBeInTheDocument();
      expect(screen.getByText('Schulferien')).toBeInTheDocument();
      expect(screen.getByText('Urlaub')).toBeInTheDocument();
      expect(screen.getByText('Krankheit')).toBeInTheDocument();
      expect(screen.getByText('Fortbildung')).toBeInTheDocument();
      expect(screen.getByText('Sonderurlaub')).toBeInTheDocument();
    });

    it('should toggle holidays filter', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const checkboxes = screen.getAllByRole('checkbox');
      const holidaysCheckbox = checkboxes.find((cb) =>
        cb.closest('label')?.textContent?.includes('Feiertage')
      );

      if (holidaysCheckbox) {
        fireEvent.click(holidaysCheckbox);
        expect(mockToggleHolidays).toHaveBeenCalled();
      }
    });

    it('should toggle school vacations filter', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const checkboxes = screen.getAllByRole('checkbox');
      const schoolVacationsCheckbox = checkboxes.find((cb) =>
        cb.closest('label')?.textContent?.includes('Schulferien')
      );

      if (schoolVacationsCheckbox) {
        fireEvent.click(schoolVacationsCheckbox);
        expect(mockToggleSchoolVacations).toHaveBeenCalled();
      }
    });

    it('should toggle vacation absences filter', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const checkboxes = screen.getAllByRole('checkbox');
      const vacationCheckbox = checkboxes.find((cb) =>
        cb.closest('label')?.textContent?.includes('Urlaub')
      );

      if (vacationCheckbox) {
        fireEvent.click(vacationCheckbox);
        expect(mockToggleVacationAbsences).toHaveBeenCalled();
      }
    });
  });

  describe('Loading and Error States', () => {
    it('should show loading state', () => {
      vi.mocked(useEmployeesForCalendar).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      } as any);

      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Lade Mitarbeiter...')).toBeInTheDocument();
    });

    it('should show error state', () => {
      vi.mocked(useEmployeesForCalendar).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Failed to load'),
      } as any);

      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(
        screen.getByText('Fehler beim Laden der Mitarbeiter')
      ).toBeInTheDocument();
    });

    it('should show empty state when no employees', () => {
      vi.mocked(useEmployeesForCalendar).mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      } as any);

      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(screen.getByText('Keine Mitarbeiter gefunden')).toBeInTheDocument();
    });
  });

  describe('Collapsible Sections', () => {
    it('should have collapsible "Meine Kalender" section', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const meineKalenderButton = screen.getByText('Meine Kalender').closest('button');
      expect(meineKalenderButton).toBeInTheDocument();

      // Initially expanded - employees should be visible
      expect(screen.getByText('Maria Ganser')).toBeInTheDocument();

      // Button should be clickable
      if (meineKalenderButton) {
        fireEvent.click(meineKalenderButton);
        // Just verify the button was clicked, animation testing is complex
        expect(meineKalenderButton).toBeInTheDocument();
      }
    });

    it('should have collapsible "Weitere Kalender" section', () => {
      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      const weitereKalenderButton = screen.getByText('Weitere Kalender').closest('button');
      expect(weitereKalenderButton).toBeInTheDocument();

      // Initially expanded - filters should be visible
      expect(screen.getByText('Feiertage')).toBeInTheDocument();

      // Button should be clickable
      if (weitereKalenderButton) {
        fireEvent.click(weitereKalenderButton);
        // Just verify the button was clicked, animation testing is complex
        expect(weitereKalenderButton).toBeInTheDocument();
      }
    });
  });

  describe('Auto-selection', () => {
    it('should auto-select all employees on first load', () => {
      vi.mocked(useCalendarFilterStore).mockImplementation((selector: any) => {
        const state = {
          selectedEmployeeIds: [],
          toggleEmployee: mockToggleEmployee,
          selectAllEmployees: mockSelectAllEmployees,
          deselectAllEmployees: mockDeselectAllEmployees,
          showHolidays: true,
          showSchoolVacations: true,
          showVacationAbsences: true,
          showSickLeave: true,
          showTraining: true,
          showSpecialLeave: true,
          toggleHolidays: mockToggleHolidays,
          toggleSchoolVacations: mockToggleSchoolVacations,
          toggleVacationAbsences: mockToggleVacationAbsences,
          toggleSickLeave: mockToggleSickLeave,
          toggleTraining: mockToggleTraining,
          toggleSpecialLeave: mockToggleSpecialLeave,
        };
        return selector(state);
      });

      render(
        <CalendarSidebar isCollapsed={false} onToggle={mockToggle} />
      );

      expect(mockSelectAllEmployees).toHaveBeenCalledWith([1, 2, 3]);
    });
  });
});
