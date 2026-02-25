import { http, HttpResponse } from 'msw'
import { Employee, VacationAllowance, FederalState } from '../../types/employee'

// Mock data
const mockEmployees: Employee[] = [
  {
    id: 1,
    title: 'Dr.',
    first_name: 'Maria',
    last_name: 'Müller',
    position: 'Gynäkologin',
    email: 'maria.mueller@gynorg.de',
    birth_date: '1980-05-15',
    date_hired: '2020-01-15',
    federal_state: FederalState.NW,
    active: true,
    school_children: false,
    created_at: '2020-01-15T00:00:00Z',
    updated_at: '2020-01-15T00:00:00Z'
  },
  {
    id: 2,
    first_name: 'Anna',
    last_name: 'Schmidt',
    position: 'MFA',
    email: 'anna.schmidt@gynorg.de',
    birth_date: '1990-03-20',
    date_hired: '2021-06-01',
    federal_state: FederalState.BY,
    active: true,
    school_children: false,
    created_at: '2021-06-01T00:00:00Z',
    updated_at: '2021-06-01T00:00:00Z'
  }
]

const mockVacationAllowances: VacationAllowance[] = [
  {
    id: 1,
    employee_id: 1,
    year: 2024,
    annual_allowance: 30,
    carryover_days: 5,
    total_allowance: 35,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    employee_id: 2,
    year: 2024,
    annual_allowance: 28,
    carryover_days: 0,
    total_allowance: 28,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
]

export const handlers = [
  // Employee endpoints
  http.get('http://localhost:8000/api/v1/employees/', () => {
    return HttpResponse.json(mockEmployees)
  }),

  http.get('http://localhost:8000/api/v1/employees/:id', ({ params }) => {
    const id = parseInt(params.id as string)
    const employee = mockEmployees.find(emp => emp.id === id)
    if (!employee) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json(employee)
  }),

  http.post('http://localhost:8000/api/v1/employees/', async ({ request }) => {
    const newEmployee = await request.json() as Omit<Employee, 'id' | 'created_at' | 'updated_at'>
    const employee: Employee = {
      ...newEmployee,
      id: mockEmployees.length + 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    mockEmployees.push(employee)
    return HttpResponse.json(employee, { status: 201 })
  }),

  http.put('http://localhost:8000/api/v1/employees/:id', async ({ params, request }) => {
    const id = parseInt(params.id as string)
    const updates = await request.json() as Partial<Employee>
    const employeeIndex = mockEmployees.findIndex(emp => emp.id === id)

    if (employeeIndex === -1) {
      return new HttpResponse(null, { status: 404 })
    }

    mockEmployees[employeeIndex] = {
      ...mockEmployees[employeeIndex],
      ...updates,
      updated_at: new Date().toISOString()
    }

    return HttpResponse.json(mockEmployees[employeeIndex])
  }),

  http.delete('http://localhost:8000/api/v1/employees/:id', ({ params }) => {
    const id = parseInt(params.id as string)
    const employeeIndex = mockEmployees.findIndex(emp => emp.id === id)

    if (employeeIndex === -1) {
      return new HttpResponse(null, { status: 404 })
    }

    mockEmployees[employeeIndex].active = false
    return new HttpResponse(null, { status: 204 })
  }),

  // Vacation allowance endpoints
  http.get('http://localhost:8000/api/v1/employees/:employeeId/vacation-allowances/', ({ params }) => {
    const employeeId = parseInt(params.employeeId as string)
    const allowances = mockVacationAllowances.filter(va => va.employee_id === employeeId)
    return HttpResponse.json(allowances)
  }),

  http.get('http://localhost:8000/api/v1/employees/:employeeId/vacation-allowances/:year', ({ params }) => {
    const employeeId = parseInt(params.employeeId as string)
    const year = parseInt(params.year as string)
    const allowance = mockVacationAllowances.find(va =>
      va.employee_id === employeeId && va.year === year
    )

    if (!allowance) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(allowance)
  }),

  http.post('http://localhost:8000/api/v1/employees/:employeeId/vacation-allowances/', async ({ params, request }) => {
    const employeeId = parseInt(params.employeeId as string)
    const data = await request.json() as Omit<VacationAllowance, 'id' | 'employee_id' | 'total_allowance' | 'created_at' | 'updated_at'>

    const allowance: VacationAllowance = {
      ...data,
      id: mockVacationAllowances.length + 1,
      employee_id: employeeId,
      total_allowance: data.annual_allowance + data.carryover_days,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    mockVacationAllowances.push(allowance)
    return HttpResponse.json(allowance, { status: 201 })
  }),

  http.put('http://localhost:8000/api/v1/vacation-allowances/:id', async ({ params, request }) => {
    const id = parseInt(params.id as string)
    const updates = await request.json() as Partial<VacationAllowance>
    const allowanceIndex = mockVacationAllowances.findIndex(va => va.id === id)

    if (allowanceIndex === -1) {
      return new HttpResponse(null, { status: 404 })
    }

    const updatedAllowance = {
      ...mockVacationAllowances[allowanceIndex],
      ...updates,
      updated_at: new Date().toISOString()
    }

    // Recalculate total_allowance
    updatedAllowance.total_allowance = updatedAllowance.annual_allowance + updatedAllowance.carryover_days

    mockVacationAllowances[allowanceIndex] = updatedAllowance
    return HttpResponse.json(updatedAllowance)
  }),

  http.delete('http://localhost:8000/api/v1/vacation-allowances/:id', ({ params }) => {
    const id = parseInt(params.id as string)
    const allowanceIndex = mockVacationAllowances.findIndex(va => va.id === id)

    if (allowanceIndex === -1) {
      return new HttpResponse(null, { status: 404 })
    }

    mockVacationAllowances.splice(allowanceIndex, 1)
    return new HttpResponse(null, { status: 204 })
  }),

  // Federal states endpoint
  http.get('http://localhost:8000/api/v1/federal-states/', () => {
    const federalStates = Object.values(FederalState).map(state => ({
      code: Object.keys(FederalState)[Object.values(FederalState).indexOf(state)],
      name: state
    }))
    return HttpResponse.json(federalStates)
  }),

  // Auth endpoints (mock)
  http.post('http://localhost:8000/api/v1/auth/login', async ({ request }) => {
    const credentials = await request.json() as { username: string; password: string }

    if (credentials.username === 'MGanser' && credentials.password === 'M4rvelf4n') {
      return HttpResponse.json({
        access_token: 'mock-jwt-token',
        token_type: 'bearer'
      })
    }

    return new HttpResponse(null, { status: 401 })
  })
]
