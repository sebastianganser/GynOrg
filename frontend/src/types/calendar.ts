import { View } from 'react-big-calendar';

// Extended view types to include custom views
export type ExtendedView = View | 'quarter' | 'year';

// Custom view configuration
export interface CustomViewConfig {
  view: ExtendedView;
  date: Date;
}

// Quarter information
export interface QuarterInfo {
  year: number;
  quarter: number; // 1-4
  startMonth: number; // 0-11 (JavaScript month index)
  endMonth: number; // 0-11
  label: string; // e.g., "Q1 2025"
}

// Year information
export interface YearInfo {
  year: number;
  label: string; // e.g., "2025"
}

// Helper functions for custom views
export const getQuarterInfo = (date: Date): QuarterInfo => {
  const year = date.getFullYear();
  const month = date.getMonth();
  const quarter = Math.floor(month / 3) + 1;
  const startMonth = (quarter - 1) * 3;
  const endMonth = startMonth + 2;
  
  return {
    year,
    quarter,
    startMonth,
    endMonth,
    label: `Q${quarter} ${year}`
  };
};

export const getYearInfo = (date: Date): YearInfo => {
  const year = date.getFullYear();
  
  return {
    year,
    label: `${year}`
  };
};

// Navigation helpers
export const navigateQuarter = (date: Date, direction: 'prev' | 'next'): Date => {
  const newDate = new Date(date);
  const months = direction === 'next' ? 3 : -3;
  newDate.setMonth(newDate.getMonth() + months);
  return newDate;
};

export const navigateYear = (date: Date, direction: 'prev' | 'next'): Date => {
  const newDate = new Date(date);
  const years = direction === 'next' ? 1 : -1;
  newDate.setFullYear(newDate.getFullYear() + years);
  return newDate;
};
