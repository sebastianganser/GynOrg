import React from 'react';
import { ChevronLeft, ChevronRight, Users, Calendar, Settings, LogOut, Activity, Receipt } from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  onLogout: () => void;
  isCollapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  currentPage, 
  onPageChange, 
  onLogout, 
  isCollapsed, 
  onToggle 
}) => {

  const menuItems = [
    { id: 'employees', label: 'Mitarbeiter', icon: Users },
    { id: 'absences', label: 'Abwesenheiten', icon: Calendar },
    { id: 'auslastung', label: 'Belegungsstatistik', icon: Activity },
    { id: 'rechnungen', label: 'Privatrechnungen', icon: Receipt },
    { id: 'settings', label: 'Einstellungen', icon: Settings },
  ];

  return (
    <div className={`bg-gray-900 text-white transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'} min-h-screen flex flex-col`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        {!isCollapsed && (
          <h1 className="text-xl font-bold text-blue-400">GynOrg</h1>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded hover:bg-gray-700 transition-colors"
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onPageChange(item.id)}
                  className={`w-full flex items-center p-3 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon size={20} />
                  {!isCollapsed && (
                    <span className="ml-3">{item.label}</span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={onLogout}
          className="w-full flex items-center p-3 rounded-lg text-gray-300 hover:bg-red-600 hover:text-white transition-colors"
          title={isCollapsed ? 'Abmelden' : undefined}
        >
          <LogOut size={20} />
          {!isCollapsed && (
            <span className="ml-3">Abmelden</span>
          )}
        </button>
      </div>
    </div>
  );
};
