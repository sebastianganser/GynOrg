import React, { useState } from 'react';
import { SchoolVacationType, HolidayType, getSchoolVacationTypeLabel, getHolidayTypeLabel } from '../types/holiday';
import type { PersonalizedHoliday } from '../services/personalizedHolidayService';

export interface HolidayLegendItem {
  id: string;
  label: string;
  color: string;
  count: number;
  isVisible: boolean;
  type: 'federal-state' | 'vacation-type' | 'holiday-type' | 'relevance-level';
  value: string;
}

interface HolidayLegendProps {
  holidays: PersonalizedHoliday[];
  visibleItems: string[];
  onToggleItem: (itemId: string) => void;
  showCounts?: boolean;
  showToggleAll?: boolean;
  groupByType?: boolean;
  className?: string;
  compact?: boolean;
}

const HolidayLegend: React.FC<HolidayLegendProps> = ({
  holidays,
  visibleItems,
  onToggleItem,
  showCounts = true,
  showToggleAll = true,
  groupByType = true,
  className = '',
  compact = false
}) => {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['federal-state', 'relevance-level']));

  // Generate legend items from holidays
  const generateLegendItems = (): Record<string, HolidayLegendItem[]> => {
    const items: Record<string, HolidayLegendItem[]> = {
      'federal-state': [],
      'vacation-type': [],
      'holiday-type': [],
      'relevance-level': []
    };

    // Count occurrences and collect unique values
    const federalStateCounts = new Map<string, number>();
    const vacationTypeCounts = new Map<SchoolVacationType, number>();
    const holidayTypeCounts = new Map<HolidayType, number>();
    const relevanceLevelCounts = new Map<string, number>();

    holidays.forEach(holiday => {
      // Federal state counts
      if (holiday.federal_state) {
        federalStateCounts.set(
          holiday.federal_state,
          (federalStateCounts.get(holiday.federal_state) || 0) + 1
        );
      }

      // Vacation type counts
      if (holiday.vacation_type) {
        vacationTypeCounts.set(
          holiday.vacation_type,
          (vacationTypeCounts.get(holiday.vacation_type) || 0) + 1
        );
      }

      // Holiday type counts
      holidayTypeCounts.set(
        holiday.holiday_type,
        (holidayTypeCounts.get(holiday.holiday_type) || 0) + 1
      );

      // Relevance level counts
      relevanceLevelCounts.set(
        holiday.relevanceLevel,
        (relevanceLevelCounts.get(holiday.relevanceLevel) || 0) + 1
      );
    });

    // Generate federal state items
    federalStateCounts.forEach((count, federalState) => {
      const holiday = holidays.find(h => h.federal_state === federalState);
      if (holiday) {
        items['federal-state'].push({
          id: `federal-state-${federalState}`,
          label: federalState,
          color: holiday.color,
          count,
          isVisible: visibleItems.includes(`federal-state-${federalState}`),
          type: 'federal-state',
          value: federalState
        });
      }
    });

    // Generate vacation type items
    vacationTypeCounts.forEach((count, vacationType) => {
      items['vacation-type'].push({
        id: `vacation-type-${vacationType}`,
        label: getSchoolVacationTypeLabel(vacationType),
        color: '#2563eb', // Blue for school vacations
        count,
        isVisible: visibleItems.includes(`vacation-type-${vacationType}`),
        type: 'vacation-type',
        value: vacationType
      });
    });

    // Generate holiday type items
    holidayTypeCounts.forEach((count, holidayType) => {
      const color = holidayType === HolidayType.PUBLIC_HOLIDAY ? '#dc2626' : '#2563eb';
      items['holiday-type'].push({
        id: `holiday-type-${holidayType}`,
        label: getHolidayTypeLabel(holidayType),
        color,
        count,
        isVisible: visibleItems.includes(`holiday-type-${holidayType}`),
        type: 'holiday-type',
        value: holidayType
      });
    });

    // Generate relevance level items
    const relevanceLevelColors = {
      primary: '#059669',    // Green
      additional: '#0891b2', // Cyan
      children: '#7c3aed',   // Purple
      all: '#6b7280'         // Gray
    };

    const relevanceLevelLabels = {
      primary: 'Haupt-Bundesland',
      additional: 'Zusätzliche Bundesländer',
      children: 'Kinder-Bundesländer',
      all: 'Alle Bundesländer'
    };

    relevanceLevelCounts.forEach((count, level) => {
      items['relevance-level'].push({
        id: `relevance-level-${level}`,
        label: relevanceLevelLabels[level as keyof typeof relevanceLevelLabels] || level,
        color: relevanceLevelColors[level as keyof typeof relevanceLevelColors] || '#6b7280',
        count,
        isVisible: visibleItems.includes(`relevance-level-${level}`),
        type: 'relevance-level',
        value: level
      });
    });

    // Sort items by count (descending)
    Object.keys(items).forEach(key => {
      items[key].sort((a, b) => b.count - a.count);
    });

    return items;
  };

  const legendItems = generateLegendItems();

  // Toggle group expansion
  const toggleGroup = (groupType: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupType)) {
        newSet.delete(groupType);
      } else {
        newSet.add(groupType);
      }
      return newSet;
    });
  };

  // Toggle all items in a group
  const toggleAllInGroup = (groupType: string, visible: boolean) => {
    legendItems[groupType].forEach(item => {
      if (item.isVisible !== visible) {
        onToggleItem(item.id);
      }
    });
  };

  // Group type labels
  const groupLabels = {
    'federal-state': 'Bundesländer',
    'vacation-type': 'Ferienarten',
    'holiday-type': 'Feiertag-Typen',
    'relevance-level': 'Relevanz-Level'
  };

  // Render legend item
  const renderLegendItem = (item: HolidayLegendItem) => (
    <div
      key={item.id}
      className={`
        flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded
        ${compact ? 'text-xs' : 'text-sm'}
        ${item.isVisible ? 'opacity-100' : 'opacity-50'}
      `}
      onClick={() => onToggleItem(item.id)}
    >
      {/* Color indicator */}
      <div
        className={`
          ${compact ? 'w-3 h-3' : 'w-4 h-4'} 
          rounded border border-gray-300 flex-shrink-0
        `}
        style={{ backgroundColor: item.color }}
      />
      
      {/* Checkbox */}
      <input
        type="checkbox"
        checked={item.isVisible}
        onChange={() => onToggleItem(item.id)}
        className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
      />
      
      {/* Label */}
      <span className="flex-1 truncate" title={item.label}>
        {item.label}
      </span>
      
      {/* Count */}
      {showCounts && (
        <span className={`
          text-gray-500 font-medium
          ${compact ? 'text-xs' : 'text-sm'}
        `}>
          {item.count}
        </span>
      )}
    </div>
  );

  // Render group
  const renderGroup = (groupType: string, items: HolidayLegendItem[]) => {
    if (items.length === 0) return null;

    const isExpanded = expandedGroups.has(groupType);
    const visibleCount = items.filter(item => item.isVisible).length;
    const totalCount = items.length;

    return (
      <div key={groupType} className="border-b border-gray-200 last:border-b-0">
        {/* Group header */}
        <div
          className="flex items-center justify-between p-2 cursor-pointer hover:bg-gray-50"
          onClick={() => toggleGroup(groupType)}
        >
          <div className="flex items-center space-x-2">
            {/* Expand/collapse icon */}
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            
            {/* Group label */}
            <span className={`font-medium ${compact ? 'text-sm' : 'text-base'}`}>
              {groupLabels[groupType as keyof typeof groupLabels]}
            </span>
            
            {/* Visible count */}
            <span className={`text-gray-500 ${compact ? 'text-xs' : 'text-sm'}`}>
              ({visibleCount}/{totalCount})
            </span>
          </div>

          {/* Toggle all button */}
          {showToggleAll && isExpanded && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                toggleAllInGroup(groupType, visibleCount < totalCount);
              }}
              className={`
                text-blue-600 hover:text-blue-800
                ${compact ? 'text-xs' : 'text-sm'}
              `}
            >
              {visibleCount < totalCount ? 'Alle' : 'Keine'}
            </button>
          )}
        </div>

        {/* Group items */}
        {isExpanded && (
          <div className="pl-4 pb-2 space-y-1">
            {items.map(renderLegendItem)}
          </div>
        )}
      </div>
    );
  };

  // Render flat list (non-grouped)
  const renderFlatList = () => {
    const allItems = Object.values(legendItems).flat();
    return (
      <div className="space-y-1 p-2">
        {allItems.map(renderLegendItem)}
      </div>
    );
  };

  if (holidays.length === 0) {
    return (
      <div className={`text-center text-gray-500 p-4 ${className}`}>
        <p className={compact ? 'text-sm' : 'text-base'}>
          Keine Feiertage zum Anzeigen
        </p>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-300 rounded-md shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
        <h3 className={`font-medium text-gray-900 ${compact ? 'text-sm' : 'text-base'}`}>
          Legende
        </h3>
        {showCounts && (
          <p className={`text-gray-500 ${compact ? 'text-xs' : 'text-sm'}`}>
            {holidays.length} Feiertage insgesamt
          </p>
        )}
      </div>

      {/* Content */}
      <div className={`${compact ? 'max-h-64' : 'max-h-96'} overflow-y-auto`}>
        {groupByType ? (
          <div>
            {Object.entries(legendItems).map(([groupType, items]) =>
              renderGroup(groupType, items)
            )}
          </div>
        ) : (
          renderFlatList()
        )}
      </div>
    </div>
  );
};

