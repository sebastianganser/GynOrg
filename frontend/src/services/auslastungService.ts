import { api } from './api';
import { 
  Station, StationCreate, StationUpdate, 
  StationCapacity, StationCapacityCreate, StationCapacityUpdate,
  DailyEntry, DailyEntryCreate, DailyFremd, DailyFremdCreate 
} from '../types/auslastung';

export const auslastungService = {
  // --- Stations ---
  getStations: async (activeOnly: boolean = true): Promise<Station[]> => {
    const response = await api.get(`/auslastung/stations?active_only=${activeOnly}`);
    return response.data;
  },

  createStation: async (data: StationCreate): Promise<Station> => {
    const response = await api.post('/auslastung/stations', data);
    return response.data;
  },

  updateStation: async (id: number, data: StationUpdate): Promise<Station> => {
    const response = await api.put(`/auslastung/stations/${id}`, data);
    return response.data;
  },

  deleteStation: async (id: number): Promise<void> => {
    await api.delete(`/auslastung/stations/${id}`);
  },

  // --- Capacities ---
  getStationCapacities: async (stationId: number): Promise<StationCapacity[]> => {
    const response = await api.get(`/auslastung/stations/${stationId}/capacities`);
    return response.data;
  },

  createStationCapacity: async (stationId: number, data: StationCapacityCreate): Promise<StationCapacity> => {
    const response = await api.post(`/auslastung/stations/${stationId}/capacities`, data);
    return response.data;
  },

  // --- Daily Entries ---
  getDailyEntries: async (startDate: string, endDate: string, stationId?: number): Promise<DailyEntry[]> => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    if (stationId) params.append('station_id', stationId.toString());
    const response = await api.get(`/auslastung/daily?${params.toString()}`);
    return response.data;
  },

  upsertDailyEntry: async (data: DailyEntryCreate): Promise<DailyEntry> => {
    const response = await api.post('/auslastung/daily', data);
    return response.data;
  },

  // --- Daily Fremd ---
  getDailyFremd: async (startDate: string, endDate: string): Promise<DailyFremd[]> => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/auslastung/fremd?${params.toString()}`);
    return response.data;
  },

  upsertDailyFremd: async (data: DailyFremdCreate): Promise<DailyFremd> => {
    const response = await api.post('/auslastung/fremd', data);
    return response.data;
  },

  // --- Trigger ---
  calculateMultipliers: async (): Promise<{ status: string; calculated_multipliers: number }> => {
    const response = await api.post('/auslastung/calculate-multipliers');
    return response.data;
  }
};
