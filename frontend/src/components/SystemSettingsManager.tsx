import React, { useState, useEffect } from 'react';
import { useSystemSettings } from '../hooks/useSystemSettings';

export const SystemSettingsManager: React.FC = () => {
    const { settings, isLoading, isError, updateSettings, isUpdating } = useSystemSettings();
    const [selectedMinutes, setSelectedMinutes] = useState<number>(30);

    // Initial sync
    useEffect(() => {
        if (settings) {
            setSelectedMinutes(settings.auto_logout_minutes);
        }
    }, [settings]);

    const handleSave = () => {
        updateSettings({ auto_logout_minutes: selectedMinutes });
    };

    if (isLoading) {
        return <div className="p-4 text-gray-500">Lade Grundeinstellungen...</div>;
    }

    if (isError) {
        return <div className="p-4 text-red-500">Fehler beim Laden der Grundeinstellungen.</div>;
    }

    const options = [5, 10, 15, 30];

    return (
        <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Sicherheit & Sitzung</h3>
                <p className="mt-1 text-sm text-gray-500">
                    Konfigurieren Sie automatische Timeouts zum Schutz Ihrer Daten.
                </p>
            </div>
            <div className="p-6 space-y-6">
                <div>
                    <label className="text-base font-semibold text-gray-900">
                        Automatischer Logout nach Inaktivität
                    </label>
                    <p className="text-sm text-gray-500 mb-4">
                        Wählen Sie die Dauer aus, nach der die App Sie bei fehlender Aktivität (z.B. keine Maus- oder Tastatureingaben) automatisch abmeldet.
                    </p>
                    <div className="space-y-4">
                        {options.map((minutes) => (
                            <div key={minutes} className="flex items-center">
                                <input
                                    id={`logout-${minutes}`}
                                    name="auto-logout"
                                    type="radio"
                                    checked={selectedMinutes === minutes}
                                    onChange={() => setSelectedMinutes(minutes)}
                                    className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-600"
                                />
                                <label htmlFor={`logout-${minutes}`} className="ml-3 block text-sm font-medium text-gray-700">
                                    {minutes} Minuten
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="pt-4 flex justify-end">
                    <button
                        onClick={handleSave}
                        disabled={isUpdating || settings?.auto_logout_minutes === selectedMinutes}
                        className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {isUpdating ? 'Speichert...' : 'Einstellungen speichern'}
                    </button>
                </div>
            </div>
        </div>
    );
};
