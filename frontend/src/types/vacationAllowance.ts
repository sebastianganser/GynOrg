export interface VacationAllowance {
    id: number;
    employee_id: number;
    year: number;
    annual_allowance: number;
    carryover_days: number;
    total_allowance: number;
    created_at: string;
    updated_at: string;
}

export interface VacationAllowanceCreate {
    employee_id: number;
    year: number;
    annual_allowance: number;
    carryover_days: number;
}

export interface VacationAllowanceUpdate {
    annual_allowance?: number;
    carryover_days?: number;
}
