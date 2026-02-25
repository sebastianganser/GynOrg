import { useQuery } from '@tanstack/react-query';
import { employeeService } from '../services/employeeService';
import { EmployeeCalendarInfo } from '../types/employeeCalendar';

/**
 * Hook to fetch simplified employee list for calendar sidebar
 * @param activeOnly - Filter for active employees only (default: true)
 */
export function useEmployeesForCalendar(activeOnly: boolean = true) {
  return useQuery<EmployeeCalendarInfo[], Error>({
    queryKey: ['employees', 'calendar', activeOnly],
    queryFn: () => employeeService.getEmployeesForCalendar(activeOnly),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
}
