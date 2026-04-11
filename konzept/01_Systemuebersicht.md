# Systemübersicht

- **Ziel und Nutzerkreis:** Browserbasiertes Abwesenheitsplanungstool für einen einzelnen Nutzer (Chefarzt) zur Verwaltung der Abwesenheiten seines Teams. Mitarbeiter selbst haben keinen eigenen Zugang – alle Eingaben erfolgen ausschließlich durch den Chefarzt.

- **Einzelbenutzer-Betrieb:** Keine Rollen, Rechtevergaben oder Stellvertretungen im System. Der Chefarzt hat Vollzugriff auf alle Funktionen; es gibt keine Unterscheidung von Benutzerrollen.

- **Einfaches Login:** Authentifizierung über einen einzigen Benutzeraccount (Chefarzt) mittels Benutzername/Passwort. Keine komplexe Benutzerverwaltung notwendig (nur ein Account). Passwort wird sicher (gehasht) in der Datenbank gespeichert.

- **Kernmodule der Anwendung:** Übersichts-Dashboard, Team-Kalender und Berichtssektion bleiben als Hauptbestandteile des UI bestehen. Diese liefern einen schnellen Überblick über Abwesenheiten und Statistiken. (Eine Mitarbeiter-Verwaltungsseite zur Pflege der Personaldaten kommt hinzu, siehe Funktionen.)

- **Kein Benachrichtigungssystem:** E-Mail-Benachrichtigungen oder interne Notifications entfallen. Das System versendet keine Mails (z. B. bei neuen Abwesenheiten), da der Chefarzt selbst direkt alle Einträge vornimmt und ein Genehmigungsworkflow im Tool nicht erforderlich ist.

- **Zukunftssicherheit:** Bereits auf Erweiterungen ausgelegt (z. B. geplantes Rechnungsmodul), aber die aktuelle Version fokussiert ausschließlich auf Abwesenheitsverwaltung. Architekturentscheidungen unterstützen künftige Module, ohne das jetzige System zu verkomplizieren.
