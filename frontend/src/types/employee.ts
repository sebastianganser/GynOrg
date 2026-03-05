// Federal State Enum - entspricht dem Backend FederalState
// Verwendet Codes als Values für API-Kompatibilität
export enum FederalState {
  BW = "BW",
  BY = "BY",
  BE = "BE",
  BB = "BB",
  HB = "HB",
  HH = "HH",
  HE = "HE",
  MV = "MV",
  NI = "NI",
  NW = "NW",
  RP = "RP",
  SL = "SL",
  SN = "SN",
  ST = "ST",
  SH = "SH",
  TH = "TH"
}

// Mapping für Vollnamen (für UI-Anzeige)
const FEDERAL_STATE_NAMES: Record<string, string> = {
  BW: "Baden-Württemberg",
  BY: "Bayern",
  BE: "Berlin",
  BB: "Brandenburg",
  HB: "Bremen",
  HH: "Hamburg",
  HE: "Hessen",
  MV: "Mecklenburg-Vorpommern",
  NI: "Niedersachsen",
  NW: "Nordrhein-Westfalen",
  RP: "Rheinland-Pfalz",
  SL: "Saarland",
  SN: "Sachsen",
  ST: "Sachsen-Anhalt",
  SH: "Schleswig-Holstein",
  TH: "Thüringen"
};

// Federal State Choice für Dropdowns
export interface FederalStateChoice {
  code: string;
  name: string;
}

// VacationAllowance Interface
export interface VacationAllowance {
  id: number;
  employee_id: number;
  year: number;
  annual_allowance: number;
  carryover_days: number;
  total_allowance: number;
  created_at: string;
  updated_at: string;
}

// VacationAllowance Create Interface
export interface VacationAllowanceCreate {
  employee_id: number;
  year: number;
  annual_allowance: number;
  carryover_days?: number;
}

// VacationAllowance Update Interface
export interface VacationAllowanceUpdate {
  annual_allowance?: number;
  carryover_days?: number;
}

// Employee Interface - neue Struktur
export interface Employee {
  id: number;
  title?: string;
  first_name: string;
  last_name: string;
  position?: string;
  email: string;
  birth_date?: string; // ISO date string
  date_hired?: string; // ISO date string
  federal_state: FederalState;
  active: boolean;
  vacation_allowance?: number; // Temporär für Kompatibilität
  profile_image_path?: string; // Der reale DB-Pfad
  avatar_filename?: string;
  avatar_url?: string; // Wird im Service dynamisch generiert
  initials?: string; // Benutzerdefinierte Initialen für Avatar
  calendar_color?: string; // Hex color code for calendar display
  school_children: boolean;
  youngest_child_birth_year?: number;
  created_at: string;
  updated_at: string;
}

// Employee mit Urlaubsdaten
export interface EmployeeWithVacation extends Employee {
  vacation_allowances: VacationAllowance[];
}

// Employee Create Interface
export interface EmployeeCreate {
  title?: string;
  first_name: string;
  last_name: string;
  position?: string;
  email: string;
  birth_date?: string;
  date_hired?: string;
  federal_state: FederalState;
  active?: boolean;
  calendar_color?: string;
  initials?: string;
  school_children?: boolean;
  youngest_child_birth_year?: number;
}

// Employee Update Interface
export interface EmployeeUpdate {
  title?: string;
  first_name?: string;
  last_name?: string;
  position?: string;
  email?: string;
  birth_date?: string;
  date_hired?: string;
  federal_state?: FederalState;
  active?: boolean;
  vacation_allowance?: number; // Temporär für Kompatibilität
  calendar_color?: string;
  initials?: string;
  school_children?: boolean;
  youngest_child_birth_year?: number;
}

// Form-spezifische Interfaces
export interface EmployeeCreateForm {
  title?: string;
  first_name: string;
  last_name: string;
  position?: string;
  email: string;
  birth_date?: string;
  date_hired?: string;
  federal_state: FederalState;
  active: boolean;
  calendar_color?: string;
  initials?: string;
  school_children: boolean;
  youngest_child_birth_year?: number;
}

export interface EmployeeUpdateForm {
  title?: string;
  first_name?: string;
  last_name?: string;
  position?: string;
  email?: string;
  birth_date?: string;
  date_hired?: string;
  federal_state?: FederalState;
  active?: boolean;
  school_children?: boolean;
  calendar_color?: string;
  initials?: string;
}

export interface VacationAllowanceForm {
  year: number;
  annual_allowance: number;
  carryover_days: number;
}

// Utility Types
export type EmployeeListItem = Pick<Employee, 'id' | 'first_name' | 'last_name' | 'position' | 'federal_state' | 'date_hired' | 'active'>;

// Helper Functions
export const getFederalStateChoices = (): FederalStateChoice[] => {
  return Object.entries(FederalState).map(([_code, value]) => ({
    code: value,
    name: FEDERAL_STATE_NAMES[value]
  }));
};

export const getFederalStateName = (code: string): string => {
  return FEDERAL_STATE_NAMES[code] || code;
};

export const getEmployeeFullName = (employee: Employee): string => {
  const parts = [];
  if (employee.title) {
    parts.push(employee.title);
  }
  parts.push(employee.first_name, employee.last_name);
  return parts.join(' ');
};

export const getEmployeeDisplayName = (employee: Employee): string => {
  return `${employee.last_name}, ${employee.first_name}`;
};

// Legacy support - für schrittweise Migration
// Diese können später entfernt werden, wenn alle Komponenten migriert sind
export interface LegacyEmployee {
  id: number;
  name: string;
  position: string | null;
  vacation_allowance: number;
  date_hired: string | null;
  active: boolean;
}

// Alias für Konsistenz mit bestehenden Komponenten
export type CreateEmployeeRequest = EmployeeCreate;
