import { useState } from 'react';

// Mock data for demonstration
const mockSyncStatus = {
  sync_id: 'sync_20250921_173000',
  status: 'COMPLETED',
  started_at: '2025-09-21T15:30:00Z',
  total_states: 16,
  completed_states: 16,
  failed_states: 0
};

const mockSyncHistory = [
  {
    sync_id: 'sync_20250921_173000',
    status: 'COMPLETED',
    started_at: '2025-09-21T15:30:00Z',
    completed_at: '2025-09-21T15:35:00Z',
    duration_seconds: 300,
    total_states: 16,
    successful_states: ['BW', 'BY', 'BE', 'BB', 'HB', 'HH', 'HE', 'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH'],
    failed_states: [],
    total_changes: 45,
    total_conflicts: 0,
    success_rate: 1.0,
    triggered_by: 'scheduler'
  }
];

const mockSchedulerStatus = {
  status: 'RUNNING',
  running: true,
  jobs_count: 1,
  next_run: '2025-10-01T02:00:00Z',
  last_run: '2025-09-21T15:30:00Z',
  uptime_seconds: 86400
};

const mockSystemHealth = {
  overall_status: 'healthy',
  database_status: 'healthy',
  api_client_status: 'healthy',
  scheduler_status: 'healthy',
  pending_conflicts: 0,
  system_uptime_seconds: 86400,
  memory_usage_mb: 256,
  disk_usage_percentage: 45
};

