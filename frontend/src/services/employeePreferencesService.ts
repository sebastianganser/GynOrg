import { SchoolVacationType } from '../types/holiday';

export interface EmployeeSchoolHolidayPreferences {
    primary_federal_state: string;
    additional_federal_states?: string[];
    children_federal_states?: string[];
    relevant_vacation_types?: SchoolVacationType[];
    show_all_states?: boolean;
}

class EmployeePreferencesService {
    async getEmployeePreferences(employeeId: number): Promise<EmployeeSchoolHolidayPreferences | undefined> {
        return undefined;
    }
}

export const employeePreferencesService = new EmployeePreferencesService();
