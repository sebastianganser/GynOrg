import { Employee } from '../types/employee';

export interface CropData {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface AvatarUploadResponse {
  employee: Employee;
  avatar_url: string;
  avatar_filename: string;
}

class AvatarService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';
  }

  /**
   * Upload eines Avatar-Bildes mit Crop-Daten
   */
  async uploadAvatar(
    employeeId: number,
    file: File,
    cropData?: CropData,
    onProgress?: (progress: UploadProgress) => void,
    abortController?: AbortController
  ): Promise<Employee> {
    try {
      // Validierung der Datei
      this.validateFile(file);

      const formData = new FormData();
      formData.append('file', file);
      
      if (cropData) {
        formData.append('crop_x', cropData.x.toString());
        formData.append('crop_y', cropData.y.toString());
        formData.append('crop_width', cropData.width.toString());
        formData.append('crop_height', cropData.height.toString());
      }

      const response = await this.uploadWithProgress(
        `${this.baseUrl}/api/v1/employees/${employeeId}/avatar`,
        formData,
        onProgress,
        abortController
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload fehlgeschlagen: ${response.status}`);
      }

      const result: AvatarUploadResponse = await response.json();
      return result.employee;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Upload wurde abgebrochen');
      }
      throw error;
    }
  }

  /**
   * Avatar löschen
   */
  async deleteAvatar(employeeId: number): Promise<Employee> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/employees/${employeeId}/avatar`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Löschen fehlgeschlagen: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  /**
   * Initialen eines Mitarbeiters aktualisieren
   */
  async updateInitials(employeeId: number, initials: string): Promise<Employee> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/employees/${employeeId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ initials: initials.toUpperCase() }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Update fehlgeschlagen: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  /**
   * Datei-Validierung
   */
  private validateFile(file: File): void {
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

    if (file.size > maxSize) {
      throw new Error('Datei ist zu groß. Maximum: 5MB');
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error('Ungültiges Dateiformat. Erlaubt: JPG, PNG, WebP');
    }
  }

  /**
   * Upload mit Progress-Tracking
   */
  private uploadWithProgress(
    url: string,
    formData: FormData,
    onProgress?: (progress: UploadProgress) => void,
    abortController?: AbortController
  ): Promise<Response> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Progress Event Handler
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress: UploadProgress = {
              loaded: event.loaded,
              total: event.total,
              percentage: Math.round((event.loaded / event.total) * 100)
            };
            onProgress(progress);
          }
        });
      }

      // Abort Controller
      if (abortController) {
        abortController.signal.addEventListener('abort', () => {
          xhr.abort();
        });
      }

      // Response Handler
      xhr.addEventListener('load', () => {
        const response = new Response(xhr.response, {
          status: xhr.status,
          statusText: xhr.statusText,
          headers: new Headers(xhr.getAllResponseHeaders().split('\r\n').reduce((headers, line) => {
            const [key, value] = line.split(': ');
            if (key && value) {
              headers[key] = value;
            }
            return headers;
          }, {} as Record<string, string>))
        });
        resolve(response);
      });

      // Error Handler
      xhr.addEventListener('error', () => {
        reject(new Error('Netzwerkfehler beim Upload'));
      });

      // Abort Handler
      xhr.addEventListener('abort', () => {
        reject(new Error('Upload wurde abgebrochen'));
      });

      // Start Upload
      xhr.open('POST', url);
      xhr.send(formData);
    });
  }

  /**
   * Bild zu Canvas konvertieren für Crop-Vorschau
   */
  async cropImageToBlob(
    imageFile: File,
    cropData: CropData,
    outputSize: { width: number; height: number } = { width: 200, height: 200 }
  ): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        reject(new Error('Canvas Context nicht verfügbar'));
        return;
      }

      img.onload = () => {
        canvas.width = outputSize.width;
        canvas.height = outputSize.height;

        // Crop und resize
        ctx.drawImage(
          img,
          cropData.x,
          cropData.y,
          cropData.width,
          cropData.height,
          0,
          0,
          outputSize.width,
          outputSize.height
        );

        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Fehler beim Erstellen des Crop-Bildes'));
          }
        }, 'image/jpeg', 0.9);
      };

      img.onerror = () => {
        reject(new Error('Fehler beim Laden des Bildes'));
      };

      img.src = URL.createObjectURL(imageFile);
    });
  }
}

export const avatarService = new AvatarService();
export default avatarService;
