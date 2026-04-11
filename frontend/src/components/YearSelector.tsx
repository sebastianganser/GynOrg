import React from 'react';
import { ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react';

interface YearSelectorProps {
  currentYear: number;
  availableYears: number[];
  onYearChange: (year: number) => void;
  loading?: boolean;
  className?: string;
}

export const YearSelector: React.FC<YearSelectorProps> = ({
  currentYear,
  availableYears,
  onYearChange,
  loading = false,
  className = ''
}) => {
  // Sortiere verfügbare Jahre absteigend (neueste zuerst)
  const sortedYears = [...availableYears].sort((a, b) => b - a);
  
  // Finde vorheriges und nächstes Jahr
  const currentIndex = sortedYears.indexOf(currentYear);
  const canGoPrev = currentIndex < sortedYears.length - 1;
  const canGoNext = currentIndex > 0;
  
  const handlePrevYear = () => {
    if (canGoPrev && !loading) {
      const prevYear = sortedYears[currentIndex + 1];
      onYearChange(prevYear);
    }
  };
  
  const handleNextYear = () => {
    if (canGoNext && !loading) {
      const nextYear = sortedYears[currentIndex - 1];
      onYearChange(nextYear);
    }
  };
  
  const handleYearSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const year = parseInt(event.target.value);
    if (!isNaN(year) && !loading) {
      onYearChange(year);
    }
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Vorheriges Jahr Button */}
      <button
        onClick={handlePrevYear}
        disabled={!canGoPrev || loading}
        className={`
          p-1.5 rounded-md transition-colors
          ${canGoPrev && !loading
            ? 'hover:bg-gray-100 text-gray-600 hover:text-gray-800'
            : 'text-gray-300 cursor-not-allowed'
          }
        `}
        title={canGoPrev ? `Zu ${sortedYears[currentIndex + 1]}` : 'Kein früheres Jahr verfügbar'}
      >
        <ChevronLeft size={16} />
      </button>

      {/* Jahr-Dropdown */}
      <div className="relative">
        <select
          value={currentYear}
          onChange={handleYearSelect}
          disabled={loading}
          className={`
            appearance-none bg-white border border-gray-300 rounded-md
            px-3 py-1.5 pr-8 text-sm font-medium text-gray-700
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            transition-colors
            ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50 cursor-pointer'}
          `}
        >
          {sortedYears.map(year => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
        
        {/* Custom Dropdown Arrow */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <ChevronDown 
            size={14} 
            className={`text-gray-400 ${loading ? 'opacity-50' : ''}`} 
          />
        </div>
      </div>

      {/* Nächstes Jahr Button */}
      <button
        onClick={handleNextYear}
        disabled={!canGoNext || loading}
        className={`
          p-1.5 rounded-md transition-colors
          ${canGoNext && !loading
            ? 'hover:bg-gray-100 text-gray-600 hover:text-gray-800'
            : 'text-gray-300 cursor-not-allowed'
          }
        `}
        title={canGoNext ? `Zu ${sortedYears[currentIndex - 1]}` : 'Kein späteres Jahr verfügbar'}
      >
        <ChevronRight size={16} />
      </button>

      {/* Loading Indikator */}
      {loading && (
        <div className="flex items-center ml-2">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
        </div>
      )}
    </div>
  );
};

// Keyboard Navigation Hook für erweiterte Funktionalität
export const useYearKeyboardNavigation = (
  currentYear: number,
  availableYears: number[],
  onYearChange: (year: number) => void,
  enabled: boolean = true
) => {
  React.useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Nur reagieren wenn kein Input-Element fokussiert ist
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return;
      }

      const sortedYears = [...availableYears].sort((a, b) => b - a);
      const currentIndex = sortedYears.indexOf(currentYear);

      switch (event.key) {
        case 'ArrowLeft':
        case 'ArrowUp':
          // Vorheriges Jahr (älter)
          if (currentIndex < sortedYears.length - 1) {
            event.preventDefault();
            onYearChange(sortedYears[currentIndex + 1]);
          }
          break;
        case 'ArrowRight':
        case 'ArrowDown':
          // Nächstes Jahr (neuer)
          if (currentIndex > 0) {
            event.preventDefault();
            onYearChange(sortedYears[currentIndex - 1]);
          }
          break;
        case 'Home':
          // Zum neuesten Jahr
          if (sortedYears.length > 0 && currentYear !== sortedYears[0]) {
            event.preventDefault();
            onYearChange(sortedYears[0]);
          }
          break;
        case 'End':
          // Zum ältesten Jahr
          if (sortedYears.length > 0 && currentYear !== sortedYears[sortedYears.length - 1]) {
            event.preventDefault();
            onYearChange(sortedYears[sortedYears.length - 1]);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [currentYear, availableYears, onYearChange, enabled]);
};
