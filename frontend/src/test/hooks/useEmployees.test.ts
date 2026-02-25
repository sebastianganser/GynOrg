import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useEmployees, useCreateEmployee, useUpdateEmployee, useDeleteEmployee } from '../../hooks/useEmployees'
import { FederalState } from '../../types/employee'
import { TestWrapper } from '../utils/test-wrapper'

describe('useEmployees', () => {
  it('should fetch employees on mount', async () => {
    const { result } = renderHook(() => useEmployees(), {
      wrapper: TestWrapper
    })

    // Initially loading
    expect(result.current.isLoading).toBe(true)
    expect(result.current.data).toBeUndefined()

    // Wait for data to load
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toHaveLength(2)
    expect(result.current.data?.[0]).toMatchObject({
      id: 1,
      first_name: 'Maria',
      last_name: 'Müller',
      position: 'Gynäkologin'
    })
  })

  it('should handle loading state correctly', () => {
    const { result } = renderHook(() => useEmployees(), {
      wrapper: TestWrapper
    })

    expect(result.current.isLoading).toBe(true)
    expect(result.current.data).toBeUndefined()
    expect(result.current.error).toBeNull()
  })
})

describe('useCreateEmployee', () => {
  it('should create a new employee', async () => {
    const { result } = renderHook(() => useCreateEmployee(), {
      wrapper: TestWrapper
    })

    const newEmployeeData = {
      first_name: 'Test',
      last_name: 'User',
      position: 'Testposition',
      email: 'test@example.com',
      birth_date: '1990-01-01',
      date_hired: '2024-01-01',
      federal_state: FederalState.NW,
      active: true
    }

    expect(result.current.isIdle).toBe(true)

    result.current.mutate(newEmployeeData)

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toMatchObject({
      ...newEmployeeData,
      id: expect.any(Number)
    })
  })
})

describe('useUpdateEmployee', () => {
  it('should update an existing employee', async () => {
    const { result } = renderHook(() => useUpdateEmployee(), {
      wrapper: TestWrapper
    })

    const updates = {
      position: 'Senior Gynäkologin'
    }

    expect(result.current.isIdle).toBe(true)

    result.current.mutate({ id: 1, data: updates })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toMatchObject({
      id: 1,
      position: 'Senior Gynäkologin'
    })
  })
})

describe('useDeleteEmployee', () => {
  it('should delete an employee', async () => {
    const { result } = renderHook(() => useDeleteEmployee(), {
      wrapper: TestWrapper
    })

    expect(result.current.isIdle).toBe(true)

    result.current.mutate(1)

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.error).toBeNull()
  })
})
