import React, { useState, useEffect } from 'react';
import { auslastungService } from '../services/auslastungService';
import { Station, StationCapacity } from '../types/auslastung';

export const StationManager: React.FC = () => {
  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);
  const [capacities, setCapacities] = useState<StationCapacity[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Forms
  const [stationForm, setStationForm] = useState({ name: '', is_internal: true, is_active: true });
  const [editingStation, setEditingStation] = useState<number | null>(null);
  
  const [capForm, setCapForm] = useState({ valid_from: new Date().toISOString().split('T')[0], valid_to: '', plan_beds: 0 });

  useEffect(() => {
    loadStations();
  }, []);

  useEffect(() => {
    if (selectedStation) {
      loadCapacities(selectedStation.id);
    }
  }, [selectedStation]);

  const loadStations = async () => {
    try {
      setLoading(true);
      const data = await auslastungService.getStations(false); // get all including inactive
      setStations(data);
    } catch (err: any) {
      setError('Fehler beim Laden der Stationen: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadCapacities = async (id: number) => {
    try {
      const data = await auslastungService.getStationCapacities(id);
      setCapacities(data);
    } catch (err: any) {
      setError('Fehler beim Laden der Kapazitäten: ' + err.message);
    }
  };

  const handleSaveStation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingStation) {
        await auslastungService.updateStation(editingStation, stationForm);
      } else {
        await auslastungService.createStation(stationForm);
      }
      setStationForm({ name: '', is_internal: true, is_active: true });
      setEditingStation(null);
      await loadStations();
    } catch (err: any) {
      setError('Fehler beim Speichern: ' + err.message);
    }
  };

  const handleSaveCapacity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStation) return;
    try {
      await auslastungService.createStationCapacity(selectedStation.id, {
        station_id: selectedStation.id,
        valid_from: capForm.valid_from,
        valid_to: capForm.valid_to || undefined,
        plan_beds: capForm.plan_beds
      });
      setCapForm({ valid_from: new Date().toISOString().split('T')[0], valid_to: '', plan_beds: 0 });
      await loadCapacities(selectedStation.id);
    } catch (err: any) {
      setError('Fehler beim Speichern der Kapazität: ' + err.message);
    }
  };

  const editStation = (station: Station) => {
    setStationForm({
      name: station.name,
      is_internal: station.is_internal ?? true,
      is_active: station.is_active
    });
    setEditingStation(station.id);
  };

  const handleDeleteStation = async (station: Station) => {
    if (window.confirm(`Sind Sie sicher, dass Sie die Station "${station.name}" löschen möchten?\n\nAchtung: Alle historischen Belegungsdaten und hinterlegten Kapazitäten für diese Station werden dabei ebenfalls unwiderruflich gelöscht!`)) {
      try {
        await auslastungService.deleteStation(station.id);
        if (selectedStation?.id === station.id) {
          setSelectedStation(null);
        }
        if (editingStation === station.id) {
          setEditingStation(null);
          setStationForm({ name: '', is_internal: true, is_active: true });
        }
        await loadStations();
      } catch (err: any) {
        setError('Fehler beim Löschen der Station: ' + err.message);
      }
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Lade Stationen...</div>;

  return (
    <div className="flex flex-col md:flex-row h-full">
      {/* Left side: Stations List */}
      <div className="w-full md:w-1/3 bg-white border-r border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Stationen</h3>
        
        {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-sm">{error}</div>}
        
        <form onSubmit={handleSaveStation} className="mb-6 space-y-3 bg-gray-50 p-4 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-700">{editingStation ? 'Station bearbeiten' : 'Neue Station anlegen'}</h4>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Name</label>
            <input required type="text" value={stationForm.name} onChange={e => setStationForm({...stationForm, name: e.target.value})} className="w-full border-gray-300 rounded-md shadow-sm text-sm p-2 border focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div className="flex space-x-4">
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700 mb-1">Verwaltung</label>
              <select 
                value={stationForm.is_internal ? "true" : "false"} 
                onChange={e => setStationForm({...stationForm, is_internal: e.target.value === "true"})} 
                className="w-full border-gray-300 rounded-md shadow-sm text-sm p-2 border focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="true">Eigenverwaltet</option>
                <option value="false">Fremdverwaltet</option>
              </select>
            </div>
            <div className="flex items-center pt-5">
              <input type="checkbox" checked={stationForm.is_active} onChange={e => setStationForm({...stationForm, is_active: e.target.checked})} className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
              <label className="ml-2 block text-sm text-gray-900">Aktiv</label>
            </div>
          </div>
          <div className="flex space-x-2 pt-2">
            <button type="submit" className="flex-1 bg-blue-600 text-white text-sm font-semibold py-2 px-4 rounded-md hover:bg-blue-700">
              {editingStation ? 'Aktualisieren' : 'Hinzufügen'}
            </button>
            {editingStation && (
              <button type="button" onClick={() => { setEditingStation(null); setStationForm({name: '', is_internal: true, is_active: true}); }} className="bg-gray-200 text-gray-700 text-sm font-semibold py-2 px-4 rounded-md hover:bg-gray-300">
                Abbrechen
              </button>
            )}
          </div>
        </form>

        <div className="space-y-2 max-h-[50vh] overflow-y-auto pr-2">
          {stations.map(station => (
            <div 
              key={station.id} 
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${selectedStation?.id === station.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}
              onClick={() => setSelectedStation(station)}
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-3">
                  <div className={`text-xs px-2 py-1 rounded-full font-medium ${station.is_internal ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
                    {station.is_internal ? "Eigen" : "Fremd"}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{station.name}</div>
                    {!station.is_active && <span className="text-xs text-red-500">Inaktiv</span>}
                  </div>
                </div>
                <div className="flex space-x-1">
                  <button 
                    onClick={(e) => { e.stopPropagation(); editStation(station); }}
                    className="text-gray-400 hover:text-blue-600 p-1 rounded"
                    title="Bearbeiten"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); handleDeleteStation(station); }}
                    className="text-gray-400 hover:text-red-600 p-1 rounded"
                    title="Löschen"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
          {stations.length === 0 && <p className="text-sm text-gray-500 italic">Keine Stationen vorhanden</p>}
        </div>
      </div>

      {/* Right side: Station Capacities */}
      <div className="w-full md:w-2/3 p-6 bg-gray-50">
        {!selectedStation ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            Wähle links eine Station aus, um die Bettenkapazitäten zu verwalten.
          </div>
        ) : (
          <div>
            <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-gray-200">
              <div className={`text-xs px-2 py-1 rounded-full font-medium ${selectedStation.is_internal ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
                {selectedStation.is_internal ? "Eigenverwaltet" : "Fremdverwaltet"}
              </div>
              <h3 className="text-xl font-bold text-gray-800">Kapazitäten: {selectedStation.name}</h3>
            </div>

            <form onSubmit={handleSaveCapacity} className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4 items-end bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Gültig ab</label>
                <input required type="date" value={capForm.valid_from} onChange={e => setCapForm({...capForm, valid_from: e.target.value})} className="w-full border-gray-300 rounded-md shadow-sm text-sm p-2 border focus:border-blue-500 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Gültig bis (optional)</label>
                <input type="date" value={capForm.valid_to} onChange={e => setCapForm({...capForm, valid_to: e.target.value})} className="w-full border-gray-300 rounded-md shadow-sm text-sm p-2 border focus:border-blue-500 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Planbetten</label>
                <input required type="number" min="0" value={capForm.plan_beds} onChange={e => setCapForm({...capForm, plan_beds: parseInt(e.target.value) || 0})} className="w-full border-gray-300 rounded-md shadow-sm text-sm p-2 border focus:border-blue-500 focus:ring-blue-500" />
              </div>
              <div>
                <button type="submit" className="w-full bg-blue-600 text-white text-sm font-semibold py-2 px-4 rounded-md hover:bg-blue-700">
                  Speichern
                </button>
              </div>
            </form>

            <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Planbetten</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gültig ab</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gültig bis</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {capacities.map(cap => (
                    <tr key={cap.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {cap.plan_beds} Betten
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(cap.valid_from).toLocaleDateString('de-DE')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {cap.valid_to ? new Date(cap.valid_to).toLocaleDateString('de-DE') : <span className="text-green-600 italic">Aktuell aktiv</span>}
                      </td>
                    </tr>
                  ))}
                  {capacities.length === 0 && (
                    <tr>
                      <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                        Keine Kapazitäten für diese Station hinterlegt.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
