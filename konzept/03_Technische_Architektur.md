# Technische Architektur

- **Client-Server-Struktur:** Trennung von Frontend und Backend. Das Frontend ist eine Single-Page Application, die über eine definierte API mit dem Backend kommuniziert.

- **Frontend:** Umsetzung mit React (aktuelle Version) mit TypeScript für robuste Typisierung. Styling mit Tailwind CSS oder vergleichbarem Utility-CSS-Framework für ein konsistentes, responsives Design. Das Frontend wird als Docker-fähige Build (statische Files) erstellt.

- **UI-Framework:** React bietet eine komponentenbasierte Architektur, ideal zur Wiederverwendung von UI-Komponenten (Kalender, Formulare, Diagramme etc.). Alternativ wäre auch Vue 3 mit Composition API denkbar – die Wahl richtet sich nach Best Practices und Vertrautheit im Team, aber React + Tailwind gilt als erprobte Kombination für zügige Entwicklung.

- **State-Management:** Verwendung eines geeigneten State-Managements (z. B. React Context oder Zustand/MobX) für globale Zustände wie angemeldeter Benutzer, Mitarbeiterliste im Speicher, etc. Simpler gehalten, da App-Umfang überschaubar (auf komplexe Stores wie Redux kann evtl. verzichtet werden).

- **Routing:** Client-seitiges Routing (z. B. mit React Router) für Navigation zwischen Login, Dashboard, Kalender, Berichte, etc. Ungeschützte Routen (Login) vs. geschützte Routen (Hauptanwendung) sind konfiguriert, sodass unautorisierte Zugriffe auf interne Seiten verhindert werden.

- **Backend:** Node.js (LTS-Version) Server mit Express Framework (oder alternativ NestJS für strukturierteren Ansatz) als REST-API. Implementierung ebenso in TypeScript zur besseren Wartbarkeit. Das Backend läuft als eigener Dienst (Docker-Container) und verwaltet Geschäftslogik, Authentifizierung und Datenzugriff.

- **Schichtenarchitektur:** Klare Trennung der Verantwortlichkeiten im Backend: Routen/Controller für die Entgegennahme von HTTP-Requests, Services/Business-Logik für Verarbeitung (z. B. Berechnung verbleibender Urlaubstage), und Data-Access-Layer mittels ORM für DB-Zugriffe.

- **ORM & Datenbankzugriff:** Verwendung einer ORM (Object-Relational Mapping) Bibliothek zur Abstraktion der MySQL-Datenbank. Prisma (empfohlen) bietet eine moderne, typensichere API und passt gut zu TypeScript. Alternativ wäre Sequelize möglich – jedoch wird Prisma als zukunftssichere und Docker-freundliche Option bevorzugt (einfache Migrationen, schlankes Schema-Definitionstool). Das ORM verwaltet die Migrationen des Datenbank-Schemas (Erstellen der Tabellen entsprechend dem Datenmodell).

- **MySQL-Datenbank:** Relationale MySQL-Datenbank zur Speicherung aller persistenten Daten (in Docker als separater DB-Container laufend). Verbindungsdetails (Host, User, Passwort) werden über Umgebungsvariablen konfiguriert. Bei Entwicklungsstart ggf. automatische Schemaerstellung/Migration via ORM.

- **REST API:** Das Backend stellt RESTful-API Endpunkte bereit, die vom Frontend per HTTP (JSON) konsumiert werden. JSON wird als Datenformat in Requests/Responses genutzt. Die API-Routen sind thematisch gegliedert (z. B. `/api/auth` , `/api/employees` , `/api/absences` , `/api/reports` ).

- **Session-Handling:** Nach Login erhält der Client einen JWT-Token vom Server, der in nachfolgenden Requests zur Authentifizierung mitgesendet wird (im Authorization-Header). Alternativ kann eine serverseitige Session mit Cookie genutzt werden; JWT bietet jedoch Vorteile für eine klare Trennung von Frontend/Backend. Das Backend validiert den Token bei jeder Anfrage und gewährt Zugriff nur mit gültiger Authentifizierung.

- **Deployment & Containerisierung:** Das gesamte System ist auf Docker-Betrieb ausgelegt. Docker-Compose kann genutzt werden, um Backend, Frontend (statisches Build) und MySQL-DB als separate Services zu orchestrieren.

- **Container Setup:** Ein Container für das Node.js Backend, ein Container für die MySQL-Datenbank. Das Frontend wird entweder von einem einfachen Webserver (Nginx/Apache in eigenem Container) ausgeliefert oder via CDN/Hosting (z. B. Vercel/Netlify) bereitgestellt – je nach Infrastrukturvorgabe.

- **Konfiguration:** Alle sensiblen Einstellungen (DB Credentials, JWT Secret, Port, etc.) sind über Environment-Variablen konfiguriert, was Docker-Deployments erleichtert.

- **Build/Run Automatisierung:** Scripts für den Container-Build und Migrationen (z. B. `docker-compose up` ruft initial DB-Migrationen auf) gehören zum Projekt. Continuous Integration/Deployment-Pipelines können das Container Image bauen und auf den Server deployen.

- **Leistung & Skalierung:** Da es sich um ein Einzelbenutzer-System handelt, sind die Lastanforderungen gering. Die Architektur (getrennte Dienste) ist dennoch gewählt, um Wartbarkeit und Erweiterbarkeit zu gewährleisten. Bei Bedarf kann z. B. die Datenbank auf einen Managed Service ausgelagert oder das Backend horizontal skaliert werden, obwohl in diesem Anwendungsfall ein einzelner Container ausreicht.

- **Logging & Monitoring:** Basis-Logging im Backend (z. B. mittels Winston oder eingebauter Logger) für Fehler und wichtige Aktionen (erfolgreiche Logins, DB-Fehler etc.). Bei Deployment in Produktion sollte zudem ein Monitoring (Docker Healthchecks, ggf. einfache Up-Time Überwachung) eingerichtet sein.
