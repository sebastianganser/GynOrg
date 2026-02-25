# Datenmodell

(Relationales Modell in MySQL, primäre Tabellen und ihre Felder:)

## Benutzer (User)

Felder: `user_id` (Primärschlüssel), `username` (Login-Name), `password_hash` (verschlüsseltes Passwort), `name` (optionaler Klarname).

## Mitarbeiter (Employee)

Felder: `employee_id` (PK), `name` (Vollname des Mitarbeiters), `position` (Rolle/Abteilung, optional), `vacation_allowance` (jährliches Urlaubskontingent in Tagen), `date_hired` oder `active` (Flag, falls benötigt).

## Abwesenheiten (Absence)

Felder: `absence_id` (PK), `employee_id` (FK), `type`, `start_date`, `end_date`, `comment`, optional `days_count`, `created_at`, `updated_at`.

Alle Einträge sind genehmigt.

## Abwesenheitsarten (AbsenceType) (optional)

Felder: `type_id`, `name`, `color_code`, optional `counts_as_vacation`.

## Feiertage (Holidays) (optional)

Felder: `date`, `name`.

## Rechnungen (Invoices) (zukünftig)

Platzhalter für zukünftige Tabellen wie `invoices` mit üblichen Feldern.

Referenzielle Integrität durch FK-Constraints, AutoIncrement PKs, Indexe auf häufig gefilterten Feldern. Migrationen via ORM.
