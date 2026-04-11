import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit2, Trash2, X, Save, UserPlus, ChevronDown, ChevronUp } from 'lucide-react';
import { patientenService } from '../services/rechnungService';
import { Patient, PatientCreate, PatientUpdate, Anrede } from '../types/rechnung';

const Patienten: React.FC = () => {
  const [patienten, setPatienten] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showInactive, setShowInactive] = useState(false);

  // Formular-State
  const emptyForm: PatientCreate = {
    anrede: 'Frau',
    vorname: '',
    nachname: '',
    geburtsdatum: '',
    strasse: '',
    hausnummer: '',
    plz: '',
    ort: '',
    telefon: null,
    email: null,
    versicherung: null,
    versicherungsnummer: null,
    notizen: null,
    aufnahme_datum: null,
  };
  const [form, setForm] = useState<PatientCreate>(emptyForm);

  useEffect(() => {
    loadPatienten();
  }, [showInactive]);

  const loadPatienten = async () => {
    try {
      setLoading(true);
      const data = await patientenService.getAll(!showInactive);
      setPatienten(data);
    } catch (err) {
      console.error('Fehler beim Laden:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof PatientCreate, value: any) => {
    setForm(prev => ({ ...prev, [field]: value || null }));
  };

  const openNewForm = () => {
    setEditingPatient(null);
    setForm(emptyForm);
    setShowForm(true);
    setError('');
  };

  const openEditForm = (patient: Patient) => {
    setEditingPatient(patient);
    setForm({
      anrede: patient.anrede,
      titel: patient.titel,
      vorname: patient.vorname,
      nachname: patient.nachname,
      geburtsdatum: patient.geburtsdatum,
      strasse: patient.strasse,
      hausnummer: patient.hausnummer,
      plz: patient.plz,
      ort: patient.ort,
      telefon: patient.telefon,
      email: patient.email,
      versicherung: patient.versicherung,
      versicherungsnummer: patient.versicherungsnummer,
      notizen: patient.notizen,
      aufnahme_datum: patient.aufnahme_datum,
    });
    setShowForm(true);
    setError('');
  };

  const handleSave = async () => {
    if (!form.vorname || !form.nachname || !form.geburtsdatum || !form.strasse || !form.plz || !form.ort) {
      setError('Bitte füllen Sie alle Pflichtfelder aus.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      if (editingPatient) {
        await patientenService.update(editingPatient.id, form as PatientUpdate);
      } else {
        await patientenService.create(form);
      }
      setShowForm(false);
      setEditingPatient(null);
      await loadPatienten();
    } catch (err: any) {
      setError(err?.data?.detail || 'Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Patient wirklich deaktivieren? (Soft-Delete)')) return;
    try {
      await patientenService.delete(id);
      await loadPatienten();
    } catch (err: any) {
      alert(err?.data?.detail || 'Fehler beim Löschen');
    }
  };

  const formatDate = (d: string | null) => {
    if (!d) return '–';
    return new Date(d).toLocaleDateString('de-DE');
  };

  const filteredPatienten = patienten.filter(p => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.vorname.toLowerCase().includes(q) ||
      p.nachname.toLowerCase().includes(q) ||
      (p.versicherung || '').toLowerCase().includes(q) ||
      (p.versicherungsnummer || '').toLowerCase().includes(q)
    );
  });

  const inputClass = "w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm";
  const labelClass = "block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1";

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Patientenverwaltung</h2>
          <p className="text-sm text-gray-500">Privatpatienten anlegen und verwalten</p>
        </div>
        <button
          onClick={openNewForm}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          id="btn-neuer-patient"
        >
          <UserPlus size={18} className="mr-2" />
          Neuer Patient
        </button>
      </div>

      {/* Suche + Filter */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Suche nach Name, Versicherung..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            id="input-patient-filter"
          />
        </div>
        <label className="flex items-center text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={e => setShowInactive(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 mr-2"
          />
          Inaktive anzeigen
        </label>
      </div>

      {/* ─── Anlage-/Bearbeitungsformular ─── */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-lg border border-blue-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {editingPatient ? 'Patient bearbeiten' : 'Neuen Patienten anlegen'}
            </h3>
            <button onClick={() => { setShowForm(false); setEditingPatient(null); }} className="text-gray-400 hover:text-gray-600">
              <X size={20} />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
          )}

          {/* Persönliche Daten */}
          <div className="mb-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 border-b pb-1">Persönliche Daten</h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div>
                <label className={labelClass}>Anrede *</label>
                <select value={form.anrede} onChange={e => handleChange('anrede', e.target.value as Anrede)} className={inputClass}>
                  <option value="Frau">Frau</option>
                  <option value="Herr">Herr</option>
                  <option value="Divers">Divers</option>
                </select>
              </div>
              <div>
                <label className={labelClass}>Titel</label>
                <input value={form.titel || ''} onChange={e => handleChange('titel', e.target.value)} placeholder="z.B. Dr." className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Vorname *</label>
                <input value={form.vorname} onChange={e => setForm(p => ({...p, vorname: e.target.value}))} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Nachname *</label>
                <input value={form.nachname} onChange={e => setForm(p => ({...p, nachname: e.target.value}))} className={inputClass} />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
              <div>
                <label className={labelClass}>Geburtsdatum *</label>
                <input type="date" value={form.geburtsdatum} onChange={e => setForm(p => ({...p, geburtsdatum: e.target.value}))} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Aufnahme-Datum</label>
                <input type="date" value={form.aufnahme_datum || ''} onChange={e => handleChange('aufnahme_datum', e.target.value)} className={inputClass} />
              </div>
            </div>
          </div>

          {/* Adresse */}
          <div className="mb-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 border-b pb-1">Adresse</h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="md:col-span-2">
                <label className={labelClass}>Straße *</label>
                <input value={form.strasse} onChange={e => setForm(p => ({...p, strasse: e.target.value}))} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Hausnummer</label>
                <input value={form.hausnummer} onChange={e => setForm(p => ({...p, hausnummer: e.target.value}))} className={inputClass} />
              </div>
              <div></div>
              <div>
                <label className={labelClass}>PLZ *</label>
                <input value={form.plz} onChange={e => setForm(p => ({...p, plz: e.target.value}))} className={inputClass} />
              </div>
              <div className="md:col-span-2">
                <label className={labelClass}>Ort *</label>
                <input value={form.ort} onChange={e => setForm(p => ({...p, ort: e.target.value}))} className={inputClass} />
              </div>
            </div>
          </div>

          {/* Kontakt & Versicherung */}
          <div className="mb-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 border-b pb-1">Kontakt & Versicherung</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className={labelClass}>Telefon</label>
                <input value={form.telefon || ''} onChange={e => handleChange('telefon', e.target.value)} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>E-Mail</label>
                <input type="email" value={form.email || ''} onChange={e => handleChange('email', e.target.value)} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Versicherung</label>
                <input value={form.versicherung || ''} onChange={e => handleChange('versicherung', e.target.value)} placeholder="z.B. Debeka, Allianz" className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Versicherungsnummer</label>
                <input value={form.versicherungsnummer || ''} onChange={e => handleChange('versicherungsnummer', e.target.value)} className={inputClass} />
              </div>
            </div>
          </div>

          {/* Notizen */}
          <div className="mb-5">
            <label className={labelClass}>Notizen</label>
            <textarea value={form.notizen || ''} onChange={e => handleChange('notizen', e.target.value)}
              className={`${inputClass} h-20 resize-none`} placeholder="Interne Notizen..." />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button onClick={() => { setShowForm(false); setEditingPatient(null); }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
              Abbrechen
            </button>
            <button onClick={handleSave} disabled={saving}
              className="inline-flex items-center px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              <Save size={16} className="mr-2" />
              {saving ? 'Speichert...' : editingPatient ? 'Änderungen speichern' : 'Patient anlegen'}
            </button>
          </div>
        </div>
      )}

      {/* ─── Patientenliste ─── */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : filteredPatienten.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <UserPlus size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Noch keine Patienten</h3>
          <p className="text-gray-500 mb-4">Legen Sie Ihren ersten Privatpatienten an.</p>
          <button onClick={openNewForm}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <Plus size={18} className="mr-2" /> Neuer Patient
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredPatienten.map(patient => {
            const isExpanded = expandedId === patient.id;
            return (
              <div key={patient.id}
                className={`bg-white rounded-lg shadow border transition-all ${
                  !patient.aktiv ? 'opacity-60 border-gray-200' : 'border-gray-100 hover:shadow-md'
                }`}
              >
                {/* Karteikarte Header */}
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {patient.titel && <span className="text-gray-500">{patient.titel} </span>}
                          {patient.nachname}, {patient.vorname}
                        </h3>
                        {!patient.aktiv && (
                          <span className="inline-flex px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-100 text-red-700">Inaktiv</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 mt-0.5">
                        {patient.anrede} · geb. {formatDate(patient.geburtsdatum)}
                      </p>
                      {patient.aufnahme_datum && (
                        <p className="text-xs text-blue-600 mt-0.5">
                          Aufnahme: {formatDate(patient.aufnahme_datum)}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-1 ml-2 flex-shrink-0">
                      <button onClick={() => openEditForm(patient)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors" title="Bearbeiten">
                        <Edit2 size={14} />
                      </button>
                      {patient.aktiv && (
                        <button onClick={() => handleDelete(patient.id)}
                          className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Deaktivieren">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Kurzinfo */}
                  <div className="mt-3 text-sm text-gray-600">
                    <p className="truncate">{patient.strasse} {patient.hausnummer}, {patient.plz} {patient.ort}</p>
                  </div>

                  {/* Expandieren */}
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : patient.id)}
                    className="mt-2 text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                    {isExpanded ? 'Weniger' : 'Details'}
                  </button>
                </div>

                {/* Details (ausgeklappt) */}
                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-100 pt-3 text-sm space-y-1.5">
                    {patient.telefon && (
                      <div className="flex justify-between"><span className="text-gray-500">Telefon</span><span>{patient.telefon}</span></div>
                    )}
                    {patient.email && (
                      <div className="flex justify-between"><span className="text-gray-500">E-Mail</span><span className="text-blue-600">{patient.email}</span></div>
                    )}
                    {patient.versicherung && (
                      <div className="flex justify-between"><span className="text-gray-500">Versicherung</span><span>{patient.versicherung}</span></div>
                    )}
                    {patient.versicherungsnummer && (
                      <div className="flex justify-between"><span className="text-gray-500">Vers.-Nr.</span><span className="font-mono">{patient.versicherungsnummer}</span></div>
                    )}
                    {patient.notizen && (
                      <div className="mt-2 p-2 bg-yellow-50 rounded text-xs text-gray-700 italic">{patient.notizen}</div>
                    )}
                    <div className="flex justify-between text-xs text-gray-400 pt-1">
                      <span>Angelegt: {formatDate(patient.created_at)}</span>
                      {patient.updated_at && <span>Geändert: {formatDate(patient.updated_at)}</span>}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Count */}
      {!loading && filteredPatienten.length > 0 && (
        <p className="text-sm text-gray-500 mt-4 text-center">
          {filteredPatienten.length} {filteredPatienten.length === 1 ? 'Patient' : 'Patienten'}
        </p>
      )}
    </div>
  );
};

export default Patienten;
