import React, { useState, ReactNode } from 'react';

export interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  badge?: string | number;
}

interface EmployeeDetailTabsProps {
  tabs: TabItem[];
  defaultActiveTab?: string;
  onTabChange?: (tabId: string) => void;
  className?: string;
}

const EmployeeDetailTabs: React.FC<EmployeeDetailTabsProps> = ({
  tabs,
  defaultActiveTab,
  onTabChange,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState(defaultActiveTab || tabs[0]?.id || '');

  const handleTabClick = (tabId: string) => {
    if (tabs.find(tab => tab.id === tabId)?.disabled) {
      return;
    }
    
    setActiveTab(tabId);
    onTabChange?.(tabId);
  };

  const activeTabContent = tabs.find(tab => tab.id === activeTab)?.content;

  return (
    <div className={`w-full ${className}`}>
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              disabled={tab.disabled}
              className={`
                group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
                ${tab.disabled
                  ? 'opacity-50 cursor-not-allowed'
                  : 'cursor-pointer'
                }
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                transition-colors duration-200
              `}
              aria-current={activeTab === tab.id ? 'page' : undefined}
              role="tab"
              aria-selected={activeTab === tab.id}
              tabIndex={activeTab === tab.id ? 0 : -1}
            >
              {/* Icon */}
              {tab.icon && (
                <span className={`
                  mr-2 h-5 w-5
                  ${activeTab === tab.id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'}
                `}>
                  {tab.icon}
                </span>
              )}
              
              {/* Label */}
              <span>{tab.label}</span>
              
              {/* Badge */}
              {tab.badge && (
                <span className={`
                  ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${activeTab === tab.id
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                  }
                `}>
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
        {activeTabContent}
      </div>
    </div>
  );
};

export default EmployeeDetailTabs;

// Hook for managing tab state
export const useEmployeeDetailTabs = (initialTab?: string) => {
  const [activeTab, setActiveTab] = useState(initialTab || '');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<Record<string, boolean>>({});

  const handleTabChange = React.useCallback((tabId: string) => {
    // Check for unsaved changes before switching
    // We access the current state via a ref or by using the functional update pattern if possible, 
    // but here we need the value. To keep the function stable, we might need a ref for hasUnsavedChanges
    // if we want to avoid re-creating this function when state changes. 
    // HOWEVER, for clearAllChanges which causes the specific bug, it has NO dependencies!
    
    // For handleTabChange, it DOES depend on hasUnsavedChanges. 
    // But EditEmployeeForm only lists clearAllChanges in dependecy array of the crashing useEffect.
    
    // Let's fallback to just fixing the infinite loop source first and foremost.
    // Actually, seeing as I can't easily change the logic without refs to make handleTabChange strictly stable 
    // without including hasUnsavedChanges in deps, I will accept that handleTabChange changes when state changes.
    // BUT clearAllChanges MUST be stable.
    
    const currentTabHasChanges = hasUnsavedChanges[activeTab];
    
    if (currentTabHasChanges) {
      const confirmSwitch = window.confirm(
        'Sie haben ungespeicherte Änderungen. Möchten Sie wirklich den Tab wechseln?'
      );
      
      if (!confirmSwitch) {
        return false;
      }
    }
    
    setActiveTab(tabId);
    return true;
  }, [activeTab, hasUnsavedChanges]);

  const markTabAsChanged = React.useCallback((tabId: string, hasChanges: boolean) => {
    setHasUnsavedChanges(prev => ({
      ...prev,
      [tabId]: hasChanges
    }));
  }, []);

  const clearAllChanges = React.useCallback(() => {
    setHasUnsavedChanges({});
  }, []);

  return {
    activeTab,
    setActiveTab,
    handleTabChange,
    hasUnsavedChanges,
    markTabAsChanged,
    clearAllChanges
  };
};

// Tab Icons as React components
export const TabIcons = {
  User: () => (
    <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
    </svg>
  ),
  
  Settings: () => (
    <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
  
  Calendar: () => (
    <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5a2.25 2.25 0 002.25-2.25m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5a2.25 2.25 0 012.25 2.25v7.5" />
    </svg>
  ),
  
  Home: () => (
    <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
    </svg>
  )
};
