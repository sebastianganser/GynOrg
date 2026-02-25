import React from 'react';
import { User } from 'lucide-react';

interface HeaderProps {
  title: string;
  username: string;
}

export const Header: React.FC<HeaderProps> = ({ title, username }) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">{title}</h2>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-gray-600">
            <User size={20} />
            <span className="text-sm font-medium">{username}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
