import React, { useState } from 'react';
import { 
  AvatarDisplayProps, 
  getAvatarInitials, 
  getAvatarSizeClasses,
  AvatarSize 
} from '../types/avatar';

const AvatarDisplay: React.FC<AvatarDisplayProps> = ({
  employee,
  size = 'medium',
  className = '',
  showFallback = true
}) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const avatarUrl = employee.avatar_url;
  const initials = getAvatarInitials(employee.first_name, employee.last_name);
  const sizeClasses = getAvatarSizeClasses(size);
  
  const handleImageError = () => {
    setImageError(true);
    setIsLoading(false);
  };

  const handleImageLoad = () => {
    setIsLoading(false);
    setImageError(false);
  };

  const handleImageLoadStart = () => {
    setIsLoading(true);
  };

  // Wenn kein Avatar vorhanden ist oder Fehler beim Laden
  if (!avatarUrl || imageError) {
    if (!showFallback) {
      return null;
    }

    return (
      <div 
        className={`
          ${sizeClasses} 
          bg-blue-500 text-white 
          rounded-full 
          flex items-center justify-center 
          font-semibold 
          select-none
          ${className}
        `}
        title={`${employee.first_name} ${employee.last_name}`}
      >
        {initials}
      </div>
    );
  }

  return (
    <div className={`relative ${sizeClasses} ${className}`}>
      {/* Loading Spinner */}
      {isLoading && (
        <div 
          className={`
            absolute inset-0 
            bg-gray-200 
            rounded-full 
            flex items-center justify-center
            animate-pulse
          `}
        >
          <div className="w-1/2 h-1/2 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      {/* Avatar Image */}
      <img
        src={avatarUrl}
        alt={`${employee.first_name} ${employee.last_name}`}
        className={`
          w-full h-full 
          rounded-full 
          object-cover 
          border-2 border-gray-200
          ${isLoading ? 'opacity-0' : 'opacity-100'}
          transition-opacity duration-200
        `}
        onError={handleImageError}
        onLoad={handleImageLoad}
        onLoadStart={handleImageLoadStart}
        title={`${employee.first_name} ${employee.last_name}`}
      />
    </div>
  );
};

export default AvatarDisplay;

// Zusätzliche Utility-Komponente für einfache Verwendung
export const SimpleAvatar: React.FC<{
  employee: { first_name: string; last_name: string; avatar_url?: string };
  size?: AvatarSize;
  className?: string;
}> = ({ employee, size = 'medium', className = '' }) => {
  return (
    <AvatarDisplay
      employee={{
        id: 0, // Dummy ID für SimpleAvatar
        ...employee
      }}
      size={size}
      className={className}
      showFallback={true}
    />
  );
};
