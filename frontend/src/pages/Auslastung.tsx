import React, { useState, useEffect } from 'react';
import { auslastungService } from '../services/auslastungService';
import { Station, DailyEntry, DailyFremd } from '../types/auslastung';

const Auslastung: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'eingabe' | 'dashboard'>('eingabe');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [stations, setStations] = useState<Station[]>([]);
  const [entries, setEntries] = useState<Record<number, DailyEntry>>({});
  const [showFremdStations, setShowFremdStations] = useState<boolean>(false);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    loadData();
  }, [date]);

  const loadData = async () => {
    setIsLoading(true);
    setMessage(null);
    try {
      // Load active stations only
      const stationsData = await auslastungService.getStations(true);
      setStations(stationsData);
      
      // Load existing entries for the date
      const entriesData = await auslastungService.getDailyEntries(date, date);
      const entriesMap: Record<number, DailyEntry> = {};
      entriesData.forEach(entry => {
        entriesMap[entry.station_id] = entry;
      });
      setEntries(entriesMap);
      
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Fehler beim Laden der Daten: ' + err.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEntryChange = (stationId: number, field: keyof DailyEntry, value: number) => {
    setEntries(prev => {
      const existing = prev[stationId] || { 
        station_id: stationId, date: date, occupied: 0, admissions: 0, discharges: 0, blocked_beds: 0 
      };
      return {
        ...prev,
        [stationId]: { ...existing, [field]: value || 0 }
      } as Record<number, DailyEntry>;
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);
    try {
      // Save all station entries
      const promises = stations.map(station => {
        const entry = entries[station.id];
        if (entry) {
          return auslastungService.upsertDailyEntry({
            station_id: station.id,
            date: date,
            occupied: entry.occupied || 0,
            admissions: entry.admissions || 0,
            discharges: entry.discharges || 0,
            blocked_beds: entry.blocked_beds || 0
          });
        }
        return Promise.resolve();
      });
      
      await Promise.all(promises);
      
      setMessage({ type: 'success', text: 'Daten erfolgreich gespeichert.' });
      setTimeout(() => setMessage(null), 3000);
      
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Fehler beim Speichern: ' + err.message });
    } finally {
      setIsSaving(false);
    }
  };

  const handleCalculateMultipliers = async () => {
    setIsCalculating(true);
    setMessage(null);
    try {
      const result = await auslastungService.calculateMultipliers();
      setMessage({ type: 'success', text: `Berechnung erfolgreich. ${result.calculated_multipliers} Multiplikatoren wurden aktualisiert.` });
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Fehler bei der Berechnung: ' + err.message });
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-2">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Belegungsstatistik</h2>
          <p className="text-gray-500 text-sm mt-1">Erfassung und Auswertung der täglichen Stationsauslastung</p>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('eingabe')}
            className={`${activeTab === 'eingabe' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Tägliche Eingabe
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`${activeTab === 'dashboard' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Dashboard & Prognosen
          </button>
        </nav>
      </div>

      {message && (
        <div className={`p-4 rounded-md shadow-sm ${message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
          {message.text}
        </div>
      )}

      {activeTab === 'eingabe' ? (
        <>
          <div className="flex justify-end mb-4">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Datum:</label>
              <input 
                type="date" 
                value={date} 
                onChange={e => setDate(e.target.value)}
                className="border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 font-medium p-2 border bg-white"
              />
            </div>
          </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-500">Lade Daten...</span>
        </div>
      ) : stations.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Keine Stationen gefunden</h3>
          <p className="mt-1 text-sm text-gray-500">Bitte lege zuerst in den Einstellungen aktive Stationen an.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Station</th>
                  <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Belegte Betten (00:00)</th>
                  <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Aufnahmen (Vortag)</th>
                  <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Entlassungen (Vortag)</th>
                  <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Gesperrte Betten</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(showFremdStations ? stations : stations.filter(s => s.is_internal)).map(station => {
                  const entry = entries[station.id] || { occupied: 0, admissions: 0, discharges: 0, blocked_beds: 0 };
                  return (
                    <tr key={station.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${station.is_internal ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
                            {station.is_internal ? "Eigen" : "Fremd"}
                          </span>
                          <span className="font-medium text-gray-900">{station.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        <input 
                          type="number" min="0" value={entry.occupied || ''} 
                          onChange={e => handleEntryChange(station.id, 'occupied', parseInt(e.target.value) || 0)}
                          className="w-20 text-center border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border"
                          placeholder="0"
                        />
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        <input 
                          type="number" min="0" value={entry.admissions || ''} 
                          onChange={e => handleEntryChange(station.id, 'admissions', parseInt(e.target.value) || 0)}
                          className="w-20 text-center border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border"
                          placeholder="0"
                        />
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        <input 
                          type="number" min="0" value={entry.discharges || ''} 
                          onChange={e => handleEntryChange(station.id, 'discharges', parseInt(e.target.value) || 0)}
                          className="w-20 text-center border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border"
                          placeholder="0"
                        />
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        <input 
                          type="number" min="0" value={entry.blocked_beds || ''} 
                          onChange={e => handleEntryChange(station.id, 'blocked_beds', parseInt(e.target.value) || 0)}
                          className="w-20 text-center border-gray-300 rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 sm:text-sm p-2 border"
                          placeholder="0"
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between rounded-b-lg">
            {!showFremdStations && stations.some(s => !s.is_internal) ? (
              <button 
                type="button" 
                onClick={() => setShowFremdStations(true)} 
                className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                Fremdlieger vorhanden?
              </button>
            ) : showFremdStations && stations.some(s => !s.is_internal) ? (
              <button 
                type="button" 
                onClick={() => setShowFremdStations(false)} 
                className="text-sm text-gray-500 hover:text-gray-700 font-medium flex items-center"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" /></svg>
                Fremdlieger ausblenden
              </button>
            ) : <div></div>}
            
            <button
              onClick={handleSave}
              disabled={isSaving}
              className={`inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${isSaving ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`}
            >
              {isSaving ? 'Speichern...' : 'Alle Änderungen speichern'}
            </button>
          </div>
        </div>
      )}
      </>
      ) : (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Einstellungen & Systemaktionen</h3>
            <p className="text-sm text-gray-500 mb-4">
              Die Belegungsstatistik wertet historische Datenbasis aus, um Multiplikatoren (z.B. für Feiertage) zu berechnen. 
              Dies geschieht normalerweise automatisch jede Nacht. Nach größeren Änderungen der Stammdaten können Sie die Berechnung hier manuell anstoßen.
            </p>
            <button
              onClick={handleCalculateMultipliers}
              disabled={isCalculating}
              className={`inline-flex items-center justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${isCalculating ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'}`}
            >
              {isCalculating ? (
                <><svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Berechne...</>
              ) : (
                'Multiplikatoren neu berechnen'
              )}
            </button>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-8 border border-gray-200 border-dashed text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Historische Daten & Prognosen</h3>
            <p className="mt-1 text-sm text-gray-500">Das visualisierte Dashboard mit den Diagrammen und Prognosen wird im nächsten Entwicklungsschritt implementiert.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Auslastung;
