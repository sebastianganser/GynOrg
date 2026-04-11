import { api } from './api';
import { SystemSettings, SystemSettingsUpdate } from '../types/systemSettings';

class SystemSettingsService {
    private basePath = '/system-settings';

    async getSystemSettings(): Promise<SystemSettings> {
        const response = await api.get<SystemSettings>(`${this.basePath}/`);
        return response.data;
    }

    async updateSystemSettings(data: SystemSettingsUpdate): Promise<SystemSettings> {
        const response = await api.put<SystemSettings>(`${this.basePath}/`, data);
        return response.data;
    }
}

export const systemSettingsService = new SystemSettingsService();
