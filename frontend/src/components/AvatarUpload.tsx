import React, { useState, useRef, useCallback } from 'react';
import ReactCrop, { Crop, PercentCrop } from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { Employee } from '../types/employee';
import { avatarService, CropData, UploadProgress } from '../services/avatarService';
import { AvatarSize } from '../types/avatar';
import Avatar from './Avatar';

interface AvatarUploadProps {
  employee: Employee;
  onAvatarUpdate: (updatedEmployee: Employee) => void;
  onError?: (error: string) => void;
  size?: AvatarSize;
  className?: string;
}

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  success: boolean;
}

const AvatarUpload: React.FC<AvatarUploadProps> = ({
  employee,
  onAvatarUpdate,
  onError,
  size = 'large',
  className = ''
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [crop, setCrop] = useState<Crop>({
    unit: '%',
    width: 50,
    height: 50,
    x: 25,
    y: 25
  });
  const [completedCrop, setCompletedCrop] = useState<PercentCrop | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    success: false
  });
  const [isInitialsModalOpen, setIsInitialsModalOpen] = useState(false);
  const [customInitials, setCustomInitials] = useState(employee.initials || '');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleAvatarClick = () => {
    setIsModalOpen(true);
  };

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      // Validierung
      const maxSize = 5 * 1024 * 1024; // 5MB
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

      if (file.size > maxSize) {
        throw new Error('Datei ist zu groß. Maximum: 5MB');
      }

      if (!allowedTypes.includes(file.type)) {
        throw new Error('Ungültiges Dateiformat. Erlaubt: JPG, PNG, WebP');
      }

      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setUploadState(prev => ({ ...prev, error: null, success: false }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unbekannter Fehler';
      setUploadState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
    }

    // Reset file input
    if (event.target) {
      event.target.value = '';
    }
  }, [onError]);

  const handleUpload = async () => {
    if (!selectedFile || !completedCrop) return;

    setUploadState(prev => ({ ...prev, isUploading: true, error: null, progress: 0 }));
    abortControllerRef.current = new AbortController();

    try {
      const cropData: CropData = {
        x: completedCrop.x,
        y: completedCrop.y,
        width: completedCrop.width,
        height: completedCrop.height
      };

      const onProgress = (progress: UploadProgress) => {
        setUploadState(prev => ({ ...prev, progress: progress.percentage }));
      };

      const updatedEmployee = await avatarService.uploadAvatar(
        employee.id,
        selectedFile,
        cropData,
        onProgress,
        abortControllerRef.current
      );

      setUploadState(prev => ({ ...prev, isUploading: false, success: true }));
      onAvatarUpdate(updatedEmployee);

      // Modal nach kurzer Verzögerung schließen
      setTimeout(() => {
        handleCloseModal();
      }, 1000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload fehlgeschlagen';
      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        error: errorMessage,
        progress: 0
      }));
      onError?.(errorMessage);
    }
  };

  const handleDeleteAvatar = async () => {
    if (!employee.avatar_url) return;

    setUploadState(prev => ({ ...prev, isUploading: true, error: null }));

    try {
      await avatarService.deleteAvatar(employee.id);

      // Manually construct the updated employee locally since the backend returns 204 No Content
      const updatedEmployee = { ...employee, avatar_url: undefined, profile_image_path: undefined };
      onAvatarUpdate(updatedEmployee);

      setUploadState(prev => ({ ...prev, isUploading: false, success: true }));

      setTimeout(() => {
        handleCloseModal();
      }, 1000);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Löschen fehlgeschlagen';
      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        error: errorMessage
      }));
      onError?.(errorMessage);
    }
  };

  const handleUpdateInitials = async () => {
    if (!customInitials.trim()) return;

    try {
      const updatedEmployee = await avatarService.updateInitials(employee.id, customInitials.trim());
      onAvatarUpdate(updatedEmployee);
      setIsInitialsModalOpen(false);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Update fehlgeschlagen';
      onError?.(errorMessage);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
    setImagePreview(null);
    setCrop({ unit: '%', width: 50, height: 50, x: 25, y: 25 });
    setCompletedCrop(null);
    setUploadState({
      isUploading: false,
      progress: 0,
      error: null,
      success: false
    });

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  const handleCancelUpload = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  return (
    <>
      <div className={className}>
        <Avatar
          employee={employee}
          size={size}
          onClick={handleAvatarClick}
          editable={true}
        />
      </div>

      {/* Avatar Upload Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Avatar bearbeiten</h3>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600"
                disabled={uploadState.isUploading}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Aktueller Avatar */}
            <div className="text-center mb-4">
              <Avatar employee={employee} size="xlarge" />
              <p className="text-sm text-gray-600 mt-2">
                {employee.first_name} {employee.last_name}
              </p>
            </div>

            {/* Aktionen */}
            <div className="space-y-3 mb-4">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadState.isUploading}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Neues Bild hochladen
              </button>

              <button
                onClick={() => setIsInitialsModalOpen(true)}
                disabled={uploadState.isUploading}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Initialen ändern
              </button>

              {employee.avatar_url && (
                <button
                  onClick={handleDeleteAvatar}
                  disabled={uploadState.isUploading}
                  className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Avatar löschen
                </button>
              )}
            </div>

            {/* Bild-Crop-Bereich */}
            {imagePreview && (
              <div className="mb-4">
                <h4 className="text-sm font-medium mb-2">Bildausschnitt wählen:</h4>
                <div className="border rounded-lg overflow-hidden">
                  <ReactCrop
                    crop={crop}
                    onChange={(_, percentCrop) => setCrop(percentCrop)}
                    onComplete={(_, percentCrop) => setCompletedCrop(percentCrop)}
                    aspect={1}
                    circularCrop
                  >
                    <img
                      ref={imageRef}
                      src={imagePreview}
                      alt="Crop preview"
                      className="max-w-full h-auto"
                      style={{ maxHeight: '300px' }}
                    />
                  </ReactCrop>
                </div>

                <div className="flex gap-2 mt-3">
                  <button
                    onClick={handleUpload}
                    disabled={uploadState.isUploading || !completedCrop}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploadState.isUploading ? 'Uploading...' : 'Speichern'}
                  </button>

                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setImagePreview(null);
                    }}
                    disabled={uploadState.isUploading}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Abbrechen
                  </button>
                </div>
              </div>
            )}

            {/* Upload Progress */}
            {uploadState.isUploading && (
              <div className="mb-4">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">Upload läuft...</span>
                  <span className="text-sm text-gray-600">{uploadState.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadState.progress}%` }}
                  ></div>
                </div>
                <button
                  onClick={handleCancelUpload}
                  className="mt-2 text-sm text-red-600 hover:text-red-800"
                >
                  Abbrechen
                </button>
              </div>
            )}

            {/* Status Messages */}
            {uploadState.error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {uploadState.error}
              </div>
            )}

            {uploadState.success && (
              <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                Avatar erfolgreich aktualisiert!
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </div>
      )}

      {/* Initialen Modal */}
      {isInitialsModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Initialen ändern</h3>
              <button
                onClick={() => setIsInitialsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Benutzerdefinierte Initialen (max. 3 Zeichen)
              </label>
              <input
                type="text"
                value={customInitials}
                onChange={(e) => setCustomInitials(e.target.value.slice(0, 3))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="z.B. MK"
                maxLength={3}
              />
              <p className="text-xs text-gray-500 mt-1">
                Leer lassen für automatische Generierung aus Vor- und Nachname
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleUpdateInitials}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Speichern
              </button>
              <button
                onClick={() => setIsInitialsModalOpen(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Abbrechen
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AvatarUpload;
