// Holiday Types - entspricht dem Backend
export enum HolidayType {
  PUBLIC_HOLIDAY = "PUBLIC_HOLIDAY",
  SCHOOL_VACATION = "SCHOOL_VACATION"
}

export enum SchoolVacationType {
  WINTER = "WINTER",
  EASTER = "EASTER",
  PENTECOST = "PENTECOST",
  SUMMER = "SUMMER",
  AUTUMN = "AUTUMN",
  CHRISTMAS = "CHRISTMAS",
  OTHER = "OTHER"
}

export enum DataSource {
  MANUAL = "MANUAL",
  MEHR_SCHULFERIEN_API = "MEHR_SCHULFERIEN_API"
}

// Erweiterte Holiday Interface
export interface Holiday {
  id: number;
  name: string;
  date: string;
  end_date?: string; // Optionales Enddatum für mehrtägige Ferien (Frontend)
  federal_state?: string;
  federal_state_code?: string;  // Kürzel wie "BW", "BY", "ST"
  is_nationwide: boolean;
  year: number;
  notes: string;
  // Neue Felder für Schulferien-Support
  holiday_type: HolidayType;
  school_vacation_type?: SchoolVacationType;
  data_source: DataSource;
  last_updated?: string;
  api_id?: string;
  created_at: string;
  updated_at?: string;
}

// Erweiterte Filter-Interface
export interface HolidayFilter {
  year?: number;
  month?: number;
  federal_state?: string;
  include_nationwide?: boolean;
  holiday_type?: HolidayType;
  school_vacation_type?: SchoolVacationType;
  data_source?: DataSource;
  start_date?: string;
  end_date?: string;
}

// UI-spezifische Filter für Frontend
export interface HolidayDisplayFilter {
  showPublicHolidays: boolean;
  showSchoolVacations: boolean;
  showOnlyMyState: boolean;
  selectedFederalStates: string[];
}

export interface HolidayImportResult {
  year: number;
  result: {
    imported: number;
    skipped: number;
    errors: number;
  };
  message: string;
}

// Utility Functions
export const getHolidayTypeLabel = (type: HolidayType): string => {
  switch (type) {
    case HolidayType.PUBLIC_HOLIDAY:
      return 'Feiertag';
    case HolidayType.SCHOOL_VACATION:
      return 'Schulferien';
    default:
      return 'Unbekannt';
  }
};

export const getSchoolVacationTypeLabel = (type: SchoolVacationType): string => {
  switch (type) {
    case SchoolVacationType.WINTER:
      return 'Winterferien';
    case SchoolVacationType.EASTER:
      return 'Osterferien';
    case SchoolVacationType.PENTECOST:
      return 'Pfingstferien';
    case SchoolVacationType.SUMMER:
      return 'Sommerferien';
    case SchoolVacationType.AUTUMN:
      return 'Herbstferien';
    case SchoolVacationType.CHRISTMAS:
      return 'Weihnachtsferien';
    case SchoolVacationType.OTHER:
      return 'Sonstige Ferien';
    default:
      return 'Unbekannt';
  }
};

export const getHolidayIcon = (holiday: Holiday): string => {
  if (holiday.holiday_type === HolidayType.PUBLIC_HOLIDAY) {
    return '🏛️';
  } else if (holiday.holiday_type === HolidayType.SCHOOL_VACATION) {
    return '🎒';
  }
  return '📅';
};

export const getHolidayColor = (holiday: Holiday): string => {
  if (holiday.holiday_type === HolidayType.PUBLIC_HOLIDAY) {
    return holiday.is_nationwide ? '#dc2626' : '#ea580c'; // Rot für Feiertage
  } else if (holiday.holiday_type === HolidayType.SCHOOL_VACATION) {
    return '#2563eb'; // Blau für Schulferien
  }
  return '#6b7280'; // Grau als Fallback
};

export const getHolidayTextColor = (holiday: Holiday): string => {
  return '#ffffff'; // Weiß für alle Holiday-Typen
};

// Hilfsfunktion für Kalender-Integration
export const formatHolidayDisplayName = (_holiday: Holiday): string => {
  // const icon = getHolidayIcon(_holiday); // Icons removed per user request
  let displayName = _holiday.name;

  // Für Schulferien den Typ hinzufügen
  if (_holiday.holiday_type === HolidayType.SCHOOL_VACATION && _holiday.school_vacation_type) {
    const vacationType = getSchoolVacationTypeLabel(_holiday.school_vacation_type);
    displayName = vacationType;
  }

  // Multi-State Support: Append State Code if applicable
  // Append if it's not nationwide AND (it's a school vacation OR it has a state assigned)
  if (!_holiday.is_nationwide && _holiday.federal_state) {
    displayName += ` (${_holiday.federal_state})`;
  }

  return displayName;
};

// Gruppierte Holiday-Interface für Kalender-Darstellung
export interface GroupedHoliday extends Holiday {
  federal_states?: string[];
  display_federal_states?: string[];
}
