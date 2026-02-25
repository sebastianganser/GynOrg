import { useQuery } from '@tanstack/react-query';
import { calendarSettingsService } from '../services/calendarSettingsService';

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
