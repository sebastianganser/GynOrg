import React, { useState, useEffect } from 'react';
import { Plus, Search, FileText, Download, CheckCircle, XCircle, Pencil } from 'lucide-react';
import { rechnungService, patientenService } from '../services/rechnungService';
import { Rechnung, Patient, statusLabel, statusColor } from '../types/rechnung';

interface RechnungenTabProps {
  onNavigateToWizard: () => void;
  onEditRechnung?: (id: number) => void;
}

const RechnungenTab: React.FC<RechnungenTabProps> = ({ onNavigateToWizard, onEditRechnung }) => {
  const [rechnungen, setRechnungen] = useState<Rechnung[]>([]);
  const [patienten, setPatienten] = useState<Record<number, Patient>>({});
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    loadRechnungen();
  }, [statusFilter]);

  const loadRechnungen = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      const data = await rechnungService.getAll(params);
      setRechnungen(data);

      const patientIds = [...new Set(data.map(r => r.patient_id))];
      const patientMap: Record<number, Patient> = {};
      for (const id of patientIds) {
        try {
          patientMap[id] = await patientenService.getById(id);
        } catch (e) { /* ignore */ }
      }
      setPatienten(patientMap);
    } catch (err) {
      console.error('Fehler beim Laden der Rechnungen:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStellen = async (id: number) => {
    if (!window.confirm('Rechnung stellen? Sie kann danach nicht mehr bearbeitet werden.')) return;
    setActionLoading(id);
    try {
      await rechnungService.stellen(id);
      await loadRechnungen();
    } catch (err: any) {
      alert(err?.data?.detail || 'Fehler beim Stellen der Rechnung');
    } finally {
      setActionLoading(null);
    }
  };

  const handleBezahlt = async (id: number) => {
    setActionLoading(id);
    try {
      await rechnungService.bezahlt(id);
      await loadRechnungen();
    } catch (err: any) {
      alert(err?.data?.detail || 'Fehler');
    } finally {
      setActionLoading(null);
    }
  };

  const handleStornieren = async (id: number) => {
    const grund = window.prompt('Stornierungsgrund:');
    if (!grund) return;
    setActionLoading(id);
    try {
      await rechnungService.stornieren(id, grund);
      await loadRechnungen();
    } catch (err: any) {
      alert(err?.data?.detail || 'Fehler');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Entwurf wirklich löschen?')) return;
    setActionLoading(id);
    try {
      await rechnungService.delete(id);
      await loadRechnungen();
    } catch (err: any) {
      alert(err?.data?.detail || 'Fehler');
    } finally {
      setActionLoading(null);
    }
  };

  const handleGeneratePdf = async (id: number) => {
    setActionLoading(id);
    try {
      await rechnungService.generatePdf(id);
      alert('PDF wurde generiert');
      await loadRechnungen();
    } catch (err: any) {
      alert(err?.data?.detail || 'PDF-Generierung fehlgeschlagen');
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (d: string) => new Date(d).toLocaleDateString('de-DE');
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val);

  const filteredRechnungen = rechnungen.filter(r => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const patient = patienten[r.patient_id];
    const patientName = patient ? `${patient.vorname} ${patient.nachname}`.toLowerCase() : '';
    return (
      r.rechnungsnummer.toLowerCase().includes(q) ||
      r.diagnose.toLowerCase().includes(q) ||
      patientName.includes(q)
    );
  });

  const statusTabs: { key: string; label: string; count: number }[] = [
    { key: '', label: 'Alle', count: rechnungen.length },
    { key: 'entwurf', label: 'Entwürfe', count: rechnungen.filter(r => r.status === 'entwurf').length },
    { key: 'gestellt', label: 'Gestellt', count: rechnungen.filter(r => r.status === 'gestellt').length },
    { key: 'bezahlt', label: 'Bezahlt', count: rechnungen.filter(r => r.status === 'bezahlt').length },
    { key: 'storniert', label: 'Storniert', count: rechnungen.filter(r => r.status === 'storniert').length },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Rechnungsübersicht</h2>
          <p className="text-sm text-gray-500">GOÄ-Rechnungen verwalten</p>
        </div>
        <button
          onClick={onNavigateToWizard}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          id="btn-neue-rechnung"
        >
          <Plus size={18} className="mr-2" />
          Neue Rechnung
        </button>
      </div>

      {/* Status-Tabs */}
      <div className="flex space-x-1 mb-4 border-b border-gray-200">
        {statusTabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setStatusFilter(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              statusFilter === tab.key
                ? 'bg-white border border-b-white border-gray-200 text-blue-600 -mb-px'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Suche */}
      <div className="relative mb-4">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Suche nach Rechnungsnummer, Patient oder Diagnose..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          id="input-rechnung-suche"
        />
      </div>

      {/* Tabelle */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredRechnungen.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <FileText size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Rechnungen vorhanden</h3>
          <p className="text-gray-500 mb-4">Erstellen Sie Ihre erste GOÄ-Rechnung.</p>
          <button
            onClick={onNavigateToWizard}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} className="mr-2" />
            Neue Rechnung
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Nr.</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Datum</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Patient</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Diagnose</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 uppercase">Betrag</th>
                <th className="text-center px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 uppercase">Aktionen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredRechnungen.map(r => {
                const patient = patienten[r.patient_id];
                return (
                  <tr key={r.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-mono font-medium text-gray-900">
                      {r.rechnungsnummer}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(r.rechnungsdatum)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {patient ? `${patient.nachname}, ${patient.vorname}` : `Patient #${r.patient_id}`}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                      {r.diagnose}
                    </td>
                    <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                      {formatCurrency(r.gesamtbetrag)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor(r.status)}`}>
                        {statusLabel(r.status)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-1">
                        {r.status === 'entwurf' && (
                          <>
                            {onEditRechnung && (
                              <button
                                onClick={() => onEditRechnung(r.id)}
                                disabled={actionLoading === r.id}
                                className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                                title="Bearbeiten"
                              >
                                <Pencil size={16} />
                              </button>
                            )}
                            <button
                              onClick={() => handleStellen(r.id)}
                              disabled={actionLoading === r.id}
                              className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                              title="Rechnung stellen"
                            >
                              <CheckCircle size={16} />
                            </button>
                            <button
                              onClick={() => handleDelete(r.id)}
                              disabled={actionLoading === r.id}
                              className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Entwurf löschen"
                            >
                              <XCircle size={16} />
                            </button>
                          </>
                        )}
                        {r.status === 'gestellt' && (
                          <>
                            <button
                              onClick={() => handleBezahlt(r.id)}
                              disabled={actionLoading === r.id}
                              className="p-1.5 text-green-600 hover:bg-green-50 rounded transition-colors"
                              title="Als bezahlt markieren"
                            >
                              <CheckCircle size={16} />
                            </button>
                            <button
                              onClick={() => handleStornieren(r.id)}
                              disabled={actionLoading === r.id}
                              className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Stornieren"
                            >
                              <XCircle size={16} />
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleGeneratePdf(r.id)}
                          disabled={actionLoading === r.id}
                          className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                          title="PDF generieren"
                        >
                          <FileText size={16} />
                        </button>
                        {r.dokumente.length > 0 && (
                          <a
                            href={`/api/v1${rechnungService.getPdfDownloadUrl(r.id)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                            title="PDF herunterladen"
                          >
                            <Download size={16} />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default RechnungenTab;
