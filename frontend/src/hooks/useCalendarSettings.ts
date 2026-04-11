import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { calendarSettingsService } from '../services/calendarSettingsService';
import { CalendarSettingsUpdate } from '../types/calendarSettings';

export const useCalendarSettings = () => {
  return useQuery({
    queryKey: ['calendar-settings'],
    queryFn: calendarSettingsService.getSettings,
    staleTime: 5 * 60 * 1000, // 5 Minuten
    gcTime: 10 * 60 * 1000, // 10 Minuten
  });
};

export const useFederalStates = () => {
  return useQuery({
    queryKey: ['federal-states'],
    queryFn: calendarSettingsService.getFederalStates,
    staleTime: 60 * 60 * 1000, // 1 Stunde (ändert sich selten)
    gcTime: 2 * 60 * 60 * 1000, // 2 Stunden
  });
};

export const useUpdateCalendarSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (settings: CalendarSettingsUpdate) => calendarSettingsService.updateSettings(settings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar-settings'] });
      // Since changing colors affects events, we might want to invalidate calendar events,
      // but reloading the window (like for employees atm) might be standard here.
      // We'll leave it simple for now.
    },
  });
};
