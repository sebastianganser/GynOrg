/**
 * TypeScript-Typen für das GOÄ-Rechnungsmodul.
 */

// ─── Enums ────────────────────────────────────────────
export type RechnungStatus = 'entwurf' | 'gestellt' | 'bezahlt' | 'storniert';
export type Anrede = 'Herr' | 'Frau' | 'Divers';

// ─── GOÄ-Ziffer ───────────────────────────────────────
export interface GoaeZiffer {
  id: number;
  ziffer: string;
  beschreibung: string;
  punkte: number;
  abschnitt: string;
  abschnitt_label?: string;
  faktor_regelhöchst: number;
  faktor_höchst: number;
  aktiv: boolean;
  einfachsatz: number;
  regelhoechstsatz: number;
  hoechstsatz: number;
  ausschlussziffern: string | null;
  hinweistext: string | null;
  detail_url: string | null;
}

export interface GoaeAbschnitt {
  key: string;
  label: string;
}

// ─── Patient ──────────────────────────────────────────
export interface Patient {
  id: number;
  anrede: Anrede;
  titel: string | null;
  vorname: string;
  nachname: string;
  geburtsdatum: string;
  strasse: string;
  hausnummer: string;
  plz: string;
  ort: string;
  telefon: string | null;
  email: string | null;
  versicherung: string | null;
  versicherungsnummer: string | null;
  notizen: string | null;
  aufnahme_datum: string | null;
  aktiv: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface PatientCreate {
  anrede: Anrede;
  titel?: string | null;
  vorname: string;
  nachname: string;
  geburtsdatum: string;
  strasse: string;
  hausnummer: string;
  plz: string;
  ort: string;
  telefon?: string | null;
  email?: string | null;
  versicherung?: string | null;
  versicherungsnummer?: string | null;
  notizen?: string | null;
  aufnahme_datum?: string | null;
}

export interface PatientUpdate extends Partial<PatientCreate> {}

// ─── Rechnungsposition ────────────────────────────────
export interface RechnungsPosition {
  id: number;
  rechnung_id: number;
  goae_ziffer: string;
  beschreibung: string;
  datum: string;
  anzahl: number;
  punkte: number;
  faktor: number;
  betrag: number;
  begruendung: string | null;
}

export interface RechnungsPositionCreate {
  goae_ziffer: string;
  beschreibung: string;
  datum: string;
  anzahl: number;
  punkte: number;
  faktor: number;
  betrag: number;
  begruendung?: string | null;
}

// ─── Rechnungsdokument ────────────────────────────────
export interface RechnungsDokument {
  id: number;
  rechnung_id: number;
  dateiname: string;
  mime_type: string;
  version: number;
  created_at: string;
}

// ─── Rechnung ─────────────────────────────────────────
export interface Rechnung {
  id: number;
  patient_id: number;
  rechnungsnummer: string;
  rechnungsdatum: string;
  leistungszeitraum_von: string;
  leistungszeitraum_bis: string;
  diagnose: string;
  status: RechnungStatus;
  gesamtbetrag: number;
  zahlungsziel_tage: number;
  bezahlt_am: string | null;
  storniert_am: string | null;
  storno_grund: string | null;
  notizen: string | null;
  created_at: string;
  updated_at: string | null;
  positionen: RechnungsPosition[];
  dokumente: RechnungsDokument[];
}

export interface RechnungCreate {
  patient_id: number;
  rechnungsdatum: string;
  leistungszeitraum_von: string;
  leistungszeitraum_bis: string;
  diagnose: string;
  zahlungsziel_tage?: number;
  notizen?: string | null;
  positionen: RechnungsPositionCreate[];
}

export interface RechnungUpdate {
  rechnungsdatum?: string;
  leistungszeitraum_von?: string;
  leistungszeitraum_bis?: string;
  diagnose?: string;
  zahlungsziel_tage?: number;
  notizen?: string | null;
  positionen?: RechnungsPositionCreate[];
}

// ─── Praxiseinstellungen ──────────────────────────────
export interface PraxisEinstellungen {
  id: number;
  arzt_titel: string | null;
  arzt_vorname: string;
  arzt_nachname: string;
  fachrichtung: string;
  praxis_name: string | null;
  strasse: string;
  hausnummer: string;
  plz: string;
  ort: string;
  telefon: string;
  fax: string | null;
  email: string;
  website: string | null;
  lanr: string | null;
  steuernummer: string | null;
  ust_befreit: boolean;
  bank_name: string;
  iban: string;
  bic: string | null;
  kontoinhaber: string | null;
  standard_zahlungsziel_tage: number;
  rechnungsnummer_praefix: string;
  naechste_rechnungsnummer: number;
  created_at: string;
  updated_at: string;
}

export interface PraxisEinstellungenUpdate extends Partial<Omit<PraxisEinstellungen, 'id' | 'created_at' | 'updated_at'>> {}

// ─── GOÄ Punktwert ────────────────────────────────────
export const GOAE_PUNKTWERT = 0.0582873;

// ─── Hilfsfunktionen ──────────────────────────────────
export function berechnePosition(punkte: number, faktor: number, anzahl: number = 1): number {
  return Math.round(punkte * GOAE_PUNKTWERT * faktor * anzahl * 100) / 100;
}

export function statusLabel(status: RechnungStatus): string {
  const labels: Record<RechnungStatus, string> = {
    entwurf: 'Entwurf',
    gestellt: 'Gestellt',
    bezahlt: 'Bezahlt',
    storniert: 'Storniert',
  };
  return labels[status] || status;
}

export function statusColor(status: RechnungStatus): string {
  const colors: Record<RechnungStatus, string> = {
    entwurf: 'bg-yellow-100 text-yellow-800',
    gestellt: 'bg-blue-100 text-blue-800',
    bezahlt: 'bg-green-100 text-green-800',
    storniert: 'bg-red-100 text-red-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}
