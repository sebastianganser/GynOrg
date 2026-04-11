import React, { useState, useMemo } from 'react';
import { useEmployees } from '../hooks/useEmployees';
import { Employee, getEmployeeFullName, getEmployeeDisplayName } from '../types/employee';
import { Button } from './ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Edit, Trash2, Plus, User, Search, X, ChevronUp, ChevronDown, ChevronsUpDown, Filter, Mail, MapPin, Palmtree } from 'lucide-react';
import { DeleteEmployeeDialog } from './DeleteEmployeeDialog';
import Avatar from './Avatar';

interface EmployeeListProps {
  onEditEmployee?: (employee: Employee) => void;
  onManageVacation?: (employee: Employee) => void;
  onCreateEmployee?: () => void;
}

const EmployeeList: React.FC<EmployeeListProps> = ({
  onEditEmployee,
  onManageVacation,
  onCreateEmployee
}) => {
  const { data: employees, isLoading, error } = useEmployees();
  const [employeeToDelete, setEmployeeToDelete] = useState<Employee | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('active');
  const [sortField, setSortField] = useState<keyof Employee | 'fullName' | null>('fullName');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleDeleteClick = (employee: Employee) => {
    setEmployeeToDelete(employee);
  };

  const handleDeleteClose = () => {
    setEmployeeToDelete(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('de-DE');
  };

  // Filter and sort employees
  const filteredAndSortedEmployees = useMemo(() => {
    if (!employees) return [];

    let filtered = employees;

    // Apply status filter
    if (statusFilter === 'active') {
      filtered = filtered.filter(employee => employee.active);
    } else if (statusFilter === 'inactive') {
      filtered = filtered.filter(employee => !employee.active);
    }


    // Apply search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(employee => {
        const fullName = getEmployeeFullName(employee).toLowerCase();
        const email = employee.email.toLowerCase();
        const position = (employee.position || '').toLowerCase();

        return fullName.includes(term) ||
          email.includes(term) ||
          position.includes(term) ||
          employee.first_name.toLowerCase().includes(term) ||
          employee.last_name.toLowerCase().includes(term);
      });
    }

    // Apply sorting
    if (sortField) {
      filtered = [...filtered].sort((a, b) => {
        let aValue: any;
        let bValue: any;

        // Handle special sorting fields
        if (sortField === 'fullName') {
          // For name sorting, prioritize active employees first, then sort by name
          if (a.active !== b.active) {
            return a.active ? -1 : 1; // Active employees first
          }
          aValue = getEmployeeDisplayName(a).toLowerCase();
          bValue = getEmployeeDisplayName(b).toLowerCase();
        } else if (sortField === 'date_hired') {
          aValue = a.date_hired ? new Date(a.date_hired).getTime() : 0;
          bValue = b.date_hired ? new Date(b.date_hired).getTime() : 0;
        } else if (sortField === 'birth_date') {
          aValue = a.birth_date ? new Date(a.birth_date).getTime() : 0;
          bValue = b.birth_date ? new Date(b.birth_date).getTime() : 0;
        } else if (sortField === 'active') {
          aValue = a.active ? 1 : 0;
          bValue = b.active ? 1 : 0;
        } else if (sortField === 'federal_state') {
          aValue = a.federal_state;
          bValue = b.federal_state;
        } else {
          // Handle regular Employee fields
          aValue = a[sortField as keyof Employee];
          bValue = b[sortField as keyof Employee];
        }

        // Convert to string for comparison if needed
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          aValue = aValue.toLowerCase();
          bValue = bValue.toLowerCase();
        }

        if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    } else {
      // Default sorting: Active first, then by last name
      filtered = [...filtered].sort((a, b) => {
        if (a.active !== b.active) {
          return a.active ? -1 : 1; // Active employees first
        }
        return getEmployeeDisplayName(a).localeCompare(getEmployeeDisplayName(b));
      });
    }

    return filtered;
  }, [employees, statusFilter, searchTerm, sortField, sortDirection]);

  const handleClearSearch = () => {
    setSearchTerm('');
  };

  const handleSort = (field: keyof Employee | 'fullName') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: keyof Employee | 'fullName') => {
    if (sortField === field) {
      // Aktive Spalte: Zeige Richtungspfeil
      return sortDirection === 'asc' ?
        <ChevronUp className="h-4 w-4 ml-1" /> :
        <ChevronDown className="h-4 w-4 ml-1" />;
    } else {
      // Inaktive Spalte: Zeige Doppelpfeil um Sortierbarkeit zu signalisieren
      return <ChevronsUpDown className="h-4 w-4 ml-1 text-gray-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Lade Mitarbeiter...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Fehler beim Laden der Mitarbeiter
            </h3>
            <div className="mt-2 text-sm text-red-700">
              {error instanceof Error ? error.message : 'Unbekannter Fehler'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!employees || employees.length === 0) {
    return (
      <div className="text-center py-12">
        <User className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Keine Mitarbeiter</h3>
        <p className="mt-1 text-sm text-gray-500">
          Beginnen Sie, indem Sie Ihren ersten Mitarbeiter hinzufügen.
        </p>
        {onCreateEmployee && (
          <div className="mt-6">
            <Button onClick={onCreateEmployee}>
              <Plus className="h-4 w-4 mr-2" />
              Mitarbeiter hinzufügen
            </Button>
          </div>
        )}
      </div>
    );
  }

  // Render the main component with filters and results
  const renderFilters = () => (
    <div className="space-y-4">
      {/* Search Field */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Nach Name, E-Mail oder Position suchen..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck="false"
          data-form-type="search"
          className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 text-gray-900 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        {searchTerm && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button
              onClick={handleClearSearch}
              className="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              aria-label="Suche löschen"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {/* Filter Row */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        {/* Status Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Status:</span>
          <div className="flex space-x-1">
            <Button
              variant={statusFilter === 'active' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter('active')}
              aria-pressed={statusFilter === 'active'}
            >
              Aktiv
            </Button>
            <Button
              variant={statusFilter === 'inactive' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter('inactive')}
              aria-pressed={statusFilter === 'inactive'}
            >
              Inaktiv
            </Button>
            <Button
              variant={statusFilter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter('all')}
              aria-pressed={statusFilter === 'all'}
            >
              Alle
            </Button>
          </div>
        </div>


        {/* Clear Filters */}
        {(searchTerm || statusFilter !== 'active') && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('active');
            }}
            aria-label="Alle Filter zurücksetzen"
          >
            <X className="h-4 w-4 mr-1" />
            Filter zurücksetzen
          </Button>
        )}
      </div>
    </div>
  );

  // Show "no results" message when search returns empty
  if (searchTerm.trim() && filteredAndSortedEmployees.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Mitarbeiter ({employees.length})
            </h3>
            <p className="text-sm text-gray-500">
              Übersicht aller Mitarbeiter in der Organisation
            </p>
          </div>
          {onCreateEmployee && (
            <Button onClick={onCreateEmployee}>
              <Plus className="h-4 w-4 mr-2" />
              Hinzufügen
            </Button>
          )}
        </div>

        {/* Reuse the same filters */}
        {renderFilters()}

        <div className="text-center py-12">
          <Search className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Keine Ergebnisse</h3>
          <p className="mt-1 text-sm text-gray-500">
            Keine Mitarbeiter gefunden für "{searchTerm}". Versuchen Sie einen anderen Suchbegriff.
          </p>
          <div className="mt-6">
            <Button variant="outline" onClick={handleClearSearch}>
              Suche zurücksetzen
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            Mitarbeiter ({searchTerm ? `${filteredAndSortedEmployees.length} von ${employees.length}` : employees.length})
          </h3>
          <p className="text-sm text-gray-500">
            {searchTerm ? `Gefilterte Ergebnisse für "${searchTerm}"` : 'Übersicht aller Mitarbeiter in der Organisation'}
          </p>
        </div>
        {onCreateEmployee && (
          <Button onClick={onCreateEmployee}>
            <Plus className="h-4 w-4 mr-2" />
            Hinzufügen
          </Button>
        )}
      </div>

      {/* Reuse the same filters */}
      {renderFilters()}

      {/* Desktop Table View */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-1/4">
                <button
                  className="flex items-center hover:text-gray-900 font-medium focus:outline-none focus:text-gray-900"
                  onClick={() => handleSort('fullName')}
                  aria-label="Nach Name sortieren"
                >
                  Name
                  {getSortIcon('fullName')}
                </button>
              </TableHead>
              <TableHead className="w-1/5">
                <button
                  className="flex items-center hover:text-gray-900 font-medium focus:outline-none focus:text-gray-900"
                  onClick={() => handleSort('email')}
                  aria-label="Nach E-Mail sortieren"
                >
                  E-Mail
                  {getSortIcon('email')}
                </button>
              </TableHead>
              <TableHead className="w-1/6">
                <button
                  className="flex items-center hover:text-gray-900 font-medium focus:outline-none focus:text-gray-900"
                  onClick={() => handleSort('position')}
                  aria-label="Nach Position sortieren"
                >
                  Position
                  {getSortIcon('position')}
                </button>
              </TableHead>
              <TableHead className="w-1/6">
                <button
                  className="flex items-center hover:text-gray-900 font-medium focus:outline-none focus:text-gray-900"
                  onClick={() => handleSort('federal_state')}
                  aria-label="Nach Bundesland sortieren"
                >
                  Bundesland
                  {getSortIcon('federal_state')}
                </button>
              </TableHead>
              <TableHead className="w-1/8">
                <button
                  className="flex items-center hover:text-gray-900 font-medium focus:outline-none focus:text-gray-900"
                  onClick={() => handleSort('date_hired')}
                  aria-label="Nach Einstellungsdatum sortieren"
                >
                  Eingestellt
                  {getSortIcon('date_hired')}
                </button>
              </TableHead>
              <TableHead className="w-1/12">
                <button
                  className="flex items-center hover:text-gray-900 font-medium focus:outline-none focus:text-gray-900"
                  onClick={() => handleSort('active')}
                  aria-label="Nach Status sortieren"
                >
                  Status
                  {getSortIcon('active')}
                </button>
              </TableHead>
              <TableHead className="text-right w-1/12">Aktionen</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedEmployees.map((employee: Employee) => (
              <TableRow
                key={employee.id}
                className="hover:bg-gray-50"
              >
                <TableCell>
                  <div className="flex items-center">
                    <Avatar
                      employee={employee}
                      size="small"
                      className="mr-3 flex-shrink-0"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-gray-900 truncate">{getEmployeeFullName(employee)}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center min-w-0">
                    <Mail className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                    <a
                      href={`mailto:${employee.email}`}
                      className="text-blue-600 hover:text-blue-800 truncate"
                    >
                      {employee.email}
                    </a>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="truncate block">
                    {employee.position || (
                      <span className="text-gray-400 italic">Keine Position</span>
                    )}
                  </span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center min-w-0">
                    <MapPin className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                    <span className="truncate">{employee.federal_state}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-sm">
                    {employee.date_hired ? formatDate(employee.date_hired) : (
                      <span className="text-gray-400 italic">Unbekannt</span>
                    )}
                  </span>
                </TableCell>
                <TableCell>
                  {employee.active ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Aktiv
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Inaktiv
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end space-x-2">
                    {onEditEmployee && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          onEditEmployee(employee);
                        }}
                        aria-label={`${getEmployeeFullName(employee)} bearbeiten`}
                        title="Stammdaten bearbeiten"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    )}
                    {onManageVacation && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          onManageVacation(employee);
                        }}
                        aria-label={`${getEmployeeFullName(employee)} Urlaubsanspruch bearbeiten`}
                        title="Urlaubsanspruch bearbeiten"
                      >
                        <Palmtree className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        handleDeleteClick(employee);
                      }}
                      aria-label={`${getEmployeeFullName(employee)} löschen`}
                      title="Mitarbeiter deaktivieren/löschen"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>


      <DeleteEmployeeDialog
        employee={employeeToDelete}
        isOpen={!!employeeToDelete}
        onClose={handleDeleteClose}
      />
    </div>
  );
};

export default EmployeeList;
