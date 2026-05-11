# Datenmodell

## Benutzer (User)
Felder: `user_id` (Primärschlüssel), `username` (Login-Name), `password_hash` (verschlüsseltes Passwort), `name` (optionaler Klarname).

## Mitarbeiter & Urlaubsverwaltung
Das Datenmodell für Mitarbeiter wurde stark normalisiert, um komplexe Urlaubsansprüche historisch korrekt abbilden zu können:
- **Mitarbeiter (`employee`)**: `id`, `name`, `active`, `date_hired`, `job_position_id`
- **Positionen (`job_position`)**: `id`, `name`, `description`, `active`
- **Urlaubskontingent (`vacation_allowance`)**: `id`, `employee_id`, `year`, `annual_allowance`, `carryover_days` (Erlaubnis pro Jahr inkl. Resturlaub)
- **Urlaubsanspruch-Historie (`vacation_entitlement`)**: `id`, `employee_id`, `from_date`, `days` (Historische Entwicklung des Anspruchs)

## Abwesenheiten (Absence)
- **Abwesenheiten (`absence`)**: `id`, `employee_id`, `type_id`, `start_date`, `end_date`, `comment`, `days_count`. (Alle Einträge gelten als genehmigt).
- **Abwesenheitsarten (`absence_type`)**: `id`, `name`, `color_code`, `counts_as_vacation`.

## Feiertage & Systemeinstellungen
- **Feiertage (`holiday`)**: `id`, `date`, `name`, `federal_state_id`, `data_source`
- **Bundesländer (`federal_state`)**: `id`, `name`, `code`
- **Kalender-Einstellungen (`calendar_settings`)**: `id`, `year`, `state_code`
- **System-Einstellungen (`system_settings`)**: `id`, `key`, `value`
- **Schulferien-Benachrichtigungen (`school_holiday_notification`)**: `id`, `state_code`, `year`, `notification_date`

---

## Zusatzmodul: Auslastungsstatistik (PostgreSQL)
```sql
stations: station_id, name, plan_beds, color, active
daily_entries: entry_id, station_id, date, occupied, admissions, discharges, blocked_beds
daily_fremd: date, count
calendar_tags: tag_id, tag_name, tag_category, is_automatic
day_tags: date, tag_id, source, comment
tag_multipliers: tag_id, metric, multiplier, sample_size, confidence, last_calculated
```

## Zusatzmodul: GOÄ-Rechnungen (PostgreSQL)
```sql
goae_ziffern: id, ziffer, leistungstext, punkte, einfachsatz, max_faktor_regel, max_faktor_abs, kapitel, abschnitt, begruendung_pflicht, analog_bewertung, aktiv
patienten: id, anrede, titel, vorname, nachname, geburtsdatum, strasse, plz, ort, land, email, telefon, versicherung, versicherungs_nr, beihilfe_satz
rechnungen: id, rechnungsnummer, rechnungsdatum, faelligkeitsdatum, patient_id, arzt_*, betrag_*, status, zugferd_profil
rechnungs_positionen: id, rechnung_id, position_nr, goae_ziffer_id, leistungstext, leistungsdatum, anzahl, punkte, einfachsatz, steigerungsfaktor, betrag, begruendung, analog_nach
rechnungs_dokumente: id, rechnung_id, dokument_typ, dateiname, pdf_daten, zugferd_xml, gesendet_an, gesendet_am, versand_status
einstellungen_praxis: id, schluessel, wert, beschreibung
```
