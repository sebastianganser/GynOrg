import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ChevronLeft, ChevronRight, Users, Calendar, Search, Palette } from 'lucide-react';
import { useEmployeesForCalendar } from '../hooks/useEmployeesForCalendar';
import { useAbsenceTypes, useUpdateAbsenceType } from '../hooks/useAbsences';
import { useCalendarSettings, useUpdateCalendarSettings } from '../hooks/useCalendarSettings';
import { useCalendarFilterStore } from '../stores/calendarFilterStore';
import { employeeService } from '../services/employeeService';
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
  const queryClient = useQueryClient();
  const { data: employees, isLoading, error } = useEmployeesForCalendar(true);

  // Zustand store for filters
  const selectedEmployeeIds = useCalendarFilterStore((state) => state.selectedEmployeeIds);
  const toggleEmployee = useCalendarFilterStore((state) => state.toggleEmployee);
  const selectAllEmployees = useCalendarFilterStore((state) => state.selectAllEmployees);
  const deselectAllEmployees = useCalendarFilterStore((state) => state.deselectAllEmployees);

  // Fetch absence types
  const { data: absenceTypes, isLoading: isLoadingTypes } = useAbsenceTypes(true);
  const { mutate: updateAbsenceType } = useUpdateAbsenceType();

  // Fetch calendar settings (for holiday & school vacation colors)
  const { data: calendarSettings } = useCalendarSettings();
  const { mutate: updateCalendarSettings } = useUpdateCalendarSettings();

  const showHolidays = useCalendarFilterStore((state) => state.showHolidays);
  const showSchoolVacations = useCalendarFilterStore((state) => state.showSchoolVacations);
  const selectedAbsenceTypeIds = useCalendarFilterStore((state) => state.selectedAbsenceTypeIds);

  const toggleHolidays = useCalendarFilterStore((state) => state.toggleHolidays);
  const toggleSchoolVacations = useCalendarFilterStore((state) => state.toggleSchoolVacations);
  const toggleAbsenceType = useCalendarFilterStore((state) => state.toggleAbsenceType);
  const selectAllAbsenceTypes = useCalendarFilterStore((state) => state.selectAllAbsenceTypes);

  // Local state for collapsible sections
  const [employeesExpanded, setEmployeesExpanded] = useState(true);
  const [calendarsExpanded, setCalendarsExpanded] = useState(true);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Color picker state for Employees
  const [colorPickerOpen, setColorPickerOpen] = useState<number | null>(null);
  const [pendingColor, setPendingColor] = useState<string>('');

  // Color picker state for Categories (Holidays, School Vacations, Absence Types)
  const [categoryColorPickerOpen, setCategoryColorPickerOpen] = useState<string | null>(null);
  const [pendingCategoryColor, setPendingCategoryColor] = useState<string>('');

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
    setCategoryColorPickerOpen(null);
    setPendingColor(currentColor);
  };

  // Handle color picker open for categories
  const handleCategoryColorPickerClick = (categoryId: string, currentColor: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setCategoryColorPickerOpen(categoryId);
    setColorPickerOpen(null);
    setPendingCategoryColor(currentColor);
  };

  // Save color for calendar categories
  const handleCategoryColorSave = (categoryId: string) => {
    if (categoryId === 'holiday' || categoryId === 'school_vacation') {
      const updatePayload = categoryId === 'holiday'
        ? { holiday_color: pendingCategoryColor }
        : { school_vacation_color: pendingCategoryColor };
      updateCalendarSettings(updatePayload, {
        onSuccess: () => {
          setCategoryColorPickerOpen(null);
          queryClient.invalidateQueries({ queryKey: ['calendar-settings'] });
        }
      });
    } else if (categoryId.startsWith('absence_type_')) {
      const typeId = parseInt(categoryId.replace('absence_type_', ''), 10);
      updateAbsenceType({ id: typeId, data: { color: pendingCategoryColor } }, {
        onSuccess: () => {
          setCategoryColorPickerOpen(null);
          queryClient.invalidateQueries({ queryKey: ['absence-types'] });
        }
      });
    }
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
                  <div className="space-y-1">
                    <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                      <Checkbox
                        checked={showHolidays}
                        onCheckedChange={toggleHolidays}
                        className="shrink-0"
                      />
                      <button
                        type="button"
                        onClick={(e) => handleCategoryColorPickerClick('holiday', calendarSettings?.holiday_color || '#EF4444', e)}
                        className="h-3 w-3 rounded-full shrink-0 hover:ring-2 hover:ring-offset-1 hover:ring-primary transition-all"
                        style={{ backgroundColor: calendarSettings?.holiday_color || '#EF4444' }}
                        title="Farbe ändern"
                      />
                      <span className="text-sm truncate flex-1 group-hover:text-foreground">
                        Feiertage
                      </span>
                      <Palette
                        className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground"
                      />
                    </label>

                    {/* Inline Color Picker für Feiertage */}
                    {categoryColorPickerOpen === 'holiday' && (
                      <div className="px-2 py-2 bg-accent/50 rounded-md space-y-2">
                        <div className="flex items-center gap-2">
                          <input
                            type="color"
                            value={pendingCategoryColor}
                            onChange={(e) => setPendingCategoryColor(e.target.value)}
                            className="h-8 w-full cursor-pointer rounded border border-input"
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleCategoryColorSave('holiday')}
                            className="flex-1 h-7 text-xs"
                          >
                            Speichern
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setCategoryColorPickerOpen(null)}
                            className="flex-1 h-7 text-xs"
                          >
                            Abbrechen
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Schulferien */}
                  <div className="space-y-1">
                    <label className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent cursor-pointer group">
                      <Checkbox
                        checked={showSchoolVacations}
                        onCheckedChange={toggleSchoolVacations}
                        className="shrink-0"
                      />
                      <button
                        type="button"
                        onClick={(e) => handleCategoryColorPickerClick('school_vacation', calendarSettings?.school_vacation_color || '#3B82F6', e)}
                        className="h-3 w-3 rounded-full shrink-0 hover:ring-2 hover:ring-offset-1 hover:ring-primary transition-all"
                        style={{ backgroundColor: calendarSettings?.school_vacation_color || '#3B82F6' }}
                        title="Farbe ändern"
                      />
                      <span className="text-sm truncate flex-1 group-hover:text-foreground">
                        Schulferien
                      </span>
                      <Palette
                        className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground"
                      />
                    </label>

                    {/* Inline Color Picker für Schulferien */}
                    {categoryColorPickerOpen === 'school_vacation' && (
                      <div className="px-2 py-2 bg-accent/50 rounded-md space-y-2">
                        <div className="flex items-center gap-2">
                          <input
                            type="color"
                            value={pendingCategoryColor}
                            onChange={(e) => setPendingCategoryColor(e.target.value)}
                            className="h-8 w-full cursor-pointer rounded border border-input"
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleCategoryColorSave('school_vacation')}
                            className="flex-1 h-7 text-xs"
                          >
                            Speichern
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setCategoryColorPickerOpen(null)}
                            className="flex-1 h-7 text-xs"
                          >
                            Abbrechen
                          </Button>
                        </div>
                      </div>
                    )}
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
                        <button
                          type="button"
                          onClick={(e) => handleCategoryColorPickerClick(`absence_type_${type.id}`, type.color || '#3B82F6', e)}
                          className="h-3 w-3 rounded-full shrink-0 hover:ring-2 hover:ring-offset-1 hover:ring-primary transition-all"
                          style={{ backgroundColor: type.color || '#3B82F6' }}
                          title="Farbe ändern"
                        />
                        <span className="text-sm truncate flex-1 group-hover:text-foreground">
                          {type.name}
                        </span>
                        <Palette
                          className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground"
                        />
                      </label>

                      {/* Inline Color Picker für Absence Types */}
                      {categoryColorPickerOpen === `absence_type_${type.id}` && (
                        <div className="px-2 py-2 bg-accent/50 rounded-md space-y-2">
                          <div className="flex items-center gap-2">
                            <input
                              type="color"
                              value={pendingCategoryColor}
                              onChange={(e) => setPendingCategoryColor(e.target.value)}
                              className="h-8 w-full cursor-pointer rounded border border-input"
                            />
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleCategoryColorSave(`absence_type_${type.id}`)}
                              className="flex-1 h-7 text-xs"
                            >
                              Speichern
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setCategoryColorPickerOpen(null)}
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
            </CollapsibleContent>
          </Collapsible>
        </div>
      </ScrollArea>
    </div>
  );
}
