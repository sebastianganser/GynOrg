import React, { useState } from 'react';
import { FileText, UserCheck } from 'lucide-react';
import RechnungenTab from './RechnungenTab';
import Patienten from './Patienten';

interface RechnungenProps {
  onNavigateToWizard: () => void;
  onEditRechnung?: (id: number) => void;
}

/**
 * Hauptseite "Privatrechnungen" mit zwei Karteikarten:
 * - Rechnungen
 * - Patientenverwaltung
 */
const Rechnungen: React.FC<RechnungenProps> = ({ onNavigateToWizard, onEditRechnung }) => {
  const [activeTab, setActiveTab] = useState<'rechnungen' | 'patienten'>('rechnungen');

  const tabs = [
    { id: 'rechnungen' as const, label: 'Rechnungen', icon: FileText },
    { id: 'patienten' as const, label: 'Patientenverwaltung', icon: UserCheck },
  ];

  return (
    <div>
      {/* Tab-Navigation */}
      <div className="bg-white border-b border-gray-200 px-6 pt-4">
        <div className="flex space-x-6">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 pb-3 px-1 border-b-2 transition-colors text-sm font-medium ${
                  isActive
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                id={`tab-${tab.id}`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab-Inhalt */}
      {activeTab === 'rechnungen' && (
        <RechnungenTab onNavigateToWizard={onNavigateToWizard} onEditRechnung={onEditRechnung} />
      )}
      {activeTab === 'patienten' && (
        <Patienten />
      )}
    </div>
  );
};

export default Rechnungen;
