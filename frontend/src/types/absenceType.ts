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
    max_days_per_request: number | null;
    description: string | null;
    active: boolean;
}

export interface AbsenceTypeCreate {
    name: string;
    category: AbsenceTypeCategory;
    color?: string;
    is_paid?: boolean;
    requires_approval?: boolean;
    max_days_per_request?: number | null;
    description?: string;
    active?: boolean;
}

export interface AbsenceTypeUpdate {
    name?: string;
    category?: AbsenceTypeCategory;
    color?: string;
    is_paid?: boolean;
    requires_approval?: boolean;
    max_days_per_request?: number | null;
    description?: string;
    active?: boolean;
}
