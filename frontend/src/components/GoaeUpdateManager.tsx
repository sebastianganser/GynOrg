import React, { useState, useEffect } from 'react';
import { Database, RefreshCw, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { goaeService } from '../services/rechnungService';

interface ImportStatus {
  total: number;
  aktive: number;
  letztes_update: string | null;
}

const GoaeUpdateManager: React.FC = () => {
  const [status, setStatus] = useState<ImportStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const data = await goaeService.getImportStatus();
      setStatus(data);
    } catch (e) {
      console.error('Fehler beim Laden des GOÄ-Status:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleImport = async () => {
    if (!window.confirm(
      'GOÄ-Ziffern jetzt importieren/aktualisieren?\n\n' +
      'Bestehende Einträge werden aktualisiert, neue hinzugefügt.\n' +
      'Dieser Vorgang kann einige Sekunden dauern.'
    )) return;

    setImporting(true);
    setResult(null);
    try {
      const res = await goaeService.triggerImport();
      setResult({ success: true, message: res.message });
      await loadStatus();
    } catch (err: any) {
      setResult({
        success: false,
        message: err?.response?.data?.detail || err?.data?.detail || 'Import fehlgeschlagen'
      });
    } finally {
      setImporting(false);
    }
  };

  const formatDate = (iso: string) => {
    // Backend speichert UTC – 'Z' anhängen damit der Browser in Lokalzeit konvertiert
    const utcIso = iso.endsWith('Z') ? iso : iso + 'Z';
    return new Date(utcIso).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 relative overflow-hidden">

      {/* ─── Import-Overlay (blockiert die Karte während des Imports) ─── */}
      {importing && (
        <div className="absolute inset-0 z-10 bg-white/90 backdrop-blur-sm flex flex-col items-center justify-center rounded-lg">
          {/* Animierter Spinner */}
          <div className="relative mb-4">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
            <Database size={24} className="absolute inset-0 m-auto text-blue-600" />
          </div>

          <h4 className="text-lg font-semibold text-gray-900 mb-1">GOÄ-Import wird durchgeführt</h4>
          <p className="text-sm text-gray-500 mb-4">
            ~2.525 Ziffern werden importiert – bitte warten...
          </p>

          {/* Animierter Fortschrittsbalken (indeterminate) */}
          <div className="w-64 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full animate-pulse"
              style={{
                width: '60%',
                animation: 'goaeProgress 1.5s ease-in-out infinite alternate',
              }}
            />
          </div>
          <style>{`
            @keyframes goaeProgress {
              0%   { width: 20%; margin-left: 0; }
              100% { width: 60%; margin-left: 40%; }
            }
          `}</style>
        </div>
      )}

      <h4 className="text-lg font-medium text-gray-900 mb-2 flex items-center gap-2">
        <Database size={20} className="text-blue-600" />
        GOÄ-Ziffern & Stammdaten
      </h4>
      <p className="text-gray-600 mb-4">
        Verwalten Sie den GOÄ-Leistungskatalog (Gebührenordnung für Ärzte).
        Über den Import werden alle verfügbaren Ziffern in die Datenbank geladen oder aktualisiert.
      </p>

      {/* Datenstand */}
      {loading ? (
        <div className="flex items-center gap-2 text-gray-400 mb-4">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
          Lade Datenstand...
        </div>
      ) : status ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Ziffern gesamt</span>
              <div className="text-2xl font-bold text-gray-900">{status.total.toLocaleString('de-DE')}</div>
            </div>
            <div>
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Davon aktiv</span>
              <div className="text-2xl font-bold text-green-600">{status.aktive.toLocaleString('de-DE')}</div>
            </div>
            <div>
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Letztes Update</span>
              <div className="text-lg font-semibold text-gray-900">
                {status.letztes_update
                  ? formatDate(status.letztes_update)
                  : <span className="text-yellow-600 text-base">Noch kein Import</span>
                }
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {/* Hinweis */}
      <div className="flex items-start gap-2 text-sm text-gray-500 mb-4 bg-blue-50 border border-blue-100 rounded-lg p-3">
        <Info size={16} className="text-blue-500 flex-shrink-0 mt-0.5" />
        <div>
          <strong>Hinweis:</strong> Der GOÄ-Katalog enthält ca. 2.525 Leistungsziffern. Beim Import werden bestehende
          Einträge aktualisiert und fehlende ergänzt. Der Vorgang ist idempotent und kann jederzeit wiederholt werden.
        </div>
      </div>

      {/* Ergebnis-Meldung */}
      {result && (
        <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
          result.success
            ? 'bg-green-50 border border-green-200 text-green-700'
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          {result.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          {result.message}
        </div>
      )}

      {/* Import-Button */}
      <button
        onClick={handleImport}
        disabled={importing}
        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <RefreshCw size={16} className="mr-2" />
        GOÄ-Ziffern importieren / aktualisieren
      </button>
    </div>
  );
};

export default GoaeUpdateManager;

