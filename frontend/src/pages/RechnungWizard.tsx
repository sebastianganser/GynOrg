import React, { useState, useEffect, useCallback } from 'react';
import {
  ArrowLeft, Check, Search, Trash2, AlertCircle,
  UserPlus, Clock, FileText, Save, Plus
} from 'lucide-react';
import { goaeService, patientenService, rechnungService } from '../services/rechnungService';
import {
  GoaeZiffer, GoaeAbschnitt, Patient, Rechnung,
  RechnungsPositionCreate, RechnungCreate, RechnungUpdate,
  GOAE_PUNKTWERT, berechnePosition,
} from '../types/rechnung';

interface RechnungWizardProps {
  onComplete: () => void;
  onCancel: () => void;
  onNavigateToPatienten?: () => void;
  /** Wenn gesetzt, wird direkt der Editor für diese Rechnung geöffnet */
  editRechnungId?: number;
}

type Phase = 'patient-selection' | 'editor';

const RechnungWizard: React.FC<RechnungWizardProps> = ({
  onComplete, onCancel, onNavigateToPatienten, editRechnungId
}) => {
  const [phase, setPhase] = useState<Phase>(editRechnungId ? 'editor' : 'patient-selection');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // ─── Phase 1: Patient auswählen ───
  const [patientSearch, setPatientSearch] = useState('');
  const [searchResults, setSearchResults] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [recentPatients, setRecentPatients] = useState<Patient[]>([]);
  const [creating, setCreating] = useState(false);

  // ─── Phase 2: Editor-Daten ───
  const [draftId, setDraftId] = useState<number | null>(editRechnungId || null);
  const [rechnungsnummer, setRechnungsnummer] = useState('');
  const [rechnungsdatum, setRechnungsdatum] = useState(new Date().toISOString().split('T')[0]);
  const [leistungszeitraumVon, setLeistungszeitraumVon] = useState(new Date().toISOString().split('T')[0]);
  const [leistungszeitraumBis, setLeistungszeitraumBis] = useState(new Date().toISOString().split('T')[0]);
  const [diagnose, setDiagnose] = useState('');
  const [zahlungszielTage, setZahlungszielTage] = useState(30);
  const [notizen, setNotizen] = useState('');

  // ─── GOÄ-Positionen ───
  const [goaeSearch, setGoaeSearch] = useState('');
  const [goaeResults, setGoaeResults] = useState<GoaeZiffer[]>([]);
  const [abschnitte, setAbschnitte] = useState<GoaeAbschnitt[]>([]);
  const [selectedAbschnitte, setSelectedAbschnitte] = useState<string[]>([]);
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [positionen, setPositionen] = useState<RechnungsPositionCreate[]>([]);

  // ─── Patienten-Suche ───
  useEffect(() => {
    if (patientSearch.length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const results = await patientenService.suche(patientSearch);
        setSearchResults(results);
      } catch (e) { /* ignore */ }
    }, 300);
    return () => clearTimeout(timer);
  }, [patientSearch]);

  // ─── Aktuelle Patienten laden ───
  useEffect(() => {
    const loadRecent = async () => {
      try {
        const results = await patientenService.getAktuelle(30);
        setRecentPatients(results);
      } catch (e) { /* ignore */ }
    };
    loadRecent();
  }, []);

  // ─── Bestehende Rechnung laden (Edit-Modus) ───
  useEffect(() => {
    if (!editRechnungId) return;
    const loadDraft = async () => {
      try {
        const r = await rechnungService.getById(editRechnungId);
        setDraftId(r.id);
        setRechnungsnummer(r.rechnungsnummer);
        setRechnungsdatum(r.rechnungsdatum);
        setLeistungszeitraumVon(r.leistungszeitraum_von);
        setLeistungszeitraumBis(r.leistungszeitraum_bis);
        setDiagnose(r.diagnose || '');
        setZahlungszielTage(r.zahlungsziel_tage);
        setNotizen(r.notizen || '');
        setPositionen(r.positionen.map(p => ({
          goae_ziffer: p.goae_ziffer,
          beschreibung: p.beschreibung,
          datum: p.datum,
          anzahl: p.anzahl,
          punkte: p.punkte,
          faktor: p.faktor,
          betrag: p.betrag,
          begruendung: p.begruendung,
        })));
        // Patient laden
        const pat = await patientenService.getById(r.patient_id);
        setSelectedPatient(pat);
      } catch (e: any) {
        setError('Rechnung konnte nicht geladen werden');
      }
    };
    loadDraft();
  }, [editRechnungId]);

  // ─── Abschnitte laden ───
  useEffect(() => {
    const loadAbschnitte = async () => {
      try {
        const data = await goaeService.getAbschnitte();
        setAbschnitte(data);
      } catch (e) { /* ignore */ }
    };
    loadAbschnitte();
  }, []);

  // ─── GOÄ-Suche ───
  useEffect(() => {
    if (goaeSearch.length < 1 && selectedAbschnitte.length === 0) {
      setGoaeResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const results = await goaeService.suche(
          goaeSearch,
          selectedAbschnitte.length > 0 ? selectedAbschnitte.join(',') : undefined,
          20
        );
        setGoaeResults(results);
      } catch (e) { /* ignore */ }
    }, 300);
    return () => clearTimeout(timer);
  }, [goaeSearch, selectedAbschnitte]);

  // ─── GOÄ-Position hinzufügen ───
  const addPosition = (ziffer: GoaeZiffer) => {
    const faktor = Number(ziffer.faktor_regelhöchst);
    const betrag = berechnePosition(ziffer.punkte, faktor, 1);
    setPositionen(prev => [...prev, {
      goae_ziffer: ziffer.ziffer,
      beschreibung: ziffer.beschreibung,
      datum: new Date().toISOString().split('T')[0],
      anzahl: 1,
      punkte: ziffer.punkte,
      faktor: faktor,
      betrag: betrag,
    }]);
    setGoaeSearch('');
    setGoaeResults([]);
  };

  // ─── Position aktualisieren ───
  const updatePosition = (index: number, field: string, value: any) => {
    const updated = [...positionen];
    (updated[index] as any)[field] = value;
    if (['faktor', 'anzahl', 'punkte'].includes(field)) {
      updated[index].betrag = berechnePosition(
        updated[index].punkte,
        Number(updated[index].faktor),
        updated[index].anzahl
      );
    }
    setPositionen(updated);
  };

  // ─── Position entfernen ───
  const removePosition = (index: number) => {
    setPositionen(positionen.filter((_, i) => i !== index));
  };

  // ─── Gesamtbetrag ───
  const gesamtbetrag = positionen.reduce((sum, p) => sum + p.betrag, 0);

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val);

  // ═══════════════════════════════════════════════════════
  // ─── Neue Rechnung als Entwurf erstellen ───
  // ═══════════════════════════════════════════════════════
  const handleCreateDraft = async () => {
    if (!selectedPatient) return;
    setCreating(true);
    setError('');
    try {
      const data: RechnungCreate = {
        patient_id: selectedPatient.id,
        rechnungsdatum,
        leistungszeitraum_von: leistungszeitraumVon,
        leistungszeitraum_bis: leistungszeitraumBis,
        diagnose: '-', // Platzhalter, wird im Editor ausgefüllt
        zahlungsziel_tage: zahlungszielTage,
        positionen: [],
      };
      const created = await rechnungService.create(data);
      setDraftId(created.id);
      setRechnungsnummer(created.rechnungsnummer);
      setDiagnose(created.diagnose || '');
      setPhase('editor');
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.data?.detail || 'Fehler beim Erstellen');
    } finally {
      setCreating(false);
    }
  };

  // ═══════════════════════════════════════════════════════
  // ─── Entwurf speichern (Update) ───
  // ═══════════════════════════════════════════════════════
  const handleSaveDraft = async () => {
    if (!draftId) return;
    setSaving(true);
    setError('');
    setSuccessMsg('');
    try {
      const data: RechnungUpdate = {
        rechnungsdatum,
        leistungszeitraum_von: leistungszeitraumVon,
        leistungszeitraum_bis: leistungszeitraumBis,
        diagnose,
        zahlungsziel_tage: zahlungszielTage,
        notizen: notizen || null,
        positionen,
      };
      await rechnungService.update(draftId, data);
      setSuccessMsg('Änderungen gespeichert');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.data?.detail || 'Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  // ═══════════════════════════════════════════════════════
  // ─── RENDER ───
  // ═══════════════════════════════════════════════════════

  // ─── Phase 1: Patient auswählen ───
  if (phase === 'patient-selection') {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Neue Rechnung erstellen</h2>
            <p className="text-sm text-gray-500">Wählen Sie einen Patienten aus</p>
          </div>
          <button onClick={onCancel} className="text-gray-500 hover:text-gray-700 text-sm">
            Abbrechen
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
            <AlertCircle size={16} /> {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-4">Patient auswählen</h3>

          {selectedPatient ? (
            /* Patient ausgewählt → Zusammenfassung */
            <div className="border border-green-200 bg-green-50 rounded-lg p-4 flex items-center justify-between mb-4">
              <div>
                <span className="font-medium">
                  {selectedPatient.anrede} {selectedPatient.titel && `${selectedPatient.titel} `}
                  {selectedPatient.vorname} {selectedPatient.nachname}
                </span>
                <span className="text-gray-500 ml-2">· geb. {new Date(selectedPatient.geburtsdatum).toLocaleDateString('de-DE')}</span>
                {selectedPatient.aufnahme_datum && (
                  <span className="text-blue-500 ml-2 text-sm">
                    · Aufnahme: {new Date(selectedPatient.aufnahme_datum).toLocaleDateString('de-DE')}
                  </span>
                )}
                <div className="text-sm text-gray-500">
                  {selectedPatient.strasse} {selectedPatient.hausnummer}, {selectedPatient.plz} {selectedPatient.ort}
                </div>
              </div>
              <button
                onClick={() => setSelectedPatient(null)}
                className="text-sm text-blue-600 hover:underline"
              >
                Ändern
              </button>
            </div>
          ) : (
            <>
              {/* Suchfeld */}
              <div className="relative mb-4">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Patient nach Name suchen..."
                  value={patientSearch}
                  onChange={e => setPatientSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  id="input-patient-suche"
                  autoFocus
                />
              </div>

              {/* Suchergebnisse */}
              {searchResults.length > 0 && (
                <ul className="border border-gray-200 rounded-lg divide-y mb-4 max-h-60 overflow-auto">
                  {searchResults.map(p => (
                    <li key={p.id}>
                      <button
                        onClick={() => { setSelectedPatient(p); setPatientSearch(''); setSearchResults([]); }}
                        className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors"
                      >
                        <span className="font-medium">{p.nachname}, {p.vorname}</span>
                        <span className="text-gray-500 ml-2">· geb. {new Date(p.geburtsdatum).toLocaleDateString('de-DE')}</span>
                        {p.aufnahme_datum && (
                          <span className="text-blue-500 ml-2 text-sm">· Aufnahme: {new Date(p.aufnahme_datum).toLocaleDateString('de-DE')}</span>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {/* Aktuelle Patienten (Aufnahme <30 Tage) */}
              {searchResults.length === 0 && recentPatients.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Clock size={14} />
                    Aktuelle Patienten
                    <span className="text-xs font-normal normal-case text-gray-400">(Aufnahme in den letzten 30 Tagen)</span>
                  </h4>
                  <ul className="border border-blue-100 bg-blue-50/30 rounded-lg divide-y divide-blue-100">
                    {recentPatients.map(p => (
                      <li key={p.id}>
                        <button
                          onClick={() => { setSelectedPatient(p); setPatientSearch(''); setSearchResults([]); }}
                          className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="font-medium text-gray-900">{p.nachname}, {p.vorname}</span>
                              <span className="text-gray-500 ml-2 text-sm">· geb. {new Date(p.geburtsdatum).toLocaleDateString('de-DE')}</span>
                            </div>
                            <span className="text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">
                              Aufnahme: {new Date(p.aufnahme_datum!).toLocaleDateString('de-DE')}
                            </span>
                          </div>
                          <div className="text-sm text-gray-500 mt-0.5">
                            {p.strasse} {p.hausnummer}, {p.plz} {p.ort}
                          </div>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Hinweis: Neuen Patienten in Patientenverwaltung anlegen */}
              <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  <UserPlus size={16} className="inline mr-1.5 text-gray-400" />
                  Patient noch nicht angelegt?
                </div>
                {onNavigateToPatienten ? (
                  <button
                    onClick={onNavigateToPatienten}
                    className="text-sm text-blue-600 hover:underline font-medium"
                  >
                    Zur Patientenverwaltung →
                  </button>
                ) : (
                  <span className="text-sm text-gray-500">Bitte zuerst in der Patientenverwaltung anlegen.</span>
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer: Abbrechen / Neue Rechnung erstellen */}
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={onCancel}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            <ArrowLeft size={16} className="mr-2" />
            Abbrechen
          </button>

          <button
            onClick={handleCreateDraft}
            disabled={!selectedPatient || creating}
            className="inline-flex items-center px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
          >
            {creating ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <FileText size={16} className="mr-2" />
            )}
            Neue Rechnung erstellen
          </button>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════
  // ─── Phase 2: Rechnungs-Editor (Rechnungsdaten + Positionen) ───
  // ═══════════════════════════════════════════════════════
  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Rechnung bearbeiten
            {rechnungsnummer && (
              <span className="text-lg font-normal text-gray-400 ml-3">#{rechnungsnummer}</span>
            )}
          </h2>
          {selectedPatient && (
            <p className="text-sm text-gray-500">
              {selectedPatient.anrede} {selectedPatient.titel && `${selectedPatient.titel} `}
              {selectedPatient.vorname} {selectedPatient.nachname}
              <span className="mx-1">·</span>
              geb. {new Date(selectedPatient.geburtsdatum).toLocaleDateString('de-DE')}
              {selectedPatient.aufnahme_datum && (
                <>
                  <span className="mx-1">·</span>
                  <span className="text-blue-600">Aufnahme: {new Date(selectedPatient.aufnahme_datum).toLocaleDateString('de-DE')}</span>
                </>
              )}
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs px-2.5 py-1 bg-yellow-100 text-yellow-800 rounded-full font-medium">
            Entwurf
          </span>
          <button onClick={onComplete} className="text-gray-500 hover:text-gray-700 text-sm">
            Schließen
          </button>
        </div>
      </div>

      {/* Status-Meldungen */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
          <AlertCircle size={16} /> {error}
        </div>
      )}
      {successMsg && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
          <Check size={16} /> {successMsg}
        </div>
      )}

      {/* ─── Rechnungsdaten ─── */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-medium mb-4 text-gray-900">Rechnungsdaten</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Rechnungsdatum</label>
            <input type="date" value={rechnungsdatum} onChange={e => setRechnungsdatum(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Zahlungsziel (Tage)</label>
            <input type="number" value={zahlungszielTage} onChange={e => setZahlungszielTage(Number(e.target.value))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2" min={7} max={90} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Leistungszeitraum von</label>
            <input type="date" value={leistungszeitraumVon} onChange={e => setLeistungszeitraumVon(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Leistungszeitraum bis</label>
            <input type="date" value={leistungszeitraumBis} onChange={e => setLeistungszeitraumBis(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2" />
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Diagnose</label>
            <textarea value={diagnose} onChange={e => setDiagnose(e.target.value)}
              placeholder="z.B. Z01.4 Gynäkologische Untersuchung ..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 h-20 resize-none focus:ring-2 focus:ring-blue-500"
              id="input-diagnose" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notizen (intern)</label>
            <textarea value={notizen} onChange={e => setNotizen(e.target.value)}
              placeholder="Interne Notizen zur Rechnung..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 h-20 resize-none" />
          </div>
        </div>
      </div>

      {/* ─── GOÄ-Leistungspositionen ─── */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            GOÄ-Leistungspositionen
            {positionen.length > 0 && (
              <span className="text-sm font-normal text-gray-400 ml-2">({positionen.length} Position{positionen.length !== 1 ? 'en' : ''})</span>
            )}
          </h3>
          <div className="text-right">
            <span className="text-sm text-gray-500">Gesamtbetrag</span>
            <div className="text-xl font-bold text-gray-900">{formatCurrency(gesamtbetrag)}</div>
          </div>
        </div>

        {/* GOÄ-Suche + Abschnitt-Filter */}
        <div className="mb-4">
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="GOÄ-Ziffer oder Leistungstext suchen..."
                value={goaeSearch}
                onChange={e => setGoaeSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                id="input-goae-suche"
              />
            </div>
            <button
              onClick={() => setShowFilterPanel(!showFilterPanel)}
              className={`inline-flex items-center gap-1.5 px-3 py-2.5 border rounded-lg text-sm font-medium transition-colors ${
                selectedAbschnitte.length > 0
                  ? 'border-blue-300 bg-blue-50 text-blue-700'
                  : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                <path d="M2 4h12M4 8h8M6 12h4" />
              </svg>
              Filter
              {selectedAbschnitte.length > 0 && (
                <span className="bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {selectedAbschnitte.length}
                </span>
              )}
            </button>
          </div>

          {/* Aktive Filter-Badges */}
          {selectedAbschnitte.length > 0 && (
            <div className="mt-2 flex items-center gap-1.5 flex-wrap">
              {selectedAbschnitte.map(key => (
                <span key={key} className="inline-flex items-center gap-1 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                  {key}: {abschnitte.find(a => a.key === key)?.label}
                  <button
                    onClick={() => setSelectedAbschnitte(prev => prev.filter(k => k !== key))}
                    className="hover:text-blue-900 ml-0.5"
                  >
                    ×
                  </button>
                </span>
              ))}
              <button
                onClick={() => setSelectedAbschnitte([])}
                className="text-xs text-gray-400 hover:text-gray-600 underline ml-1"
              >
                alle zurücksetzen
              </button>
            </div>
          )}

          {/* Filter-Panel mit Checkboxen */}
          {showFilterPanel && (
            <div className="mt-2 border border-gray-200 rounded-lg bg-gray-50 p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Abschnitte filtern</span>
                <button
                  onClick={() => setShowFilterPanel(false)}
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  schließen
                </button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                {abschnitte.map(a => (
                  <label
                    key={a.key}
                    className={`flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer text-sm transition-colors ${
                      selectedAbschnitte.includes(a.key)
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedAbschnitte.includes(a.key)}
                      onChange={e => {
                        if (e.target.checked) {
                          setSelectedAbschnitte(prev => [...prev, a.key]);
                        } else {
                          setSelectedAbschnitte(prev => prev.filter(k => k !== a.key));
                        }
                      }}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="font-medium min-w-[4ch]">{a.key}:</span>
                    <span className="truncate">{a.label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* GOÄ-Suchergebnisse */}
        {goaeResults.length > 0 && (
          <ul className="border border-blue-200 bg-blue-50/30 rounded-lg divide-y divide-blue-100 mb-4 max-h-80 overflow-auto">
            {goaeResults.map(z => (
              <li key={z.id}>
                <button
                  onClick={() => addPosition(z)}
                  className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <Plus size={14} className="text-blue-500 flex-shrink-0" />
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-bold text-blue-600">GOÄ {z.ziffer}</span>
                          <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                            {z.abschnitt_label || z.abschnitt}
                          </span>
                        </div>
                        <div className="text-gray-700 text-sm mt-0.5">{z.beschreibung}</div>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500 flex-shrink-0 ml-4">
                      <div>{z.punkte} Pkt · ×{z.faktor_regelhöchst}</div>
                      <div className="font-medium text-gray-900">{formatCurrency(z.regelhoechstsatz)}</div>
                    </div>
                  </div>
                  {/* Ausschlussziffern & Hinweistext */}
                  {(z.ausschlussziffern || z.hinweistext) && (
                    <div className="mt-1.5 pl-6 space-y-1">
                      {z.ausschlussziffern && (
                        <div className="text-xs text-orange-600">
                          ⚠ Ausschluss: GOÄ {z.ausschlussziffern}
                        </div>
                      )}
                      {z.hinweistext && (
                        <div className="text-xs text-gray-500 italic line-clamp-2">
                          {z.hinweistext}
                        </div>
                      )}
                    </div>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}

        {/* Positionen-Tabelle */}
        {positionen.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-2.5 px-3 font-medium text-gray-600">Ziffer</th>
                  <th className="text-left py-2.5 px-3 font-medium text-gray-600">Beschreibung</th>
                  <th className="text-left py-2.5 px-3 font-medium text-gray-600 w-28">Datum</th>
                  <th className="text-center py-2.5 px-3 font-medium text-gray-600 w-16">Anz.</th>
                  <th className="text-right py-2.5 px-3 font-medium text-gray-600 w-16">Pkt.</th>
                  <th className="text-center py-2.5 px-3 font-medium text-gray-600 w-20">Faktor</th>
                  <th className="text-right py-2.5 px-3 font-medium text-gray-600 w-24">Betrag</th>
                  <th className="w-10"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {positionen.map((pos, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-mono font-bold text-blue-600">{pos.goae_ziffer}</td>
                    <td className="py-2.5 px-3 text-gray-700 max-w-xs truncate">{pos.beschreibung}</td>
                    <td className="py-2.5 px-3">
                      <input type="date" value={pos.datum}
                        onChange={e => updatePosition(i, 'datum', e.target.value)}
                        className="w-full border border-gray-200 rounded px-1.5 py-1 text-sm" />
                    </td>
                    <td className="py-2.5 px-3">
                      <input type="number" value={pos.anzahl} min={1}
                        onChange={e => updatePosition(i, 'anzahl', Number(e.target.value))}
                        className="w-full text-center border border-gray-200 rounded px-1.5 py-1" />
                    </td>
                    <td className="py-2.5 px-3 text-right text-gray-500">{pos.punkte}</td>
                    <td className="py-2.5 px-3">
                      <input type="number" value={pos.faktor} step="0.1" min="0.1"
                        onChange={e => updatePosition(i, 'faktor', Number(e.target.value))}
                        className="w-full text-center border border-gray-200 rounded px-1.5 py-1" />
                    </td>
                    <td className="py-2.5 px-3 text-right font-medium">{formatCurrency(pos.betrag)}</td>
                    <td className="py-2.5 px-3">
                      <button onClick={() => removePosition(i)} className="text-red-400 hover:text-red-600">
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-gray-300 font-bold">
                  <td colSpan={6} className="py-3 px-3 text-right">Gesamtbetrag:</td>
                  <td className="py-3 px-3 text-right text-lg">{formatCurrency(gesamtbetrag)}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
        ) : (
          <div className="text-center py-10 text-gray-400 border-2 border-dashed border-gray-200 rounded-lg">
            <Search size={32} className="mx-auto mb-2 text-gray-300" />
            <p className="font-medium">Noch keine Positionen hinzugefügt</p>
            <p className="text-sm mt-1">Suchen Sie oben nach GOÄ-Ziffern, um Leistungspositionen hinzuzufügen.</p>
            <p className="text-sm text-gray-400 mt-1">Positionen können jederzeit ergänzt werden.</p>
          </div>
        )}
      </div>

      {/* ─── Footer: Aktionen ─── */}
      <div className="flex items-center justify-between">
        <button
          onClick={onComplete}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          <ArrowLeft size={16} className="mr-2" />
          Zurück zur Übersicht
        </button>

        <button
          onClick={handleSaveDraft}
          disabled={saving}
          className="inline-flex items-center px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium shadow-sm"
        >
          {saving ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <Save size={16} className="mr-2" />
          )}
          Änderungen speichern
        </button>
      </div>
    </div>
  );
};

export default RechnungWizard;
