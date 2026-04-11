import React from 'react';
import { AvatarEditorProps } from '../types/avatar';
import { Employee } from '../types/employee';
import AvatarUpload from './AvatarUpload';

const AvatarEditor: React.FC<AvatarEditorProps> = ({
  employee,
  onAvatarChange,
  size = 'large',
  className = ''
}) => {
  const handleAvatarUpdate = (updatedEmployee: Employee) => {
    onAvatarChange?.(updatedEmployee.avatar_url || null);
  };

  const handleUploadError = (error: string) => {
    console.error('Avatar upload error:', error);
    // Hier könnte man zusätzliche Error-Handling-Logik hinzufügen
  };

  return (
    <div className={`avatar-editor ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Profilbild
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Laden Sie ein Profilbild für {employee.first_name} {employee.last_name} hoch.
        </p>
      </div>

      <AvatarUpload
        employee={employee}
        onAvatarUpdate={handleAvatarUpdate}
        onError={handleUploadError}
        size={size}
      />
    </div>
  );
};

export default AvatarEditor;
