import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Absence,
  AbsenceCreate,
  AbsenceUpdate,
  AbsenceType,
  AbsenceFilters
} from '../types/absence';
import { absenceService } from '../services/absenceService';

// Query keys
export const absenceKeys = {
  all: ['absences'] as const,
  lists: () => [...absenceKeys.all, 'list'] as const,
  list: (filters?: AbsenceFilters) => [...absenceKeys.lists(), filters] as const,
  details: () => [...absenceKeys.all, 'detail'] as const,
  detail: (id: number) => [...absenceKeys.details(), id] as const,
  types: ['absence-types'] as const,
  typesList: () => [...absenceKeys.types, 'list'] as const,
  conflicts: ['absence-conflicts'] as const,
  conflictCheck: (employeeId: number, startDate: string, endDate: string, excludeId?: number) =>
    [...absenceKeys.conflicts, 'check', employeeId, startDate, endDate, excludeId] as const,
};

// Absences hooks
export const useAbsences = (filters?: AbsenceFilters) => {
  return useQuery({
    queryKey: absenceKeys.list(filters),
    queryFn: () => absenceService.getAbsences(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useAbsence = (id: number) => {
  return useQuery({
    queryKey: absenceKeys.detail(id),
    queryFn: () => absenceService.getAbsence(id),
    enabled: !!id,
  });
};

export const useCreateAbsence = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (absenceData: AbsenceCreate) => absenceService.createAbsence(absenceData),
    onSuccess: () => {
      // Invalidate and refetch absences list
      queryClient.invalidateQueries({ queryKey: absenceKeys.lists() });
    },
  });
};

export const useUpdateAbsence = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AbsenceUpdate }) =>
      absenceService.updateAbsence(id, data),
    onSuccess: (updatedAbsence) => {
      // Update the specific absence in cache
      queryClient.setQueryData(
        absenceKeys.detail(updatedAbsence.id),
        updatedAbsence
      );
      // Invalidate lists to ensure consistency
      queryClient.invalidateQueries({ queryKey: absenceKeys.lists() });
    },
  });
};

export const useDeleteAbsence = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => absenceService.deleteAbsence(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: absenceKeys.detail(deletedId) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: absenceKeys.lists() });
    },
  });
};

export const useApproveAbsence = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => absenceService.approveAbsence(id),
    onSuccess: (updatedAbsence) => {
      queryClient.setQueryData(
        absenceKeys.detail(updatedAbsence.id),
        updatedAbsence
      );
      queryClient.invalidateQueries({ queryKey: absenceKeys.lists() });
    },
  });
};

export const useRejectAbsence = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => absenceService.rejectAbsence(id),
    onSuccess: (updatedAbsence) => {
      queryClient.setQueryData(
        absenceKeys.detail(updatedAbsence.id),
        updatedAbsence
      );
      queryClient.invalidateQueries({ queryKey: absenceKeys.lists() });
    },
  });
};

// Absence Types hooks
export const useAbsenceTypes = (activeOnly: boolean = true) => {
  return useQuery({
    queryKey: [...absenceKeys.typesList(), activeOnly],
    queryFn: () => absenceService.getAbsenceTypes(activeOnly),
    staleTime: 10 * 60 * 1000, // 10 minutes - absence types don't change often
  });
};

export const useAbsenceType = (id: number) => {
  return useQuery({
    queryKey: [...absenceKeys.types, 'detail', id],
    queryFn: () => absenceService.getAbsenceType(id),
    enabled: !!id,
  });
};

export const useCreateAbsenceType = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (absenceTypeData: Omit<AbsenceType, 'id'>) =>
      absenceService.createAbsenceType(absenceTypeData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: absenceKeys.typesList() });
    },
  });
};

export const useUpdateAbsenceType = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<AbsenceType> }) =>
      absenceService.updateAbsenceType(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: absenceKeys.typesList() });
    },
  });
};

export const useDeleteAbsenceType = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, hardDelete }: { id: number; hardDelete?: boolean }) =>
      absenceService.deleteAbsenceType(id, hardDelete),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: absenceKeys.typesList() });
    },
  });
};

// Conflict checking hook
export const useCheckConflicts = () => {
  return useMutation({
    mutationFn: ({
      employeeId,
      startDate,
      endDate,
      excludeAbsenceId
    }: {
      employeeId: number;
      startDate: string;
      endDate: string;
      excludeAbsenceId?: number;
    }) => absenceService.checkConflicts(employeeId, startDate, endDate, excludeAbsenceId),
  });
};

// Utility hook for optimistic updates
export const useOptimisticAbsenceUpdate = () => {
  const queryClient = useQueryClient();

  const updateAbsenceOptimistically = (id: number, updates: Partial<Absence>) => {
    queryClient.setQueryData(
      absenceKeys.detail(id),
      (oldData: Absence | undefined) => {
        if (!oldData) return oldData;
        return { ...oldData, ...updates };
      }
    );

    // Also update in lists
    queryClient.setQueriesData(
      { queryKey: absenceKeys.lists() },
      (oldData: Absence[] | undefined) => {
        if (!oldData) return oldData;
        return oldData.map(absence =>
          absence.id === id ? { ...absence, ...updates } : absence
        );
      }
    );
  };

  return { updateAbsenceOptimistically };
};

// Combined hook for absence management
export const useAbsenceManagement = (filters?: AbsenceFilters) => {
  const absencesQuery = useAbsences(filters);
  const absenceTypesQuery = useAbsenceTypes();
  const createMutation = useCreateAbsence();
  const updateMutation = useUpdateAbsence();
  const deleteMutation = useDeleteAbsence();
  const approveMutation = useApproveAbsence();
  const checkConflictsMutation = useCheckConflicts();

  return {
    // Data
    absences: absencesQuery.data || [],
    absenceTypes: absenceTypesQuery.data || [],

    // Loading states
    isLoading: absencesQuery.isLoading || absenceTypesQuery.isLoading,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isApproving: approveMutation.isPending,
    isCheckingConflicts: checkConflictsMutation.isPending,

    // Error states
    error: absencesQuery.error || absenceTypesQuery.error,
    createError: createMutation.error,
    updateError: updateMutation.error,
    deleteError: deleteMutation.error,
    approveError: approveMutation.error,
    conflictError: checkConflictsMutation.error,

    // Mutations
    createAbsence: createMutation.mutate,
    updateAbsence: updateMutation.mutate,
    deleteAbsence: deleteMutation.mutate,
    approveAbsence: approveMutation.mutate,
    checkConflicts: checkConflictsMutation.mutate,

    // Conflict check result
    conflictResult: checkConflictsMutation.data,

    // Refetch functions
    refetchAbsences: absencesQuery.refetch,
    refetchAbsenceTypes: absenceTypesQuery.refetch,
  };
};
