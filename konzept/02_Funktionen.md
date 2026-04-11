# Funktionen (Features)

- **Benutzer-Authentifizierung:** Einfaches Login für den Chefarzt. Nach erfolgreicher Anmeldung erhält der Nutzer Zugriff auf alle Bereiche. (Kein Registrierungsvorgang für weitere Benutzer nötig.)

- **Mitarbeiterverwaltung:** Der Chefarzt kann Personalstammdaten seines Teams pflegen.

- **Mitarbeiter anlegen/bearbeiten/löschen:** Erfassung von Mitarbeiterdaten (Name, Position/Abteilung optional, jährliches Urlaubskontingent etc.). Bearbeiten und Entfernen von Mitarbeiterdatensätzen ist möglich.

- **Übersicht aller Mitarbeiter:** Liste aller angelegten Teammitglieder mit ihren Basisdaten und ggf. verbleibenden Urlaubstagen.

- **Abwesenheitsverwaltung:** Zentrale Funktion zum Planen und Verwalten von Abwesenheiten der Teammitglieder.

- **Abwesenheitseintrag erstellen:** Eingabe einer neuen Abwesenheit für einen Mitarbeiter (Auswahl des Mitarbeiters, Abwesenheitsart, Start- und Enddatum, optional Kommentar). Jede neu erfasste Abwesenheit gilt als direkt genehmigt (da vom Chefarzt selbst eingetragen).

- **Abwesenheit bearbeiten/löschen:** Möglichkeit, bestehende Abwesenheitseinträge zu ändern (z. B. Zeitraum korrigieren) oder zu entfernen. Änderungen werden in der Datenbank versioniert oder mit Zeitstempel aktualisiert (für die Nachvollziehbarkeit).

- **Abwesenheitstypen:** Vordefinierte Abwesenheitsarten wie Urlaub, Krankmeldung, Fortbildung etc. stehen zur Auswahl. Diese sind initial fest im System hinterlegt oder als Stammdaten konfigurierbar (für zukünftige Anpassungen durch den Chefarzt, z. B. Hinzufügen neuer Abwesenheitstypen). Farbcodes je Typ sorgen für konsistente Darstellung im Kalender und in Berichten.

- **Konfliktprüfung:** Beim Eintragen prüft das System auf Überschneidungen (gleicher Mitarbeiter bereits abwesend im Zeitraum) und zeigt Warnungen bei Konflikten oder ungültigen Eingaben (z. B. Enddatum vor Startdatum).

- **Team-Kalenderansicht:** Grafische Kalenderübersicht aller Abwesenheiten im Team.

- **Übersichtliches Kalender-UI:** Darstellung als Gantt-Chart-ähnlicher Zeitstrahl: horizontal die Zeitachse (Tage/Wochen), vertikal die Mitarbeiter. Jeder Abwesenheitseintrag erscheint als farbiger Balken beim jeweiligen Mitarbeiter an den entsprechenden Tagen.

- **Ansichtsoptionen:** Umschaltbar zwischen Monats- und Wochenansicht. Scroll- und Zoom-Funktion für längere Zeiträume. Der aktuelle Tag wird hervorgehoben.

- **Detailanzeige:** Bei Hover oder Klick auf einen Abwesenheitsbalken Anzeige von Details (Mitarbeitername, Abwesenheitstyp, Dauer, Kommentar).

- **Kalenderaktualität:** Änderungen (Hinzufügen/Löschen von Abwesenheiten) reflektieren sich sofort in der Ansicht. Wochenenden und hinterlegte Feiertage werden visuell gekennzeichnet oder ausgeblendet (optional), um Arbeits- vs. Freitage zu verdeutlichen.

## Dashboard (Übersichtsseite)

- **Kacheln/Kennzahlen:** Anzeige von z. B. der Anzahl der heute abwesenden Mitarbeiter, dem nächsten bevorstehenden Urlaubszeitraum und ggf. der insgesamt genommenen Urlaubstage im laufenden Jahr.

- **Resturlaubsübersicht:** Zusammenfassung pro Mitarbeiter, wie viele Urlaubstage noch verfügbar sind (berechnet aus Urlaubskontingent minus bereits genehmigter Urlaubstage).

- **Schnellzugriff:** Direkte Links oder Buttons zum neuen Abwesenheitseintrag oder zur Mitarbeiteranlage, um häufige Aktionen schnell zu erreichen.

## Berichte und Auswertungen

- **Statistikfunktionen:** Erzeugung von Berichten, z. B. Jahresübersicht pro Mitarbeiter (Urlaubstage genommen, Krankheitstage), Abwesenheitsverteilung nach Typ (z. B. Prozentanteil Urlaub vs. Krankheit im Team), monatliche Abwesenheitstage etc.

- **Visualisierung:** Grafische Darstellung mittels Balken- und Kreisdiagrammen für einen schnellen Überblick. (Beispiel: Balkendiagramm mit Abwesenheitstagen pro Monat, Kreisdiagramm mit Anteil der Abwesenheitstypen.)

- **Export:** Möglichkeit, einen Bericht als PDF herunterzuladen oder auszudrucken, für Dokumentation oder Besprechungen. (Generierung serverseitig als PDF mit Logo/Kopfzeile, optional in Phase 2 umzusetzen.)

- **Filter:** Interaktive Filtermöglichkeit nach Zeitraum (Jahr, Monat) und Abwesenheitsart, um spezifische Auswertungen zu erhalten.

## Einstellungen (Basis-Konfiguration)

- **Abwesenheitsarten verwalten:** (Falls nicht fest codiert) Möglichkeit, die Liste der Abwesenheitsarten zu bearbeiten – neue Typen hinzufügen, Farbe zuordnen.

- **Feiertagskalender hinterlegen:** Eingabe von regionalen Feiertagen, die bei Berechnungen und im Kalender berücksichtigt werden (Wochenenden/Feiertage werden bei der Tagezählung automatisch ausgenommen).

- **Passwort ändern:** Option für den Chefarzt, sein Login-Passwort zu ändern.

- *(Platzhalter für Rechnungsmodul)* Hinweis auf zukünftige Integration eines Rechnungsmoduls.

## Nicht implementierte Features

Funktionen wie Abwesenheitsantrag durch Mitarbeiter, Genehmigungs-Workflows oder automatische Benachrichtigungen sind im Einzelbenutzer-MVP bewusst nicht enthalten. Der Fokus liegt auf direkter Datenerfassung und Übersicht durch den Chefarzt selbst.
