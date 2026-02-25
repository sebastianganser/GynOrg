import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  EmployeeWithVacation, 
  EmployeeUpdateForm, 
  VacationAllowance,
  VacationAllowanceForm,
  FederalState,
  getFederalStateChoices,
  getEmployeeFullName 
} from '../types/employee';
import { employeeService } from '../services/employeeService';
import { vacationService } from '../services/vacationService';
import { Button } from './ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { 
  ArrowLeft, 
  Edit, 
  Save, 
  X, 
  Plus, 
  Trash2, 
  User, 
  Mail, 
  MapPin, 
  Calendar,
  Briefcase,
  Award,
  ChevronRight,
  Home
} from 'lucide-react';

interface EmployeeDetailProps {
  employeeId?: number;
}

const EmployeeDetail: React.FC<EmployeeDetailProps> = ({ employeeId: propEmployeeId }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const employeeId = propEmployeeId || (id ? parseInt(id, 10) : null);

  // State
  const [employee, setEmployee] = useState<EmployeeWithVacation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditingEmployee, setIsEditingEmployee] = useState(false);
  const [isEditingVacation, setIsEditingVacation] = useState<number | null>(null);
  const [isAddingVacation, setIsAddingVacation] = useState(false);
  const [activeTab, setActiveTab] = useState<'employee' | 'vacation'>('employee');

  // Form states
  const [employeeForm, setEmployeeForm] = useState<EmployeeUpdateForm>({});
  const [vacationForm, setVacationForm] = useState<VacationAllowanceForm>({
    year: new Date().getFullYear(),
    annual_allowance: 30,
    carryover_days: 0
  });
  const [editingVacationForm, setEditingVacationForm] = useState<Partial<VacationAllowanceForm>>({});

  // Toast notification function (simple implementation)
  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    // Simple alert for now - can be replaced with proper toast library later
    if (type === 'success') {
      alert(`✅ ${message}`);
    } else {
      alert(`❌ ${message}`);
    }
  };

  // Load employee data
  useEffect(() => {
    if (!employeeId) {
      setError('Keine Mitarbeiter-ID angegeben');
      setIsLoading(false);
      return;
    }

    loadEmployee();
  }, [employeeId]);

  const loadEmployee = async () => {
    if (!employeeId) return;

    try {
      setIsLoading(true);
      setError(null);
      const data = await employeeService.getEmployee(employeeId, true) as EmployeeWithVacation;
      setEmployee(data);
      
      // Initialize employee form with current data
      setEmployeeForm({
        title: data.title || '',
        first_name: data.first_name,
        last_name: data.last_name,
        position: data.position || '',
        email: data.email,
        birth_date: data.birth_date || '',
        date_hired: data.date_hired || '',
        federal_state: data.federal_state,
        active: data.active
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Laden der Mitarbeiterdaten');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmployeeUpdate = async () => {
    if (!employee || !employeeId) return;

    try {
      const updatedEmployee = await employeeService.updateEmployee(employeeId, employeeForm);
      setEmployee({ ...employee, ...updatedEmployee });
      setIsEditingEmployee(false);
      showToast('Mitarbeiterdaten erfolgreich aktualisiert');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Fehler beim Aktualisieren der Mitarbeiterdaten', 'error');
    }
  };

  const handleVacationCreate = async () => {
    if (!employeeId) return;

    try {
      const newVacation = await vacationService.createVacationAllowance(employeeId, vacationForm);
      setEmployee(prev => prev ? {
        ...prev,
        vacation_allowances: [...prev.vacation_allowances, newVacation].sort((a, b) => b.year - a.year)
      } : null);
      setIsAddingVacation(false);
      setVacationForm({
        year: new Date().getFullYear() + 1,
        annual_allowance: 30,
        carryover_days: 0
      });
      showToast('Urlaubsanspruch erfolgreich hinzugefügt');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Fehler beim Hinzufügen des Urlaubsanspruchs', 'error');
    }
  };

  const handleVacationUpdate = async (vacationId: number) => {
    try {
      const updatedVacation = await vacationService.updateVacationAllowance(vacationId, editingVacationForm);
      setEmployee(prev => prev ? {
        ...prev,
        vacation_allowances: prev.vacation_allowances.map(v => 
          v.id === vacationId ? updatedVacation : v
        )
      } : null);
      setIsEditingVacation(null);
      setEditingVacationForm({});
      showToast('Urlaubsanspruch erfolgreich aktualisiert');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Fehler beim Aktualisieren des Urlaubsanspruchs', 'error');
    }
  };

  const handleVacationDelete = async (vacationId: number, year: number) => {
    if (!confirm(`Möchten Sie den Urlaubsanspruch für ${year} wirklich löschen?`)) {
      return;
    }

    try {
      await vacationService.deleteVacationAllowance(vacationId);
      setEmployee(prev => prev ? {
        ...prev,
        vacation_allowances: prev.vacation_allowances.filter(v => v.id !== vacationId)
      } : null);
      showToast('Urlaubsanspruch erfolgreich gelöscht');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Fehler beim Löschen des Urlaubsanspruchs', 'error');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('de-DE');
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('de-DE');
  };

  const startEditingVacation = (vacation: VacationAllowance) => {
    setIsEditingVacation(vacation.id);
    setEditingVacationForm({
      annual_allowance: vacation.annual_allowance,
      carryover_days: vacation.carryover_days
    });
  };

  const cancelEditingVacation = () => {
    setIsEditingVacation(null);
    setEditingVacationForm({});
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Lade Mitarbeiterdaten...</span>
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
              Fehler beim Laden der Mitarbeiterdaten
            </h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <div className="mt-4">
              <Button variant="outline" onClick={() => navigate('/employees')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Zurück zur Liste
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="text-center py-12">
        <User className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Mitarbeiter nicht gefunden</h3>
        <p className="mt-1 text-sm text-gray-500">
          Der angeforderte Mitarbeiter konnte nicht gefunden werden.
        </p>
        <div className="mt-6">
          <Button onClick={() => navigate('/employees')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück zur Liste
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center space-x-2 text-sm text-gray-500">
        <button
          onClick={() => navigate('/employees')}
          className="hover:text-gray-700 flex items-center"
        >
          <Home className="h-4 w-4 mr-1" />
          Mitarbeiter
        </button>
        <ChevronRight className="h-4 w-4" />
        <span className="text-gray-900 font-medium">{getEmployeeFullName(employee)}</span>
      </nav>

      {/* Header */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="h-16 w-16 rounded-full bg-blue-500 flex items-center justify-center mr-4">
              <span className="text-xl font-medium text-white">
                {employee.first_name[0]}{employee.last_name[0]}
              </span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{getEmployeeFullName(employee)}</h1>
              <p className="text-gray-600">{employee.position || 'Keine Position angegeben'}</p>
              <div className="flex items-center mt-1">
                {employee.active ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Aktiv
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Inaktiv
                  </span>
                )}
              </div>
            </div>
          </div>
          <Button variant="outline" onClick={() => navigate('/employees')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück zur Liste
          </Button>
        </div>
      </div>

      {/* Mobile Tab Navigation */}
      <div className="lg:hidden">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('employee')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'employee'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <User className="h-4 w-4 mr-2 inline" />
              Stammdaten
            </button>
            <button
              onClick={() => setActiveTab('vacation')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'vacation'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Award className="h-4 w-4 mr-2 inline" />
              Urlaubsdaten
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Employee Data Section */}
        <div className={`${activeTab === 'vacation' ? 'hidden lg:block' : ''}`}>
          <div className="bg-white rounded-lg border">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900 flex items-center">
                  <User className="h-5 w-5 mr-2" />
                  Stammdaten
                </h2>
                {!isEditingEmployee ? (
                  <Button variant="outline" size="sm" onClick={() => setIsEditingEmployee(true)}>
                    <Edit className="h-4 w-4 mr-2" />
                    Bearbeiten
                  </Button>
                ) : (
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" onClick={() => setIsEditingEmployee(false)}>
                      <X className="h-4 w-4 mr-2" />
                      Abbrechen
                    </Button>
                    <Button size="sm" onClick={handleEmployeeUpdate}>
                      <Save className="h-4 w-4 mr-2" />
                      Speichern
                    </Button>
                  </div>
                )}
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              {isEditingEmployee ? (
                // Edit Form
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Titel
                      </label>
                      <input
                        type="text"
                        value={employeeForm.title || ''}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, title: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="z.B. Dr., Prof."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Status
                      </label>
                      <select
                        value={employeeForm.active ? 'true' : 'false'}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, active: e.target.value === 'true' }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="true">Aktiv</option>
                        <option value="false">Inaktiv</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Vorname *
                      </label>
                      <input
                        type="text"
                        value={employeeForm.first_name || ''}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, first_name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nachname *
                      </label>
                      <input
                        type="text"
                        value={employeeForm.last_name || ''}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, last_name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Position
                    </label>
                    <input
                      type="text"
                      value={employeeForm.position || ''}
                      onChange={(e) => setEmployeeForm(prev => ({ ...prev, position: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="z.B. Softwareentwickler, Projektmanager"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      E-Mail *
                    </label>
                    <input
                      type="email"
                      value={employeeForm.email || ''}
                      onChange={(e) => setEmployeeForm(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Bundesland *
                    </label>
                    <select
                      value={employeeForm.federal_state || ''}
                      onChange={(e) => setEmployeeForm(prev => ({ ...prev, federal_state: e.target.value as FederalState }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      required
                    >
                      <option value="">Bundesland auswählen</option>
                      {getFederalStateChoices().map((state) => (
                        <option key={state.code} value={state.code}>
                          {state.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Geburtsdatum
                      </label>
                      <input
                        type="date"
                        value={employeeForm.birth_date || ''}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, birth_date: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Einstellungsdatum
                      </label>
                      <input
                        type="date"
                        value={employeeForm.date_hired || ''}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, date_hired: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                // Display Mode
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="flex items-center">
                      <Mail className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm text-gray-500">E-Mail</div>
                        <a href={`mailto:${employee.email}`} className="text-blue-600 hover:text-blue-800">
                          {employee.email}
                        </a>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm text-gray-500">Bundesland</div>
                        <div className="font-medium">{employee.federal_state}</div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="flex items-center">
                      <Briefcase className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm text-gray-500">Position</div>
                        <div className="font-medium">{employee.position || 'Nicht angegeben'}</div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm text-gray-500">Eingestellt seit</div>
                        <div className="font-medium">
                          {employee.date_hired ? formatDate(employee.date_hired) : 'Nicht angegeben'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {employee.birth_date && (
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm text-gray-500">Geburtsdatum</div>
                        <div className="font-medium">{formatDate(employee.birth_date)}</div>
                      </div>
                    </div>
                  )}

                  <div className="pt-4 border-t border-gray-200">
                    <div className="text-xs text-gray-500">
                      Erstellt: {formatDateTime(employee.created_at)}
                      {employee.updated_at !== employee.created_at && (
                        <span className="block">Zuletzt geändert: {formatDateTime(employee.updated_at)}</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Vacation Data Section */}
        <div className={`${activeTab === 'employee' ? 'hidden lg:block' : ''}`}>
          <div className="bg-white rounded-lg border">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900 flex items-center">
                  <Award className="h-5 w-5 mr-2" />
                  Urlaubsdaten
                </h2>
                <Button variant="outline" size="sm" onClick={() => setIsAddingVacation(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Jahr hinzufügen
                </Button>
              </div>
            </div>

            <div className="p-6">
              {/* Add Vacation Form */}
              {isAddingVacation && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Neuen Urlaubsanspruch hinzufügen</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Jahr</label>
                      <input
                        type="number"
                        value={vacationForm.year}
                        onChange={(e) => setVacationForm(prev => ({ ...prev, year: parseInt(e.target.value) }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        min="2020"
                        max="2030"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Jahresanspruch</label>
                      <input
                        type="number"
                        value={vacationForm.annual_allowance}
                        onChange={(e) => setVacationForm(prev => ({ ...prev, annual_allowance: parseInt(e.target.value) }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        min="0"
                        max="50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Übertrag</label>
                      <input
                        type="number"
                        value={vacationForm.carryover_days}
                        onChange={(e) => setVacationForm(prev => ({ ...prev, carryover_days: parseInt(e.target.value) }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        min="0"
                        max="20"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end space-x-2 mt-4">
                    <Button variant="outline" size="sm" onClick={() => setIsAddingVacation(false)}>
                      Abbrechen
                    </Button>
                    <Button size="sm" onClick={handleVacationCreate}>
                      Hinzufügen
                    </Button>
                  </div>
                </div>
              )}

              {/* Vacation Table */}
              {employee.vacation_allowances && employee.vacation_allowances.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Jahr</TableHead>
                        <TableHead>Jahresanspruch</TableHead>
                        <TableHead>Übertrag</TableHead>
                        <TableHead>Gesamt</TableHead>
                        <TableHead className="text-right">Aktionen</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {employee.vacation_allowances
                        .sort((a, b) => b.year - a.year)
                        .map((vacation) => (
                          <TableRow 
                            key={vacation.id}
                            className={vacation.year === new Date().getFullYear() ? 'bg-blue-50' : ''}
                          >
                            <TableCell>
                              <div className="flex items-center">
                                <span className="font-medium">{vacation.year}</span>
                                {vacation.year === new Date().getFullYear() && (
                                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                    Aktuell
                                  </span>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>
                              {isEditingVacation === vacation.id ? (
                                <input
                                  type="number"
                                  value={editingVacationForm.annual_allowance || vacation.annual_allowance}
                                  onChange={(e) => setEditingVacationForm(prev => ({ 
                                    ...prev, 
                                    annual_allowance: parseInt(e.target.value) 
                                  }))}
                                  className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                                  min="0"
                                  max="50"
                                />
                              ) : (
                                <span className="font-medium">{vacation.annual_allowance} Tage</span>
                              )}
                            </TableCell>
                            <TableCell>
                              {isEditingVacation === vacation.id ? (
                                <input
                                  type="number"
                                  value={editingVacationForm.carryover_days || vacation.carryover_days}
                                  onChange={(e) => setEditingVacationForm(prev => ({ 
                                    ...prev, 
                                    carryover_days: parseInt(e.target.value) 
                                  }))}
                                  className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                                  min="0"
                                  max="20"
                                />
                              ) : (
                                <span>{vacation.carryover_days} Tage</span>
                              )}
                            </TableCell>
                            <TableCell>
                              <span className="font-semibold text-blue-600">
                                {vacation.annual_allowance + vacation.carryover_days} Tage
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex items-center justify-end space-x-2">
                                {isEditingVacation === vacation.id ? (
                                  <>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={cancelEditingVacation}
                                    >
                                      <X className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      size="sm"
                                      onClick={() => handleVacationUpdate(vacation.id)}
                                    >
                                      <Save className="h-4 w-4" />
                                    </Button>
                                  </>
                                ) : (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => startEditingVacation(vacation)}
                                      aria-label={`Urlaubsanspruch für ${vacation.year} bearbeiten`}
                                    >
                                      <Edit className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleVacationDelete(vacation.id, vacation.year)}
                                      aria-label={`Urlaubsanspruch für ${vacation.year} löschen`}
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Award className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Keine Urlaubsdaten</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Fügen Sie den ersten Urlaubsanspruch für diesen Mitarbeiter hinzu.
                  </p>
                  <div className="mt-6">
                    <Button onClick={() => setIsAddingVacation(true)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Urlaubsanspruch hinzufügen
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDetail;
