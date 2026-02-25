import { VacationAllowance, VacationAllowanceCreate, VacationAllowanceUpdate } from '../types/vacationAllowance';
import { API_BASE_URL } from './config';
import { authService } from './authService';

export const vacationAllowanceService = {
    async getAllowances(employeeId: number): Promise<VacationAllowance[]> {
        const url = new URL(`${API_BASE_URL}/vacation-allowances/`, window.location.origin);
        url.searchParams.append('employee_id', employeeId.toString());

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: authService.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch allowances: ${response.statusText}`);
        }

        return response.json();
    },

    async createAllowance(data: VacationAllowanceCreate): Promise<VacationAllowance> {
        const response = await fetch(`${API_BASE_URL}/vacation-allowances/`, {
            method: 'POST',
            headers: authService.getAuthHeaders(),
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to create allowance: ${response.statusText}`);
        }

        return response.json();
    },

    async updateAllowance(id: number, data: VacationAllowanceUpdate): Promise<VacationAllowance> {
        const response = await fetch(`${API_BASE_URL}/vacation-allowances/${id}`, {
            method: 'PUT',
            headers: authService.getAuthHeaders(),
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to update allowance: ${response.statusText}`);
        }

        return response.json();
    },

    async deleteAllowance(id: number): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/vacation-allowances/${id}`, {
            method: 'DELETE',
            headers: authService.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error(`Failed to delete allowance: ${response.statusText}`);
        }
    },
};
