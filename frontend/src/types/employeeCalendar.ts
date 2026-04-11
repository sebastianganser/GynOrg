/**
 * TypeScript types for employee calendar information
 * Simplified employee data for calendar sidebar display
 */

export interface EmployeeCalendarInfo {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  calendar_color: string;
  active: boolean;
  initials?: string;
}

export interface EmployeeCalendarFilter {
  visible_employee_ids: number[] | null;
  show_inactive: boolean;
}
