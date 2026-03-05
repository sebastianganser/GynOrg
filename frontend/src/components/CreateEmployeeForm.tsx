import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { employeeService } from '../services/employeeService';
import { jobPositionService } from '../services/jobPositionService';
import type { EmployeeCreateForm } from '../types/employee';
import { FederalState, getFederalStateChoices } from '../types/employee';
import 'react-image-crop/dist/ReactCrop.css';

interface CreateEmployeeFormProps {
  onSuccess?: (employeeId: number) => void;
  onCancel?: () => void;
}

const titleOptions = [
  { value: '', label: 'Kein Titel' },
  { value: 'Dr.', label: 'Dr.' },
  { value: 'Prof.', label: 'Prof.' },
  { value: 'Prof. Dr.', label: 'Prof. Dr.' },
];

export const CreateEmployeeForm: React.FC<CreateEmployeeFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState<EmployeeCreateForm>({
    title: '',
    first_name: '',
    last_name: '',
    position: '',
    email: '',
    birth_date: '',
    date_hired: '',
    federal_state: FederalState.ST, // Default: Sachsen-Anhalt
    active: true,
    calendar_color: '#3B82F6',
    initials: '',
    school_children: false,
    youngest_child_birth_year: undefined,
  });

  const [isInitialsManuallySet, setIsInitialsManuallySet] = useState(false);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const queryClient = useQueryClient();

  const { data: jobPositions } = useQuery({
    queryKey: ['jobPositions', 'active'],
    queryFn: () => jobPositionService.getPositions(true),
  });

  const createEmployeeMutation = useMutation({
    mutationFn: employeeService.createEmployee,
    onSuccess: (newEmployee) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setFormData({
        title: '',
        first_name: '',
        last_name: '',
        position: '',
        email: '',
        birth_date: '',
        date_hired: '',
        federal_state: FederalState.ST, // Default: Sachsen-Anhalt
        active: true,
        calendar_color: '#3B82F6',
        school_children: false,
        youngest_child_birth_year: undefined,
      });
      setErrors({});
      onSuccess?.(newEmployee.id);
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
        setErrors({ general: 'Ein Fehler ist aufgetreten beim Erstellen des Mitarbeiters.' });
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

    setFormData((prev: EmployeeCreateForm) => ({
      ...prev,
      [name]: processedValue,
    }));

    // Clear youngest child birth year if school children is unchecked
    if (name === 'school_children' && !processedValue) {
      setFormData((prev: EmployeeCreateForm) => ({
        ...prev,
        youngest_child_birth_year: undefined,
      }));
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev: Record<string, string>) => ({ ...prev, [name]: '' }));
    }

    // Manual initials override checking
    if (name === 'initials') {
      setIsInitialsManuallySet(true);
    }
  };

  // Auto-generate initials effect
  useEffect(() => {
    if (!isInitialsManuallySet) {
      const firstInitial = formData.first_name?.charAt(0) || '';
      const lastInitial = formData.last_name?.charAt(0) || '';
      const autoInitials = (firstInitial + lastInitial).toUpperCase();
      setFormData((prev) => ({ ...prev, initials: autoInitials }));
    }
  }, [formData.first_name, formData.last_name, isInitialsManuallySet]);

  const validateEmail = (email: string): string | null => {
    // Grundlegende Struktur prüfen
    if (!email.includes('@')) {
      return 'E-Mail-Adresse muss ein @ enthalten';
    }

    const parts = email.split('@');
    if (parts.length !== 2) {
      return 'E-Mail-Adresse darf nur ein @ enthalten';
    }

    const [localPart, domainPart] = parts;

    // Lokaler Teil (vor @) prüfen
    if (!localPart || localPart.length === 0) {
      return 'E-Mail-Adresse benötigt einen Benutzernamen vor dem @';
    }

    // Doppelte Punkte prüfen
    if (localPart.includes('..') || domainPart.includes('..')) {
      return 'E-Mail-Adresse darf keine aufeinanderfolgenden Punkte enthalten';
    }

    // Domain-Teil prüfen
    if (!domainPart || domainPart.length === 0) {
      return 'E-Mail-Adresse benötigt eine Domain nach dem @';
    }

    if (!domainPart.includes('.')) {
      return 'Domain muss eine Top-Level-Domain enthalten (z.B. .com, .de)';
    }

    // Grundlegende Regex für finale Validierung
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      return 'Bitte geben Sie eine gültige E-Mail-Adresse ein';
    }

    return null; // Kein Fehler
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Pflichtfelder
    if (!formData.first_name?.trim()) {
      newErrors.first_name = 'Vorname ist erforderlich';
    }

    if (!formData.last_name?.trim()) {
      newErrors.last_name = 'Nachname ist erforderlich';
    }

    if (!formData.email?.trim()) {
      newErrors.email = 'E-Mail ist erforderlich';
    } else {
      const emailError = validateEmail(formData.email);
      if (emailError) {
        newErrors.email = emailError;
      }
    }

    if (!formData.federal_state) {
      newErrors.federal_state = 'Bundesland ist erforderlich';
    }

    // Optionale Felder validieren
    if (formData.position && formData.position.length > 100) {
      newErrors.position = 'Position darf maximal 100 Zeichen lang sein';
    }

    // Datum-Validierungen
    if (formData.birth_date) {
      const birthDate = new Date(formData.birth_date);
      const today = new Date();
      if (birthDate > today) {
        newErrors.birth_date = 'Geburtsdatum darf nicht in der Zukunft liegen';
      }

      // Mindestens 16 Jahre alt
      const minAge = new Date();
      minAge.setFullYear(today.getFullYear() - 16);
      if (birthDate > minAge) {
        newErrors.birth_date = 'Mitarbeiter muss mindestens 16 Jahre alt sein';
      }
    }

    if (formData.date_hired) {
      const hiredDate = new Date(formData.date_hired);
      const today = new Date();

      // Erlaubt zukünftige Einstellungsdaten bis zu 1 Jahr im Voraus
      const maxFutureDate = new Date();
      maxFutureDate.setFullYear(today.getFullYear() + 1);

      if (hiredDate > maxFutureDate) {
        newErrors.date_hired = 'Einstellungsdatum darf maximal 1 Jahr in der Zukunft liegen';
      }

      // Einstellungsdatum nicht vor Geburtsdatum
      if (formData.birth_date) {
        const birthDate = new Date(formData.birth_date);
        const minHireAge = new Date(birthDate);
        minHireAge.setFullYear(birthDate.getFullYear() + 14); // Mindestens 14 Jahre alt bei Einstellung

        if (hiredDate < minHireAge) {
          newErrors.date_hired = 'Einstellungsdatum muss nach dem 14. Geburtstag liegen';
        }
      }
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
      // Prepare data for submission - remove empty optional fields
      const submitData: EmployeeCreateForm = {
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim(),
        federal_state: formData.federal_state,
        active: formData.active ?? true,
        calendar_color: formData.calendar_color,
        school_children: formData.school_children ?? false,
      };

      if (formData.initials?.trim()) {
        submitData.initials = formData.initials.trim().toUpperCase();
      }

      if (formData.title?.trim()) {
        submitData.title = formData.title.trim();
      }

      if (formData.position?.trim()) {
        submitData.position = formData.position.trim();
      }

      if (formData.birth_date?.trim()) {
        submitData.birth_date = formData.birth_date.trim();
      }

      if (formData.date_hired?.trim()) {
        submitData.date_hired = formData.date_hired.trim();
      }

      if (formData.school_children && formData.youngest_child_birth_year) {
        submitData.youngest_child_birth_year = formData.youngest_child_birth_year;
      }

      createEmployeeMutation.mutate(submitData);
    }
  };

  const federalStateChoices = getFederalStateChoices();

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Neuen Mitarbeiter erstellen</h2>

      {/* ARIA Live Region for Form Status */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id="form-status"
      >
        {createEmployeeMutation.isPending && "Mitarbeiter wird erstellt..."}
        {Object.keys(errors).length > 0 && `Formular enthält ${Object.keys(errors).length} Fehler. Bitte korrigieren Sie die markierten Felder.`}
        {createEmployeeMutation.isSuccess && "Mitarbeiter wurde erfolgreich erstellt."}
      </div>

      {errors.general && (
        <div
          className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded"
          role="alert"
          aria-describedby="form-status"
        >
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Persönliche Daten */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Persönliche Daten</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Titel
              </label>
              <select
                id="title"
                name="title"
                value={formData.title || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
              >
                {titleOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

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

            <div>
              <label htmlFor="initials" className="block text-sm font-medium text-gray-700 mb-1">
                Initialien
              </label>
              <input
                type="text"
                id="initials"
                name="initials"
                value={formData.initials || ''}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.initials ? 'border-red-500' : 'border-gray-300'
                  }`}
                placeholder="2-3 Buchstaben"
                maxLength={3}
                style={{ textTransform: 'uppercase' }}
              />
              {errors.initials && (
                <p className="mt-1 text-sm text-red-600">{errors.initials}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
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
                placeholder="email@beispiel.de"
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
                value={formData.birth_date || ''}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.birth_date ? 'border-red-500' : 'border-gray-300'
                  }`}
              />
              {errors.birth_date && (
                <p className="mt-1 text-sm text-red-600">{errors.birth_date}</p>
              )}
            </div>
          </div>
        </div>

        {/* Arbeitsdaten */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Arbeitsdaten</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="position" className="block text-sm font-medium text-gray-700 mb-1">
                Position
              </label>
              <select
                id="position"
                name="position"
                value={formData.position || ''}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.position ? 'border-red-500' : 'border-gray-300'
                  }`}
              >
                <option value="">Keine Auswahl</option>
                {jobPositions?.map((pos) => (
                  <option key={pos.id} value={pos.name}>
                    {pos.name}
                  </option>
                ))}
              </select>
              {errors.position && (
                <p className="mt-1 text-sm text-red-600">{errors.position}</p>
              )}
            </div>

            <div>
              <label htmlFor="date_hired" className="block text-sm font-medium text-gray-700 mb-1">
                Einstellungsdatum
              </label>
              <input
                type="date"
                id="date_hired"
                name="date_hired"
                value={formData.date_hired || ''}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.date_hired ? 'border-red-500' : 'border-gray-300'
                  }`}
              />
              {errors.date_hired && (
                <p className="mt-1 text-sm text-red-600">{errors.date_hired}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label htmlFor="federal_state" className="block text-sm font-medium text-gray-700 mb-1">
                Bundesland *
              </label>
              <select
                id="federal_state"
                name="federal_state"
                value={formData.federal_state}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${errors.federal_state ? 'border-red-500' : 'border-gray-300'
                  }`}
              >
                {federalStateChoices.map((state) => (
                  <option key={state.code} value={state.code}>
                    {state.name}
                  </option>
                ))}
              </select>
              {errors.federal_state && (
                <p className="mt-1 text-sm text-red-600">{errors.federal_state}</p>
              )}
            </div>

            <div>
              <label htmlFor="calendar_color" className="block text-sm font-medium text-gray-700 mb-1">
                Darstellungsfarbe (Kalender)
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="color"
                  id="calendar_color"
                  name="calendar_color"
                  value={formData.calendar_color || '#3B82F6'}
                  onChange={handleInputChange}
                  className="h-10 w-16 p-1 border border-gray-300 rounded-md cursor-pointer"
                />
                <span className="text-sm text-gray-500 uppercase">{formData.calendar_color || '#3B82F6'}</span>
              </div>
            </div>

            <div className="flex flex-col gap-4 pt-6">
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
                  <label htmlFor="school_children" className="ml-2 block text-sm font-medium text-gray-700">
                    Mitarbeiter hat schulpflichtige Kinder
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

        <div className="flex justify-end space-x-3 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
              disabled={createEmployeeMutation.isPending}
            >
              Abbrechen
            </button>
          )}
          <button
            type="submit"
            disabled={createEmployeeMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createEmployeeMutation.isPending ? 'Wird erstellt...' : 'Mitarbeiter erstellen'}
          </button>
        </div>
      </form>
    </div>
  );
};
