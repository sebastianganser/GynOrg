import React from 'react';
import moment from '../utils/locale';
import { Holiday } from '../services/holidayService';

interface CustomDateCellProps {
  date: Date;
  holidays: Holiday[];
  isToday: boolean;
  isWeekend: boolean;
  isCurrentMonth: boolean;
  onClick?: () => void;
}

export const CustomDateCell: React.FC<CustomDateCellProps> = ({
  date,
  holidays,
  isToday,
  isWeekend,
  isCurrentMonth,
  onClick
}) => {
  // Find holidays for this specific date
  const dayHolidays = holidays.filter(holiday => 
    moment(holiday.date).isSame(date, 'day')
  );

  // Get the first holiday name (truncated if too long)
  const getHolidayDisplayName = (holiday: Holiday): string => {
    const name = holiday.name;
    if (name.length <= 20) return name;
    
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

    return abbreviations[name] || (name.length > 20 ? name.substring(0, 17) + '...' : name);
  };

  // Get full holiday names for tooltip
  const getTooltipText = (): string => {
    if (dayHolidays.length === 0) return '';
    if (dayHolidays.length === 1) return dayHolidays[0].name;
    return dayHolidays.map(h => h.name).join(', ');
  };

  const dayNumber = moment(date).format('D');
  const isOutsideMonth = !isCurrentMonth;

  return (
    <div
      className={`
        relative h-full w-full p-1 cursor-pointer transition-colors
        ${isToday ? 'bg-blue-100 text-blue-900 font-semibold' : 
          isOutsideMonth ? 'text-gray-400' : 
          isWeekend ? 'bg-gray-50 text-gray-700' : 'text-gray-900'}
        hover:bg-blue-50 hover:text-blue-900
      `}
      onClick={onClick}
      title={getTooltipText()}
    >
      {/* Date number */}
      <div className="flex items-start justify-between">
        <span className={`text-sm ${isToday ? 'font-bold' : 'font-medium'}`}>
          {dayNumber}
        </span>
      </div>
      
      {/* Holiday indicator */}
      {dayHolidays.length > 0 && (
        <div className="mt-0.5">
          <div 
            className={`
              text-xs font-medium text-red-600 leading-tight
              ${dayHolidays.length > 1 ? 'cursor-help' : ''}
            `}
            title={getTooltipText()}
          >
            {getHolidayDisplayName(dayHolidays[0])}
            {dayHolidays.length > 1 && (
              <span className="ml-1 text-red-500">+{dayHolidays.length - 1}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
