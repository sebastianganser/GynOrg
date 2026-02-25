import { EmployeeSchoolHolidayPreferences } from '../services/employeePreferencesService';

export const useEmployeePreferences = (employeeId: number | string) => {
    return {
        data: null as EmployeeSchoolHolidayPreferences | null,
        isLoading: false,
        isError: false,
        error: null
    };
};

export const useEmployeePreferencesManager = () => {
    return {
        preferences: null,
        isLoading: false,
        isError: false,
        error: null,
        savePreferences: async () => { },
        deletePreferences: async () => { },
        isSaving: false,
        isDeleting: false,
        saveError: null,
        deleteError: null
    };
};
