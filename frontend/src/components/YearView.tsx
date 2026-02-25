import React from 'react';
import moment from '../utils/locale';
import { CalendarAbsence } from '../types/absence';
import { Holiday } from '../services/holidayService';

interface YearViewProps {
  date: Date;
  events: CalendarAbsence[];
  holidays?: Holiday[];
  onSelectEvent?: (event: CalendarAbsence) => void;
  onSelectSlot?: (slotInfo: { start: Date; end: Date }) => void;
  onMonthClick?: (monthDate: Date) => void;
}

export const YearView: React.FC<YearViewProps> = ({
  date,
  events,
  holidays = [],
  onSelectEvent,
  onSelectSlot,
  onMonthClick
}) => {
  // Get the year start date
  const yearStart = moment(date).startOf('year');
  
  // Generate all 12 months of the year
  const months = Array.from({ length: 12 }, (_, index) => 
    yearStart.clone().add(index, 'month')
  );

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

  // Generate calendar days for a month (simplified for year view)
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

  const handleMonthClick = (monthDate: moment.Moment) => {
    if (onMonthClick) {
      onMonthClick(monthDate.toDate());
    }
  };

  const handleDayClick = (dayDate: moment.Moment, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onSelectSlot) {
      onSelectSlot({
        start: dayDate.toDate(),
        end: dayDate.toDate()
      });
    }
  };

  return (
    <div className="p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {months.map((month, monthIndex) => {
          const monthEvents = getEventsForMonth(month);
          const monthDays = generateMonthDays(month);
          const isCurrentMonth = month.isSame(moment(), 'month');
          
          return (
            <div 
              key={monthIndex} 
              className={`
                bg-white border rounded-lg overflow-hidden cursor-pointer transition-all hover:shadow-md
                ${isCurrentMonth ? 'border-blue-300 bg-blue-50' : 'border-gray-200'}
              `}
              onClick={() => handleMonthClick(month)}
            >
              {/* Month header */}
              <div className={`
                px-3 py-2 border-b text-center
                ${isCurrentMonth 
                  ? 'bg-blue-100 border-blue-200 text-blue-900' 
                  : 'bg-gray-50 border-gray-200 text-gray-900'
                }
              `}>
                <h3 className="text-sm font-semibold">
                  {month.format('MMMM')}
                </h3>
                {monthEvents.length > 0 && (
                  <div className="text-xs text-gray-600 mt-1">
                    {monthEvents.length} Abwesenheit{monthEvents.length !== 1 ? 'en' : ''}
                  </div>
                )}
              </div>
              
              {/* Mini calendar grid */}
              <div className="p-2">
                {/* Weekday headers */}
                <div className="grid grid-cols-7 gap-0.5 mb-1">
                  {['S', 'M', 'D', 'M', 'D', 'F', 'S'].map((day, index) => (
                    <div key={index} className="text-xs text-gray-400 text-center py-0.5">
                      {day}
                    </div>
                  ))}
                </div>
                
                {/* Calendar days */}
                <div className="grid grid-cols-7 gap-0.5">
                  {monthDays.map((day, dayIndex) => {
                    const isCurrentMonth = day.month() === month.month();
                    const isToday = day.isSame(moment(), 'day');
                    const isWeekend = day.day() === 0 || day.day() === 6;
                    const dayEvents = getEventsForDay(day, monthEvents);
                    const hasEvents = dayEvents.length > 0;
                    
                    return (
                      <div
                        key={dayIndex}
                        onClick={(e) => isCurrentMonth && handleDayClick(day, e)}
                        className={`
                          relative w-6 h-6 text-xs flex items-center justify-center transition-colors
                          ${isCurrentMonth 
                            ? isToday 
                              ? 'bg-blue-500 text-white font-semibold rounded-full' 
                              : hasEvents
                                ? 'bg-red-100 text-red-900 rounded'
                                : isWeekend 
                                  ? 'text-gray-500 hover:bg-gray-100 rounded' 
                                  : 'text-gray-900 hover:bg-gray-100 rounded'
                            : 'text-gray-300'
                          }
                          ${isCurrentMonth && !isToday ? 'cursor-pointer' : ''}
                        `}
                      >
                        {day.format('D')}
                        
                        {/* Event indicator */}
                        {hasEvents && !isToday && (
                          <div className="absolute bottom-0 right-0 w-1.5 h-1.5 bg-red-500 rounded-full" />
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
      
      {/* Year summary */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total events summary */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Jahresübersicht</h4>
          <div className="space-y-1 text-sm text-gray-600">
            <div>Gesamt Abwesenheiten: {events.length}</div>
            <div>
              Urlaubstage: {events.filter(e => e.resource.absence_type?.name?.toLowerCase().includes('urlaub')).length}
            </div>
            <div>
              Krankheitstage: {events.filter(e => e.resource.absence_type?.name?.toLowerCase().includes('krank')).length}
            </div>
          </div>
        </div>
        
        {/* Monthly distribution */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Monatsverteilung</h4>
          <div className="space-y-1 text-sm">
            {months
              .map(month => ({
                month: month.format('MMM'),
                count: getEventsForMonth(month).length
              }))
              .filter(item => item.count > 0)
              .slice(0, 6)
              .map((item, index) => (
                <div key={index} className="flex justify-between text-gray-600">
                  <span>{item.month}</span>
                  <span>{item.count}</span>
                </div>
              ))}
          </div>
        </div>
        
        {/* Legend */}
        {events.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Abwesenheitstypen</h4>
            <div className="space-y-2">
              {Array.from(new Set(events.map(e => e.resource.absence_type?.name).filter(Boolean)))
                .slice(0, 5)
                .map((typeName, index) => {
                  const event = events.find(e => e.resource.absence_type?.name === typeName);
                  const color = event?.resource.absence_type?.color || '#3B82F6';
                  const count = events.filter(e => e.resource.absence_type?.name === typeName).length;
                  
                  return (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: color }}
                        />
                        <span className="text-xs text-gray-700">{typeName}</span>
                      </div>
                      <span className="text-xs text-gray-500">{count}</span>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
