import { describe, it, expect, beforeEach } from 'vitest'
import { employeeService } from '../../services/employeeService'
import { FederalState } from '../../types/employee'

describe('employeeService', () => {
  beforeEach(() => {
    // Reset any state if needed
  })

  describe('getEmployees', () => {
    it('should fetch all employees', async () => {
      const employees = await employeeService.getEmployees()

      expect(employees).toHaveLength(2)
      expect(employees[0]).toMatchObject({
        id: 1,
        first_name: 'Maria',
        last_name: 'Müller',
        position: 'Gynäkologin',
        email: 'maria.mueller@gynorg.de'
      })
    })
  })

  describe('getEmployee', () => {
    it('should fetch a specific employee', async () => {
      const employee = await employeeService.getEmployee(1)

      expect(employee).toMatchObject({
        id: 1,
        title: 'Dr.',
        first_name: 'Maria',
        last_name: 'Müller',
        position: 'Gynäkologin',
        email: 'maria.mueller@gynorg.de',
        federal_state: FederalState.NW
      })
    })

    it('should throw error for non-existent employee', async () => {
      await expect(employeeService.getEmployee(999)).rejects.toThrow()
    })
  })

  describe('createEmployee', () => {
    it('should create a new employee', async () => {
      const newEmployeeData = {
        first_name: 'Test',
        last_name: 'User',
        position: 'Testposition',
        email: 'test@example.com',
        birth_date: '1990-01-01',
        date_hired: '2024-01-01',
        federal_state: FederalState.NW,
        active: true,
        school_children: false
      }

      const createdEmployee = await employeeService.createEmployee(newEmployeeData)

      expect(createdEmployee).toMatchObject({
        ...newEmployeeData,
        id: expect.any(Number)
      })
      expect(createdEmployee.created_at).toBeDefined()
      expect(createdEmployee.updated_at).toBeDefined()
    })
  })

  describe('updateEmployee', () => {
    it('should update an existing employee', async () => {
      const updates = {
        position: 'Senior Gynäkologin',
        email: 'maria.mueller.senior@gynorg.de'
      }

      const updatedEmployee = await employeeService.updateEmployee(1, updates)

      expect(updatedEmployee).toMatchObject({
        id: 1,
        position: 'Senior Gynäkologin',
        email: 'maria.mueller.senior@gynorg.de'
      })
    })

    it('should throw error for non-existent employee', async () => {
      await expect(employeeService.updateEmployee(999, { position: 'Test' }))
        .rejects.toThrow()
    })
  })

  describe('deleteEmployee', () => {
    it('should deactivate an employee', async () => {
      await expect(employeeService.deleteEmployee(1)).resolves.not.toThrow()
    })

    it('should throw error for non-existent employee', async () => {
      await expect(employeeService.deleteEmployee(999)).rejects.toThrow()
    })
  })
})
