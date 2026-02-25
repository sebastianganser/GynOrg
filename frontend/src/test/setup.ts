import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll, beforeEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server'
import { setupMockAuth, clearMockAuth } from './utils/test-utils'

// Start server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

// Set up mock authentication before each test
beforeEach(() => {
  setupMockAuth()
})

// Clean up after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup()
  server.resetHandlers()
  clearMockAuth()
})

// Close server after all tests
afterAll(() => server.close())
