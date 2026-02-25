import { describe, it, expect, beforeEach } from 'vitest'
import { vacationService } from '../../services/vacationService'

describe('vacationService', () => {
  beforeEach(() => {
    // Reset any state if needed
  })

  describe('getVacationAllowances', () => {
    it('should fetch vacation allowances for an employee', async () => {
      const allowances = await vacationService.getVacationAllowances(1)
      
      expect(allowances).toHaveLength(1)
      expect(allowances[0]).toMatchObject({
        id: 1,
        employee_id: 1,
        year: 2024,
        annual_allowance: 30,
        carryover_days: 5,
        total_allowance: 35
      })
    })

    it('should return empty array for employee without allowances', async () => {
      const allowances = await vacationService.getVacationAllowances(999)
      expect(allowances).toHaveLength(0)
    })
  })

  describe('getVacationAllowance', () => {
    it('should fetch specific vacation allowance', async () => {
      const allowance = await vacationService.getVacationAllowance(1, 2024)
      
      expect(allowance).toMatchObject({
        id: 1,
        employee_id: 1,
        year: 2024,
        annual_allowance: 30,
        carryover_days: 5,
        total_allowance: 35
      })
    })

    it('should throw error for non-existent allowance', async () => {
      await expect(vacationService.getVacationAllowance(1, 2023))
        .rejects.toThrow()
    })
  })

  describe('createVacationAllowance', () => {
    it('should create a new vacation allowance', async () => {
      const newAllowanceData = {
        year: 2025,
        annual_allowance: 32,
        carryover_days: 3
      }

      const createdAllowance = await vacationService.createVacationAllowance(1, newAllowanceData)
      
      expect(createdAllowance).toMatchObject({
        ...newAllowanceData,
        employee_id: 1,
        total_allowance: 35, // 32 + 3
        id: expect.any(Number)
      })
      expect(createdAllowance.created_at).toBeDefined()
      expect(createdAllowance.updated_at).toBeDefined()
    })
  })

  describe('updateVacationAllowance', () => {
    it('should update an existing vacation allowance', async () => {
      const updates = {
        annual_allowance: 35,
        carryover_days: 2
      }

      const updatedAllowance = await vacationService.updateVacationAllowance(1, updates)
      
      expect(updatedAllowance).toMatchObject({
        id: 1,
        annual_allowance: 35,
        carryover_days: 2,
        total_allowance: 37 // 35 + 2
      })
    })

    it('should throw error for non-existent allowance', async () => {
      await expect(vacationService.updateVacationAllowance(999, { annual_allowance: 30 }))
        .rejects.toThrow()
    })
  })

  describe('deleteVacationAllowance', () => {
    it('should delete a vacation allowance', async () => {
      await expect(vacationService.deleteVacationAllowance(1)).resolves.not.toThrow()
    })

    it('should throw error for non-existent allowance', async () => {
      await expect(vacationService.deleteVacationAllowance(999)).rejects.toThrow()
    })
  })
})
