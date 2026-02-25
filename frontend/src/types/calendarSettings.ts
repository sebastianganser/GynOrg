export interface FederalStateOption {
  code: string;
  name: string;
}

export interface CalendarSettings {
  id: number;
  user_id: string;
  selected_federal_states: string[];
  school_holiday_federal_states: string[];
  show_nationwide_holidays: boolean;
  show_calendar_weeks: boolean;
  visible_employee_ids: number[];
  show_vacation_absences: boolean;
  show_sick_leave: boolean;
  show_training: boolean;
  show_special_leave: boolean;
  created_at: string;
  updated_at: string;
  federal_states_display: FederalStateOption[];
}

export interface CalendarSettingsUpdate {
  selected_federal_states?: string[];
  school_holiday_federal_states?: string[];
  show_nationwide_holidays?: boolean;
  show_calendar_weeks?: boolean;
  visible_employee_ids?: number[];
  show_vacation_absences?: boolean;
  show_sick_leave?: boolean;
  show_training?: boolean;
  show_special_leave?: boolean;
}

export interface CalendarSettingsFormData {
  selected_federal_states: string[];
  school_holiday_federal_states: string[];
  show_nationwide_holidays: boolean;
  show_calendar_weeks: boolean;
  visible_employee_ids: number[];
  show_vacation_absences: boolean;
  show_sick_leave: boolean;
  show_training: boolean;
  show_special_leave: boolean;
}
