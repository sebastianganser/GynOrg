/**
 * API-Service für das GOÄ-Rechnungsmodul.
 * Bündelt alle Aufrufe für Rechnungen, Patienten, GOÄ-Ziffern und Praxiseinstellungen.
 */
import { api } from './api';
import {
  GoaeZiffer, GoaeAbschnitt,
  Patient, PatientCreate, PatientUpdate,
  Rechnung, RechnungCreate, RechnungUpdate,
  RechnungsDokument,
  PraxisEinstellungen, PraxisEinstellungenUpdate,
} from '../types/rechnung';

// ─── GOÄ-Ziffern ─────────────────────────────────────

export const goaeService = {
  async suche(q: string = '', abschnitt?: string, limit: number = 20): Promise<GoaeZiffer[]> {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (abschnitt) params.set('abschnitt', abschnitt);
    params.set('limit', String(limit));
    const res = await api.get<GoaeZiffer[]>(`/goae/suche?${params}`);
    return res.data;
  },

  async getZiffer(ziffer: string): Promise<GoaeZiffer> {
    const res = await api.get<GoaeZiffer>(`/goae/ziffer/${ziffer}`);
    return res.data;
  },

  async getAbschnitte(): Promise<GoaeAbschnitt[]> {
    const res = await api.get<GoaeAbschnitt[]>('/goae/abschnitte');
    return res.data;
  },

  async getImportStatus(): Promise<{ total: number; aktive: number; letztes_update: string | null }> {
    const res = await api.get<{ total: number; aktive: number; letztes_update: string | null }>('/goae/import-status');
    return res.data;
  },

  async triggerImport(): Promise<{ success: boolean; message: string; total: number }> {
    const res = await api.post<{ success: boolean; message: string; total: number }>('/goae/import');
    return res.data;
  },
};

// ─── Patienten ────────────────────────────────────────

export const patientenService = {
  async getAll(nurAktive: boolean = true): Promise<Patient[]> {
    const res = await api.get<Patient[]>(`/patienten/?nur_aktive=${nurAktive}`);
    return res.data;
  },

  async suche(q: string): Promise<Patient[]> {
    const res = await api.get<Patient[]>(`/patienten/suche?q=${encodeURIComponent(q)}`);
    return res.data;
  },

  async getAktuelle(tage: number = 30): Promise<Patient[]> {
    const res = await api.get<Patient[]>(`/patienten/aktuell?tage=${tage}`);
    return res.data;
  },

  async getById(id: number): Promise<Patient> {
    const res = await api.get<Patient>(`/patienten/${id}`);
    return res.data;
  },

  async create(data: PatientCreate): Promise<Patient> {
    const res = await api.post<Patient>('/patienten/', data);
    return res.data;
  },

  async update(id: number, data: PatientUpdate): Promise<Patient> {
    const res = await api.put<Patient>(`/patienten/${id}`, data);
    return res.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/patienten/${id}`);
  },
};

// ─── Rechnungen ───────────────────────────────────────

export const rechnungService = {
  async getAll(params?: {
    status?: string;
    patient_id?: number;
    jahr?: number;
  }): Promise<Rechnung[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.patient_id) searchParams.set('patient_id', String(params.patient_id));
    if (params?.jahr) searchParams.set('jahr', String(params.jahr));
    const res = await api.get<Rechnung[]>(`/rechnungen/?${searchParams}`);
    return res.data;
  },

  async getById(id: number): Promise<Rechnung> {
    const res = await api.get<Rechnung>(`/rechnungen/${id}`);
    return res.data;
  },

  async create(data: RechnungCreate): Promise<Rechnung> {
    const res = await api.post<Rechnung>('/rechnungen/', data);
    return res.data;
  },

  async update(id: number, data: RechnungUpdate): Promise<Rechnung> {
    const res = await api.put<Rechnung>(`/rechnungen/${id}`, data);
    return res.data;
  },

  async stellen(id: number): Promise<Rechnung> {
    const res = await api.post<Rechnung>(`/rechnungen/${id}/stellen`);
    return res.data;
  },

  async bezahlt(id: number, datum?: string): Promise<Rechnung> {
    const params = datum ? `?datum=${datum}` : '';
    const res = await api.post<Rechnung>(`/rechnungen/${id}/bezahlt${params}`);
    return res.data;
  },

  async stornieren(id: number, grund: string): Promise<Rechnung> {
    const res = await api.post<Rechnung>(
      `/rechnungen/${id}/stornieren?grund=${encodeURIComponent(grund)}`
    );
    return res.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/rechnungen/${id}`);
  },

  async generatePdf(id: number): Promise<RechnungsDokument> {
    const res = await api.post<RechnungsDokument>(`/rechnungen/${id}/pdf`);
    return res.data;
  },

  getPdfDownloadUrl(id: number, version?: number): string {
    const params = version ? `?version=${version}` : '';
    return `/rechnungen/${id}/pdf/download${params}`;
  },

  async exportCsv(jahrVon: number, jahrBis: number): Promise<Blob> {
    const url = `/rechnungen/export/csv?jahr_von=${jahrVon}&jahr_bis=${jahrBis}`;
    const response = await fetch(`${api['baseURL'] || ''}${url}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
    });
    return response.blob();
  },
};

// ─── Praxiseinstellungen ──────────────────────────────

export const praxisEinstellungenService = {
  async get(): Promise<PraxisEinstellungen> {
    const res = await api.get<PraxisEinstellungen>('/praxis-einstellungen/');
    return res.data;
  },

  async update(data: PraxisEinstellungenUpdate): Promise<PraxisEinstellungen> {
    const res = await api.put<PraxisEinstellungen>('/praxis-einstellungen/', data);
    return res.data;
  },
};
