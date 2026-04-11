import { VacationEntitlement, VacationEntitlementCreate } from '../types/vacationEntitlement';
import { API_BASE_URL } from './config';
import { authService } from './authService';

export const vacationEntitlementService = {
    async getEntitlements(employeeId: number): Promise<VacationEntitlement[]> {
        const url = new URL(`${API_BASE_URL}/vacation-entitlements/`, window.location.origin);
        url.searchParams.append('employee_id', employeeId.toString());

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: authService.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch entitlements: ${response.statusText}`);
        }

        return response.json();
    },

    async createEntitlement(data: VacationEntitlementCreate): Promise<VacationEntitlement> {
        const response = await fetch(`${API_BASE_URL}/vacation-entitlements/`, {
            method: 'POST',
            headers: authService.getAuthHeaders(),
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to create entitlement: ${response.statusText}`);
        }

        return response.json();
    },

    async deleteEntitlement(id: number): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/vacation-entitlements/${id}`, {
            method: 'DELETE',
            headers: authService.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error(`Failed to delete entitlement: ${response.statusText}`);
        }
    },
};
