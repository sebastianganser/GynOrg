import React from 'react';
import { Employee } from '../types/employee';
import { AvatarSize } from '../types/avatar';

interface AvatarProps {
  employee: Employee;
  size?: AvatarSize;
  onClick?: () => void;
  editable?: boolean;
  className?: string;
}

const sizeClasses: Record<AvatarSize, string> = {
  small: 'w-8 h-8 text-xs',
  medium: 'w-10 h-10 text-sm',
  large: 'w-15 h-15 text-base',
  xlarge: 'w-20 h-20 text-lg'
};

const getInitials = (employee: Employee): string => {
  // Wenn initials im Employee-Objekt vorhanden sind, verwende diese
  if (employee.initials) {
    return employee.initials.toUpperCase();
  }
  
  // Ansonsten generiere aus Vor- und Nachname
  const firstInitial = employee.first_name?.charAt(0) || '';
  const lastInitial = employee.last_name?.charAt(0) || '';
  return (firstInitial + lastInitial).toUpperCase();
};

const getAvatarColor = (initials: string): string => {
  const colors = [
    'bg-blue-500',
    'bg-green-500', 
    'bg-purple-500',
    'bg-orange-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-red-500',
    'bg-yellow-500',
    'bg-teal-500',
    'bg-cyan-500'
  ];
  
  const hash = initials.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

export const Avatar: React.FC<AvatarProps> = ({
  employee,
  size = 'medium',
  onClick,
  editable = false,
  className = ''
}) => {
  const initials = getInitials(employee);
  const colorClass = getAvatarColor(initials);
  const sizeClass = sizeClasses[size];
  
  const baseClasses = `
    relative inline-flex items-center justify-center
    rounded-full font-medium text-white
    ${sizeClass}
    ${onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
    ${className}
  `;

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  return (
    <div 
      className={baseClasses}
      onClick={handleClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {employee.avatar_url ? (
        <>
          <img
            src={employee.avatar_url}
            alt={`Avatar von ${employee.first_name} ${employee.last_name}`}
            className="w-full h-full rounded-full object-cover"
            onError={(e) => {
              // Fallback zu Initialen wenn Bild nicht geladen werden kann
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
            }}
          />
          <div className={`absolute inset-0 flex items-center justify-center rounded-full ${colorClass}`}>
            <span className="font-medium">{initials}</span>
          </div>
        </>
      ) : (
        <div className={`w-full h-full flex items-center justify-center rounded-full ${colorClass}`}>
          <span className="font-medium">{initials}</span>
        </div>
      )}
      
      {editable && (
        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-gray-600 rounded-full flex items-center justify-center">
          <svg 
            className="w-2.5 h-2.5 text-white" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" 
            />
          </svg>
        </div>
      )}
    </div>
  );
};

export default Avatar;
