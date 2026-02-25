import { 
  VacationAllowance, 
  VacationAllowanceCreate, 
  VacationAllowanceUpdate,
  VacationAllowanceForm 
} from '../types/employee';
import { API_BASE_URL } from './config';
import { authService } from './authService';

export const vacationService = {
  // Get all vacation allowances for an employee
  async getVacationAllowances(employeeId: number): Promise<VacationAllowance[]> {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/vacation-allowances/`, {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch vacation allowances: ${response.statusText}`);
    }

    return response.json();
  },

  // Get vacation allowance for specific employee and year
  async getVacationAllowance(employeeId: number, year: number): Promise<VacationAllowance> {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/vacation-allowances/${year}`, {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch vacation allowance: ${response.statusText}`);
    }

    return response.json();
  },

  // Create new vacation allowance
  async createVacationAllowance(employeeId: number, data: VacationAllowanceForm): Promise<VacationAllowance> {
    const createData: VacationAllowanceCreate = {
      employee_id: employeeId,
      year: data.year,
      annual_allowance: data.annual_allowance,
      carryover_days: data.carryover_days || 0,
    };

    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/vacation-allowances/`, {
      method: 'POST',
      headers: authService.getAuthHeaders(),
      body: JSON.stringify(createData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to create vacation allowance: ${response.statusText}`);
    }

    return response.json();
  },

  // Update vacation allowance
  async updateVacationAllowance(id: number, data: Partial<VacationAllowanceForm>): Promise<VacationAllowance> {
    const updateData: VacationAllowanceUpdate = {};
    
    if (data.annual_allowance !== undefined) {
      updateData.annual_allowance = data.annual_allowance;
    }
    if (data.carryover_days !== undefined) {
      updateData.carryover_days = data.carryover_days;
    }

    const response = await fetch(`${API_BASE_URL}/vacation-allowances/${id}`, {
      method: 'PUT',
      headers: authService.getAuthHeaders(),
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to update vacation allowance: ${response.statusText}`);
    }

    return response.json();
  },

  // Delete vacation allowance
  async deleteVacationAllowance(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/vacation-allowances/${id}`, {
      method: 'DELETE',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete vacation allowance: ${response.statusText}`);
    }
  },

  // Get vacation allowances for current year across all employees
  async getCurrentYearVacationAllowances(): Promise<VacationAllowance[]> {
    const currentYear = new Date().getFullYear();
    const response = await fetch(`${API_BASE_URL}/vacation-allowances/?year=${currentYear}`, {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch current year vacation allowances: ${response.statusText}`);
    }

    return response.json();
  },

  // Get vacation statistics for an employee
  async getVacationStatistics(employeeId: number, year?: number): Promise<{
    total_allowance: number;
    used_days: number;
    remaining_days: number;
    carryover_days: number;
  }> {
    const url = new URL(`${API_BASE_URL}/employees/${employeeId}/vacation-statistics`);
    if (year) {
      url.searchParams.append('year', year.toString());
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch vacation statistics: ${response.statusText}`);
    }

    return response.json();
  },

  // Bulk create vacation allowances for multiple employees
  async bulkCreateVacationAllowances(
    employeeIds: number[], 
    year: number, 
    annualAllowance: number
  ): Promise<VacationAllowance[]> {
    const bulkData = employeeIds.map(employeeId => ({
      employee_id: employeeId,
      year,
      annual_allowance: annualAllowance,
      carryover_days: 0,
    }));

    const response = await fetch(`${API_BASE_URL}/vacation-allowances/bulk`, {
      method: 'POST',
      headers: authService.getAuthHeaders(),
      body: JSON.stringify({ vacation_allowances: bulkData }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to bulk create vacation allowances: ${response.statusText}`);
    }

    return response.json();
  },
};
