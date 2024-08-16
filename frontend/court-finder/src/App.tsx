import React, { useState, useRef } from 'react';
import Map from './Map';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

const App: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [location, setLocation] = useState<string>('');
  const mapRef = useRef<{ findCourts: () => void } | null>(null); // Reference to trigger findCourts

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleFindCourts = () => {
    console.log(`Finding courts near: ${location}`);
    if (mapRef.current) {
      mapRef.current.findCourts(); // Trigger findCourts in the Map component
    }
  };

  return (
    <div className="App">
      <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        <h2>CourtFind!</h2>
        <div className="search-container">
          <input
            type="text"
            placeholder="Enter location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="search-input"
          />
          <button className="search-button">
            <i className="fas fa-map-marker-alt"></i>
          </button>
        </div>
        <button onClick={handleFindCourts} className="find-button">
          Find Courts
        </button>
        <div className="sidebar-footer">
          <p>Dhruv Agarwal | dhruv.agarwals@gmail.com</p>
          <p>v 1.0.0</p>
        </div>
      </div>
      <div className="map-container">
        <Map ref={mapRef} />
      </div>
      <button className="toggle-button" onClick={toggleSidebar}>
        <i className={`fas fa-caret-${isSidebarOpen ? 'left' : 'right'}`}></i>
      </button>
    </div>
  );
};

export default App;
