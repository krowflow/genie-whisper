import React from 'react';
import ReactDOM from 'react-dom/client';
import AppContainer from './AppContainer';
import './styles/main.css';

// Initialize the React application
document.addEventListener('DOMContentLoaded', () => {
  const rootElement = document.getElementById('root');

  if (rootElement) {
    // Create a React root and render the AppContainer component
    const root = ReactDOM.createRoot(rootElement);
    root.render(
      <React.StrictMode>
        <AppContainer />
      </React.StrictMode>
    );
  } else {
    console.error('Root element not found');
  }
});
