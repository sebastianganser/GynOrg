import React, { useMemo, useState, useEffect } from 'react';
import moment from 'moment';
import { CalendarAbsence } from '../types/absence';
import { Employee, VacationAllowance } from '../types/employee';
import { getHolidayColor } from '../types/holiday';
import { vacationService } from '../services/vacationService';

interface YearlyPrintViewProps {
  events: any[]; // Combined absences and holidays from react-big-calendar
  date: Date;
  localizer: any;
  employees: Employee[];
}

export const YearlyPrintView: React.FC<YearlyPrintViewProps> = ({ events, date, localizer, employees }) => {
  const year = moment(date).year();
  const [allowances, setAllowances] = useState<Record<number, VacationAllowance>>({});
  
  // Fetch vacation allowances for the selected year
  useEffect(() => {
    let isMounted = true;
    const fetchAllowances = async () => {
      try {
        const data = await vacationService.getVacationAllowancesByYear(year);
        if (isMounted) {
          const allowanceMap: Record<number, VacationAllowance> = {};
          data.forEach(a => {
            allowanceMap[a.employee_id] = a;
          });
          setAllowances(allowanceMap);
        }
      } catch (error) {
        console.error("Failed to fetch allowances for print view:", error);
      }
    };
    fetchAllowances();
    return () => { isMounted = false; };
  }, [year]);

  // Process data for the views
  const currentYearEvents = useMemo(() => {
    return events.filter((e: any) => {
      if (e.isHoliday || e.isConsolidated) return false;
      
      const eStart = moment(e.start);
      const eEndActual = e.allDay && !e.halfDayTime ? moment(e.end).subtract(1, 'day') : moment(e.end);
      const startOfYear = moment(date).startOf('year');
      const endOfYear = moment(date).endOf('year');
      return eStart.isSameOrBefore(endOfYear, 'day') && eEndActual.isSameOrAfter(startOfYear, 'day');
    });
  }, [events, date]);

  // Months array for the Gantt Grid
  const months = useMemo(() => {
    const result = [];
    for (let i = 0; i < 12; i++) {
      result.push(moment(date).month(i));
    }
    return result;
  }, [date]);

  // Employee summaries
  const employeeSummaries = useMemo(() => {
    const sortedEmployees = [...employees].sort((a, b) => a.last_name.localeCompare(b.last_name));
    
    return sortedEmployees.map(emp => {
      // Find absences for this employee in the current year
      const empEvents = currentYearEvents.filter(e => e.resource?.employee_id === emp.id);
      
      // Calculate used days (rough calculation based on absence data, excluding weekends/holidays ideally, 
      // but we use the resource.duration if available, otherwise fallback)
      let usedDays = 0;
      const absenceList = empEvents.map(e => {
        const absence = e.resource;
        // The backend should calculate duration, fallback to basic day diff if missing
        let days = absence.duration || 0; 
        if (!days) {
          const s = moment(absence.start_date);
          const e = moment(absence.end_date);
          days = Math.max(1, e.diff(s, 'days') + 1);
          if (absence.half_day_time) days = 0.5;
        }
        
        // Add to total
        if (absence.absence_type?.name?.toLowerCase().includes('urlaub')) {
           usedDays += days;
        }

        return {
          id: absence.id,
          type: absence.absence_type?.name || 'Abwesenheit',
          start: moment(absence.start_date).format('DD.MM.YYYY'),
          end: moment(absence.end_date).format('DD.MM.YYYY'),
          days: days,
          status: absence.status
        };
      }).sort((a, b) => moment(a.start, 'DD.MM.YYYY').valueOf() - moment(b.start, 'DD.MM.YYYY').valueOf());

      const allowance = allowances[emp.id];
      const annual = allowance?.annual_allowance || 0;
      const carryover = allowance?.carryover_days || 0;
      const total = annual + carryover;
      const balance = total - usedDays;

      return {
        employee: emp,
        allowance: { annual, carryover, total, used: usedDays, balance },
        absences: absenceList
      };
    });
  }, [employees, currentYearEvents, allowances]);

  // CSS for printing
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      @media print {
        @page { size: A4 portrait; margin: 10mm; }
        @page landscapePage { size: A4 landscape; margin: 10mm; }
        
        body * { visibility: hidden; }
        .print-section, .print-section * { visibility: visible; }
        .print-section { position: absolute; left: 0; top: 0; width: 100%; height: auto; overflow: visible; background: white; }
        .print-page-break { page-break-before: always; }
        .landscape-section { page: landscapePage; }
        .no-print { display: none !important; }
        
        /* Prevent background colors from being stripped in some browsers */
        * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      }
    `;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  return (
    <div className="print-section bg-white text-gray-900 h-full overflow-y-auto text-sm w-full pb-20">
      <div className="flex justify-end p-4 no-print border-b bg-gray-50 sticky top-0 z-10">
        <button 
          onClick={() => window.print()}
          className="px-4 py-2 bg-blue-600 text-white rounded font-medium shadow hover:bg-blue-700 flex items-center gap-2 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
          PDF / Drucken
        </button>
      </div>

      {/* PAGE 1..N-1: Employee Invoices */}
      {employeeSummaries.map((summary, idx) => (
        <div key={summary.employee.id} className={`p-8 w-full max-w-[800px] mx-auto min-h-screen pt-12 ${idx > 0 ? 'print-page-break' : ''} border-b-8 border-gray-100 print:border-b-0`}>
          <div className="border-b-2 border-gray-800 pb-4 mb-8">
            <h2 className="text-3xl font-bold">{summary.employee.last_name}, {summary.employee.first_name}</h2>
            <p className="text-gray-500 mt-1">Urlaubsabrechnung für das Jahr {year}</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-6 mb-8 flex justify-between text-lg">
            <div>
              <div className="text-gray-600 text-sm">Urlaubsanspruch {year}:</div>
              <div className="font-bold">{summary.allowance.annual} Tage</div>
            </div>
            <div>
              <div className="text-gray-600 text-sm">Resturlaub Vorjahr:</div>
              <div className="font-bold">{summary.allowance.carryover} Tage</div>
            </div>
            <div className="text-right">
              <div className="text-gray-600 text-sm">Gesamtanspruch:</div>
              <div className="font-bold text-blue-800 text-xl">{summary.allowance.total} Tage</div>
            </div>
          </div>

          <h3 className="text-xl font-bold mb-4">Urlaube im Jahr {year}</h3>
          
          {summary.absences.length === 0 ? (
            <p className="text-gray-500 italic py-4 border-b border-t border-gray-100">Keine Urlaube verzeichnet.</p>
          ) : (
            <table className="w-full text-left border-collapse mb-8">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="py-2">Art</th>
                  <th className="py-2">Zeitraum</th>
                  <th className="py-2">Status</th>
                  <th className="py-2 text-right">Tage</th>
                </tr>
              </thead>
              <tbody>
                {summary.absences.map((abs, i) => (
                  <tr key={abs.id} className="border-b border-gray-200">
                    <td className="py-3">{abs.type}</td>
                    <td className="py-3">{abs.start === abs.end ? abs.start : `${abs.start} - ${abs.end}`}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${abs.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {abs.status === 'approved' ? 'Genehmigt' : 'Antrag'}
                      </span>
                    </td>
                    <td className="py-3 text-right font-medium">{abs.days}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-gray-50 font-bold border-b border-gray-300">
                  <td colSpan={3} className="py-3 px-2 text-right">Summe verplanter Urlaubstage:</td>
                  <td className="py-3 text-right">{summary.allowance.used}</td>
                </tr>
              </tfoot>
            </table>
          )}

          <div className="mt-8 border-t-2 border-gray-800 pt-6 flex justify-between items-end">
            <div className="text-gray-500 text-sm">
              Stand: {moment().format('DD.MM.YYYY')}
            </div>
            <div className="text-right">
              <div className="text-gray-600">Verbleibender Resturlaub:</div>
              <div className={`font-bold text-3xl mt-1 ${summary.allowance.balance < 0 ? 'text-red-600' : 'text-green-700'}`}>
                {summary.allowance.balance} Tage
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* PAGE N: Yearly Gantt Calendar (Landscape) */}
      <div className="landscape-section print-page-break p-8 w-full max-w-[1200px] mx-auto min-h-screen">
        <h1 className="text-2xl font-bold mb-6 text-center">Urlaubsplan {year}</h1>
        
        {/* Gantt Grid */}
        <div className="border border-gray-300 rounded overflow-hidden relative">
          {/* Header Row (Days) */}
          <div className="flex border-b border-gray-300 bg-gray-100 font-medium text-xs">
            <div className="w-24 flex-shrink-0 border-r border-gray-300 p-2">Monat</div>
            {Array.from({ length: 31 }, (_, i) => (
              <div key={i} className="flex-1 text-center border-r border-gray-200 py-2 last:border-r-0">
                {i + 1}
              </div>
            ))}
          </div>

          {/* Month Rows */}
          {months.map(monthObj => {
            const daysInMonth = monthObj.daysInMonth();
            const monthEvents = currentYearEvents.filter(e => {
              const s = moment(e.start);
              const endActual = e.allDay && !e.halfDayTime ? moment(e.end).subtract(1, 'day') : moment(e.end);
              return s.isSameOrBefore(monthObj.endOf('month'), 'day') && endActual.isSameOrAfter(monthObj.startOf('month'), 'day');
            });

            // Calculate overlap rows for stacking
            const eventsWithRow = monthEvents.map(event => {
                const s = moment.max(moment(event.start), monthObj.startOf('month'));
                const e = moment.min(event.allDay && !event.halfDayTime ? moment(event.end).subtract(1, 'day') : moment(event.end), monthObj.endOf('month'));
                return { event, startDay: s.date(), endDay: e.date(), row: 0 };
            });

            // Very simple row assignment for overlaps
            for (let i = 0; i < eventsWithRow.length; i++) {
                for (let j = 0; j < i; j++) {
                    if (eventsWithRow[i].startDay <= eventsWithRow[j].endDay && eventsWithRow[i].endDay >= eventsWithRow[j].startDay) {
                        if (eventsWithRow[i].row <= eventsWithRow[j].row) {
                            eventsWithRow[i].row = eventsWithRow[j].row + 1;
                        }
                    }
                }
            }

            const maxRow = eventsWithRow.reduce((max, ev) => Math.max(max, ev.row), 0);
            const rowHeight = 24;
            const containerHeight = Math.max(40, (maxRow + 1) * rowHeight + 8);

            return (
              <div key={monthObj.month()} className="flex border-b border-gray-200 last:border-b-0 relative" style={{ minHeight: `${containerHeight}px` }}>
                <div className="w-24 flex-shrink-0 border-r border-gray-300 p-2 font-medium bg-gray-50 flex items-center">
                  {monthObj.format('MMMM')}
                </div>
                <div className="flex-1 flex relative">
                  {/* Grid Lines */}
                  {Array.from({ length: 31 }, (_, i) => {
                    const isInvalidDay = i >= daysInMonth;
                    const date = moment(monthObj).date(i + 1);
                    const isWeekend = date.day() === 0 || date.day() === 6;
                    return (
                      <div 
                        key={i} 
                        className={`flex-1 border-r border-gray-100 last:border-r-0 ${isInvalidDay ? 'bg-gray-200' : isWeekend ? 'bg-gray-50' : ''}`}
                      />
                    );
                  })}
                  
                  {/* Events Layer */}
                  {eventsWithRow.map(({ event, startDay, endDay, row }, idx) => {
                    const leftPct = ((startDay - 1) / 31) * 100;
                    const widthPct = ((endDay - startDay + 1) / 31) * 100;
                    
                    const emp = employees.find(e => e.id === event.resource?.employee_id);
                    const color = emp?.calendar_color || '#3b82f6';
                    const initials = emp?.initials || (emp ? `${emp.first_name?.[0] || ''}${emp.last_name?.[0] || ''}` : '');
                    const isPending = event.resource?.status === 'pending';
                    const topOffset = 4 + (row * rowHeight);

                    return (
                      <div 
                        key={event.id}
                        className="absolute rounded text-[10px] font-bold text-white flex items-center justify-center overflow-hidden shadow-sm"
                        style={{
                          left: `${leftPct}%`,
                          width: `${widthPct}%`,
                          top: `${topOffset}px`,
                          height: '20px',
                          backgroundColor: color,
                          opacity: isPending ? 0.5 : 1,
                          border: isPending ? `1px dashed #fff` : '1px solid rgba(0,0,0,0.1)'
                        }}
                        title={event.title}
                      >
                        {widthPct > 3 ? initials : ''}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-8 flex flex-wrap gap-4 p-4 border border-gray-200 rounded bg-gray-50 text-xs">
          <div className="w-full font-bold mb-1">Mitarbeiter Legende:</div>
          {employees.map(emp => (
            <div key={emp.id} className="flex items-center gap-1.5 w-[200px]">
              <div className="w-4 h-4 rounded shadow-sm flex-shrink-0" style={{ backgroundColor: emp.calendar_color || '#3b82f6' }} />
              <span className="truncate">{emp.last_name}, {emp.first_name}</span>
            </div>
          ))}
          <div className="w-full mt-2 flex items-center gap-2 text-gray-600">
             <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ccc', opacity: 0.5, border: '1px dashed #999' }} />
             <span>Reduzierte Deckkraft/Gestrichelt = Urlaubsantrag (nicht genehmigt)</span>
          </div>
        </div>
      </div>

    </div>
  );
};

(YearlyPrintView as any).title = (date: Date, { localizer }: any) => `Jahr ${localizer.format(date, 'YYYY', 'de')}`;
(YearlyPrintView as any).navigate = (date: Date, action: string, { localizer }: any) => {
  switch (action) {
    case 'PREV': return localizer.add(date, -1, 'year');
    case 'NEXT': return localizer.add(date, 1, 'year');
    default: return date;
  }
};
