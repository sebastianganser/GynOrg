import { api } from './api';
import { JobPosition, JobPositionCreate, JobPositionUpdate } from '../types/jobPosition';

export const jobPositionService = {
    getPositions: async (activeOnly: boolean = false): Promise<JobPosition[]> => {
        const params = new URLSearchParams();
        if (activeOnly) {
            params.append('active_only', 'true');
        }
        const response = await api.get(`/job-positions/?${params.toString()}`);
        return response.data;
    },

    createPosition: async (data: JobPositionCreate): Promise<JobPosition> => {
        const response = await api.post('/job-positions/', data);
        return response.data;
    },

    updatePosition: async (id: number, data: JobPositionUpdate): Promise<JobPosition> => {
        const response = await api.put(`/job-positions/${id}`, data);
        return response.data;
    },

    deletePosition: async (id: number): Promise<void> => {
        await api.delete(`/job-positions/${id}`);
    }
};
