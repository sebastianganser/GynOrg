import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ChevronLeft, ChevronRight, Users, Calendar, Search, Palette, Info } from 'lucide-react';
import { useEmployeesForCalendar } from '../hooks/useEmployeesForCalendar';
import { useAbsenceTypes } from '../hooks/useAbsences';
import { useCalendarSettings } from '../hooks/useCalendarSettings';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import { employeeService } from '../services/employeeService';
import { getTextColorForBackground } from '../utils/colorUtils';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { Input } from './ui/input';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from './ui/collapsible';
import { cn } from '../lib/utils';
import type { Absence } from '../types/absence';
import type { Employee } from '../types/employee';

interface CalendarSidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  className?: string;
  selectedAbsence?: Absence | null;
  employees?: Employee[];
  onApproveAbsence?: (id: number) => void;
  onDeleteAbsence?: (id: number) => void;
  onEditAbsence?: () => void;
  onCloseDetails?: () => void;
}

export function CalendarSidebar({
  isCollapsed,
  onToggle,
  className,
  selectedAbsence,
  employees: propEmployees,
  onApproveAbsence,
  onDeleteAbsence,
  onEditAbsence,
  onCloseDetails,
}: CalendarSidebarProps) {
  // Fetch employees for calendar
  const queryClient = useQueryClient();
  const { data: employees, isLoading, error } = useEmployeesForCalendar(true);

  // Zustand store for filters
  const selectedEmployeeIds = useCalendarFilterStore((state) => state.selectedEmployeeIds);
  const toggleEmployee = useCalendarFilterStore((state) => state.toggleEmployee);
  const selectAllEmployees = useCalendarFilterStore((state) => state.selectAllEmployees);
  const deselectAllEmployees = useCalendarFilterStore((state) => state.deselectAllEmployees);

  // Fetch absence types
  const { data: absenceTypes, isLoading: isLoadingTypes } = useAbsenceTypes(true);

  // Fetch calendar settings (for holiday & school vacation colors)
  const { data: calendarSettings } = useCalendarSettings();

  const showHolidays = useCalendarFilterStore((state) => state.showHolidays);
  const showSchoolVacations = useCalendarFilterStore((state) => state.showSchoolVacations);
  const selectedAbsenceTypeIds = useCalendarFilterStore((state) => state.selectedAbsenceTypeIds);

  const toggleHolidays = useCalendarFilterStore((state) => state.toggleHolidays);
  const toggleSchoolVacations = useCalendarFilterStore((state) => state.toggleSchoolVacations);
  const toggleAbsenceType = useCalendarFilterStore((state) => state.toggleAbsenceType);
  const selectAllAbsenceTypes = useCalendarFilterStore((state) => state.selectAllAbsenceTypes);

  // Local state for collapsible sections
  const [employeesExpanded, setEmployeesExpanded] = useState(true);
  const [calendarsExpanded, setCalendarsExpanded] = useState(false);
  const [detailsExpanded, setDetailsExpanded] = useState(true);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Color picker state for Employees
  const [colorPickerOpen, setColorPickerOpen] = useState<number | null>(null);
  const [pendingColor, setPendingColor] = useState<string>('');



  // Filter employees based on search query
  const filteredEmployees = employees?.filter((employee) =>
    employee.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  // Handle color change
  const handleColorChange = async (employeeId: number, newColor: string) => {
    try {
      await employeeService.patchEmployee(employeeId, { calendar_color: newColor });

      // Refetch employees to update the UI
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    } catch (error) {
      console.error('Error updating employee color:', error);
    }
  };

  // Handle color picker open for employees
  const handleColorPickerClick = (employeeId: number, currentColor: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setColorPickerOpen(employeeId);
    setPendingColor(currentColor);
  };



  // Auto-select all employees on first load if none selected
  useEffect(() => {
    if (employees && employees.length > 0 && selectedEmployeeIds.length === 0) {
      const allIds = employees.map((emp) => emp.id);
      selectAllEmployees(allIds);
    }
  }, [employees, selectedEmployeeIds.length, selectAllEmployees]);

  // Auto-select all absence types on first load if none selected
  useEffect(() => {
    if (absenceTypes && absenceTypes.length > 0 && selectedAbsenceTypeIds.length === 0) {
      const allIds = absenceTypes.map((t) => t.id);
      selectAllAbsenceTypes(allIds);
    }
  }, [absenceTypes, selectedAbsenceTypeIds.length, selectAllAbsenceTypes]);

  // Handle select/deselect all employees
  const handleSelectAllEmployees = () => {
    if (selectedEmployeeIds.length === employees?.length) {
      deselectAllEmployees();
    } else {
      const allIds = employees?.map((emp) => emp.id) || [];
      selectAllEmployees(allIds);
    }
  };

  return (
    <div
      className={cn(
        'flex flex-col border-r bg-background transition-all duration-200',
        isCollapsed ? 'w-[60px]' : 'w-[250px]',
        className
      )}
    >
      {/* Header with Toggle Button */}
      <div className="flex h-14 items-center justify-between border-b px-3">

        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="h-8 w-8"
          title={isCollapsed ? 'Sidebar erweitern' : 'Sidebar minimieren'}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Scrollable Content */}
      <ScrollArea className="flex-1">
        <div className="space-y-4 p-3">
          {/* Meine Kalender Section */}
          <Collapsible
            open={employeesExpanded}
            onOpenChange={setEmployeesExpanded}
          >
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  'w-full justify-start px-2 py-1.5 h-auto font-medium text-sm hover:bg-accent',
                  isCollapsed && 'justify-center px-0'
                )}
              >
                <Users className="h-4 w-4 shrink-0" />
                {!isCollapsed && (
                  <>
                    <span className="ml-2 flex-1 text-left">
                      Mitarbeiter
                    </span>
                    <ChevronRight
                      className={cn(
                        'h-4 w-4 transition-transform',
                        employeesExpanded && 'rotate-90'
                      )}
                    />
                  </>
                )}
              </Button>
            </CollapsibleTrigger>

            <CollapsibleContent className="space-y-1 pt-2">
              {!isCollapsed && (
                <>

                  {/* Select All Button */}
                  {employees && employees.length > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleSelectAllEmployees}
                      className="w-full justify-start px-2 py-1 h-auto text-xs text-muted-foreground hover:text-foreground"
                    >
                      {selectedEmployeeIds.length === employees.length
                        ? 'Alle abwählen'
                        : 'Alle auswählen'}
                    </Button>
                  )}

                  {/* Loading State */}
                  {isLoading && (
                    <div className="px-2 py-4 text-xs text-muted-foreground">
                      Lade Mitarbeiter...
                    </div>
                  )}

                  {/* Error State */}
                  {error && (
                    <div className="px-2 py-4 text-xs text-destructive">
                      Fehler beim Laden der Mitarbeiter
                    </div>
                  )}

                  {/* Employee List */}
                  {filteredEmployees.length > 0 && (
                    <div className="space-y-1">
                      {filteredEmployees.map((employee) => (
                        <div key={employee.id} className="space-y-1">
                          <label className="flex items-center gap-2 cursor-pointer">
                            <Checkbox
                              checked={selectedEmployeeIds.includes(employee.id)}
                              onCheckedChange={() =>
                                toggleEmployee(employee.id)
                              }
                              className="shrink-0"
                            />
                            <button
                              type="button"
                              onClick={(e) => handleColorPickerClick(employee.id, employee.calendar_color, e)}
                              className="flex items-center gap-2 flex-1 px-2 py-1.5 rounded-md transition-all duration-150"
                              style={{
                                backgroundColor: employee.calendar_color,
                                color: getTextColorForBackground(employee.calendar_color),
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.25), 0 1px 2px rgba(0,0,0,0.15)';
                                e.currentTarget.style.transform = 'translateY(-1px)';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.boxShadow = 'none';
                                e.currentTarget.style.transform = 'none';
                              }}
                              title="Farbe ändern"
                            >
                              <span className="text-sm truncate flex-1 text-left font-medium">
                                {employee.full_name} ({employee.initials || `${employee.first_name?.[0] || ''}${employee.last_name?.[0] || ''}`})
                              </span>
                              <Palette
                                className="h-3.5 w-3.5 shrink-0 opacity-70"
                              />
                            </button>
                          </label>

                          {/* Inline Color Picker */}
                          {colorPickerOpen === employee.id && (
                            <div className="px-2 py-2 bg-accent/50 rounded-md space-y-2">
                              <div className="flex items-center gap-2">
                                <input
                                  type="color"
                                  value={pendingColor}
                                  onChange={(e) => setPendingColor(e.target.value)}
                                  className="h-8 w-full cursor-pointer rounded border border-input"
                                />
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  onClick={() => {
                                    handleColorChange(employee.id, pendingColor);
                                    setColorPickerOpen(null);
                                  }}
                                  className="flex-1 h-7 text-xs"
                                >
                                  Speichern
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setColorPickerOpen(null)}
                                  className="flex-1 h-7 text-xs"
                                >
                                  Abbrechen
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Empty State - No employees at all */}
                  {employees && employees.length === 0 && (
                    <div className="px-2 py-4 text-xs text-muted-foreground">
                      Keine Mitarbeiter gefunden
                    </div>
                  )}

                  {/* Empty State - No search results */}
                  {employees && employees.length > 0 && filteredEmployees.length === 0 && (
                    <div className="px-2 py-4 text-xs text-muted-foreground text-center">
                      Keine Ergebnisse für "{searchQuery}"
                    </div>
                  )}
                </>
              )}
            </CollapsibleContent>
          </Collapsible>

          <Separator />

          {/* Weitere Kalender Section */}
          <Collapsible
            open={calendarsExpanded}
            onOpenChange={setCalendarsExpanded}
          >
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  'w-full justify-start px-2 py-1.5 h-auto font-medium text-sm hover:bg-accent',
                  isCollapsed && 'justify-center px-0'
                )}
              >
                <Calendar className="h-4 w-4 shrink-0" />
                {!isCollapsed && (
                  <>
                    <span className="ml-2 flex-1 text-left">
                      Einträge anzeigen:
                    </span>
                    <ChevronRight
                      className={cn(
                        'h-4 w-4 transition-transform',
                        calendarsExpanded && 'rotate-90'
                      )}
                    />
                  </>
                )}
              </Button>
            </CollapsibleTrigger>

            <CollapsibleContent className="space-y-1 pt-2">
              {!isCollapsed && (
                <div className="space-y-1">
                  {/* Feiertage */}
                  <div className="space-y-1">
                    <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                      <Checkbox
                        checked={showHolidays}
                        onCheckedChange={toggleHolidays}
                        className="shrink-0"
                      />
                      <span className="text-sm truncate flex-1 group-hover:text-foreground">
                        Feiertage
                      </span>
                    </label>
                  </div>

                  {/* Schulferien */}
                  <div className="space-y-1">
                    <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                      <Checkbox
                        checked={showSchoolVacations}
                        onCheckedChange={toggleSchoolVacations}
                        className="shrink-0"
                      />
                      <span className="text-sm truncate flex-1 group-hover:text-foreground">
                        Schulferien
                      </span>
                    </label>
                  </div>

                  {/* Dynamic Absence Types */}
                  {isLoadingTypes && (
                    <div className="px-2 py-4 text-xs text-muted-foreground">
                      Lade Abwesenheitsarten...
                    </div>
                  )}

                  {absenceTypes && absenceTypes.map(type => (
                    <div key={type.id} className="space-y-1">
                      <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                        <Checkbox
                          checked={selectedAbsenceTypeIds.includes(type.id)}
                          onCheckedChange={() => toggleAbsenceType(type.id)}
                          className="shrink-0"
                        />
                        <span className="text-sm truncate flex-1 group-hover:text-foreground">
                          {type.name}
                        </span>
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </CollapsibleContent>
          </Collapsible>

          <Separator />

          {/* Abwesenheitsdetails Section */}
          <Collapsible
            open={detailsExpanded}
            onOpenChange={setDetailsExpanded}
          >
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  'w-full justify-start px-2 py-1.5 h-auto font-medium text-sm hover:bg-accent',
                  isCollapsed && 'justify-center px-0'
                )}
              >
                <Info className="h-4 w-4 shrink-0" />
                {!isCollapsed && (
                  <>
                    <span className="ml-2 flex-1 text-left">
                      Abwesenheitsdetails
                    </span>
                    <ChevronRight
                      className={cn(
                        'h-4 w-4 transition-transform',
                        detailsExpanded && 'rotate-90'
                      )}
                    />
                  </>
                )}
              </Button>
            </CollapsibleTrigger>

            <CollapsibleContent className="pt-2">
              {!isCollapsed && (
                <div className="px-2">
                  {selectedAbsence ? (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground">Mitarbeiter</label>
                        <p className="text-sm text-foreground">
                          {propEmployees?.find(e => e.id === selectedAbsence.employee_id)?.first_name}{' '}
                          {propEmployees?.find(e => e.id === selectedAbsence.employee_id)?.last_name}
                        </p>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground">Typ</label>
                        <p className="text-sm text-foreground">
                          {selectedAbsence.absence_type?.name || 'Abwesenheit'}
                        </p>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground">Zeitraum</label>
                        <p className="text-sm text-foreground">
                          {new Date(selectedAbsence.start_date).toLocaleDateString('de-DE')} - {new Date(selectedAbsence.end_date).toLocaleDateString('de-DE')}
                        </p>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground">Dauer</label>
                        <p className="text-sm text-foreground">
                          {selectedAbsence.duration_days} {selectedAbsence.duration_days === 1 ? 'Tag' : 'Tage'}
                          {selectedAbsence.half_day_time === 'AM' ? ' (Vormittag)' : selectedAbsence.half_day_time === 'PM' ? ' (Nachmittag)' : ''}
                        </p>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground">Status</label>
                        <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${
                          selectedAbsence.status === 'approved'
                            ? 'bg-green-100 text-green-800'
                            : selectedAbsence.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedAbsence.status === 'approved' ? 'Genehmigt' :
                            selectedAbsence.status === 'pending' ? 'Wartend' : selectedAbsence.status}
                        </span>
                      </div>
                      {selectedAbsence.comment && (
                        <div>
                          <label className="block text-xs font-medium text-muted-foreground">Kommentar</label>
                          <p className="text-sm text-foreground">{selectedAbsence.comment}</p>
                        </div>
                      )}
                      <div className="flex flex-col gap-1.5 pt-2">
                        {selectedAbsence.status === 'pending' && onApproveAbsence && (
                          <div className="flex gap-1.5">
                            <button
                              onClick={() => onApproveAbsence(selectedAbsence.id)}
                              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-2 py-1.5 rounded text-xs font-medium transition-colors"
                            >
                              Genehmigen
                            </button>
                            {onDeleteAbsence && (
                              <button
                                onClick={() => onDeleteAbsence(selectedAbsence.id)}
                                className="flex-1 bg-red-600 hover:bg-red-700 text-white px-2 py-1.5 rounded text-xs font-medium transition-colors"
                              >
                                Ablehnen
                              </button>
                            )}
                          </div>
                        )}
                        <div className="flex gap-1.5">
                          {onEditAbsence && (
                            <button
                              onClick={onEditAbsence}
                              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-2 py-1.5 rounded text-xs font-medium transition-colors"
                            >
                              Bearbeiten
                            </button>
                          )}
                          {selectedAbsence.status !== 'pending' && onDeleteAbsence && (
                            <button
                              onClick={() => onDeleteAbsence(selectedAbsence.id)}
                              className="flex-1 bg-red-600 hover:bg-red-700 text-white px-2 py-1.5 rounded text-xs font-medium transition-colors"
                            >
                              Löschen
                            </button>
                          )}
                          {onCloseDetails && (
                            <button
                              onClick={onCloseDetails}
                              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-2 py-1.5 rounded text-xs font-medium transition-colors"
                            >
                              Schließen
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="py-4 text-xs text-muted-foreground text-center">
                      Klicken Sie auf eine Abwesenheit im Kalender, um die Details hier anzuzeigen.
                    </div>
                  )}
                </div>
              )}
            </CollapsibleContent>
          </Collapsible>
        </div>
      </ScrollArea>
    </div>
  );
}
