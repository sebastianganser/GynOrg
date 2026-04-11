import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { calendarSettingsService } from '../services/calendarSettingsService';
import type { CalendarSettingsFormData, FederalStateOption } from '../types/calendarSettings';

interface CalendarSettingsFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const CalendarSettingsForm: React.FC<CalendarSettingsFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState<CalendarSettingsFormData>({
    selected_federal_states: [],
    school_holiday_federal_states: [],
    show_nationwide_holidays: true,
    show_calendar_weeks: false,
    visible_employee_ids: [],
    show_vacation_absences: true,
    show_sick_leave: true,
    show_training: true,
    show_special_leave: true,
    holiday_color: '#EF4444',
    school_vacation_color: '#3B82F6',
    employer_federal_state: 'NORDRHEIN_WESTFALEN',
    dec_24_is_half_day: true,
    dec_31_is_half_day: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const queryClient = useQueryClient();

  // Lade aktuelle Einstellungen
  const { data: currentSettings, isLoading: settingsLoading } = useQuery({
    queryKey: ['calendar-settings'],
    queryFn: calendarSettingsService.getSettings,
  });

  // Lade verfügbare Bundesländer
  const { data: federalStates = [], isLoading: statesLoading } = useQuery({
    queryKey: ['federal-states'],
    queryFn: calendarSettingsService.getFederalStates,
  });

  // Formular mit aktuellen Einstellungen initialisieren
  useEffect(() => {
    if (currentSettings) {
      setFormData({
        selected_federal_states: currentSettings.selected_federal_states,
        school_holiday_federal_states: currentSettings.school_holiday_federal_states || [],
        show_nationwide_holidays: currentSettings.show_nationwide_holidays,
        show_calendar_weeks: currentSettings.show_calendar_weeks,
        visible_employee_ids: currentSettings.visible_employee_ids || [],
        show_vacation_absences: currentSettings.show_vacation_absences,
        show_sick_leave: currentSettings.show_sick_leave,
        show_training: currentSettings.show_training,
        show_special_leave: currentSettings.show_special_leave,
        holiday_color: currentSettings.holiday_color || '#EF4444',
        school_vacation_color: currentSettings.school_vacation_color || '#3B82F6',
        employer_federal_state: currentSettings.employer_federal_state || 'NORDRHEIN_WESTFALEN',
        dec_24_is_half_day: currentSettings.dec_24_is_half_day ?? true,
        dec_31_is_half_day: currentSettings.dec_31_is_half_day ?? true,
      });
    }
  }, [currentSettings]);

  const updateSettingsMutation = useMutation({
    mutationFn: calendarSettingsService.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar-settings'] });
      queryClient.invalidateQueries({ queryKey: ['holidays'] }); // Kalender neu laden
      setErrors({});
      onSuccess?.();
    },
    onError: (error: any) => {
      if (error.message) {
        setErrors({ general: error.message });
      } else {
        setErrors({ general: 'Ein Fehler ist aufgetreten beim Speichern der Einstellungen.' });
      }
    },
  });

  const resetSettingsMutation = useMutation({
    mutationFn: calendarSettingsService.resetSettings,
    onSuccess: (resetSettings) => {
      queryClient.invalidateQueries({ queryKey: ['calendar-settings'] });
      queryClient.invalidateQueries({ queryKey: ['holidays'] }); // Kalender neu laden
      setFormData({
        selected_federal_states: resetSettings.selected_federal_states,
        school_holiday_federal_states: resetSettings.school_holiday_federal_states || [],
        show_nationwide_holidays: resetSettings.show_nationwide_holidays,
        show_calendar_weeks: resetSettings.show_calendar_weeks,
        visible_employee_ids: resetSettings.visible_employee_ids || [],
        show_vacation_absences: resetSettings.show_vacation_absences,
        show_sick_leave: resetSettings.show_sick_leave,
        show_training: resetSettings.show_training,
        show_special_leave: resetSettings.show_special_leave,
        holiday_color: resetSettings.holiday_color || '#EF4444',
        school_vacation_color: resetSettings.school_vacation_color || '#3B82F6',
        employer_federal_state: resetSettings.employer_federal_state || 'NORDRHEIN_WESTFALEN',
        dec_24_is_half_day: resetSettings.dec_24_is_half_day ?? true,
        dec_31_is_half_day: resetSettings.dec_31_is_half_day ?? true,
      });
      setErrors({});
    },
    onError: (error: any) => {
      setErrors({ general: error.message || 'Fehler beim Zurücksetzen der Einstellungen.' });
    },
  });

  const handleFederalStateChange = (stateCode: string, checked: boolean) => {
    setFormData((prev) => {
      const newStates = checked
        ? [...prev.selected_federal_states, stateCode]
        : prev.selected_federal_states.filter((code) => code !== stateCode);

      return {
        ...prev,
        selected_federal_states: newStates,
      };
    });

    // Clear error when user makes changes
    if (errors.selected_federal_states) {
      setErrors((prev) => ({ ...prev, selected_federal_states: '' }));
    }
  };

  const handleSchoolHolidayFederalStateChange = (stateCode: string, checked: boolean) => {
    setFormData((prev) => {
      const newStates = checked
        ? [...prev.school_holiday_federal_states, stateCode]
        : prev.school_holiday_federal_states.filter((code) => code !== stateCode);

      return {
        ...prev,
        school_holiday_federal_states: newStates,
      };
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let processedValue: any = value;

    if (type === 'checkbox') {
      processedValue = (e.target as HTMLInputElement).checked;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: processedValue,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Mindestens ein Bundesland muss ausgewählt sein
    if (formData.selected_federal_states.length === 0) {
      newErrors.selected_federal_states = 'Mindestens ein Bundesland muss ausgewählt werden';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      updateSettingsMutation.mutate({
        selected_federal_states: formData.selected_federal_states,
        school_holiday_federal_states: formData.school_holiday_federal_states,
        show_nationwide_holidays: formData.show_nationwide_holidays,
        show_calendar_weeks: formData.show_calendar_weeks,
        employer_federal_state: formData.employer_federal_state,
        dec_24_is_half_day: formData.dec_24_is_half_day,
        dec_31_is_half_day: formData.dec_31_is_half_day,
      });
    }
  };

  const handleReset = () => {
    resetSettingsMutation.mutate();
  };

  if (settingsLoading || statesLoading) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="text-lg">Lade Einstellungen...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Kalender anpassen</h2>

      {/* ARIA Live Region for Form Status */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id="form-status"
      >
        {updateSettingsMutation.isPending && "Einstellungen werden gespeichert..."}
        {resetSettingsMutation.isPending && "Einstellungen werden zurückgesetzt..."}
        {Object.keys(errors).length > 0 && `Formular enthält ${Object.keys(errors).length} Fehler. Bitte korrigieren Sie die markierten Felder.`}
        {updateSettingsMutation.isSuccess && "Einstellungen wurden erfolgreich gespeichert."}
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
        {/* Sektion 0: Urlaubsberechnung */}
        <div className="bg-blue-50 p-4 border border-blue-100 rounded-lg">
          <h3 className="text-lg font-medium text-blue-900 mb-4">Urlaubsberechnung</h3>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="employer_federal_state" className="block text-sm font-medium text-gray-700">
                Stammsitz des Arbeitgebers (Bundesland)
              </label>
              <p className="text-xs text-gray-500 mb-2">
                Dieses Bundesland ist Grundlage für die automatische Abzugs-Berechnung von Feiertagen bei Urlaubsanträgen.
              </p>
              <select
                id="employer_federal_state"
                name="employer_federal_state"
                value={formData.employer_federal_state}
                onChange={handleInputChange}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                {federalStates.map((state: FederalStateOption) => (
                  <option key={state.code} value={state.code}>
                    {state.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="pt-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sonderregelungen zum Jahreswechsel
              </label>
              <div className="flex flex-col space-y-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="dec_24_is_half_day"
                    name="dec_24_is_half_day"
                    checked={formData.dec_24_is_half_day}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="dec_24_is_half_day" className="ml-2 block text-sm text-gray-700">
                    Heiligabend (24.12.) zählt als halber Urlaubstag
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="dec_31_is_half_day"
                    name="dec_31_is_half_day"
                    checked={formData.dec_31_is_half_day}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="dec_31_is_half_day" className="ml-2 block text-sm text-gray-700">
                    Silvester (31.12.) zählt als halber Urlaubstag
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sektion 1: Bundesweite Feiertage */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Bundesweite Feiertage</h3>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="show_nationwide_holidays"
              name="show_nationwide_holidays"
              checked={formData.show_nationwide_holidays}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="show_nationwide_holidays" className="ml-2 block text-sm text-gray-700">
              Bundesweite Feiertage anzeigen
            </label>
          </div>
        </div>

        {/* Sektion 2: Feiertage nach Bundesland */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Feiertage nach Bundesland</h3>
          <p className="text-sm text-gray-600 mb-4">
            Wählen Sie die Bundesländer aus, deren Feiertage im Kalender angezeigt werden sollen.
          </p>

          <div className={`grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 ${errors.selected_federal_states ? 'border border-red-500 rounded p-3' : ''
            }`}>
            {federalStates.map((state: FederalStateOption) => (
              <div key={state.code} className="flex items-center">
                <input
                  type="checkbox"
                  id={`state-${state.code}`}
                  checked={formData.selected_federal_states.includes(state.code)}
                  onChange={(e) => handleFederalStateChange(state.code, e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor={`state-${state.code}`}
                  className="ml-2 block text-sm text-gray-700 cursor-pointer"
                >
                  {state.name}
                </label>
              </div>
            ))}
          </div>

          {errors.selected_federal_states && (
            <p className="mt-2 text-sm text-red-600">{errors.selected_federal_states}</p>
          )}
        </div>

        {/* Sektion 2b: Schulferien nach Bundesland */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Schulferien nach Bundesland</h3>
              <p className="text-sm text-gray-600">
                Wählen Sie die Bundesländer aus, deren Schulferien im Kalender angezeigt werden sollen.
              </p>
            </div>
            <div className="flex flex-col items-end ml-4 shrink-0">
              <label htmlFor="school_vacation_color" className="text-sm font-medium text-gray-700 mb-1">
                Kennzeichnungsfarbe
              </label>
              <input
                type="color"
                id="school_vacation_color"
                name="school_vacation_color"
                value={formData.school_vacation_color || '#3B82F6'}
                onChange={handleInputChange}
                className="h-8 w-24 cursor-pointer rounded border border-gray-300"
                title="Farbe für Schulferien im Kalender"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {federalStates.map((state: FederalStateOption) => (
              <div key={`school-${state.code}`} className="flex items-center">
                <input
                  type="checkbox"
                  id={`school-state-${state.code}`}
                  checked={formData.school_holiday_federal_states.includes(state.code)}
                  onChange={(e) => handleSchoolHolidayFederalStateChange(state.code, e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor={`school-state-${state.code}`}
                  className="ml-2 block text-sm text-gray-700 cursor-pointer"
                >
                  {state.name}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Sektion 3: Kalenderwochen anzeigen */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Kalenderwochen anzeigen</h3>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="show_calendar_weeks"
              name="show_calendar_weeks"
              checked={formData.show_calendar_weeks}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="show_calendar_weeks" className="ml-2 block text-sm text-gray-700">
              Kalenderwochen anzeigen
            </label>
          </div>
        </div>

        <div className="flex justify-between pt-4">
          <button
            type="button"
            onClick={handleReset}
            disabled={updateSettingsMutation.isPending || resetSettingsMutation.isPending}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {resetSettingsMutation.isPending ? 'Wird zurückgesetzt...' : 'Zurücksetzen'}
          </button>

          <div className="flex space-x-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
                disabled={updateSettingsMutation.isPending || resetSettingsMutation.isPending}
              >
                Abbrechen
              </button>
            )}
            <button
              type="submit"
              disabled={updateSettingsMutation.isPending || resetSettingsMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {updateSettingsMutation.isPending ? 'Wird gespeichert...' : 'Einstellungen speichern'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
