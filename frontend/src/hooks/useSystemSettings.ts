import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { systemSettingsService } from '../services/systemSettingsService';
import { SystemSettings, SystemSettingsUpdate } from '../types/systemSettings';

export const useSystemSettings = () => {
    const queryClient = useQueryClient();
    const queryKey = ['systemSettings'];

    const settingsQuery = useQuery<SystemSettings, Error>({
        queryKey,
        queryFn: () => systemSettingsService.getSystemSettings(),
    });

    const updateSettingsMutation = useMutation<SystemSettings, Error, SystemSettingsUpdate>({
        mutationFn: (data: SystemSettingsUpdate) => systemSettingsService.updateSystemSettings(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey });
        },
    });

    return {
        settings: settingsQuery.data,
        isLoading: settingsQuery.isLoading,
        isError: settingsQuery.isError,
        error: settingsQuery.error,
        updateSettings: updateSettingsMutation.mutate,
        isUpdating: updateSettingsMutation.isPending,
    };
};
