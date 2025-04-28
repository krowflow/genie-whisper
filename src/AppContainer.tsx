// Genie Whisper - Main App Container
// Provides the main application structure with header and content area

import React from 'react';
import DraggableHeader from './components/DraggableHeader';
import GenieHome from './pages/GenieHome';

/**
 * AppContainer Component
 * 
 * The main container for the Genie Whisper application.
 * Includes the draggable header and main content area.
 */
const AppContainer: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-indigo-950">
      {/* Draggable title bar */}
      <DraggableHeader />
      
      {/* Main content area */}
      <div className="flex-grow">
        <GenieHome />
      </div>
    </div>
  );
};

export default AppContainer;
