import React, { useRef, useState, useEffect } from 'react';
import Map from './Map';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { LoadScript, Autocomplete } from '@react-google-maps/api';

const App: React.FC = () => {
  const mapRef = useRef<{ findCourts: (center?: { lat: number; lng: number }) => void } | null>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const [location, setLocation] = useState<string>('');

  useEffect(() => {
    const interval = setInterval(() => {
      const gmapsIframe = document.querySelector('.pac-container');
      if (gmapsIframe) {
        const style = document.createElement('style');
        style.innerHTML = `
          .pac-item {
            background-color: #3a4750 !important;
            color: #ffffff !important;
            font-family: Arial, sans-serif !important;
          }
          .pac-item:hover {
            background-color: #4CAF50 !important;
          }
          .pac-item .pac-icon {
            color: #4CAF50 !important;
          }
        `;
        gmapsIframe.appendChild(style);
        clearInterval(interval);
      }
    }, 500);
  }, []);

  const handleLocationChange = () => {
    const place = autocompleteRef.current?.getPlace();
    if (place?.geometry?.location) {
      const newCenter = {
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
      };
      setLocation(place.formatted_address || '');
      if (mapRef.current) {
        mapRef.current.findCourts(newCenter);
      }
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleLocationChange();
    }
  };

  return (
    <div className="App">
      <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY} libraries={['places']}>
        <div className="navbar">
          <div className="navbar-title">CourtFind!</div>
          <div className="navbar-location">
            <div style={{ position: 'relative', width: '100%' }}>
              <Autocomplete
                onLoad={(auto) => (autocompleteRef.current = auto)}
                onPlaceChanged={() => setLocation(autocompleteRef.current?.getPlace()?.formatted_address || '')}
              >
                <input
                  type="text"
                  placeholder="Enter location"
                  className="search-input"
                  value={location}
                  onKeyPress={handleKeyPress}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </Autocomplete>
              <button className="search-button" onClick={handleLocationChange}>
                <i className="fas fa-map-marker-alt"></i>
              </button>
            </div>
          </div>
          <button onClick={() => mapRef.current?.findCourts()} className="find-button">
            Find Courts
          </button>
        </div>
        <div className="map-container">
          <Map ref={mapRef} />
        </div>
        <div className="footer-overlay">
          Dhruv Agarwal | dhruv.agarwals@gmail.com
        </div>
      </LoadScript>
    </div>
  );
};

export default App;
