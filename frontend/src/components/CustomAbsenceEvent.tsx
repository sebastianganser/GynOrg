import React from 'react';
import { EventProps } from 'react-big-calendar';
import { CalendarAbsence } from '../types/absence';

interface CustomAbsenceEventProps extends EventProps<CalendarAbsence> { }

export const CustomAbsenceEvent: React.FC<CustomAbsenceEventProps> = ({ event }) => {
  const { resource: absence } = event;

  const getStatusIcon = () => {
    switch (absence.status) {
      case 'pending':
        return '⏳';
      case 'approved':
        return '✅';
      case 'rejected':
        return '❌';
      case 'cancelled':
        return '🚫';
      default:
        return '';
    }
  };

  const getStatusText = () => {
    switch (absence.status) {
      case 'pending':
        return 'Wartend';
      case 'approved':
        return 'Genehmigt';
      case 'rejected':
        return 'Abgelehnt';
      case 'cancelled':
        return 'Storniert';
      default:
        return absence.status;
    }
  };

  const getBorderStyle = () => {
    switch (absence.status) {
      case 'pending':
        return 'border-l-4 border-yellow-400';
      case 'approved':
        return 'border-l-4 border-green-500';
      case 'rejected':
        return 'border-l-4 border-red-500';
      case 'cancelled':
        return 'border-l-4 border-gray-500';
      default:
        return 'border-l-4 border-blue-400';
    }
  };

  const getOpacity = () => {
    return 'opacity-100';
  };

  return (
    <div
      className={`
        h-full w-full p-1 text-xs text-white rounded-sm
        ${getBorderStyle()} ${getOpacity()}
        hover:shadow-md transition-shadow duration-200
        cursor-pointer
      `}
      style={{
        backgroundColor: absence.absence_type?.color || '#3B82F6',
        minHeight: '20px'
      }}
      title={`${absence.absence_type?.name || 'Abwesenheit'} - ${getStatusText()}\n${absence.comment || ''}`}
    >
      <div className="flex items-center justify-between h-full">
        <div className="flex-1 truncate">
          <div className="font-medium truncate">
            {absence.absence_type?.name || 'Abwesenheit'}
          </div>
          {absence.duration_days > 1 && (
            <div className="text-xs opacity-90">
              {absence.duration_days} Tage
            </div>
          )}
        </div>
        <div className="ml-1 flex-shrink-0">
          {getStatusIcon()}
        </div>
      </div>
    </div>
  );
};
