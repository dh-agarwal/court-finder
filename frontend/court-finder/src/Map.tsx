import React, { useState, useEffect } from 'react';
import { GoogleMap, LoadScript } from '@react-google-maps/api';

const containerStyle = {
  width: '100%',
  height: '100vh',
};

const Map: React.FC = () => {
  const [center, setCenter] = useState<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCenter({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        () => {
          console.error('Error fetching location');
        }
      );
    }
  }, []);

  const mapOptions = center
    ? {
        disableDefaultUI: false,
        zoomControl: true,
        zoomControlOptions: {
          position: window.google.maps.ControlPosition.RIGHT_BOTTOM,
        },
        streetViewControl: false,
        fullscreenControl: false,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        mapTypeControl: false,
        rotateControl: false,
      }
    : {};

  return (
    <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      {center && (
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={center}
            zoom={15}
            options={mapOptions}
          />
          {/* Custom Indicator */}
          <div className="custom-marker"></div>
        </div>
      )}
    </LoadScript>
  );
};

export default Map;
