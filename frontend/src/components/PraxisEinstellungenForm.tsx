import React, { useState, useEffect } from 'react';
import { Save, Loader2, CheckCircle } from 'lucide-react';
import { praxisEinstellungenService } from '../services/rechnungService';
import { PraxisEinstellungen, PraxisEinstellungenUpdate } from '../types/rechnung';

/**
 * Praxiseinstellungen-Formular für den Settings-Bereich
 * "Modul: Rechnungslegung".
 * 
 * Der Nutzer kann hier seine Kontakt- und Bankdaten eigenständig pflegen.
 */
const PraxisEinstellungenForm: React.FC = () => {
  const [settings, setSettings] = useState<PraxisEinstellungen | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [form, setForm] = useState<PraxisEinstellungenUpdate>({});

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await praxisEinstellungenService.get();
      setSettings(data);
      setForm(data);
    } catch (err) {
      console.error('Fehler beim Laden der Praxiseinstellungen:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof PraxisEinstellungenUpdate, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSaved(false);
    try {
      const updated = await praxisEinstellungenService.update(form);
      setSettings(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err?.data?.detail || 'Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 size={24} className="animate-spin text-blue-600" />
      </div>
    );
  }

  const inputClass = "w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <div className="space-y-6">
      {/* Arzt / Leistungserbringer */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Arzt / Leistungserbringer</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className={labelClass}>Titel</label>
            <input value={form.arzt_titel || ''} onChange={e => handleChange('arzt_titel', e.target.value || null)}
              placeholder="z.B. Dr. med." className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Vorname *</label>
            <input value={form.arzt_vorname || ''} onChange={e => handleChange('arzt_vorname', e.target.value)}
              className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Nachname *</label>
            <input value={form.arzt_nachname || ''} onChange={e => handleChange('arzt_nachname', e.target.value)}
              className={inputClass} />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
          <div>
            <label className={labelClass}>Fachrichtung</label>
            <input value={form.fachrichtung || ''} onChange={e => handleChange('fachrichtung', e.target.value)}
              placeholder="z.B. Fachärztin für Gynäkologie und Geburtshilfe" className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Praxisbezeichnung</label>
            <input value={form.praxis_name || ''} onChange={e => handleChange('praxis_name', e.target.value || null)}
              placeholder="(optional, falls abweichend)" className={inputClass} />
          </div>
        </div>
      </div>

      {/* Adresse */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Praxisadresse</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className={labelClass}>Straße</label>
            <input value={form.strasse || ''} onChange={e => handleChange('strasse', e.target.value)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Hausnummer</label>
            <input value={form.hausnummer || ''} onChange={e => handleChange('hausnummer', e.target.value)} className={inputClass} />
          </div>
          <div></div>
          <div>
            <label className={labelClass}>PLZ</label>
            <input value={form.plz || ''} onChange={e => handleChange('plz', e.target.value)} className={inputClass} />
          </div>
          <div className="md:col-span-2">
            <label className={labelClass}>Ort</label>
            <input value={form.ort || ''} onChange={e => handleChange('ort', e.target.value)} className={inputClass} />
          </div>
        </div>
      </div>

      {/* Kontakt */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Kontaktdaten</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Telefon</label>
            <input value={form.telefon || ''} onChange={e => handleChange('telefon', e.target.value)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Fax</label>
            <input value={form.fax || ''} onChange={e => handleChange('fax', e.target.value || null)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>E-Mail</label>
            <input type="email" value={form.email || ''} onChange={e => handleChange('email', e.target.value)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Website</label>
            <input value={form.website || ''} onChange={e => handleChange('website', e.target.value || null)} className={inputClass} />
          </div>
        </div>
      </div>

      {/* Abrechnung */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Abrechnungsdaten</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>LANR (Lebenslange Arztnummer)</label>
            <input value={form.lanr || ''} onChange={e => handleChange('lanr', e.target.value || null)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Steuernummer / USt-IdNr.</label>
            <input value={form.steuernummer || ''} onChange={e => handleChange('steuernummer', e.target.value || null)} className={inputClass} />
          </div>
        </div>
        <div className="mt-3">
          <label className="flex items-center space-x-2">
            <input type="checkbox" checked={form.ust_befreit ?? true}
              onChange={e => handleChange('ust_befreit', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            <span className="text-sm text-gray-700">Umsatzsteuerbefreit gem. §4 Nr. 14 UStG (Standard für ärztliche Leistungen)</span>
          </label>
        </div>
      </div>

      {/* Bankverbindung */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Bankverbindung</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Bank</label>
            <input value={form.bank_name || ''} onChange={e => handleChange('bank_name', e.target.value)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Kontoinhaber (falls abweichend)</label>
            <input value={form.kontoinhaber || ''} onChange={e => handleChange('kontoinhaber', e.target.value || null)}
              placeholder="(optional)" className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>IBAN</label>
            <input value={form.iban || ''} onChange={e => handleChange('iban', e.target.value)}
              placeholder="DE00 0000 0000 0000 0000 00" className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>BIC</label>
            <input value={form.bic || ''} onChange={e => handleChange('bic', e.target.value || null)} className={inputClass} />
          </div>
        </div>
      </div>

      {/* Rechnungs-Defaults */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Rechnungs-Einstellungen</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className={labelClass}>Rechnungsnummer-Präfix</label>
            <input value={form.rechnungsnummer_praefix || 'RE'} onChange={e => handleChange('rechnungsnummer_praefix', e.target.value)}
              className={inputClass} />
            <p className="text-xs text-gray-500 mt-1">Beispiel: {form.rechnungsnummer_praefix || 'RE'}-2026-0001</p>
          </div>
          <div>
            <label className={labelClass}>Nächste Rechnungsnummer</label>
            <input type="number" value={form.naechste_rechnungsnummer || 1} min={1}
              onChange={e => handleChange('naechste_rechnungsnummer', Number(e.target.value))} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Standard-Zahlungsziel (Tage)</label>
            <input type="number" value={form.standard_zahlungsziel_tage || 30} min={7} max={90}
              onChange={e => handleChange('standard_zahlungsziel_tage', Number(e.target.value))} className={inputClass} />
          </div>
        </div>
      </div>

      {/* Speichern */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
        >
          {saving ? (
            <Loader2 size={16} className="mr-2 animate-spin" />
          ) : saved ? (
            <CheckCircle size={16} className="mr-2 text-green-300" />
          ) : (
            <Save size={16} className="mr-2" />
          )}
          {saved ? 'Gespeichert!' : 'Einstellungen speichern'}
        </button>
      </div>
    </div>
  );
};

export default PraxisEinstellungenForm;
