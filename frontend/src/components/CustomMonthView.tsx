import React from 'react';
import moment from '../utils/locale';
import { Holiday, HolidayType, getHolidayIcon } from '../types/holiday';
import { Absence } from '../types/absence';
import { getFederalStateAbbreviation, FEDERAL_STATE_NAMES } from '../utils/federalStates';

interface CustomMonthViewProps {
  date: Date;
  events: Array<{
    id: number;
    title: string;
    start: Date;
    end: Date;
    resource: Absence;
    allDay: boolean;
  }>;
  holidays: Holiday[];
  onSelectEvent?: (event: any) => void;
  onSelectSlot?: (slotInfo: { start: Date; end: Date }) => void;
  calendarSettings?: any;
  holidayDisplayFilter?: any;
}

export const CustomMonthView: React.FC<CustomMonthViewProps> = ({
  date,
  events,
  holidays,
  onSelectEvent,
  onSelectSlot,
  calendarSettings,
  holidayDisplayFilter
}) => {
  // Get the first and last day of the month
  const startOfMonth = moment(date).startOf('month');
  const endOfMonth = moment(date).endOf('month');
  
  // Get the first day of the calendar (start of week containing first day of month)
  const startOfCalendar = moment(startOfMonth).startOf('week');
  
  // Get the last day of the calendar (end of week containing last day of month)
  const endOfCalendar = moment(endOfMonth).endOf('week');
  
  // Generate all weeks in the calendar
  const weeks: Date[][] = [];
  let currentWeek: Date[] = [];
  let currentDate = moment(startOfCalendar);
  
  while (currentDate.isSameOrBefore(endOfCalendar)) {
    currentWeek.push(currentDate.toDate());
    
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
    
    currentDate.add(1, 'day');
  }
  
  // Helper function to get events for a specific date
  const getEventsForDate = (cellDate: Date) => {
    return events.filter(event => {
      const eventStart = moment(event.start);
      const eventEnd = moment(event.end);
      const cell = moment(cellDate);
      
      return cell.isSameOrAfter(eventStart, 'day') && cell.isSameOrBefore(eventEnd, 'day');
    });
  };
  
  // Helper function to get holidays for a specific date
  const getHolidaysForDate = (cellDate: Date) => {
    return holidays.filter(holiday => 
      moment(holiday.date).isSame(cellDate, 'day')
    );
  };
  
  // Helper function to format holiday display name
  const getHolidayDisplayName = (holiday: Holiday): string => {
    const icon = getHolidayIcon(holiday);
    let displayName = holiday.name;
    
    if (holiday.holiday_type === HolidayType.SCHOOL_VACATION && holiday.school_vacation_type) {
      const vacationTypeLabels = {
        'WINTER': 'Winterferien',
        'EASTER': 'Osterferien', 
        'SUMMER': 'Sommerferien',
        'AUTUMN': 'Herbstferien',
        'OTHER': 'Ferien'
      };
      displayName = vacationTypeLabels[holiday.school_vacation_type] || holiday.name;
    }
    
    // Add federal state information
    if (!holiday.is_nationwide && calendarSettings) {
      const holidayFederalStates = (holiday as any).federal_states || (holiday.federal_state ? [holiday.federal_state] : []);
      
      if (holidayFederalStates.length > 0) {
        const activatedStates = holidayFederalStates.filter((state: string) => {
          return calendarSettings.selected_federal_states.some((selectedState: string) => {
            if (selectedState === state) return true;
            
            const nameFromCode = Object.keys(FEDERAL_STATE_NAMES).find(
              code => code === selectedState && FEDERAL_STATE_NAMES[code] === state
            );
            if (nameFromCode) return true;
            
            const codeFromName = Object.keys(FEDERAL_STATE_NAMES).find(
              code => FEDERAL_STATE_NAMES[code] === selectedState && code === state
            );
            if (codeFromName) return true;
            
            return false;
          });
        });
        
        if (activatedStates.length > 0) {
          const stateAbbreviations = activatedStates
            .map((state: string) => getFederalStateAbbreviation(state))
            .sort();
          
          if (stateAbbreviations.length === 1) {
            displayName = `${displayName} (${stateAbbreviations[0]})`;
          } else if (stateAbbreviations.length <= 4) {
            displayName = `${displayName} (${stateAbbreviations.join(', ')})`;
          } else {
            displayName = `${displayName} (${stateAbbreviations.length} BL)`;
          }
        }
      }
    }
    
    const fullDisplayName = `${icon} ${displayName}`;
    
    if (fullDisplayName.length > 25) {
      const parenIndex = fullDisplayName.indexOf(' (');
      if (parenIndex > 0 && parenIndex < 22) {
        return fullDisplayName.substring(0, parenIndex) + ' (...)';
      }
      return fullDisplayName.substring(0, 22) + '...';
    }
    
    return fullDisplayName;
  };
  
  const handleDateClick = (cellDate: Date) => {
    if (onSelectSlot) {
      onSelectSlot({
        start: cellDate,
        end: cellDate
      });
    }
  };
  
  const handleEventClick = (event: any) => {
    if (onSelectEvent) {
      onSelectEvent(event);
    }
  };
  
  const today = new Date();
  const currentMonth = moment(date).month();
  const currentYear = moment(date).year();
  
  return (
    <div className="custom-month-view">
      {/* Header with day names */}
      <div className="grid grid-cols-8 border-b border-gray-200 bg-gray-50">
        <div className="week-number-header text-center py-2 px-1 text-xs font-semibold text-gray-600 border-r-2 border-gray-300">
          KW
        </div>
        {['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'].map((day, index) => (
          <div key={index} className="text-center py-2 px-1 text-sm font-semibold text-gray-700">
            {day}
          </div>
        ))}
      </div>
      
      {/* Calendar grid */}
      <div className="calendar-grid">
        {weeks.map((week, weekIndex) => {
          const weekNumber = moment(week[0]).isoWeek();
          
          return (
            <div key={weekIndex} className="grid grid-cols-8 border-b border-gray-200">
              {/* Week number cell */}
              <div className="week-number-cell text-center py-2 px-1 text-xs font-semibold text-gray-600 bg-gray-100 border-r-2 border-gray-300">
                {weekNumber}
              </div>
              
              {/* Day cells */}
              {week.map((cellDate, dayIndex) => {
                const isToday = moment(cellDate).isSame(today, 'day');
                const isWeekend = moment(cellDate).day() === 0 || moment(cellDate).day() === 6;
                const isCurrentMonth = moment(cellDate).month() === currentMonth && moment(cellDate).year() === currentYear;
                const dayEvents = getEventsForDate(cellDate);
                const dayHolidays = getHolidaysForDate(cellDate);
                
                // Filter holidays based on display filter
                const filteredHolidays = dayHolidays.filter(holiday => {
                  if (holidayDisplayFilter) {
                    if (!holidayDisplayFilter.showPublicHolidays && holiday.holiday_type === HolidayType.PUBLIC_HOLIDAY) {
                      return false;
                    }
                    if (!holidayDisplayFilter.showSchoolVacations && holiday.holiday_type === HolidayType.SCHOOL_VACATION) {
                      return false;
                    }
                  }
                  return true;
                });
                
                return (
                  <div
                    key={dayIndex}
                    className={`
                      h-[100px] p-1 border-r border-gray-200 cursor-pointer transition-colors overflow-hidden
                      ${isToday ? 'bg-blue-50' : isWeekend ? 'bg-gray-50' : 'bg-white'}
                      ${!isCurrentMonth ? 'opacity-50' : ''}
                      hover:bg-blue-100
                    `}
                    onClick={() => handleDateClick(cellDate)}
                  >
                    {/* Date number */}
                    <div className={`
                      text-sm font-medium mb-1
                      ${isToday ? 'text-blue-900 font-bold' : isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
                    `}>
                      {moment(cellDate).format('D')}
                    </div>
                    
                    {/* Holidays */}
                    {filteredHolidays.length > 0 && (
                      <div className="mb-1">
                        {filteredHolidays.slice(0, 2).map((holiday, idx) => (
                          <div
                            key={idx}
                            className={`text-xs font-medium mb-0.5 truncate ${
                              holiday.holiday_type === HolidayType.PUBLIC_HOLIDAY 
                                ? 'text-red-600' 
                                : 'text-blue-600'
                            }`}
                            style={{ maxWidth: '120px' }}
                            title={holiday.name}
                          >
                            {getHolidayDisplayName(holiday)}
                          </div>
                        ))}
                        {filteredHolidays.length > 2 && (
                          <div className="text-xs text-gray-500">
                            +{filteredHolidays.length - 2} weitere
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Events */}
                    {dayEvents.length > 0 && (
                      <div className="space-y-0.5">
                        {dayEvents.slice(0, 3).map((event, idx) => (
                          <div
                            key={idx}
                            className="text-xs px-1 py-0.5 rounded truncate cursor-pointer"
                            style={{
                              backgroundColor: event.resource.absence_type?.color || '#3B82F6',
                              color: 'white'
                            }}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEventClick(event);
                            }}
                            title={event.title}
                          >
                            {event.title}
                          </div>
                        ))}
                        {dayEvents.length > 3 && (
                          <div className="text-xs text-gray-500 px-1">
                            +{dayEvents.length - 3} weitere
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
};
