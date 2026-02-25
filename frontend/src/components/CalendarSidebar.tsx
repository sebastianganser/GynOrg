import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Users, Calendar, Search, Palette } from 'lucide-react';
import { useEmployeesForCalendar } from '../hooks/useEmployeesForCalendar';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
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

interface CalendarSidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  className?: string;
}

export function CalendarSidebar({
  isCollapsed,
  onToggle,
  className,
}: CalendarSidebarProps) {
  // Fetch employees for calendar
  const { data: employees, isLoading, error } = useEmployeesForCalendar(true);

  // Zustand store for filters
  const selectedEmployeeIds = useCalendarFilterStore((state) => state.selectedEmployeeIds);
  const toggleEmployee = useCalendarFilterStore((state) => state.toggleEmployee);
  const selectAllEmployees = useCalendarFilterStore((state) => state.selectAllEmployees);
  const deselectAllEmployees = useCalendarFilterStore((state) => state.deselectAllEmployees);

  const showHolidays = useCalendarFilterStore((state) => state.showHolidays);
  const showSchoolVacations = useCalendarFilterStore((state) => state.showSchoolVacations);
  const showVacationAbsences = useCalendarFilterStore((state) => state.showVacationAbsences);
  const showSickLeave = useCalendarFilterStore((state) => state.showSickLeave);
  const showTraining = useCalendarFilterStore((state) => state.showTraining);
  const showSpecialLeave = useCalendarFilterStore((state) => state.showSpecialLeave);

  const toggleHolidays = useCalendarFilterStore((state) => state.toggleHolidays);
  const toggleSchoolVacations = useCalendarFilterStore((state) => state.toggleSchoolVacations);
  const toggleVacationAbsences = useCalendarFilterStore((state) => state.toggleVacationAbsences);
  const toggleSickLeave = useCalendarFilterStore((state) => state.toggleSickLeave);
  const toggleTraining = useCalendarFilterStore((state) => state.toggleTraining);
  const toggleSpecialLeave = useCalendarFilterStore((state) => state.toggleSpecialLeave);

  // Local state for collapsible sections
  const [employeesExpanded, setEmployeesExpanded] = useState(true);
  const [calendarsExpanded, setCalendarsExpanded] = useState(true);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Color picker state
  const [colorPickerOpen, setColorPickerOpen] = useState<number | null>(null);
  const [pendingColor, setPendingColor] = useState<string>('');

  // Filter employees based on search query
  const filteredEmployees = employees?.filter((employee) =>
    employee.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  // Handle color change
  const handleColorChange = async (employeeId: number, newColor: string) => {
    try {
      const response = await fetch(`/api/employees/${employeeId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ calendar_color: newColor }),
      });

      if (!response.ok) {
        throw new Error('Failed to update color');
      }

      // Refetch employees to update the UI
      window.location.reload(); // Simple solution - in production use React Query's refetch
    } catch (error) {
      console.error('Error updating employee color:', error);
    }
  };

  // Handle color picker open
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
                          <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
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
                              className="h-3 w-3 rounded-full shrink-0 hover:ring-2 hover:ring-offset-1 hover:ring-primary transition-all"
                              style={{ backgroundColor: employee.calendar_color }}
                              title="Farbe ändern"
                            />
                            <span className="text-sm truncate flex-1 group-hover:text-foreground">
                              {employee.full_name}
                            </span>
                            <Palette
                              className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground"
                            />
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
                  <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                    <Checkbox
                      checked={showHolidays}
                      onCheckedChange={toggleHolidays}
                      className="shrink-0"
                    />
                    <div
                      className="h-3 w-3 rounded-full shrink-0 bg-red-500"
                      title="Feiertage"
                    />
                    <span className="text-sm truncate flex-1 group-hover:text-foreground">
                      Feiertage
                    </span>
                  </label>

                  {/* Schulferien */}
                  <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                    <Checkbox
                      checked={showSchoolVacations}
                      onCheckedChange={toggleSchoolVacations}
                      className="shrink-0"
                    />
                    <div
                      className="h-3 w-3 rounded-full shrink-0 bg-blue-500"
                      title="Schulferien"
                    />
                    <span className="text-sm truncate flex-1 group-hover:text-foreground">
                      Schulferien
                    </span>
                  </label>

                  {/* Urlaub */}
                  <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                    <Checkbox
                      checked={showVacationAbsences}
                      onCheckedChange={toggleVacationAbsences}
                      className="shrink-0"
                    />
                    <div
                      className="h-3 w-3 rounded-full shrink-0 bg-green-500"
                      title="Urlaub"
                    />
                    <span className="text-sm truncate flex-1 group-hover:text-foreground">
                      Urlaub
                    </span>
                  </label>

                  {/* Krankheit */}
                  <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                    <Checkbox
                      checked={showSickLeave}
                      onCheckedChange={toggleSickLeave}
                      className="shrink-0"
                    />
                    <div
                      className="h-3 w-3 rounded-full shrink-0 bg-orange-500"
                      title="Krankheit"
                    />
                    <span className="text-sm truncate flex-1 group-hover:text-foreground">
                      Krankheit
                    </span>
                  </label>

                  {/* Fortbildung */}
                  <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                    <Checkbox
                      checked={showTraining}
                      onCheckedChange={toggleTraining}
                      className="shrink-0"
                    />
                    <div
                      className="h-3 w-3 rounded-full shrink-0 bg-purple-500"
                      title="Fortbildung"
                    />
                    <span className="text-sm truncate flex-1 group-hover:text-foreground">
                      Fortbildung
                    </span>
                  </label>

                  {/* Sonderurlaub */}
                  <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                    <Checkbox
                      checked={showSpecialLeave}
                      onCheckedChange={toggleSpecialLeave}
                      className="shrink-0"
                    />
                    <div
                      className="h-3 w-3 rounded-full shrink-0 bg-pink-500"
                      title="Sonderurlaub"
                    />
                    <span className="text-sm truncate flex-1 group-hover:text-foreground">
                      Sonderurlaub
                    </span>
                  </label>
                </div>
              )}
            </CollapsibleContent>
          </Collapsible>
        </div>
      </ScrollArea>
    </div>
  );
}
