import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { employeeService } from '../services/employeeService';
import type { Employee, EmployeeUpdate } from '../types/employee';
import { getFederalStateChoices } from '../types/employee';
import AvatarUpload from './AvatarUpload';
import EmployeeDetailTabs, { TabItem, TabIcons, useEmployeeDetailTabs } from './EmployeeDetailTabs';
// EmployeePreferencesTab import removed
// EmployeePreferencesTab import removed

interface EditEmployeeFormProps {
  employee: Employee;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const EditEmployeeForm: React.FC<EditEmployeeFormProps> = ({
  employee,
  onSuccess,
  onCancel,
}) => {
  // Tab management
  const {
    activeTab,
    handleTabChange,
    hasUnsavedChanges,
    markTabAsChanged,
    clearAllChanges
  } = useEmployeeDetailTabs('personal');

  // Employee form state
  const [formData, setFormData] = useState<EmployeeUpdate>({
    first_name: employee.first_name,
    last_name: employee.last_name,
    email: employee.email,
    title: employee.title || '',
    position: employee.position || '',
    vacation_allowance: employee.vacation_allowance,
    date_hired: employee.date_hired || '',
    birth_date: employee.birth_date || '',
    federal_state: employee.federal_state,
    active: employee.active,
    school_children: employee.school_children,
    youngest_child_birth_year: employee.youngest_child_birth_year,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const queryClient = useQueryClient();

  // Reset form data when employee changes
  useEffect(() => {
    const newFormData = {
      first_name: employee.first_name,
      last_name: employee.last_name,
      email: employee.email,
      title: employee.title || '',
      position: employee.position || '',
      vacation_allowance: employee.vacation_allowance,
      date_hired: employee.date_hired || '',
      birth_date: employee.birth_date || '',
      federal_state: employee.federal_state,
      active: employee.active,
      school_children: employee.school_children,
      youngest_child_birth_year: employee.youngest_child_birth_year,
    };
    setFormData(newFormData);
    setErrors({});
    clearAllChanges();
  }, [employee, clearAllChanges]);

  const updateEmployeeMutation = useMutation({
    mutationFn: (data: EmployeeUpdate) => employeeService.updateEmployee(employee.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setErrors({});
      clearAllChanges();
      onSuccess?.();
    },
    onError: (error: any) => {
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          const validationErrors: Record<string, string> = {};
          error.response.data.detail.forEach((err: any) => {
            if (err.loc && err.msg) {
              const field = err.loc[err.loc.length - 1];
              validationErrors[field] = err.msg;
            }
          });
          setErrors(validationErrors);
        } else {
          setErrors({ general: error.response.data.detail });
        }
      } else {
        setErrors({ general: 'Ein Fehler ist aufgetreten beim Aktualisieren des Mitarbeiters.' });
      }
    },
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let processedValue: any = value;

    if (type === 'checkbox') {
      processedValue = (e.target as HTMLInputElement).checked;
    } else if (type === 'number') {
      processedValue = value === '' ? undefined : parseInt(value, 10);
    }

    setFormData((prev: EmployeeUpdate) => ({
      ...prev,
      [name]: processedValue,
    }));

    // Clear youngest child birth year if school children is unchecked
    if (name === 'school_children' && !processedValue) {
      setFormData((prev: EmployeeUpdate) => ({
        ...prev,
        youngest_child_birth_year: undefined,
      }));
    }

    // Mark personal tab as changed
    markTabAsChanged('personal', true);

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev: Record<string, string>) => ({ ...prev, [name]: '' }));
    }
  };

  const handleAvatarUpdate = (updatedEmployee: Employee) => {
    console.log('Avatar updated for employee:', updatedEmployee.id);
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.first_name?.trim()) {
      newErrors.first_name = 'Vorname ist erforderlich';
    }

    if (!formData.last_name?.trim()) {
      newErrors.last_name = 'Nachname ist erforderlich';
    }

    if (!formData.email?.trim()) {
      newErrors.email = 'E-Mail ist erforderlich';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Ungültige E-Mail-Adresse';
    }

    if (formData.title && formData.title.length > 100) {
      newErrors.title = 'Titel darf maximal 100 Zeichen lang sein';
    }

    if (formData.position && formData.position.length > 100) {
      newErrors.position = 'Position darf maximal 100 Zeichen lang sein';
    }



    if (formData.school_children && formData.youngest_child_birth_year) {
      const year = formData.youngest_child_birth_year;
      const currentYear = new Date().getFullYear();
      if (year < 1900 || year > currentYear) {
        newErrors.youngest_child_birth_year = `Gültiges Geburtsjahr (max. ${currentYear}) angeben`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      // Prepare data for submission - only include changed fields
      const submitData: EmployeeUpdate = {};

      if (formData.first_name?.trim() && formData.first_name !== employee.first_name) {
        submitData.first_name = formData.first_name.trim();
      }

      if (formData.last_name?.trim() && formData.last_name !== employee.last_name) {
        submitData.last_name = formData.last_name.trim();
      }

      if (formData.email?.trim() && formData.email !== employee.email) {
        submitData.email = formData.email.trim();
      }

      if (formData.title !== employee.title) {
        submitData.title = formData.title?.trim() || undefined;
      }

      if (formData.position !== employee.position) {
        submitData.position = formData.position?.trim() || undefined;
      }



      if (formData.date_hired !== employee.date_hired) {
        submitData.date_hired = formData.date_hired?.trim() || undefined;
      }

      if (formData.birth_date !== employee.birth_date) {
        submitData.birth_date = formData.birth_date?.trim() || undefined;
      }

      if (formData.federal_state !== employee.federal_state) {
        submitData.federal_state = formData.federal_state;
      }

      if (formData.school_children !== employee.school_children) {
        submitData.school_children = formData.school_children;
      }

      if (formData.active !== employee.active) {
        submitData.active = formData.active;
      }

      if (formData.youngest_child_birth_year !== employee.youngest_child_birth_year) {
        submitData.youngest_child_birth_year = formData.youngest_child_birth_year;
      }

      // Only submit if there are actual changes
      if (Object.keys(submitData).length > 0) {
        updateEmployeeMutation.mutate(submitData);
      } else {
        // No changes made, just close the form
        onSuccess?.();
      }
    }
  };

  const formatDateForInput = (dateString: string | null): string => {
    if (!dateString) return '';
    return dateString.split('T')[0];
  };

  // Personal Information Tab Content
  const PersonalInfoTab = () => (
    <div className="space-y-6">
      {/* Avatar Section */}
      <div className="border-b border-gray-200 pb-6">
        <AvatarUpload
          employee={employee}
          onAvatarUpdate={handleAvatarUpdate}
        />
      </div>

      {/* Personal Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Persönliche Informationen</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
              Vorname *
            </label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name || ''}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.first_name ? 'border-red-500' : 'border-gray-300'
                }`}
              placeholder="Vorname eingeben"
              maxLength={50}
            />
            {errors.first_name && (
              <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
            )}
          </div>

          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
              Nachname *
            </label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name || ''}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.last_name ? 'border-red-500' : 'border-gray-300'
                }`}
              placeholder="Nachname eingeben"
              maxLength={50}
            />
            {errors.last_name && (
              <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            E-Mail *
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email || ''}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
            placeholder="E-Mail-Adresse eingeben"
            maxLength={100}
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600">{errors.email}</p>
          )}
        </div>

        <div>
          <label htmlFor="birth_date" className="block text-sm font-medium text-gray-700 mb-1">
            Geburtsdatum
          </label>
          <input
            type="date"
            id="birth_date"
            name="birth_date"
            value={formatDateForInput(formData.birth_date || '')}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.birth_date ? 'border-red-500' : 'border-gray-300'
              }`}
          />
          {errors.birth_date && (
            <p className="mt-1 text-sm text-red-600">{errors.birth_date}</p>
          )}
        </div>
      </div>

      {/* Work Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Berufliche Informationen</h3>

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Titel
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title || ''}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
            placeholder="z.B. Dr., Prof. (optional)"
            maxLength={20}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
          )}
        </div>

        <div>
          <label htmlFor="position" className="block text-sm font-medium text-gray-700 mb-1">
            Position
          </label>
          <input
            type="text"
            id="position"
            name="position"
            value={formData.position || ''}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.position ? 'border-red-500' : 'border-gray-300'
              }`}
            placeholder="Position eingeben (optional)"
            maxLength={100}
          />
          {errors.position && (
            <p className="mt-1 text-sm text-red-600">{errors.position}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">


          <div>
            <label htmlFor="date_hired" className="block text-sm font-medium text-gray-700 mb-1">
              Einstellungsdatum
            </label>
            <input
              type="date"
              id="date_hired"
              name="date_hired"
              value={formatDateForInput(formData.date_hired || '')}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.date_hired ? 'border-red-500' : 'border-gray-300'
                }`}
            />
            {errors.date_hired && (
              <p className="mt-1 text-sm text-red-600">{errors.date_hired}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="federal_state" className="block text-sm font-medium text-gray-700 mb-1">
            Bundesland *
          </label>
          <select
            id="federal_state"
            name="federal_state"
            value={formData.federal_state || ''}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.federal_state ? 'border-red-500' : 'border-gray-300'
              }`}
          >
            <option value="">Bundesland auswählen</option>
            {getFederalStateChoices().map((state) => (
              <option key={state.code} value={state.code}>
                {state.name}
              </option>
            ))}
          </select>
          {errors.federal_state && (
            <p className="mt-1 text-sm text-red-600">{errors.federal_state}</p>
          )}
        </div>

        <div className="flex flex-col gap-4 pt-6 mt-4 border-t border-gray-100">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="active"
              name="active"
              checked={formData.active ?? true}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
              Aktiver Mitarbeiter
            </label>
          </div>

          <div className="flex flex-col space-y-2">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="school_children"
                name="school_children"
                checked={formData.school_children ?? false}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="school_children" className="ml-2 block text-sm text-gray-700">
                Schulpflichtige Kinder
              </label>
            </div>

            {formData.school_children && (
              <div className="ml-6 animate-in slide-in-from-top-2 fade-in duration-200">
                <label htmlFor="youngest_child_birth_year" className="block text-xs text-gray-500 mb-1">
                  Geburtsjahr des jüngsten Kindes (optional)
                </label>
                <input
                  type="number"
                  id="youngest_child_birth_year"
                  name="youngest_child_birth_year"
                  value={formData.youngest_child_birth_year || ''}
                  onChange={handleInputChange}
                  min="1900"
                  max={new Date().getFullYear()}
                  className={`w-32 px-3 py-1 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white ${errors.youngest_child_birth_year ? 'border-red-500' : 'border-gray-300'
                    }`}
                  placeholder="z.B. 2015"
                />
                {errors.youngest_child_birth_year && (
                  <p className="mt-1 text-xs text-red-600">{errors.youngest_child_birth_year}</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );



  // Define tabs
  const tabs: TabItem[] = [
    {
      id: 'personal',
      label: 'Persönliche Daten',
      icon: <TabIcons.User />,
      content: <PersonalInfoTab />,
      badge: hasUnsavedChanges.personal ? '●' : undefined
    },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* ARIA Live Region for Form Status */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id="edit-form-status"
      >
        {updateEmployeeMutation.isPending && "Mitarbeiter wird aktualisiert..."}
        {Object.keys(errors).length > 0 && `Formular enthält ${Object.keys(errors).length} Fehler. Bitte korrigieren Sie die markierten Felder.`}
        {updateEmployeeMutation.isSuccess && "Mitarbeiter wurde erfolgreich aktualisiert."}
      </div>

      {/* General Errors */}
      {errors.general && (
        <div
          className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded"
          role="alert"
          aria-describedby="edit-form-status"
        >
          {errors.general}
        </div>
      )}

      {/* Tab System */}
      <EmployeeDetailTabs
        tabs={tabs}
        defaultActiveTab="personal"
        onTabChange={handleTabChange}
        className="mb-6"
      />

      {/* Action Buttons - Only show for personal tab */}
      {activeTab === 'personal' && (
        <form onSubmit={handleSubmit}>
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
                disabled={updateEmployeeMutation.isPending}
              >
                Abbrechen
              </button>
            )}
            <button
              type="submit"
              disabled={updateEmployeeMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {updateEmployeeMutation.isPending ? 'Wird aktualisiert...' : 'Änderungen speichern'}
            </button>
          </div>
        </form>
      )}

      {/* Global Action Buttons for other tabs */}
      {activeTab !== 'personal' && (
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Schließen
            </button>
          )}
        </div>
      )}
    </div>
  );
};
