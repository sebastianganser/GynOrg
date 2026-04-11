import { useState, useEffect, useCallback } from 'react';
import { api } from '@/services/api';

// Types for Admin Sync API responses
interface SyncStatus {
  sync_id?: string;
  status: string;
  started_at?: string;
  progress?: {
    completed: number;
    failed: number;
    remaining: number;
    percentage: number;
  };
  estimated_completion?: string;
  current_state?: string;
  total_states: number;
  completed_states: number;
  failed_states: number;
}

interface SyncHistoryItem {
  sync_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_seconds: number;
  total_states: number;
  successful_states: string[];
  failed_states: string[];
  total_changes: number;
  total_conflicts: number;
  success_rate: number;
  triggered_by: string;
  error_summary?: string;
}

interface SyncStatistics {
  total_syncs: number;
  successful_syncs: number;
  failed_syncs: number;
  average_duration_seconds: number;
  last_successful_sync?: string;
  last_failed_sync?: string;
  total_holidays_synced: number;
  total_conflicts_resolved: number;
  uptime_percentage: number;
  next_scheduled_sync?: string;
}

interface SchedulerStatus {
  status: string;
  running: boolean;
  jobs_count: number;
  next_run?: string;
  last_run?: string;
  last_run_status?: string;
  uptime_seconds: number;
  configuration: Record<string, any>;
}

interface SystemHealth {
  overall_status: string;
  database_status: string;
  api_client_status: string;
  scheduler_status: string;
  last_successful_sync?: string;
  pending_conflicts: number;
  system_uptime_seconds: number;
  memory_usage_mb: number;
  disk_usage_percentage: number;
  checks_performed_at: string;
}

interface SyncTriggerRequest {
  federal_states?: string[];
  years?: number[];
  dry_run?: boolean;
  conflict_strategy?: string;
}

export function useAdminSync() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [syncHistory, setSyncHistory] = useState<SyncHistoryItem[]>([]);
  const [syncStatistics, setSyncStatistics] = useState<SyncStatistics | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch sync status
  const fetchSyncStatus = useCallback(async () => {
    try {
      const response = await api.get('/admin/sync/status');
      setSyncStatus(response.data);
    } catch (err) {
      console.error('Error fetching sync status:', err);
      setError(err as Error);
    }
  }, []);

  // Fetch sync history
  const fetchSyncHistory = useCallback(async () => {
    try {
      const response = await api.get('/admin/sync/history?page=1&page_size=20');
      setSyncHistory(response.data.items || []);
    } catch (err) {
      console.error('Error fetching sync history:', err);
      setError(err as Error);
    }
  }, []);

  // Fetch sync statistics
  const fetchSyncStatistics = useCallback(async () => {
    try {
      const response = await api.get('/admin/sync/statistics');
      setSyncStatistics(response.data);
    } catch (err) {
      console.error('Error fetching sync statistics:', err);
      setError(err as Error);
    }
  }, []);

  // Fetch scheduler status
  const fetchSchedulerStatus = useCallback(async () => {
    try {
      const response = await api.get('/admin/sync/scheduler/status');
      setSchedulerStatus(response.data);
    } catch (err) {
      console.error('Error fetching scheduler status:', err);
      setError(err as Error);
    }
  }, []);

  // Fetch system health
  const fetchSystemHealth = useCallback(async () => {
    try {
      const response = await api.get('/admin/sync/health');
      setSystemHealth(response.data);
    } catch (err) {
      console.error('Error fetching system health:', err);
      setError(err as Error);
    }
  }, []);

  // Refresh all data
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchSyncStatus(),
        fetchSyncHistory(),
        fetchSyncStatistics(),
        fetchSchedulerStatus(),
        fetchSystemHealth()
      ]);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [
    fetchSyncStatus,
    fetchSyncHistory,
    fetchSyncStatistics,
    fetchSchedulerStatus,
    fetchSystemHealth
  ]);

  // Trigger manual sync
  const triggerManualSync = useCallback(async (request: SyncTriggerRequest) => {
    try {
      setIsLoading(true);
      const response = await api.post('/admin/sync/trigger', request);
      
      // Refresh status after triggering
      setTimeout(() => {
        fetchSyncStatus();
      }, 1000);
      
      return response.data;
    } catch (err) {
      console.error('Error triggering manual sync:', err);
      setError(err as Error);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchSyncStatus]);

  // Pause scheduler
  const pauseScheduler = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/admin/sync/scheduler/pause');
      
      // Refresh scheduler status
      setTimeout(() => {
        fetchSchedulerStatus();
      }, 500);
      
      return response.data;
    } catch (err) {
      console.error('Error pausing scheduler:', err);
      setError(err as Error);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchSchedulerStatus]);

  // Resume scheduler
  const resumeScheduler = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/admin/sync/scheduler/resume');
      
      // Refresh scheduler status
      setTimeout(() => {
        fetchSchedulerStatus();
      }, 500);
      
      return response.data;
    } catch (err) {
      console.error('Error resuming scheduler:', err);
      setError(err as Error);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchSchedulerStatus]);

  // Initial data load
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  return {
    // Data
    syncStatus,
    syncHistory,
    syncStatistics,
    schedulerStatus,
    systemHealth,
    
    // State
    isLoading,
    error,
    
    // Actions
    triggerManualSync,
    pauseScheduler,
    resumeScheduler,
    refreshData,
    
    // Individual fetchers (for specific refreshes)
    fetchSyncStatus,
    fetchSyncHistory,
    fetchSyncStatistics,
    fetchSchedulerStatus,
    fetchSystemHealth
  };
}
