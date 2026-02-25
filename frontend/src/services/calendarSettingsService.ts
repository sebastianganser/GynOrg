import { CalendarSettings, CalendarSettingsUpdate, FederalStateOption } from '../types/calendarSettings';

const API_BASE_URL = '/api/v1';

class CalendarSettingsService {
  async getSettings(): Promise<CalendarSettings> {
    const response = await fetch(`${API_BASE_URL}/calendar-settings/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async updateSettings(settings: CalendarSettingsUpdate): Promise<CalendarSettings> {
    const response = await fetch(`${API_BASE_URL}/calendar-settings/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async resetSettings(): Promise<CalendarSettings> {
    const response = await fetch(`${API_BASE_URL}/calendar-settings/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getFederalStates(): Promise<FederalStateOption[]> {
    const response = await fetch(`${API_BASE_URL}/calendar-settings/federal-states`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.federal_states;
  }
}

export const calendarSettingsService = new CalendarSettingsService();
