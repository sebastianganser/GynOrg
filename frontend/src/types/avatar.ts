// Avatar-spezifische Interfaces und Types
import { Employee } from './employee';

export interface AvatarUploadResponse {
  message: string;
  avatar_url: string;
  avatar_filename: string;
}

export interface AvatarUploadError {
  detail: string;
  error_code?: string;
}

// Erlaubte Dateiformate für Avatar-Upload
export const ALLOWED_AVATAR_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'] as const;
export type AvatarFormat = typeof ALLOWED_AVATAR_FORMATS[number];

// Maximale Dateigröße für Avatar (5MB)
export const MAX_AVATAR_SIZE = 5 * 1024 * 1024; // 5MB in bytes

// Avatar-Größen für verschiedene Verwendungszwecke
export const AVATAR_SIZES = {
  small: 32,    // für Listen
  medium: 64,   // für Karten
  large: 128,   // für Detailansicht
  xlarge: 256   // für Profil-Editor
} as const;

export type AvatarSize = keyof typeof AVATAR_SIZES;

// Avatar-Upload-Status
export enum AvatarUploadStatus {
  IDLE = 'idle',
  UPLOADING = 'uploading',
  SUCCESS = 'success',
  ERROR = 'error'
}

// Props für Avatar-Komponenten
export interface AvatarDisplayProps {
  employee: {
    id: number;
    first_name: string;
    last_name: string;
    initials?: string;
    avatar_url?: string;
  };
  size?: AvatarSize;
  className?: string;
  showFallback?: boolean;
}

export interface AvatarUploadProps {
  employeeId: number;
  currentAvatarUrl?: string;
  onUploadSuccess?: (avatarUrl: string) => void;
  onUploadError?: (error: string) => void;
  size?: AvatarSize;
  className?: string;
}

export interface AvatarEditorProps {
  employee: Employee;
  onAvatarChange?: (avatarUrl: string | null) => void;
  size?: AvatarSize;
  className?: string;
}

// Utility-Funktionen für Avatar-Handling
export const getAvatarInitials = (firstName: string, lastName: string, customInitials?: string): string => {
  if (customInitials) {
    return customInitials;
  }
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
};

export const isValidAvatarFile = (file: File): { valid: boolean; error?: string } => {
  // Prüfe Dateigröße
  if (file.size > MAX_AVATAR_SIZE) {
    return {
      valid: false,
      error: `Datei ist zu groß. Maximale Größe: ${Math.round(MAX_AVATAR_SIZE / 1024 / 1024)}MB`
    };
  }

  // Prüfe Dateiformat
  if (!ALLOWED_AVATAR_FORMATS.includes(file.type as AvatarFormat)) {
    return {
      valid: false,
      error: `Ungültiges Dateiformat. Erlaubt: ${ALLOWED_AVATAR_FORMATS.join(', ')}`
    };
  }

  return { valid: true };
};

export const getAvatarSizeInPx = (size: AvatarSize): number => {
  return AVATAR_SIZES[size];
};

// CSS-Klassen für Avatar-Größen (Tailwind)
export const getAvatarSizeClasses = (size: AvatarSize): string => {
  const sizeMap = {
    small: 'w-8 h-8 text-xs',
    medium: 'w-16 h-16 text-sm',
    large: 'w-32 h-32 text-lg',
    xlarge: 'w-64 h-64 text-2xl'
  };

  return sizeMap[size];
};
