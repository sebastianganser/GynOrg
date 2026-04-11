import React, { useState, useEffect } from 'react';
import { X, Calendar, AlertTriangle } from 'lucide-react';
import { Absence, AbsenceFormData, ConflictCheckResponse, AbsenceStatus } from '../types/absence';
import { useAbsenceManagement } from '../hooks/useAbsences';
import { absenceService } from '../services/absenceService';
import { employeeService } from '../services/employeeService';
import { Employee } from '../types/employee';
import { useVacationSummary } from '../hooks/useEmployees';
import { useCalendarSettings } from '../hooks/useCalendarSettings';
import { useHolidays } from '../hooks/useHolidays';

interface EditAbsenceFormProps {
  isOpen: boolean;
  onClose: () => void;
  absence: Absence;
}

export const EditAbsenceForm: React.FC<EditAbsenceFormProps> = ({
  isOpen,
  onClose,
  absence
}) => {
  const [formData, setFormData] = useState<AbsenceFormData>({
    absence_type_id: absence.absence_type_id,
    start_date: new Date(absence.start_date),
    end_date: new Date(absence.end_date),
    comment: absence.comment || '',
    half_day_time: absence.half_day_time || null
  });

  const [isHalfDay, setIsHalfDay] = useState(!!absence.half_day_time);

  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number>(absence.employee_id);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoadingEmployees, setIsLoadingEmployees] = useState(false);
  const [conflicts, setConflicts] = useState<ConflictCheckResponse | null>(null);
  const [isCheckingConflicts, setIsCheckingConflicts] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const {
    absenceTypes,
    isLoading,
    updateAbsence,
    isUpdating,
    updateError
  } = useAbsenceManagement();

  const { data: vacationSummary } = useVacationSummary(
    selectedEmployeeId || undefined,
    formData.start_date ? formData.start_date.getFullYear() : undefined
  );

  const { data: calendarSettings } = useCalendarSettings();
  const { holidays } = useHolidays(formData.start_date ? formData.start_date.getFullYear() : new Date().getFullYear());

  // Reset half_day info if dates don't match
  useEffect(() => {
    if (formData.start_date && formData.end_date) {
      if (formData.start_date.getTime() !== formData.end_date.getTime()) {
        if (isHalfDay) setIsHalfDay(false);
        if (formData.half_day_time) handleInputChange('half_day_time', null);
      }
    }
  }, [formData.start_date, formData.end_date]);

  // Load employees when modal opens
  useEffect(() => {
    if (isOpen) {
      loadEmployees();
    }
  }, [isOpen]);

  const loadEmployees = async () => {
    setIsLoadingEmployees(true);
    try {
      const employeeList = await employeeService.getEmployees();
      // Filter only active employees
      const activeEmployees = employeeList.filter(emp => emp.active);
      setEmployees(activeEmployees);

      // Auto-select is disabled for EditForm because employee is already set.
    } catch (error) {
      console.error('Error loading employees:', error);
    } finally {
      setIsLoadingEmployees(false);
    }
  };

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFormData({
        absence_type_id: absence.absence_type_id,
        start_date: new Date(absence.start_date),
        end_date: new Date(absence.end_date),
        comment: absence.comment || '',
        half_day_time: absence.half_day_time || null
      });
      setIsHalfDay(!!absence.half_day_time);
      setSelectedEmployeeId(absence.employee_id);
      setConflicts(null);
      setValidationErrors({});
    }
  }, [isOpen, absence]);

  // Check for conflicts when dates or absence type change
  useEffect(() => {
    if (formData.absence_type_id && formData.start_date && formData.end_date) {
      checkConflicts();
    }
  }, [formData.absence_type_id, formData.start_date, formData.end_date]);

  const checkConflicts = async () => {
    if (!formData.start_date || !formData.end_date) return;

    setIsCheckingConflicts(true);
    try {
      const result = await absenceService.checkConflicts(
        selectedEmployeeId,
        absenceService.formatDateForAPI(formData.start_date),
        absenceService.formatDateForAPI(formData.end_date),
        absence.id
      );
      setConflicts(result);
    } catch (error) {
      console.error('Error checking conflicts:', error);
    } finally {
      setIsCheckingConflicts(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!selectedEmployeeId) {
      errors.employee_id = 'Bitte wählen Sie einen Mitarbeiter aus';
    }

    if (!formData.absence_type_id) {
      errors.absence_type_id = 'Bitte wählen Sie einen Abwesenheitstyp aus';
    }

    if (!formData.start_date) {
      errors.start_date = 'Startdatum ist erforderlich';
    }

    if (!formData.end_date) {
      errors.end_date = 'Enddatum ist erforderlich';
    }

    if (formData.start_date && formData.end_date && formData.start_date > formData.end_date) {
      errors.end_date = 'Enddatum muss nach dem Startdatum liegen';
    }

    // Check max days per request
    const selectedType = absenceTypes.find(type => type.id === formData.absence_type_id);
    if (selectedType?.max_days_per_request && formData.start_date && formData.end_date) {
      const duration = calculateDuration();
      if (duration > selectedType.max_days_per_request) {
        errors.duration = `Maximale Anzahl Tage überschritten: ${duration} > ${selectedType.max_days_per_request}`;
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    if (conflicts?.has_conflicts) {
      return;
    }

    const absenceUpdateData = {
      employee_id: selectedEmployeeId,
      absence_type_id: formData.absence_type_id,
      start_date: absenceService.formatDateForAPI(formData.start_date),
      end_date: absenceService.formatDateForAPI(formData.end_date),
      comment: formData.comment || undefined,
      status: absence.status,
      half_day_time: isHalfDay ? (formData.half_day_time || 'AM') : null
    };

    updateAbsence({ id: absence.id, data: absenceUpdateData }, {
      onSuccess: () => {
        onClose();
      }
    });
  };

  const handleInputChange = (field: keyof AbsenceFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const formatDateForInput = (date: Date): string => {
    // Return YYYY-MM-DD in local time
    if (!date) return '';
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const parseInputDate = (dateString: string): Date => {
    // Parse YYYY-MM-DD back to local midnight
    if (!dateString) return new Date();
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(year, month - 1, day, 0, 0, 0);
  };

  const calculateDuration = (): number => {
    if (!formData.start_date || !formData.end_date) return 0;
    return absenceService.calculateDurationWithHolidays(
      formData.start_date, 
      formData.end_date, 
      isHalfDay ? (formData.half_day_time || 'AM') : null,
      calendarSettings,
      holidays?.filter((h: any) => h.holiday_type === 'PUBLIC_HOLIDAY') || []
    );
  };

  const isSingleDay = formData.start_date && formData.end_date && 
    formData.start_date.getTime() === formData.end_date.getTime();

  const selectedAbsenceType = absenceTypes.find(type => type.id === formData.absence_type_id);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Abwesenheit bearbeiten
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Employee Selection */}
          <div>
            <label htmlFor="employee_id" className="block text-sm font-medium text-gray-700 mb-2">
              Mitarbeiter *
            </label>
            <select
              id="employee_id"
              name="employee_id"
              value={selectedEmployeeId}
              onChange={(e) => setSelectedEmployeeId(parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${validationErrors.employee_id ? 'border-red-500' : 'border-gray-300'
                }`}
              disabled={isLoadingEmployees}
            >
              <option value={0}>Bitte wählen...</option>
              {employees.map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {employee.first_name} {employee.last_name} ({employee.position})
                </option>
              ))}
            </select>
            {validationErrors.employee_id && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.employee_id}</p>
            )}
            {isLoadingEmployees && (
              <p className="mt-1 text-sm text-gray-600">Lade Mitarbeiter...</p>
            )}
          </div>

          {/* Absence Type */}
          <div>
            <label htmlFor="absence_type_id" className="block text-sm font-medium text-gray-700 mb-2">
              Abwesenheitstyp *
            </label>
            <select
              id="absence_type_id"
              name="absence_type_id"
              value={formData.absence_type_id}
              onChange={(e) => handleInputChange('absence_type_id', parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${validationErrors.absence_type_id ? 'border-red-500' : 'border-gray-300'
                }`}
              disabled={isLoading}
            >
              <option value={0}>Bitte wählen...</option>
              {absenceTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
            {validationErrors.absence_type_id && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.absence_type_id}</p>
            )}
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-2">
                Startdatum *
              </label>
              <input
                type="date"
                id="start_date"
                name="start_date"
                value={formatDateForInput(formData.start_date)}
                onChange={(e) => handleInputChange('start_date', parseInputDate(e.target.value))}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${validationErrors.start_date ? 'border-red-500' : 'border-gray-300'
                  }`}
              />
              {validationErrors.start_date && (
                <p className="mt-1 text-sm text-red-600">{validationErrors.start_date}</p>
              )}
            </div>

            <div>
              <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-2">
                Enddatum *
              </label>
              <input
                type="date"
                id="end_date"
                name="end_date"
                value={formatDateForInput(formData.end_date)}
                onChange={(e) => handleInputChange('end_date', parseInputDate(e.target.value))}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white ${validationErrors.end_date ? 'border-red-500' : 'border-gray-300'
                  }`}
              />
              {validationErrors.end_date && (
                <p className="mt-1 text-sm text-red-600">{validationErrors.end_date}</p>
              )}
            </div>
          </div>

          {/* Half Day Option */}
          {isSingleDay && (
            <div className="bg-blue-50 p-3 border border-blue-100 rounded-lg">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="isHalfDay"
                  checked={isHalfDay}
                  onChange={(e) => {
                    setIsHalfDay(e.target.checked);
                    if (e.target.checked && !formData.half_day_time) {
                      handleInputChange('half_day_time', 'AM');
                    } else if (!e.target.checked) {
                      handleInputChange('half_day_time', null);
                    }
                  }}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="isHalfDay" className="text-sm font-medium text-blue-900 cursor-pointer">
                  Halber Urlaubstag beantragen
                </label>
              </div>
              
              {isHalfDay && (
                <div className="mt-3 ml-6">
                  <select
                    value={formData.half_day_time || 'AM'}
                    onChange={(e) => handleInputChange('half_day_time', e.target.value)}
                    className="block w-full pl-3 pr-10 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                  >
                    <option value="AM">Vormittag (AM)</option>
                    <option value="PM">Nachmittag (PM)</option>
                  </select>
                </div>
              )}
            </div>
          )}

          {/* Duration Display */}
          {formData.start_date && formData.end_date && (() => {
            const selectedAbsenceType = absenceTypes.find(type => type.id === formData.absence_type_id);
            const isVacationType = selectedAbsenceType?.is_vacation;

            // If the original absence was a VACATION and was APPROVED or PENDING, it's included in the backend's taken_days
            const wasVacationAndCounted = absence.absence_type?.is_vacation &&
              (absence.status === 'approved' || absence.status === 'pending');
            const oldDuration = wasVacationAndCounted ? absence.duration_days : 0;

            // Adjust the remaining days by adding the old duration back, then subtracting the new duration
            const adjustedRemaining = vacationSummary
              ? vacationSummary.remaining_days + oldDuration - calculateDuration()
              : 0;

            return (
              <div className="flex flex-col space-y-2 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Calendar size={16} />
                  <span>Dauer: {calculateDuration()} Tag{calculateDuration() !== 1 ? 'e' : ''}</span>
                </div>

                {isVacationType && vacationSummary && (
                  <div className="ml-6 flex flex-col space-y-1 text-xs text-gray-500 border-l-2 border-blue-200 pl-3 py-1">
                    <span>Initial verfügbar: <strong>{vacationSummary.total_allowance} Tage</strong></span>
                    <span>Resturlaub (inkl. diesem Antrag): <strong className={adjustedRemaining < 0 ? 'text-red-600' : 'text-green-600'}>{adjustedRemaining} Tage</strong></span>
                  </div>
                )}
              </div>
            );
          })()}

          {/* Duration Validation */}
          {validationErrors.duration && (
            <div className="flex items-center space-x-2 text-sm text-red-600">
              <AlertTriangle size={16} />
              <span>{validationErrors.duration}</span>
            </div>
          )}

          {/* Conflict Warning */}
          {isCheckingConflicts && (
            <div className="flex items-center space-x-2 text-sm text-yellow-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
              <span>Prüfe Konflikte...</span>
            </div>
          )}

          {conflicts?.has_conflicts && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2 text-sm text-red-800 mb-2">
                <AlertTriangle size={16} />
                <span className="font-medium">Konflikt erkannt!</span>
              </div>
              <div className="text-sm text-red-700">
                {conflicts.conflicts.map((conflict, index) => (
                  <div key={index}>
                    Überschneidung vom {conflict.start_date} bis {conflict.end_date}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Comment */}
          <div>
            <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-2">
              Kommentar
            </label>
            <textarea
              id="comment"
              name="comment"
              value={formData.comment}
              onChange={(e) => handleInputChange('comment', e.target.value)}
              placeholder="Optional: Zusätzliche Informationen..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            />
          </div>

          {/* Error Display */}
          {updateError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2 text-sm text-red-800">
                <AlertTriangle size={16} />
                <span>Fehler: {updateError.message}</span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end pt-4">
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                disabled={isUpdating || conflicts?.has_conflicts}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {isUpdating && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                )}
                <span>Speichern</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
