export enum AbsenceStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  CANCELLED = "cancelled"
}

export interface AbsenceType {
  id: number;
  name: string;
  is_vacation: boolean;
  is_paid: boolean;
  requires_approval: boolean;
  max_days_per_request?: number;
  active: boolean;
}

export interface Absence {
  id: number;
  employee_id: number;
  absence_type_id: number;
  start_date: string; // ISO date string
  end_date: string; // ISO date string
  comment?: string;
  status: AbsenceStatus;
  half_day_time?: string | null;
  duration_days: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  absence_type?: AbsenceType;
}

export interface AbsenceCreate {
  employee_id: number;
  absence_type_id: number;
  start_date: string;
  end_date: string;
  comment?: string;
  status?: AbsenceStatus;
  half_day_time?: string | null;
}

export interface AbsenceUpdate {
  start_date?: string;
  end_date?: string;
  absence_type_id?: number;
  comment?: string;
  status?: AbsenceStatus;
  half_day_time?: string | null;
}

// Calendar-specific types
export interface CalendarAbsence {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: Absence;
  allDay: boolean;
  color?: string;
}

export interface AbsenceConflict {
  id: number;
  start_date: string;
  end_date: string;
  status: AbsenceStatus;
}

export interface ConflictCheckResponse {
  has_conflicts: boolean;
  conflicts: AbsenceConflict[];
}

// Form types
export interface AbsenceFormData {
  absence_type_id: number;
  start_date: Date;
  end_date: Date;
  comment?: string;
  save_as_draft?: boolean;
  half_day_time?: string | null;
}

// Filter types
export interface AbsenceFilters {
  status?: AbsenceStatus;
  start_date?: string;
  end_date?: string;
  absence_type_id?: number;
}
