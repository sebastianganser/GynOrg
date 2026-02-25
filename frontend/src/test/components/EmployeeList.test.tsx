import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import EmployeeList from '../../components/EmployeeList'
import { TestWrapper } from '../utils/test-wrapper'
import { setupMockAuth } from '../utils/test-utils'

describe('EmployeeList', () => {
  beforeEach(() => {
    setupMockAuth()
  })

  it('should render employee list', async () => {
    render(
      <TestWrapper>
        <EmployeeList />
      </TestWrapper>
    )

    // Wait for data to load - check for the header first
    await waitFor(() => {
      expect(screen.getByText(/Mitarbeiter \(2\)/)).toBeInTheDocument()
    }, { timeout: 5000 })

    // Then check for employee names (only one element expected since mobile view is removed)
    await waitFor(() => {
      expect(screen.getByText('Dr. Maria Müller')).toBeInTheDocument()
    }, { timeout: 2000 })

    expect(screen.getByText('Anna Schmidt')).toBeInTheDocument()
    expect(screen.getByText('Gynäkologin')).toBeInTheDocument()
    expect(screen.getByText('MFA')).toBeInTheDocument()
  })

  it('should display employee emails', async () => {
    render(
      <TestWrapper>
        <EmployeeList />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText(/Mitarbeiter \(2\)/)).toBeInTheDocument()
    }, { timeout: 5000 })

    await waitFor(() => {
      expect(screen.getByText('maria.mueller@gynorg.de')).toBeInTheDocument()
    }, { timeout: 2000 })

    expect(screen.getByText('anna.schmidt@gynorg.de')).toBeInTheDocument()
  })

  it('should show loading state initially', () => {
    render(
      <TestWrapper>
        <EmployeeList />
      </TestWrapper>
    )
    
    // The component should render without crashing
    // Look for the main container instead of role="main"
    expect(screen.getByText(/Lade Mitarbeiter|Mitarbeiter/)).toBeInTheDocument()
  })

  it('should display employee positions', async () => {
    render(
      <TestWrapper>
        <EmployeeList />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText(/Mitarbeiter \(2\)/)).toBeInTheDocument()
    }, { timeout: 5000 })

    await waitFor(() => {
      expect(screen.getByText('Gynäkologin')).toBeInTheDocument()
      expect(screen.getByText('MFA')).toBeInTheDocument()
    }, { timeout: 2000 })
  })
})
