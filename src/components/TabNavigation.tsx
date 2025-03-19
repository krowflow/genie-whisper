import React from 'react';

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="tab-navigation flex border-b border-indigo-700 mb-4">
      <button 
        className={`px-4 py-2 ${activeTab === 'main' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400 hover:text-white'}`}
        onClick={() => onTabChange('main')}
      >
        Main
      </button>
      <button 
        className={`px-4 py-2 ${activeTab === 'settings' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400 hover:text-white'}`}
        onClick={() => onTabChange('settings')}
      >
        Settings
      </button>
      <button 
        className={`px-4 py-2 ${activeTab === 'devices' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400 hover:text-white'}`}
        onClick={() => onTabChange('devices')}
      >
        Devices
      </button>
      <button 
        className={`px-4 py-2 ${activeTab === 'help' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400 hover:text-white'}`}
        onClick={() => onTabChange('help')}
      >
        Help
      </button>
    </div>
  );
};

export default TabNavigation;