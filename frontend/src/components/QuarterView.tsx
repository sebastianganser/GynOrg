import React from 'react';
import moment from '../utils/locale';
import { CalendarAbsence } from '../types/absence';
import { Holiday } from '../services/holidayService';
import { getFederalStateAbbreviation, FEDERAL_STATE_NAMES } from '../utils/federalStates';
import { useCalendarSettings } from '../hooks/useCalendarSettings';

// Extended Holiday interface for grouped holidays
interface GroupedHoliday extends Holiday {
  federal_states?: string[]; // All federal states for this holiday
  display_federal_states?: string[]; // Only the activated federal states
}

interface QuarterViewProps {
  date: Date;
  events: CalendarAbsence[];
  holidays?: GroupedHoliday[];
  onSelectEvent?: (event: CalendarAbsence) => void;
  onSelectSlot?: (slotInfo: { start: Date; end: Date }) => void;
}

export const QuarterView: React.FC<QuarterViewProps> = ({
  date,
  events,
  holidays = [],
  onSelectEvent,
  onSelectSlot
}) => {
  // Load calendar settings to get active federal states
  const { data: calendarSettings } = useCalendarSettings();
  
  // Get the quarter start date
  const quarterStart = moment(date).startOf('quarter');
  
  // Generate the three months of the quarter
  const months = [
    quarterStart.clone(),
    quarterStart.clone().add(1, 'month'),
    quarterStart.clone().add(2, 'month')
  ];

  // Filter events for each month
  const getEventsForMonth = (monthDate: moment.Moment) => {
    const monthStart = monthDate.clone().startOf('month');
    const monthEnd = monthDate.clone().endOf('month');
    
    return events.filter(event => {
      const eventStart = moment(event.start);
      const eventEnd = moment(event.end);
      
      // Check if event overlaps with this month
      return eventStart.isSameOrBefore(monthEnd, 'day') && 
             eventEnd.isSameOrAfter(monthStart, 'day');
    });
  };

  // Generate calendar days for a month
  const generateMonthDays = (monthDate: moment.Moment) => {
    const startOfMonth = monthDate.clone().startOf('month');
    const endOfMonth = monthDate.clone().endOf('month');
    const startOfCalendar = startOfMonth.clone().startOf('week');
    const endOfCalendar = endOfMonth.clone().endOf('week');
    
    const days = [];
    const current = startOfCalendar.clone();
    
    while (current.isSameOrBefore(endOfCalendar, 'day')) {
      days.push(current.clone());
      current.add(1, 'day');
    }
    
    return days;
  };

  // Get events for a specific day
  const getEventsForDay = (dayDate: moment.Moment, monthEvents: CalendarAbsence[]) => {
    return monthEvents.filter(event => {
      const eventStart = moment(event.start);
      const eventEnd = moment(event.end);
      
      return dayDate.isBetween(eventStart, eventEnd, 'day', '[]');
    });
  };

  // Get holidays for a specific day
  const getHolidaysForDay = (dayDate: moment.Moment) => {
    return holidays.filter(holiday => 
      moment(holiday.date).isSame(dayDate, 'day')
    );
  };

  // Get holiday display name with federal state information
  const getHolidayDisplayName = (holiday: GroupedHoliday): string => {
    let displayName = holiday.name;
    
    // Add federal state information for state-specific holidays
    if (!holiday.is_nationwide && calendarSettings) {
      // Get all federal states for this holiday
      const holidayFederalStates = holiday.federal_states || [];
      
      if (holidayFederalStates.length > 0) {
        // Filter to only show activated federal states
        const activatedStates = holidayFederalStates.filter(state => {
          return calendarSettings.selected_federal_states.some(selectedState => {
            // Direct match (same format)
            if (selectedState === state) {
              return true;
            }
            
            // Check if selectedState is a code and state is a name
            const nameFromCode = Object.keys(FEDERAL_STATE_NAMES).find(
              code => code === selectedState && FEDERAL_STATE_NAMES[code] === state
            );
            if (nameFromCode) {
              return true;
            }
            
            // Check if selectedState is a name and state is a code
            const codeFromName = Object.keys(FEDERAL_STATE_NAMES).find(
              code => FEDERAL_STATE_NAMES[code] === selectedState && code === state
            );
            if (codeFromName) {
              return true;
            }
            
            return false;
          });
        });
        
        if (activatedStates.length > 0) {
          // Convert to abbreviations and sort
          const stateAbbreviations = activatedStates
            .map(state => getFederalStateAbbreviation(state))
            .sort();
          
          // Format based on number of states
          if (stateAbbreviations.length === 1) {
            displayName = `${holiday.name} (${stateAbbreviations[0]})`;
          } else if (stateAbbreviations.length <= 4) {
            displayName = `${holiday.name} (${stateAbbreviations.join(', ')})`;
          } else {
            displayName = `${holiday.name} (${stateAbbreviations.length} BL)`;
          }
        }
      }
    }
    
    // Apply abbreviations if the name is too long
    if (displayName.length > 20) {
      // Common abbreviations for German holidays
      const abbreviations: { [key: string]: string } = {
        'Reformationstag': 'Ref.tag',
        'Buß- und Bettag': 'Buß-/Bettag',
        'Heilige Drei Könige': 'Hl. 3 Könige',
        'Christi Himmelfahrt': 'Chr. Himmelfahrt',
        'Fronleichnam': 'Fronleichnam',
        'Mariä Himmelfahrt': 'Mariä Himmelfahrt',
        'Tag der Deutschen Einheit': 'Tag d. Einheit',
        'Allerheiligen': 'Allerheiligen',
        'Weihnachtstag': '1. Weihnachtstag',
        '2. Weihnachtstag': '2. Weihnachtstag'
      };

      // Check if we can abbreviate the holiday name part
      const abbreviatedName = abbreviations[holiday.name];
      if (abbreviatedName && !holiday.is_nationwide && holiday.federal_states && holiday.federal_states.length > 0) {
        const stateAbbr = getFederalStateAbbreviation(holiday.federal_states[0]);
        displayName = `${abbreviatedName} (${stateAbbr})`;
      } else if (abbreviatedName) {
        displayName = abbreviatedName;
      } else if (displayName.length > 20) {
        // Fallback: truncate if still too long
        displayName = displayName.substring(0, 17) + '...';
      }
    }

    return displayName;
  };

  const handleDayClick = (dayDate: moment.Moment) => {
    if (onSelectSlot) {
      onSelectSlot({
        start: dayDate.toDate(),
        end: dayDate.toDate()
      });
    }
  };

  return (
    <div className="p-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {months.map((month, monthIndex) => {
          const monthEvents = getEventsForMonth(month);
          const monthDays = generateMonthDays(month);
          
          return (
            <div key={monthIndex} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              {/* Month header */}
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  {month.format('MMMM YYYY')}
                </h3>
              </div>
              
              {/* Calendar grid */}
              <div className="p-3">
                {/* Weekday headers */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'].map((day) => (
                    <div key={day} className="text-xs font-medium text-gray-500 text-center py-1">
                      {day}
                    </div>
                  ))}
                </div>
                
                {/* Calendar days */}
                <div className="grid grid-cols-7 gap-1">
                  {monthDays.map((day, dayIndex) => {
                    const isCurrentMonth = day.month() === month.month();
                    const isToday = day.isSame(moment(), 'day');
                    const isWeekend = day.day() === 0 || day.day() === 6;
                    const dayEvents = getEventsForDay(day, monthEvents);
                    const dayHolidays = getHolidaysForDay(day);
                    
                    const getTooltipText = (): string => {
                      if (dayHolidays.length === 0) return '';
                      if (dayHolidays.length === 1) return dayHolidays[0].name;
                      return dayHolidays.map(h => h.name).join(', ');
                    };
                    
                    return (
                      <div
                        key={dayIndex}
                        onClick={() => handleDayClick(day)}
                        className={`
                          relative min-h-[40px] p-1 text-xs cursor-pointer transition-colors
                          ${isCurrentMonth 
                            ? isToday 
                              ? 'bg-blue-100 text-blue-900 font-semibold' 
                              : isWeekend 
                                ? 'bg-gray-50 text-gray-700' 
                                : 'text-gray-900 hover:bg-gray-50'
                            : 'text-gray-400'
                          }
                        `}
                        title={getTooltipText()}
                      >
                        <div className="flex items-start justify-between">
                          <span className="text-xs font-medium">
                            {day.format('D')}
                          </span>
                        </div>
                        
                        {/* Holiday indicator */}
                        {dayHolidays.length > 0 && (
                          <div className="mt-0.5">
                            <div className="text-xs text-red-600 font-medium leading-tight">
                              {getHolidayDisplayName(dayHolidays[0])}
                              {dayHolidays.length > 1 && (
                                <span className="ml-1 text-red-500">+{dayHolidays.length - 1}</span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {/* Event indicators */}
                        {dayEvents.length > 0 && (
                          <div className="mt-1 space-y-0.5">
                            {dayEvents.slice(0, 2).map((event, eventIndex) => (
                              <div
                                key={eventIndex}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onSelectEvent?.(event);
                                }}
                                className="w-full h-1 rounded-sm cursor-pointer"
                                style={{ 
                                  backgroundColor: event.resource.absence_type?.color || '#3B82F6' 
                                }}
                                title={event.title}
                              />
                            ))}
                            {dayEvents.length > 2 && (
                              <div className="text-center text-gray-500 text-xs">
                                +{dayEvents.length - 2}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Legend */}
      {events.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Abwesenheitstypen</h4>
          <div className="flex flex-wrap gap-4">
            {Array.from(new Set(events.map(e => e.resource.absence_type?.name).filter(Boolean)))
              .map((typeName, index) => {
                const event = events.find(e => e.resource.absence_type?.name === typeName);
                const color = event?.resource.absence_type?.color || '#3B82F6';
                
                return (
                  <div key={index} className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-sm"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-sm text-gray-700">{typeName}</span>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
};
