import { authService } from '../../services/authService'

// Mock authentication utilities for tests
export const mockAuthToken = 'mock-jwt-token'

export const setupMockAuth = () => {
  // Set mock token in localStorage
  localStorage.setItem('auth_token', mockAuthToken)
  // Force authService to reload token from localStorage
  ;(authService as any).token = mockAuthToken
}

export const clearMockAuth = () => {
  // Clear mock token from localStorage
  localStorage.removeItem('auth_token')
  // Clear token from authService
  ;(authService as any).token = null
}

export const mockAuthHeaders = {
  'Authorization': `Bearer ${mockAuthToken}`,
  'Content-Type': 'application/json'
}

// Mock user data
export const mockUser = {
  id: 1,
  username: 'admin',
  email: 'admin@gynorg.de'
}

// Helper to wait for async operations in tests
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))
