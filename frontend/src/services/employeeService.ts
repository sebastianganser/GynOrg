import {
  Employee,
  EmployeeWithVacation,
  EmployeeCreateForm,
  EmployeeUpdateForm,
  FederalState
} from '../types/employee';
import { EmployeeCalendarInfo } from '../types/employeeCalendar';
import { API_BASE_URL } from './config';
import { authService } from './authService';

export const employeeService = {
  // Get all employees with optional vacation data
  async getEmployees(includeVacation: boolean = false): Promise<Employee[]> {
    const url = new URL(`${API_BASE_URL}/employees/`, window.location.origin);
    if (includeVacation) {
      url.searchParams.append('include_vacation', 'true');
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch employees: ${response.statusText}`);
    }

    return response.json();
  },

  // Get employee by ID with optional vacation data
  async getEmployee(id: number, includeVacation: boolean = false): Promise<Employee | EmployeeWithVacation> {
    const url = new URL(`${API_BASE_URL}/employees/${id}`, window.location.origin);
    if (includeVacation) {
      url.searchParams.append('include_vacation', 'true');
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch employee: ${response.statusText}`);
    }

    return response.json();
  },

  // Create new employee
  async createEmployee(employeeData: EmployeeCreateForm): Promise<Employee> {
    const response = await fetch(`${API_BASE_URL}/employees/`, {
      method: 'POST',
      headers: authService.getAuthHeaders(),
      body: JSON.stringify(employeeData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to create employee: ${response.statusText}`);
    }

    return response.json();
  },

  // Update employee (full update)
  async updateEmployee(id: number, employeeData: EmployeeUpdateForm): Promise<Employee> {
    const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
      method: 'PUT',
      headers: authService.getAuthHeaders(),
      body: JSON.stringify(employeeData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to update employee: ${response.statusText}`);
    }

    return response.json();
  },

  // Partial update employee
  async patchEmployee(id: number, employeeData: Partial<EmployeeUpdateForm>): Promise<Employee> {
    const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
      method: 'PATCH',
      headers: authService.getAuthHeaders(),
      body: JSON.stringify(employeeData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to update employee: ${response.statusText}`);
    }

    return response.json();
  },

  // Search employees
  async searchEmployees(query: string, federalState?: FederalState): Promise<Employee[]> {
    const url = new URL(`${API_BASE_URL}/employees/search`, window.location.origin);
    url.searchParams.append('q', query);
    if (federalState) {
      url.searchParams.append('federal_state', federalState);
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to search employees: ${response.statusText}`);
    }

    return response.json();
  },

  // Soft delete employee (set active = false)
  async deleteEmployee(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
      method: 'DELETE',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete employee: ${response.statusText}`);
    }
  },

  // Hard delete employee (permanent removal)
  async hardDeleteEmployee(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/employees/${id}/hard`, {
      method: 'DELETE',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to hard delete employee: ${response.statusText}`);
    }
  },

  // Toggle employee active status
  async toggleEmployeeStatus(id: number): Promise<Employee> {
    const response = await fetch(`${API_BASE_URL}/employees/${id}/toggle-status`, {
      method: 'PATCH',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle employee status: ${response.statusText}`);
    }

    return response.json();
  },

  // Get simplified employee list for calendar sidebar
  async getEmployeesForCalendar(activeOnly: boolean = true): Promise<EmployeeCalendarInfo[]> {
    const url = new URL(`${API_BASE_URL}/employees/calendar-list`, window.location.origin);
    url.searchParams.append('active_only', activeOnly.toString());

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch employees for calendar: ${response.statusText}`);
    }

    return response.json();
  },
};
