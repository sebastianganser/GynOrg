import { FederalState, FederalStateChoice } from '../types/employee';
import { API_BASE_URL } from './config';
import { authService } from './authService';

export const utilityService = {
  // Get all federal states from backend
  async getFederalStates(): Promise<FederalStateChoice[]> {
    const response = await fetch(`${API_BASE_URL}/federal-states/`, {
      method: 'GET',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch federal states: ${response.statusText}`);
    }

    return response.json();
  },

  // Get federal states as enum values (client-side fallback)
  getFederalStatesLocal(): FederalStateChoice[] {
    return Object.entries(FederalState).map(([code, name]) => ({
      code,
      name
    }));
  },

  // Validate email format
  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Format date for display
  formatDate(dateString: string | null | undefined, locale: string = 'de-DE'): string {
    if (!dateString) return '-';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString(locale, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    } catch (error) {
      return dateString;
    }
  },

  // Format date for input fields (YYYY-MM-DD)
  formatDateForInput(dateString: string | null | undefined): string {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    } catch (error) {
      return '';
    }
  },

  // Parse date from input field
  parseDateFromInput(inputValue: string): string | null {
    if (!inputValue) return null;
    
    try {
      const date = new Date(inputValue);
      return date.toISOString();
    } catch (error) {
      return null;
    }
  },

  // Validate date is not in the future
  isDateNotInFuture(dateString: string): boolean {
    try {
      const date = new Date(dateString);
      const today = new Date();
      today.setHours(23, 59, 59, 999); // End of today
      return date <= today;
    } catch (error) {
      return false;
    }
  },

  // Validate hire date is not before birth date
  isHireDateValid(hireDate: string, birthDate?: string): boolean {
    if (!birthDate) return true; // If no birth date, hire date is valid
    
    try {
      const hire = new Date(hireDate);
      const birth = new Date(birthDate);
      return hire >= birth;
    } catch (error) {
      return false;
    }
  },

  // Generate initials from name
  generateInitials(firstName: string, lastName: string, title?: string): string {
    const initials = [];
    
    if (title && title.length > 0) {
      initials.push(title.charAt(0).toUpperCase());
    }
    
    if (firstName && firstName.length > 0) {
      initials.push(firstName.charAt(0).toUpperCase());
    }
    
    if (lastName && lastName.length > 0) {
      initials.push(lastName.charAt(0).toUpperCase());
    }
    
    return initials.slice(0, 3).join(''); // Max 3 characters
  },

  // Get current year
  getCurrentYear(): number {
    return new Date().getFullYear();
  },

  // Get years for vacation allowance dropdown
  getVacationYears(startYear?: number, endYear?: number): number[] {
    const currentYear = this.getCurrentYear();
    const start = startYear || currentYear - 2;
    const end = endYear || currentYear + 1;
    
    const years = [];
    for (let year = start; year <= end; year++) {
      years.push(year);
    }
    
    return years.sort((a, b) => b - a); // Descending order (newest first)
  },

  // Debounce function for search inputs
  debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: ReturnType<typeof setTimeout>;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  },

  // Format file size for display
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // Check if file type is allowed for avatar upload
  isAllowedImageType(file: File): boolean {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    return allowedTypes.includes(file.type);
  },

  // Check if file size is within limit
  isFileSizeValid(file: File, maxSizeMB: number = 5): boolean {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
  },

  // Generate random color for avatar background
  generateAvatarColor(seed: string): string {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
      '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
      '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
    ];
    
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
      hash = seed.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    const index = Math.abs(hash) % colors.length;
    return colors[index];
  },

  // Export data to CSV
  exportToCSV(data: any[], filename: string): void {
    if (!data.length) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          // Escape commas and quotes in CSV
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  },
};
