# APIs (Schnittstellenentwurf)

## Authentifizierung

POST `/api/auth/login`, POST `/api/auth/logout`

## Mitarbeiter

GET, POST, PUT, DELETE `/api/employees`

## Abwesenheiten

GET, POST, PUT, DELETE `/api/absences`, optional GET `/api/absences/calendar`

## Reports

GET `/api/reports/summary`, GET `/api/reports/employee/{id}`, optional GET `/api/reports/export`

## Stammdaten

GET `/api/absence-types`, GET `/api/holidays`

Folgt REST-Konventionen, Statuscodes 200/201/400/401 usw.
