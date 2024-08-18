import React, { useRef, useState, useEffect } from 'react';
import Map from './Map';
import Spinner from './Spinner';
import { LoadScript, Autocomplete } from '@react-google-maps/api';
import { useToken } from './TokenContext';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './bootstrap-custom.css'; // Custom scoped Bootstrap styles
import './App.css';
import { FaCoins, FaQuestionCircle, FaSearch, FaClock } from 'react-icons/fa';
import { Form, InputGroup, Button } from 'react-bootstrap';
import logo from './assets/logo.png';

const App: React.FC = () => {
  const mapRef = useRef<{ findCourts: (center?: { lat: number; lng: number }) => void } | null>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const [location, setLocation] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const { tokens } = useToken();

  const handleSearch = () => {
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
      handleSearch();
    }
  };

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
            font-size: 16px !important;
          }
          .pac-item-query {
            font-size: 16px !important;
          }
          .pac-item:hover {
            background-color: #4CAF50 !important;
          }
          .pac-item .pac-icon {
            color: #4CAF50 !important;
            font-size: 20px !important;
          }
        `;
        gmapsIframe.appendChild(style);
        clearInterval(interval);
      }
    }, 500);
  }, []);

  return (
    <div className="App">
      {loading && <Spinner />}
      <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY} libraries={['places']}>
        <div className="navbar">
          {/* Left: Logo and Title */}
          <div className="navbar-left">
            <img src={logo} alt="CourtFind Logo" className="logo" />
            <div className="navbar-title">CourtFind!</div>
          </div>

          {/* Center: Location Input */}
          <div className="navbar-middle">
            <div className="custom-bootstrap">
              <InputGroup className="location-search">
                <Autocomplete
                  onLoad={(auto) => (autocompleteRef.current = auto)}
                  onPlaceChanged={() => setLocation(autocompleteRef.current?.getPlace()?.formatted_address || '')}
                >
                  <Form.Control
                    placeholder="Enter location"
                    aria-label="Enter location"
                    value={location}
                    onKeyPress={handleKeyPress}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </Autocomplete>
                <Button variant="success" onClick={handleSearch}>
                  <i className="fas fa-map-marker-alt"></i>
                </Button>
              </InputGroup>
            </div>
          </div>

          {/* Right: Info, Tokens, and Find Button */}
          <div className="navbar-right">
            <div className="info-container">
              <FaQuestionCircle className="info-button" />

              <div className="info-popup">
                <div className="info-item">
                  <FaSearch className="info-icon search-icon" />
                  <span>Costs are based on search size</span>
                </div>
                <div className="info-item">
                  <FaClock className="info-icon clock-icon" />
                  <span>Tokens reset daily</span>
                </div>
              </div>

            </div>
            <div className="token-display">
              <FaCoins className="token-icon" />
              <span>{tokens} tokens</span>
            </div>
            <button className="find-button" onClick={() => mapRef.current?.findCourts()}>
              Find Courts
            </button>
          </div>
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
