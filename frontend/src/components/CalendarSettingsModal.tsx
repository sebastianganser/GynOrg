import React from 'react';
import { CalendarSettingsForm } from './CalendarSettingsForm';

interface CalendarSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CalendarSettingsModal: React.FC<CalendarSettingsModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSuccess = () => {
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="calendar-settings-title"
    >
      <div 
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header mit Schließen-Button */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200">
          <h2 id="calendar-settings-title" className="text-xl font-semibold text-gray-900">
            Kalendereinstellungen
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full p-1"
            aria-label="Einstellungen schließen"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Formular-Inhalt */}
        <div className="p-0">
          <CalendarSettingsForm 
            onSuccess={handleSuccess}
            onCancel={onClose}
          />
        </div>
      </div>
    </div>
  );
};
