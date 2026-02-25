import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { EditEmployeeForm } from '../components/EditEmployeeForm';
import { Employee, FederalState } from '../types/employee';

// Mock the services
vi.mock('../services/employeeService', () => ({
  employeeService: {
    updateEmployee: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock('../hooks/useEmployeePreferences', () => ({
  useEmployeePreferencesManager: vi.fn(() => ({
    preferences: null,
    isLoading: false,
    isError: false,
    error: null,
    savePreferences: vi.fn(),
    deletePreferences: vi.fn(),
    isSaving: false,
    isDeleting: false,
    saveError: null,
    deleteError: null,
  })),
  useFederalStateOptions: vi.fn(() => ({
    federalStateOptions: [
      { value: 'NW', label: 'Nordrhein-Westfalen', code: 'NW' },
      { value: 'BY', label: 'Bayern', code: 'BY' },
    ],
    isLoading: false,
  })),
  useVacationTypeOptions: vi.fn(() => ({
    vacationTypeOptions: [
      { value: 'SUMMER', label: 'Sommerferien', description: 'Sommerferien' },
      { value: 'WINTER', label: 'Winterferien', description: 'Winterferien' },
    ],
    isLoading: false,
  })),
  useNotificationDaysOptions: vi.fn(() => ({
    notificationDaysOptions: [
      { value: 7, label: '7 Tage' },
      { value: 14, label: '14 Tage' },
    ],
  })),
}));

// Mock AvatarUpload component
vi.mock('../components/AvatarUpload', () => {
  return {
    default: function MockAvatarUpload({ employee }: { employee: Employee }) {
      return <div data-testid="avatar-upload">Avatar for {employee.first_name}</div>;
    }
  };
});

const mockEmployee: Employee = {
  id: 1,
  first_name: 'Max',
  last_name: 'Mustermann',
  email: 'max.mustermann@example.com',
  title: 'Dr.',
  position: 'Entwickler',
  vacation_allowance: 30,
  date_hired: '2023-01-01',
  birth_date: '1990-01-01',
  federal_state: FederalState.NW,
  active: true,
  avatar_url: undefined,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('Employee Tabs Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders both tabs correctly', () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Check if both tabs are present
    expect(screen.getByText('Persönliche Daten')).toBeInTheDocument();
    expect(screen.getByText('Schulferien-Präferenzen')).toBeInTheDocument();
  });

  it('shows personal data tab by default', () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Personal data tab should be active
    const personalTab = screen.getByRole('tab', { name: /persönliche daten/i });
    expect(personalTab).toHaveAttribute('aria-selected', 'true');

    // Personal data form should be visible
    expect(screen.getByDisplayValue('Max')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Mustermann')).toBeInTheDocument();
    expect(screen.getByDisplayValue('max.mustermann@example.com')).toBeInTheDocument();
  });

  it('switches to preferences tab when clicked', async () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Click on preferences tab
    const preferencesTab = screen.getByRole('tab', { name: /schulferien-präferenzen/i });
    fireEvent.click(preferencesTab);

    await waitFor(() => {
      expect(preferencesTab).toHaveAttribute('aria-selected', 'true');
    });

    // Preferences content should be visible
    expect(screen.getByText('🏠 Schulferien-Präferenzen')).toBeInTheDocument();
    expect(screen.getByText('Haupt-Bundesland')).toBeInTheDocument();
  });

  it('shows unsaved changes indicator', async () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Make a change in the personal data tab
    const firstNameInput = screen.getByDisplayValue('Max');
    fireEvent.change(firstNameInput, { target: { value: 'Maximilian' } });

    await waitFor(() => {
      // Check if unsaved changes indicator appears (● badge)
      const personalTab = screen.getByRole('tab', { name: /persönliche daten/i });
      expect(personalTab).toHaveTextContent('●');
    });
  });

  it('shows different action buttons for different tabs', async () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Personal tab should show "Änderungen speichern"
    expect(screen.getByText('Änderungen speichern')).toBeInTheDocument();

    // Switch to preferences tab
    const preferencesTab = screen.getByRole('tab', { name: /schulferien-präferenzen/i });
    fireEvent.click(preferencesTab);

    await waitFor(() => {
      // Preferences tab should show "Schließen" instead
      expect(screen.getByText('Schließen')).toBeInTheDocument();
      expect(screen.queryByText('Änderungen speichern')).not.toBeInTheDocument();
    });
  });

  it('handles tab switching with unsaved changes', async () => {
    // Mock window.confirm
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Make a change in personal data
    const firstNameInput = screen.getByDisplayValue('Max');
    fireEvent.change(firstNameInput, { target: { value: 'Maximilian' } });

    // Try to switch tabs
    const preferencesTab = screen.getByRole('tab', { name: /schulferien-präferenzen/i });
    fireEvent.click(preferencesTab);

    await waitFor(() => {
      // Should show confirmation dialog
      expect(confirmSpy).toHaveBeenCalledWith(
        'Sie haben ungespeicherte Änderungen. Möchten Sie wirklich den Tab wechseln?'
      );
    });

    confirmSpy.mockRestore();
  });

  it('renders avatar upload in personal tab', () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    expect(screen.getByTestId('avatar-upload')).toBeInTheDocument();
    expect(screen.getByText('Avatar for Max')).toBeInTheDocument();
  });

  it('handles form submission from personal tab', async () => {
    const onSuccess = vi.fn();
    
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={onSuccess}
        onCancel={vi.fn()}
      />
    );

    // Make a change
    const firstNameInput = screen.getByDisplayValue('Max');
    fireEvent.change(firstNameInput, { target: { value: 'Maximilian' } });

    // Submit form
    const submitButton = screen.getByText('Änderungen speichern');
    fireEvent.click(submitButton);

    // Form should be submitted (mocked to resolve immediately)
    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('shows correct tab icons', () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Both tabs should have icons (SVG elements)
    const tabs = screen.getAllByRole('tab');
    tabs.forEach(tab => {
      expect(tab.querySelector('svg')).toBeInTheDocument();
    });
  });

  it('maintains accessibility attributes', () => {
    renderWithQueryClient(
      <EditEmployeeForm
        employee={mockEmployee}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    // Check ARIA attributes
    const personalTab = screen.getByRole('tab', { name: /persönliche daten/i });
    expect(personalTab).toHaveAttribute('aria-selected', 'true');
    expect(personalTab).toHaveAttribute('tabIndex', '0');

    const preferencesTab = screen.getByRole('tab', { name: /schulferien-präferenzen/i });
    expect(preferencesTab).toHaveAttribute('aria-selected', 'false');
    expect(preferencesTab).toHaveAttribute('tabIndex', '-1');

    // Check for tabpanel
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });
});
