import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vacationService } from '../services/vacationService';
import { 
  VacationAllowanceForm 
} from '../types/employee';

// Query keys
export const vacationKeys = {
  all: ['vacationAllowances'] as const,
  lists: () => [...vacationKeys.all, 'list'] as const,
  byEmployee: (employeeId: number) => [...vacationKeys.all, 'employee', employeeId] as const,
  byEmployeeAndYear: (employeeId: number, year: number) => [...vacationKeys.all, 'employee', employeeId, 'year', year] as const,
  currentYear: () => [...vacationKeys.all, 'currentYear'] as const,
  statistics: (employeeId: number, year?: number) => [...vacationKeys.all, 'statistics', employeeId, { year }] as const,
};

// Hook to get vacation allowances for a specific employee
export const useEmployeeVacationAllowances = (employeeId: number) => {
  return useQuery({
    queryKey: vacationKeys.byEmployee(employeeId),
    queryFn: () => vacationService.getVacationAllowances(employeeId),
    enabled: !!employeeId,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook to get a specific vacation allowance by employee and year
export const useVacationAllowance = (employeeId: number, year: number) => {
  return useQuery({
    queryKey: vacationKeys.byEmployeeAndYear(employeeId, year),
    queryFn: () => vacationService.getVacationAllowance(employeeId, year),
    enabled: !!employeeId && !!year,
  });
};

// Hook to get current year vacation allowances for all employees
export const useCurrentYearVacationAllowances = () => {
  return useQuery({
    queryKey: vacationKeys.currentYear(),
    queryFn: () => vacationService.getCurrentYearVacationAllowances(),
    staleTime: 5 * 60 * 1000,
  });
};

// Hook to get vacation statistics for an employee
export const useVacationStatistics = (employeeId: number, year?: number) => {
  return useQuery({
    queryKey: vacationKeys.statistics(employeeId, year),
    queryFn: () => vacationService.getVacationStatistics(employeeId, year),
    enabled: !!employeeId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Hook to create a vacation allowance
export const useCreateVacationAllowance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ employeeId, data }: { employeeId: number; data: VacationAllowanceForm }) =>
      vacationService.createVacationAllowance(employeeId, data),
    onSuccess: (newAllowance) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ 
        queryKey: vacationKeys.byEmployee(newAllowance.employee_id) 
      });
      queryClient.invalidateQueries({ queryKey: vacationKeys.currentYear() });
      queryClient.invalidateQueries({ 
        queryKey: vacationKeys.statistics(newAllowance.employee_id) 
      });
    },
  });
};

// Hook to bulk create vacation allowances
export const useBulkCreateVacationAllowances = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ employeeIds, year, annualAllowance }: { 
      employeeIds: number[]; 
      year: number; 
      annualAllowance: number; 
    }) => vacationService.bulkCreateVacationAllowances(employeeIds, year, annualAllowance),
    onSuccess: () => {
      // Invalidate all vacation-related queries
      queryClient.invalidateQueries({ queryKey: vacationKeys.all });
    },
  });
};

// Hook to update a vacation allowance
export const useUpdateVacationAllowance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<VacationAllowanceForm> }) =>
      vacationService.updateVacationAllowance(id, data),
    onSuccess: (updatedAllowance) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ 
        queryKey: vacationKeys.byEmployee(updatedAllowance.employee_id) 
      });
      queryClient.invalidateQueries({ queryKey: vacationKeys.currentYear() });
      queryClient.invalidateQueries({ 
        queryKey: vacationKeys.statistics(updatedAllowance.employee_id) 
      });
    },
  });
};

// Hook to delete a vacation allowance
export const useDeleteVacationAllowance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => vacationService.deleteVacationAllowance(id),
    onSuccess: () => {
      // Invalidate all vacation-related queries
      queryClient.invalidateQueries({ queryKey: vacationKeys.all });
    },
  });
};
