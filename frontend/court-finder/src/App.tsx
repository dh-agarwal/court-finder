import React, { useState } from 'react';
import Map from './Map';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

const App: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="App">
      <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        <h2>Sidebar</h2>
        <p>Additional content here</p>
      </div>
      <div className="map-container">
        <Map />
      </div>
      <button className="toggle-button" onClick={toggleSidebar}>
        <i className={`fas fa-caret-${isSidebarOpen ? 'left' : 'right'}`}></i>
      </button>
    </div>
  );
};

export default App;
