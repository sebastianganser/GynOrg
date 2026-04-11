import { API_BASE_URL } from './config';
import { authService } from './authService';

interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

interface ApiError {
  message: string;
  status?: number;
  data?: any;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T = any>(
    method: string,
    endpoint: string,
    data?: any,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      method,
      headers: {
        ...authService.getAuthHeaders(),
        ...(options?.headers || {}),
      },
      ...options,
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      config.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, config);
      
      let responseData: any;
      if (response.status === 204) {
        responseData = null;
      } else {
        const contentType = response.headers.get('content-type');
        const text = await response.text();
        if (text && contentType && contentType.includes('application/json')) {
          try {
            responseData = JSON.parse(text);
          } catch (e) {
            responseData = text;
          }
        } else {
          responseData = text;
        }
      }

      if (!response.ok) {
        if (response.status === 401) {
          authService.logout();
          window.location.reload();
        }
        const error: ApiError = {
          message: `Request failed with status ${response.status}`,
          status: response.status,
          data: responseData,
        };
        throw error;
      }

      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
      };
    } catch (error) {
      if ((error as ApiError).status) {
        throw error;
      }
      throw {
        message: error instanceof Error ? error.message : 'Network error',
        data: null,
      } as ApiError;
    }
  }

  async get<T = any>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, undefined, options);
  }

  async post<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, data, options);
  }

  async put<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', endpoint, data, options);
  }

  async patch<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', endpoint, data, options);
  }

  async delete<T = any>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', endpoint, undefined, options);
  }
}

export const api = new ApiClient(API_BASE_URL);
