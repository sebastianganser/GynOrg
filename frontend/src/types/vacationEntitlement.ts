export interface VacationEntitlement {
    id: number;
    employee_id: number;
    from_date: string;
    days: number;
    created_at: string;
    updated_at: string;
}

export interface VacationEntitlementCreate {
    employee_id: number;
    from_date: string;
    days: number;
}
