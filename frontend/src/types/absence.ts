export enum AbsenceStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  CANCELLED = "cancelled",
  DRAFT = "draft",
  CONFIRMED = "confirmed"
}

export enum AbsenceTypeCategory {
  VACATION = "vacation",
  SICK_LEAVE = "sick_leave",
  TRAINING = "training",
  SPECIAL_LEAVE = "special_leave",
  UNPAID_LEAVE = "unpaid_leave",
  OTHER = "other"
}

export interface AbsenceType {
  id: number;
  name: string;
  category: AbsenceTypeCategory;
  color: string;
  is_paid: boolean;
  requires_approval: boolean;
  max_days_per_request?: number;
  description?: string;
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
}

export interface AbsenceUpdate {
  start_date?: string;
  end_date?: string;
  absence_type_id?: number;
  comment?: string;
  status?: AbsenceStatus;
}

// Calendar-specific types
export interface CalendarAbsence {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: Absence;
  allDay: boolean;
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
}

// Filter types
export interface AbsenceFilters {
  status?: AbsenceStatus;
  start_date?: string;
  end_date?: string;
  absence_type_id?: number;
}
