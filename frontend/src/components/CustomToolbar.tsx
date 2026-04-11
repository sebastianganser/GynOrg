import React from 'react';
import { ToolbarProps } from 'react-big-calendar';
import { ChevronLeft, ChevronRight, Plus, Filter } from 'lucide-react';
import { CalendarAbsence } from '../types/absence';
import { YearSelector } from './YearSelector';

interface CustomToolbarProps extends ToolbarProps<CalendarAbsence> {
  onNewAbsence?: () => void;
  onFilterToggle?: () => void;
  showFilters?: boolean;
  // Jahr-Navigation Props
  currentYear?: number;
  availableYears?: number[];
  onYearChange?: (year: number) => void;
  yearLoading?: boolean;
}

export const CustomToolbar: React.FC<CustomToolbarProps> = ({
  date,
  view,
  views,
  label,
  onNavigate,
  onView,
  onNewAbsence,
  onFilterToggle,
  showFilters = false,
  currentYear,
  availableYears = [],
  onYearChange,
  yearLoading = false
}) => {
  const navigate = (action: 'PREV' | 'NEXT' | 'TODAY') => {
    onNavigate(action as any);
  };

  // Define available views and their German names
  const availableViews = ['month', 'week', 'quarter', 'year'];
  const viewNamesMap: Record<string, string> = {
    month: 'Monat',
    week: 'Woche',
    quarter: 'Quartal',
    year: 'Jahr',
    work_week: 'Arbeitswoche',
    day: 'Tag',
    agenda: 'Agenda'
  };

  return (
    <div className="bg-white border-b border-gray-200 p-4">
      <div className="flex items-center justify-between">
        {/* Left side - Navigation */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('PREV')}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title={view === 'week' ? 'Vorherige Woche' : 'Vorheriger Monat'}
            >
              <ChevronLeft size={20} className="text-gray-600" />
            </button>
            
            <button
              onClick={() => navigate('TODAY')}
              className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Heute
            </button>
            
            <button
              onClick={() => navigate('NEXT')}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title={view === 'week' ? 'Nächste Woche' : 'Nächster Monat'}
            >
              <ChevronRight size={20} className="text-gray-600" />
            </button>
          </div>

          {/* Current date/period label */}
          <h2 className="text-xl font-semibold text-gray-900">
            {label}
          </h2>
        </div>

        {/* Center - Year selector and View selector */}
        <div className="flex items-center space-x-4">
          {/* Jahr-Navigation */}
          {currentYear && availableYears.length > 0 && onYearChange && (
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-600">Jahr:</span>
              <YearSelector
                currentYear={currentYear}
                availableYears={availableYears}
                onYearChange={onYearChange}
                loading={yearLoading}
              />
            </div>
          )}

          {/* View selector */}
          <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            {availableViews.map((viewKey) => (
              <button
                key={viewKey}
                onClick={() => onView(viewKey as any)}
                className={`
                  px-3 py-2 text-sm font-medium rounded-md transition-colors
                  ${view === viewKey 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
              >
                {viewNamesMap[viewKey]}
              </button>
            ))}
          </div>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center space-x-3">
          {onFilterToggle && (
            <button
              onClick={onFilterToggle}
              className={`
                p-2 rounded-lg transition-colors
                ${showFilters 
                  ? 'bg-blue-100 text-blue-600' 
                  : 'hover:bg-gray-100 text-gray-600'
                }
              `}
              title="Filter"
            >
              <Filter size={20} />
            </button>
          )}
          
          {onNewAbsence && (
            <button
              onClick={onNewAbsence}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={20} />
              <span>Neue Abwesenheit</span>
            </button>
          )}
        </div>
      </div>

      {/* Optional filter bar */}
      {showFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="text-sm font-medium text-gray-700">Filter:</div>
            <div className="flex items-center space-x-2">
              <select className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white">
                <option value="">Alle Status</option>
                <option value="draft">Entwurf</option>
                <option value="pending">Wartend</option>
                <option value="confirmed">Bestätigt</option>
                <option value="cancelled">Storniert</option>
              </select>
              
              <select className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white">
                <option value="">Alle Typen</option>
                <option value="vacation">Urlaub</option>
                <option value="sick_leave">Krankheit</option>
                <option value="training">Fortbildung</option>
                <option value="special_leave">Sonderurlaub</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
