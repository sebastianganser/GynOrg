import React, { useState } from 'react';
import { Modal } from './ui/modal';
import { Button } from './ui/button';
import { AlertTriangle, Trash2, UserX } from 'lucide-react';
import { Employee, getEmployeeFullName } from '../types/employee';
import { useDeleteEmployee, useHardDeleteEmployee } from '../hooks/useEmployees';

interface DeleteEmployeeDialogProps {
  employee: Employee | null;
  isOpen: boolean;
  onClose: () => void;
}

export const DeleteEmployeeDialog: React.FC<DeleteEmployeeDialogProps> = ({
  employee,
  isOpen,
  onClose,
}) => {
  const [deleteType, setDeleteType] = useState<'soft' | 'hard'>('soft');
  const [confirmText, setConfirmText] = useState('');
  
  const deleteEmployeeMutation = useDeleteEmployee();
  const hardDeleteEmployeeMutation = useHardDeleteEmployee();

  const handleDelete = async () => {
    if (!employee) return;

    try {
      if (deleteType === 'soft') {
        await deleteEmployeeMutation.mutateAsync(employee.id);
      } else {
        await hardDeleteEmployeeMutation.mutateAsync(employee.id);
      }
      onClose();
      setConfirmText('');
      setDeleteType('soft');
    } catch (error) {
      console.error('Fehler beim Löschen des Mitarbeiters:', error);
    }
  };

  const handleClose = () => {
    onClose();
    setConfirmText('');
    setDeleteType('soft');
  };

  const isConfirmValid = confirmText === 'LÖSCHEN';
  const isLoading = deleteEmployeeMutation.isPending || hardDeleteEmployeeMutation.isPending;

  if (!employee) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Mitarbeiter löschen"
      size="md"
      closeOnBackdropClick={false}
    >
      <div className="space-y-6">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <AlertTriangle className="h-6 w-6 text-red-500" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {getEmployeeFullName(employee)} löschen
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Wählen Sie die Art der Löschung für diesen Mitarbeiter.
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="space-y-3">
            <label className="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                name="deleteType"
                value="soft"
                checked={deleteType === 'soft'}
                onChange={(e) => {
                  e.stopPropagation();
                  setDeleteType(e.target.value as 'soft' | 'hard');
                }}
                onClick={(e) => e.stopPropagation()}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <UserX className="h-4 w-4 text-orange-500" />
                  <span className="font-medium text-gray-900">Deaktivieren (Empfohlen)</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Der Mitarbeiter wird als inaktiv markiert, aber alle Daten bleiben erhalten. 
                  Dies ist die empfohlene Option für historische Aufzeichnungen.
                </p>
              </div>
            </label>

            <label className="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                name="deleteType"
                value="hard"
                checked={deleteType === 'hard'}
                onChange={(e) => {
                  e.stopPropagation();
                  setDeleteType(e.target.value as 'soft' | 'hard');
                }}
                onClick={(e) => e.stopPropagation()}
                className="mt-1 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <Trash2 className="h-4 w-4 text-red-500" />
                  <span className="font-medium text-gray-900">Permanent löschen</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Der Mitarbeiter wird permanent aus der Datenbank entfernt. 
                  <strong className="text-red-600"> Diese Aktion kann nicht rückgängig gemacht werden!</strong>
                </p>
              </div>
            </label>
          </div>

          {deleteType === 'hard' && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-red-400 flex-shrink-0" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-red-800">
                    Bestätigung erforderlich
                  </h4>
                  <p className="mt-1 text-sm text-red-700">
                    Geben Sie <strong>LÖSCHEN</strong> ein, um die permanente Löschung zu bestätigen:
                  </p>
                  <div className="mt-3">
                    <input
                      type="text"
                      value={confirmText}
                      onChange={(e) => setConfirmText(e.target.value)}
                      placeholder="LÖSCHEN eingeben"
                      autoComplete="new-password"
                      autoCorrect="off"
                      autoCapitalize="off"
                      spellCheck="false"
                      data-form-type="other"
                      className="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-400"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Abbrechen
          </Button>
          <Button
            variant={deleteType === 'hard' ? 'destructive' : 'default'}
            onClick={handleDelete}
            disabled={isLoading || (deleteType === 'hard' && !isConfirmValid)}
            className={deleteType === 'soft' ? 'bg-orange-600 hover:bg-orange-700' : ''}
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Wird gelöscht...</span>
              </div>
            ) : (
              <>
                {deleteType === 'soft' ? (
                  <>
                    <UserX className="h-4 w-4 mr-2" />
                    Deaktivieren
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Permanent löschen
                  </>
                )}
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
