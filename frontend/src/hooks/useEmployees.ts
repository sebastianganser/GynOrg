import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { employeeService } from '../services/employeeService';
import { utilityService } from '../services/utilityService';
import {
  EmployeeUpdate,
  EmployeeWithVacation,
  FederalState
} from '../types/employee';

// Query keys
export const employeeKeys = {
  all: ['employees'] as const,
  lists: () => [...employeeKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...employeeKeys.lists(), { filters }] as const,
  details: () => [...employeeKeys.all, 'detail'] as const,
  detail: (id: number) => [...employeeKeys.details(), id] as const,
  withVacation: () => [...employeeKeys.all, 'withVacation'] as const,
  withVacationDetail: (id: number) => [...employeeKeys.withVacation(), id] as const,
  vacationSummary: (employeeId: number, year: number) => [...employeeKeys.all, 'vacationSummary', employeeId, year] as const,
};

// Utility keys
export const utilityKeys = {
  all: ['utility'] as const,
  federalStates: () => [...utilityKeys.all, 'federalStates'] as const,
};

// Search and filter interfaces
export interface EmployeeSearchParams {
  search?: string;
  federal_state?: FederalState;
  active?: boolean;
  include_vacation?: boolean;
}

// Hook to get all employees (basic)
export const useEmployees = (includeVacation: boolean = false) => {
  return useQuery({
    queryKey: employeeKeys.list({ includeVacation }),
    queryFn: () => employeeService.getEmployees(includeVacation),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook to get employees with search and filters
export const useEmployeesWithSearch = (params: EmployeeSearchParams = {}) => {
  const { search, federal_state, active, include_vacation = false } = params;

  return useQuery({
    queryKey: employeeKeys.list({ search, federal_state, active, include_vacation }),
    queryFn: async () => {
      if (search) {
        return employeeService.searchEmployees(search, federal_state);
      }
      return employeeService.getEmployees(include_vacation);
    },
    staleTime: 5 * 60 * 1000,
    enabled: true,
  });
};

// Hook to get a single employee
export const useEmployee = (id: number, includeVacation: boolean = false) => {
  return useQuery({
    queryKey: includeVacation
      ? employeeKeys.withVacationDetail(id)
      : employeeKeys.detail(id),
    queryFn: () => employeeService.getEmployee(id, includeVacation),
    enabled: !!id,
  });
};

// Hook to get employee with vacation data
export const useEmployeeWithVacation = (id: number) => {
  return useQuery({
    queryKey: employeeKeys.withVacationDetail(id),
    queryFn: () => employeeService.getEmployee(id, true) as Promise<EmployeeWithVacation>,
    enabled: !!id,
  });
};

// Hook to get federal states
export const useFederalStates = () => {
  return useQuery({
    queryKey: utilityKeys.federalStates(),
    queryFn: utilityService.getFederalStates,
    staleTime: 60 * 60 * 1000, // 1 hour - rarely changes
  });
};

// Hook to create an employee
export const useCreateEmployee = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: employeeService.createEmployee,
    onSuccess: () => {
      // Invalidate and refetch employees list
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
    onError: (error) => {
      console.error('Error creating employee:', error);
    },
  });
};

export const useVacationSummary = (employeeId: number | undefined, year: number | undefined) => {
  return useQuery({
    queryKey: employeeKeys.vacationSummary(employeeId || 0, year || 0),
    queryFn: () => employeeService.getVacationSummary(employeeId!, year!),
    enabled: !!employeeId && !!year,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook to update an employee (full update)
export const useUpdateEmployee = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EmployeeUpdate }) =>
      employeeService.updateEmployee(id, data),
    onSuccess: (updatedEmployee) => {
      // Update the specific employee in cache
      queryClient.setQueryData(
        employeeKeys.detail(updatedEmployee.id),
        updatedEmployee
      );
      // Invalidate employees list to ensure consistency
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};

// Hook to partially update an employee (PATCH)
export const usePartialUpdateEmployee = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<EmployeeUpdate> }) =>
      employeeService.patchEmployee(id, data),
    onSuccess: (updatedEmployee) => {
      // Update the specific employee in cache
      queryClient.setQueryData(
        employeeKeys.detail(updatedEmployee.id),
        updatedEmployee
      );
      // Invalidate employees list to ensure consistency
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};

// Hook to toggle employee status
export const useToggleEmployeeStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => employeeService.toggleEmployeeStatus(id),
    onSuccess: (updatedEmployee) => {
      // Update the specific employee in cache
      queryClient.setQueryData(
        employeeKeys.detail(updatedEmployee.id),
        updatedEmployee
      );
      // Invalidate employees list to ensure consistency
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};

// Hook to delete an employee (soft delete)
export const useDeleteEmployee = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => employeeService.deleteEmployee(id),
    onSuccess: () => {
      // Invalidate employees list
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};

// Hook to hard delete an employee
export const useHardDeleteEmployee = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => employeeService.hardDeleteEmployee(id),
    onSuccess: () => {
      // Invalidate employees list
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};
