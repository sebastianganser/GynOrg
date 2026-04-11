export interface AbsenceType {
    id: number;
    name: string;
    is_vacation: boolean;
    is_paid: boolean;
    requires_approval: boolean;
    max_days_per_request: number | null;
    active: boolean;
}

export interface AbsenceTypeCreate {
    name: string;
    is_vacation: boolean;
    is_paid?: boolean;
    requires_approval?: boolean;
    max_days_per_request?: number | null;
    active?: boolean;
}

export interface AbsenceTypeUpdate {
    name?: string;
    is_vacation?: boolean;
    is_paid?: boolean;
    requires_approval?: boolean;
    max_days_per_request?: number | null;
    active?: boolean;
}
