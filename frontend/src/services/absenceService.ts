import {
  Absence,
  AbsenceCreate,
  AbsenceUpdate,
  AbsenceType,
  AbsenceFilters,
  ConflictCheckResponse
} from '../types/absence';
import { API_BASE_URL } from './config';

class AbsenceService {
  private baseUrl = API_BASE_URL;

  // Helper method to get auth headers
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Helper method to handle API responses
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  // Absence CRUD operations
  async getAbsences(filters?: AbsenceFilters): Promise<Absence[]> {
    const params = new URLSearchParams();

    if (filters?.status) params.append('status', filters.status);
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.absence_type_id) params.append('absence_type_id', filters.absence_type_id.toString());

    const url = `${this.baseUrl}/absences/${params.toString() ? `?${params.toString()}` : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<Absence[]>(response);
  }

  async getAbsence(id: number): Promise<Absence> {
    const response = await fetch(`${this.baseUrl}/absences/${id}`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<Absence>(response);
  }

  async createAbsence(absenceData: AbsenceCreate): Promise<Absence> {
    const response = await fetch(`${this.baseUrl}/absences/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(absenceData)
    });

    return this.handleResponse<Absence>(response);
  }

  async updateAbsence(id: number, absenceData: AbsenceUpdate): Promise<Absence> {
    const response = await fetch(`${this.baseUrl}/absences/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(absenceData)
    });

    return this.handleResponse<Absence>(response);
  }

  async deleteAbsence(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/absences/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  // Absence status management
  async approveAbsence(id: number): Promise<Absence> {
    const response = await fetch(`${this.baseUrl}/absences/${id}/approve`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<Absence>(response);
  }

  async rejectAbsence(id: number): Promise<Absence> {
    const response = await fetch(`${this.baseUrl}/absences/${id}/reject`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<Absence>(response);
  }

  // Conflict detection
  async checkConflicts(
    employeeId: number,
    startDate: string,
    endDate: string,
    excludeAbsenceId?: number
  ): Promise<ConflictCheckResponse> {
    const params = new URLSearchParams({
      employee_id: employeeId.toString(),
      start_date: startDate,
      end_date: endDate
    });

    if (excludeAbsenceId) {
      params.append('exclude_absence_id', excludeAbsenceId.toString());
    }

    const response = await fetch(`${this.baseUrl}/absences/conflicts/check?${params.toString()}`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<ConflictCheckResponse>(response);
  }

  // Absence Types CRUD operations
  async getAbsenceTypes(activeOnly: boolean = true): Promise<AbsenceType[]> {
    const params = new URLSearchParams();
    if (activeOnly) params.append('active_only', 'true');

    const url = `${this.baseUrl}/absence-types/${params.toString() ? `?${params.toString()}` : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<AbsenceType[]>(response);
  }

  async getAbsenceType(id: number): Promise<AbsenceType> {
    const response = await fetch(`${this.baseUrl}/absence-types/${id}`, {
      method: 'GET',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse<AbsenceType>(response);
  }

  async createAbsenceType(absenceTypeData: Omit<AbsenceType, 'id'>): Promise<AbsenceType> {
    const response = await fetch(`${this.baseUrl}/absence-types/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(absenceTypeData)
    });

    return this.handleResponse<AbsenceType>(response);
  }

  async updateAbsenceType(id: number, absenceTypeData: Partial<AbsenceType>): Promise<AbsenceType> {
    const response = await fetch(`${this.baseUrl}/absence-types/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(absenceTypeData)
    });

    return this.handleResponse<AbsenceType>(response);
  }

  async deleteAbsenceType(id: number, hardDelete: boolean = false): Promise<void> {
    const endpoint = hardDelete ? `/absence-types/${id}/hard` : `/absence-types/${id}`;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  // Utility methods
  formatDateForAPI(date: Date): string {
    if (!date) return '';
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  parseAPIDate(dateString: string): Date {
    return new Date(dateString);
  }

  calculateDuration(startDate: Date, endDate: Date): number {
    const timeDiff = endDate.getTime() - startDate.getTime();
    return Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1; // +1 to include both start and end date
  }
}

export const absenceService = new AbsenceService();
