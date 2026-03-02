import { api } from './api';
import { AbsenceType, AbsenceTypeCreate, AbsenceTypeUpdate } from '../types/absenceType';

export const absenceTypeService = {
    getAbsenceTypes: async (activeOnly: boolean = false): Promise<AbsenceType[]> => {
        const params = new URLSearchParams();
        if (activeOnly) {
            params.append('active_only', 'true');
        }
        const response = await api.get(`/absence-types/?${params.toString()}`);
        return response.data;
    },

    getAbsenceType: async (id: number): Promise<AbsenceType> => {
        const response = await api.get(`/absence-types/${id}`);
        return response.data;
    },

    createAbsenceType: async (data: AbsenceTypeCreate): Promise<AbsenceType> => {
        const response = await api.post('/absence-types/', data);
        return response.data;
    },

    updateAbsenceType: async (id: number, data: AbsenceTypeUpdate): Promise<AbsenceType> => {
        const response = await api.put(`/absence-types/${id}`, data);
        return response.data;
    },

    // Soft delete
    deleteAbsenceType: async (id: number): Promise<void> => {
        await api.delete(`/absence-types/${id}`);
    },

    // Hard delete
    hardDeleteAbsenceType: async (id: number): Promise<void> => {
        await api.delete(`/absence-types/${id}/hard`);
    }
};
