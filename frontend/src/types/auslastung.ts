export interface Station {
  id: number;
  name: string;
  is_internal: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface StationCreate {
  name: string;
  is_internal?: boolean;
  is_active?: boolean;
}

export interface StationUpdate {
  name?: string;
  is_internal?: boolean;
  is_active?: boolean;
}

export interface StationCapacity {
  id: number;
  station_id: number;
  valid_from: string;
  valid_to?: string;
  plan_beds: number;
  created_at: string;
}

export interface StationCapacityCreate {
  station_id: number;
  valid_from: string;
  valid_to?: string;
  plan_beds: number;
}

export interface StationCapacityUpdate {
  valid_from?: string;
  valid_to?: string;
  plan_beds?: number;
}

export interface DailyEntry {
  id: number;
  station_id: number;
  date: string;
  occupied: number;
  admissions: number;
  discharges: number;
  blocked_beds: number;
  created_at: string;
  updated_at?: string;
}

export interface DailyEntryCreate {
  station_id: number;
  date: string;
  occupied: number;
  admissions?: number;
  discharges?: number;
  blocked_beds?: number;
}

export interface DailyFremd {
  date: string;
  count: number;
  created_at: string;
  updated_at?: string;
}

export interface DailyFremdCreate {
  date: string;
  count: number;
}
