import React, { useState, useRef, useEffect } from 'react';
import { getFederalStateChoices } from '../types/employee';

export interface FederalStateOption {
  code: string;
  name: string;
  color: string;
  isActive: boolean;
  isPrimary?: boolean;
  isChildren?: boolean;
}

interface FederalStateSwitcherProps {
  activeFederalStates: string[];
  primaryFederalState?: string;
  childrenFederalStates?: string[];
  onStateToggle: (stateCode: string) => void;
  onPrimaryStateChange: (stateCode: string) => void;
  showAllStates?: boolean;
  className?: string;
  disabled?: boolean;
}

const FederalStateSwitcher: React.FC<FederalStateSwitcherProps> = ({
  activeFederalStates,
  primaryFederalState,
  childrenFederalStates = [],
  onStateToggle,
  onPrimaryStateChange,
  showAllStates = false,
  className = '',
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Color scheme for federal states
  const getStateColor = (stateCode: string): string => {
    const colors = {
      'Baden-Württemberg': '#FF6B6B',
      'Bayern': '#4ECDC4',
      'Berlin': '#45B7D1',
      'Brandenburg': '#96CEB4',
      'Bremen': '#FFEAA7',
      'Hamburg': '#DDA0DD',
      'Hessen': '#98D8C8',
      'Mecklenburg-Vorpommern': '#F7DC6F',
      'Niedersachsen': '#BB8FCE',
      'Nordrhein-Westfalen': '#85C1E9',
      'Rheinland-Pfalz': '#F8C471',
      'Saarland': '#82E0AA',
      'Sachsen': '#F1948A',
      'Sachsen-Anhalt': '#85C1E9',
      'Schleswig-Holstein': '#D7BDE2',
      'Thüringen': '#A9DFBF'
    };
    return colors[stateCode as keyof typeof colors] || '#95A5A6';
  };

  // Prepare federal state options
  const federalStateOptions: FederalStateOption[] = getFederalStateChoices().map(state => ({
    code: state.code,
    name: state.name,
    color: getStateColor(state.code),
    isActive: activeFederalStates.includes(state.code),
    isPrimary: state.code === primaryFederalState,
    isChildren: childrenFederalStates.includes(state.code)
  }));

  // Filter options based on showAllStates
  const visibleOptions = showAllStates 
    ? federalStateOptions
    : federalStateOptions.filter(option => 
        option.isPrimary || 
        option.isChildren || 
        activeFederalStates.includes(option.code)
      );

  // Get primary state for display
  const primaryState = federalStateOptions.find(option => option.isPrimary);
  const activeCount = activeFederalStates.length;

  const handleStateToggle = (stateCode: string) => {
    if (!disabled) {
      onStateToggle(stateCode);
    }
  };

  const handlePrimaryChange = (stateCode: string) => {
    if (!disabled) {
      onPrimaryStateChange(stateCode);
      setIsOpen(false);
    }
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Main Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm
          bg-white text-sm font-medium text-gray-700 hover:bg-gray-50
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          transition-colors duration-200
        `}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="Bundesland-Auswahl"
      >
        {/* Primary State Indicator */}
        {primaryState && (
          <div
            className="w-3 h-3 rounded-full mr-2 border border-gray-300"
            style={{ backgroundColor: primaryState.color }}
            title={`Haupt-Bundesland: ${primaryState.name}`}
          />
        )}
        
        {/* State Text */}
        <span className="mr-2">
          {primaryState ? primaryState.name : 'Bundesland wählen'}
          {activeCount > 1 && (
            <span className="ml-1 text-xs text-gray-500">
              (+{activeCount - 1})
            </span>
          )}
        </span>

        {/* Dropdown Arrow */}
        <svg
          className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-80 bg-white border border-gray-300 rounded-md shadow-lg">
          <div className="py-2 max-h-96 overflow-y-auto">
            {/* Header */}
            <div className="px-4 py-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-900">Bundesländer-Auswahl</h3>
              <p className="text-xs text-gray-500 mt-1">
                Wählen Sie die anzuzeigenden Bundesländer für Schulferien
              </p>
            </div>

            {/* Primary State Selection */}
            <div className="px-4 py-2 border-b border-gray-200">
              <h4 className="text-xs font-medium text-gray-700 mb-2">Haupt-Bundesland</h4>
              <div className="space-y-1">
                {federalStateOptions.map(option => (
                  <label
                    key={`primary-${option.code}`}
                    className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
                  >
                    <input
                      type="radio"
                      name="primaryState"
                      checked={option.isPrimary}
                      onChange={() => handlePrimaryChange(option.code)}
                      className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300"
                    />
                    <div
                      className="w-3 h-3 rounded-full border border-gray-300"
                      style={{ backgroundColor: option.color }}
                    />
                    <span className="text-sm text-gray-700">{option.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Additional States */}
            <div className="px-4 py-2">
              <h4 className="text-xs font-medium text-gray-700 mb-2">Zusätzliche Bundesländer</h4>
              <div className="space-y-1">
                {visibleOptions
                  .filter(option => !option.isPrimary)
                  .map(option => (
                    <label
                      key={`additional-${option.code}`}
                      className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={option.isActive}
                        onChange={() => handleStateToggle(option.code)}
                        className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <div
                        className="w-3 h-3 rounded-full border border-gray-300"
                        style={{ backgroundColor: option.color }}
                      />
                      <span className="text-sm text-gray-700">{option.name}</span>
                      {option.isChildren && (
                        <span className="text-xs text-blue-600 bg-blue-100 px-1 rounded">
                          Kinder
                        </span>
                      )}
                    </label>
                  ))}
              </div>
            </div>

            {/* Show All Toggle */}
            {!showAllStates && (
              <div className="px-4 py-2 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Alle Bundesländer anzeigen →
                </button>
              </div>
            )}

            {/* Quick Actions */}
            <div className="px-4 py-2 border-t border-gray-200 flex justify-between">
              <button
                type="button"
                onClick={() => {
                  // Clear all except primary
                  federalStateOptions.forEach(option => {
                    if (!option.isPrimary && option.isActive) {
                      handleStateToggle(option.code);
                    }
                  });
                }}
                className="text-xs text-gray-600 hover:text-gray-800"
              >
                Nur Haupt-Bundesland
              </button>
              
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                Fertig
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FederalStateSwitcher;

// Helper hook for managing federal state selection
export const useFederalStateSwitcher = (
  initialPrimary?: string,
  initialAdditional: string[] = [],
  initialChildren: string[] = []
) => {
  const [primaryFederalState, setPrimaryFederalState] = useState(
    initialPrimary || 'Nordrhein-Westfalen'
  );
  const [additionalFederalStates, setAdditionalFederalStates] = useState<string[]>(
    initialAdditional
  );
  const [childrenFederalStates, setChildrenFederalStates] = useState<string[]>(
    initialChildren
  );

  // Calculate all active states
  const activeFederalStates = [
    primaryFederalState,
    ...additionalFederalStates,
    ...childrenFederalStates
  ].filter((state, index, array) => array.indexOf(state) === index);

  const handleStateToggle = (stateCode: string) => {
    if (stateCode === primaryFederalState) {
      // Can't toggle off primary state
      return;
    }

    if (additionalFederalStates.includes(stateCode)) {
      setAdditionalFederalStates(prev => prev.filter(s => s !== stateCode));
    } else if (childrenFederalStates.includes(stateCode)) {
      setChildrenFederalStates(prev => prev.filter(s => s !== stateCode));
    } else {
      setAdditionalFederalStates(prev => [...prev, stateCode]);
    }
  };

  const handlePrimaryStateChange = (stateCode: string) => {
    // Remove from additional/children if it was there
    setAdditionalFederalStates(prev => prev.filter(s => s !== stateCode));
    setChildrenFederalStates(prev => prev.filter(s => s !== stateCode));
    
    // Set as primary
    setPrimaryFederalState(stateCode);
  };

  const resetToDefaults = () => {
    setPrimaryFederalState('Nordrhein-Westfalen');
    setAdditionalFederalStates([]);
    setChildrenFederalStates([]);
  };

  return {
    primaryFederalState,
    additionalFederalStates,
    childrenFederalStates,
    activeFederalStates,
    handleStateToggle,
    handlePrimaryStateChange,
    setPrimaryFederalState,
    setAdditionalFederalStates,
    setChildrenFederalStates,
    resetToDefaults
  };
};
