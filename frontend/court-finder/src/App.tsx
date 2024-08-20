import React, { useRef, useState, useEffect } from 'react';
import io from 'socket.io-client';
import Map from './Map';
import { LoadScript, Autocomplete } from '@react-google-maps/api';
import { useToken } from './useToken';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './bootstrap-custom.css';
import './App.css';
import { FaCoins, FaQuestionCircle, FaSearch, FaClock } from 'react-icons/fa';
import { Form, InputGroup, Button } from 'react-bootstrap';
import logo from './assets/logo.png';
import CustomModal from './CustomModal';

const socket = io('http://localhost:5000');

const App = () => {
  const mapRef = useRef(null);
  const autocompleteRef = useRef(null);
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const { tokens, spendTokens } = useToken();

  const [showModal, setShowModal] = useState(false);
  const [tokenCost, setTokenCost] = useState(0);
  const [newCenter, setNewCenter] = useState(null);
  const [rectangleSize, setRectangleSize] = useState({ width: '', height: '' });
  const [courtCount, setCourtCount] = useState(null);
  const [error, setError] = useState(null);  // Error state

  useEffect(() => {
    socket.on('status', (data) => {
      setLoadingMessage(data.message);
    });

    socket.on('complete', (data) => {
      setLoading(false);
      setCourtCount(data.courtCount);
    });

    socket.on('error', (data) => {
      setLoading(false);
      setError(data.message);  // Set error message
    });

    return () => {
      socket.off('status');
      socket.off('complete');
      socket.off('error');
    };
  }, []);

  const handlePlaceChanged = () => {
    const place = autocompleteRef.current?.getPlace();
    if (place?.geometry?.location) {
      const center = {
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
      };
      setNewCenter(center);
      setLocation(place.formatted_address || '');

      if (mapRef.current) {
        mapRef.current.updateLocation(center);
      }
    } else {
      console.error('Place not selected or location data not available');
    }
  };

  const calculateTokenCost = (topLeft, bottomRight, boxSize = 140) => {
    const toRadians = (degrees) => degrees * (Math.PI / 180);

    const R = 6371e3;
    const latStart = topLeft.lat;
    const lonStart = topLeft.lng;
    const latEnd = bottomRight.lat;
    const lonEnd = bottomRight.lng;

    const latStartRad = toRadians(latStart);
    const lonStartRad = toRadians(lonStart);
    const latEndRad = toRadians(latEnd);
    const lonEndRad = toRadians(lonEnd);

    const dLat = boxSize / R;
    const dLon = boxSize / (R * Math.cos((latStartRad + latEndRad) / 2));

    let lat = latStartRad;
    let imageCount = 0;

    while (lat > latEndRad) {
      let lon = lonStartRad;
      while (lon < lonEndRad) {
        lon += dLon;
        imageCount++;
      }
      lat -= dLat;
    }

    return imageCount;
  };

  const handleSearch = () => {
    const rectangle = mapRef.current?.getRectangleRef();
    if (!rectangle) {
      console.error('Rectangle reference is null');
      return;
    }

    const bounds = rectangle.getBounds();
    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();

    const R = 6371e3;
    const width = (google.maps.geometry.spherical.computeDistanceBetween(
      new google.maps.LatLng(ne.lat(), sw.lng()),
      new google.maps.LatLng(ne.lat(), ne.lng())
    ) / 1609.34).toFixed(2);

    const height = (google.maps.geometry.spherical.computeDistanceBetween(
      new google.maps.LatLng(ne.lat(), sw.lng()),
      new google.maps.LatLng(sw.lat(), sw.lng())
    ) / 1609.34).toFixed(2);

    const cost = calculateTokenCost(
      { lat: ne.lat(), lng: sw.lng() },
      { lat: sw.lat(), lng: ne.lng() }
    );
    setTokenCost(cost);
    setShowModal(true);
    setRectangleSize({ width, height });
  };

  const confirmSearch = async () => {
    if (tokens >= tokenCost) {
      spendTokens(tokenCost);
      setLoading(true);
      setLoadingMessage('Fetching images...');
      setCourtCount(null);
      setError(null);  // Clear previous errors
      if (mapRef.current) {
        await mapRef.current.findCourts();
        setLoading(false);
        setLoadingMessage('');
      }
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCourtCount(null);
    setLoading(false);
    setLoadingMessage('');
    setError(null);  // Clear previous errors
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
      <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY} libraries={['places']}>
        <div className="navbar">
          <div className="navbar-left">
            <img src={logo} alt="CourtFind Logo" className="logo" />
            <div className="navbar-title">CourtFind!</div>
          </div>

          <div className="navbar-middle">
            <div className="custom-bootstrap">
              <InputGroup className="location-search">
                <Autocomplete
                  onLoad={(auto) => {
                    autocompleteRef.current = auto;
                  }}
                  onPlaceChanged={handlePlaceChanged}
                >
                  <Form.Control
                    placeholder="Enter location"
                    aria-label="Enter location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </Autocomplete>
                <Button variant="success" onClick={handlePlaceChanged}>
                  <i className="fas fa-map-marker-alt"></i>
                </Button>
              </InputGroup>
            </div>
          </div>

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
            <button className="find-button" onClick={handleSearch}>
              Find Courts
            </button>
          </div>
        </div>

        <div className="map-container">
          <Map
            ref={mapRef}
            setCourtCount={setCourtCount}
          />
        </div>

        <div className="footer-overlay">
          Dhruv Agarwal | dhruv.agarwals@gmail.com
        </div>
      </LoadScript>

      <CustomModal
        show={showModal}
        onClose={handleCloseModal}
        onConfirm={confirmSearch}
        tokenCost={tokenCost}
        rectangleSize={rectangleSize}
        courtCount={courtCount}
        loading={loading}
        loadingMessage={loadingMessage}
        tokens={tokens}
        error={error}  // Pass the error state to the modal
      />
    </div>
  );
};

export default App;
