
import React, { useState } from 'react';
import EmployeeList from '../components/EmployeeList';
import { CreateEmployeeForm } from '../components/CreateEmployeeForm';
import { EditEmployeeForm } from '../components/EditEmployeeForm';
import { VacationEntitlementManager } from '../components/VacationEntitlementManager';
import { Button } from '../components/ui/button';
import { Modal } from '../components/ui/modal';
import { Employee } from '../types/employee';

const Employees: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [vacationEmployee, setVacationEmployee] = useState<Employee | null>(null);

  const fetchEmployees = async () => {
    // TODO: Implement fetching employees
  };

  const handleEditEmployee = (employee: Employee) => {
    setSelectedEmployee(employee);
    setShowCreateForm(false);
  };

  const handleCreateEmployee = () => {
    setSelectedEmployee(null);
    setShowCreateForm(true);
  };

  const handleCloseForm = () => {
    setSelectedEmployee(null);
    setShowCreateForm(false);
    setVacationEmployee(null); // Also close vacation form
  };

  return (
    <div className="p-6">
      <div className="space-y-6">
        <EmployeeList
          onEditEmployee={handleEditEmployee}
          onManageVacation={(employee) => setVacationEmployee(employee)}
          onCreateEmployee={handleCreateEmployee}
        />

        <Modal
          isOpen={showCreateForm}
          onClose={handleCloseForm}
          title="Neuen Mitarbeiter hinzufügen"
          size="lg"
          closeOnBackdropClick={false}
        >
          <CreateEmployeeForm
            onSuccess={handleCloseForm}
            onCancel={handleCloseForm}
          />
        </Modal>

        <Modal
          isOpen={!!selectedEmployee}
          onClose={handleCloseForm}
          title="Mitarbeiter bearbeiten"
          size="lg"
          closeOnBackdropClick={false}
        >
          {selectedEmployee && (
            <EditEmployeeForm
              employee={selectedEmployee}
              onSuccess={handleCloseForm}
              onCancel={handleCloseForm}
            />
          )}
        </Modal>

        <Modal
          isOpen={!!vacationEmployee}
          onClose={() => setVacationEmployee(null)}
          title={vacationEmployee ? `Urlaubsanspruch: ${vacationEmployee.first_name} ${vacationEmployee.last_name} ` : 'Urlaubsanspruch verwalten'}
          size="lg"
        >
          {vacationEmployee && (
            <VacationEntitlementManager employee={vacationEmployee} />
          )}
        </Modal>
      </div>
    </div>
  );
};

export default Employees;