export default function AdminSync() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const refreshData = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setLastRefresh(new Date());
    }, 1000);
  };

  const triggerManualSync = () => {
    alert('Manueller Sync würde hier gestartet werden');
  };

  const pauseScheduler = () => {
    alert('Scheduler würde pausiert werden');
  };

  const resumeScheduler = () => {
    alert('Scheduler würde fortgesetzt werden');
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'healthy':
        return '#10b981'; // green
      case 'running':
      case 'in-progress':
        return '#3b82f6'; // blue
      case 'failed':
      case 'unhealthy':
        return '#ef4444'; // red
      case 'pending':
      case 'degraded':
        return '#f59e0b'; // yellow
      default:
        return '#6b7280'; // gray
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('de-DE');
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
          Schulferien Sync Administration
        </h1>
        <p style={{ color: '#6b7280', marginBottom: '16px' }}>
          Verwaltung und Überwachung der automatischen Schulferien-Synchronisation
        </p>
        <button
          onClick={refreshData}
          disabled={isLoading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#f3f4f6',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? '🔄 Lädt...' : '🔄 Aktualisieren'}
        </button>
        <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
          Letzte Aktualisierung: {lastRefresh.toLocaleTimeString('de-DE')}
        </p>
      </div>

      {/* Status Overview Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '16px', 
        marginBottom: '32px' 
      }}>
        {/* Sync Status */}
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px', 
          padding: '16px',
          backgroundColor: 'white'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '500' }}>Sync Status</h3>
            <span style={{ fontSize: '20px' }}>📊</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: getStatusColor(mockSyncStatus.status) 
            }} />
            <span style={{ fontSize: '14px', fontWeight: '500' }}>
              {mockSyncStatus.status}
            </span>
          </div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            ID: {mockSyncStatus.sync_id}
          </p>
        </div>

        {/* Scheduler Status */}
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px', 
          padding: '16px',
          backgroundColor: 'white'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '500' }}>Scheduler</h3>
            <span style={{ fontSize: '20px' }}>📅</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: mockSchedulerStatus.running ? '#10b981' : '#ef4444'
            }} />
            <span style={{ fontSize: '14px', fontWeight: '500' }}>
              {mockSchedulerStatus.running ? 'Aktiv' : 'Gestoppt'}
            </span>
          </div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            Nächster Lauf: {formatDateTime(mockSchedulerStatus.next_run)}
          </p>
        </div>

        {/* System Health */}
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px', 
          padding: '16px',
          backgroundColor: 'white'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '500' }}>System Health</h3>
            <span style={{ fontSize: '20px' }}>🖥️</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: getStatusColor(mockSystemHealth.overall_status)
            }} />
            <span style={{ fontSize: '14px', fontWeight: '500' }}>
              {mockSystemHealth.overall_status}
            </span>
          </div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            {mockSystemHealth.pending_conflicts} Konflikte
          </p>
        </div>

        {/* Statistics */}
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px', 
          padding: '16px',
          backgroundColor: 'white'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '500' }}>Erfolgsrate</h3>
            <span style={{ fontSize: '20px' }}>💾</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
            100%
          </div>
          <p style={{ fontSize: '12px', color: '#6b7280' }}>
            1 Sync gesamt
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb' }}>
          {['dashboard', 'history', 'statistics', 'scheduler', 'health'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '12px 16px',
                border: 'none',
                backgroundColor: 'transparent',
                borderBottom: activeTab === tab ? '2px solid #3b82f6' : '2px solid transparent',
                color: activeTab === tab ? '#3b82f6' : '#6b7280',
                cursor: 'pointer',
                textTransform: 'capitalize'
              }}
            >
              {tab === 'dashboard' ? 'Dashboard' : 
               tab === 'history' ? 'Historie' :
               tab === 'statistics' ? 'Statistiken' :
               tab === 'scheduler' ? 'Scheduler' : 'System'}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: '400px' }}>
        {activeTab === 'dashboard' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
            {/* Manual Sync Trigger */}
            <div style={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px', 
              padding: '24px',
              backgroundColor: 'white'
            }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
                Manueller Sync
              </h3>
              <p style={{ color: '#6b7280', marginBottom: '16px' }}>
                Starten Sie eine sofortige Synchronisation aller Bundesländer.
              </p>
              <button
                onClick={triggerManualSync}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                🚀 Sync starten
              </button>
            </div>

            {/* Current Status */}
            <div style={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px', 
              padding: '24px',
              backgroundColor: 'white'
            }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
                Aktueller Status
              </h3>
              <div style={{ marginBottom: '12px' }}>
                <strong>Status:</strong> {mockSyncStatus.status}
              </div>
              <div style={{ marginBottom: '12px' }}>
                <strong>Bundesländer:</strong> {mockSyncStatus.completed_states}/{mockSyncStatus.total_states}
              </div>
              <div style={{ marginBottom: '12px' }}>
                <strong>Gestartet:</strong> {formatDateTime(mockSyncStatus.started_at)}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            padding: '24px',
            backgroundColor: 'white'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Sync Historie
            </h3>
            {mockSyncHistory.map((item) => (
              <div key={item.sync_id} style={{ 
                padding: '16px', 
                border: '1px solid #f3f4f6', 
                borderRadius: '6px',
                marginBottom: '12px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <strong>{item.sync_id}</strong>
                  <span style={{ 
                    padding: '4px 8px', 
                    backgroundColor: getStatusColor(item.status), 
                    color: 'white', 
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    {item.status}
                  </span>
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  <div>Dauer: {formatDuration(item.duration_seconds)}</div>
                  <div>Änderungen: {item.total_changes}</div>
                  <div>Erfolgsrate: {Math.round(item.success_rate * 100)}%</div>
                  <div>Ausgelöst von: {item.triggered_by}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'scheduler' && (
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            padding: '24px',
            backgroundColor: 'white'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Scheduler Kontrolle
            </h3>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>Status:</strong> {mockSchedulerStatus.running ? 'Aktiv' : 'Gestoppt'}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Nächster Lauf:</strong> {formatDateTime(mockSchedulerStatus.next_run)}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Letzter Lauf:</strong> {formatDateTime(mockSchedulerStatus.last_run)}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={pauseScheduler}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#f59e0b',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                ⏸️ Pausieren
              </button>
              <button
                onClick={resumeScheduler}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                ▶️ Fortsetzen
              </button>
            </div>
          </div>
        )}

        {activeTab === 'health' && (
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            padding: '24px',
            backgroundColor: 'white'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              System Health
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <div style={{ fontWeight: '500', marginBottom: '4px' }}>Datenbank</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: '50%', 
                    backgroundColor: getStatusColor(mockSystemHealth.database_status)
                  }} />
                  {mockSystemHealth.database_status}
                </div>
              </div>
              <div>
                <div style={{ fontWeight: '500', marginBottom: '4px' }}>API Client</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: '50%', 
                    backgroundColor: getStatusColor(mockSystemHealth.api_client_status)
                  }} />
                  {mockSystemHealth.api_client_status}
                </div>
              </div>
              <div>
                <div style={{ fontWeight: '500', marginBottom: '4px' }}>Scheduler</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: '50%', 
                    backgroundColor: getStatusColor(mockSystemHealth.scheduler_status)
                  }} />
                  {mockSystemHealth.scheduler_status}
                </div>
              </div>
            </div>
            <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>Speicherverbrauch:</strong> {mockSystemHealth.memory_usage_mb} MB
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Festplattennutzung:</strong> {mockSystemHealth.disk_usage_percentage}%
              </div>
              <div>
                <strong>System Uptime:</strong> {formatDuration(mockSystemHealth.system_uptime_seconds)}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'statistics' && (
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            padding: '24px',
            backgroundColor: 'white'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Sync Statistiken
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '6px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#16a34a' }}>1</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Erfolgreiche Syncs</div>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fef2f2', borderRadius: '6px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc2626' }}>0</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Fehlgeschlagene Syncs</div>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0f9ff', borderRadius: '6px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2563eb' }}>45</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Synchronisierte Feiertage</div>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fffbeb', borderRadius: '6px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#d97706' }}>5m</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Durchschnittliche Dauer</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
