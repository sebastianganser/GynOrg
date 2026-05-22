# Sicherheit

- **Authentifizierung:** Auth-Token (JWT) notwendig. Das System gibt den HTTP Statuscode 401 bei fehlender Authentifizierung zurück.
- **Session-Timeout (Auto-Logout):** In den Systemeinstellungen konfigurierbarer Inaktivitäts-Timer (z.B. 5, 10, 15 oder 30 Minuten), nach dessen Ablauf der Benutzer automatisch abgemeldet wird, um unbefugten Zugriff am Arbeitsplatz zu verhindern.
- **Passwort-Speicherung:** bcrypt-Hashing der Passwörter in der Datenbank.
- **Kommunikation:** HTTPS-only in Produktion. Secure & HttpOnly Cookies für Sessions/Token-Speicherung empfohlen.
- **Architektur:** Serverseitige Validierung aller Eingaben.
- **Betrieb:** Fehler-Logging, regelmäßige Backups der Datenbank, Einhaltung der Datenschutzrichtlinien.
- **Single User System:** Benutzername und Passwort-Hash werden sicher über Umgebungsvariablen (`.env`) konfiguriert.