export default HolidayLegend;

// Utility hook for managing legend visibility
export const useHolidayLegend = (holidays: PersonalizedHoliday[]) => {
  const [visibleItems, setVisibleItems] = useState<string[]>([]);

  // Initialize visible items when holidays change
  React.useEffect(() => {
    const defaultVisible: string[] = [];
    
    // Auto-show federal states and relevance levels
    const federalStates = new Set(holidays.map(h => h.federal_state).filter(Boolean));
    const relevanceLevels = new Set(holidays.map(h => h.relevanceLevel));
    
    federalStates.forEach(state => {
      defaultVisible.push(`federal-state-${state}`);
    });
    
    relevanceLevels.forEach(level => {
      defaultVisible.push(`relevance-level-${level}`);
    });

    setVisibleItems(defaultVisible);
  }, [holidays]);

  const toggleItem = (itemId: string) => {
    setVisibleItems(prev => {
      if (prev.includes(itemId)) {
        return prev.filter(id => id !== itemId);
      } else {
        return [...prev, itemId];
      }
    });
  };

  const showAll = () => {
    const allItems: string[] = [];
    
    holidays.forEach(holiday => {
      if (holiday.federal_state) {
        allItems.push(`federal-state-${holiday.federal_state}`);
      }
      if (holiday.vacation_type) {
        allItems.push(`vacation-type-${holiday.vacation_type}`);
      }
      allItems.push(`holiday-type-${holiday.holiday_type}`);
      allItems.push(`relevance-level-${holiday.relevanceLevel}`);
    });

    setVisibleItems([...new Set(allItems)]);
  };

  const hideAll = () => {
    setVisibleItems([]);
  };

  return {
    visibleItems,
    toggleItem,
    showAll,
    hideAll,
    setVisibleItems
  };
};
