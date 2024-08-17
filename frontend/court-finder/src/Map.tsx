import React, { useState, useRef, useCallback, forwardRef, useImperativeHandle } from 'react';
import { GoogleMap, Marker, Circle } from '@react-google-maps/api';
import axios from 'axios';

const containerStyle = {
  width: '100%',
  height: '100%',
};

const Map = forwardRef((props, ref) => {
  const [center, setCenter] = useState<{ lat: number; lng: number } | null>(null);
  const [customMarkerIcon, setCustomMarkerIcon] = useState<any>(null);
  const [tennisCourts, setTennisCourts] = useState<{ lat: number; lng: number }[]>([]);
  const rectangleRef = useRef<google.maps.Rectangle | null>(null);
  const mapRef = useRef<google.maps.Map | null>(null);

  useImperativeHandle(ref, () => ({
    findCourts,
  }));

  const initializeRectangle = useCallback(() => {
    if (mapRef.current && center) {
      const latOffset = 0.009;
      const lngOffset = 0.009;

      const bounds = new window.google.maps.LatLngBounds(
        new window.google.maps.LatLng(center.lat - latOffset, center.lng - lngOffset),
        new window.google.maps.LatLng(center.lat + latOffset, center.lng + lngOffset)
      );

      if (!rectangleRef.current) {
        const rectangle = new window.google.maps.Rectangle({
          bounds,
          editable: true,
          draggable: true,
          map: mapRef.current,
          fillColor: 'rgba(0, 0, 255, 0.3)',
          strokeColor: 'dodgerblue',
          strokeWeight: 2,
        });

        rectangleRef.current = rectangle;
      } else {
        rectangleRef.current.setBounds(bounds); // Adjust the rectangle bounds when the center changes
      }
    }
  }, [center]);

  const initializeMap = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          setCenter(userLocation);

          const icon = {
            path: window.google.maps.SymbolPath.CIRCLE,
            fillColor: 'dodgerblue',
            fillOpacity: 1,
            scale: 10,
            strokeColor: 'white',
            strokeWeight: 2,
          };
          setCustomMarkerIcon(icon);
        },
        () => {
          console.error('Error fetching location');
        }
      );
    }
  };

  const handleMapLoad = (map) => {
    mapRef.current = map;
    initializeMap();
  };

  const findCourts = async (newCenter) => {
    if (newCenter) {
      setCenter(newCenter);
      mapRef.current.panTo(newCenter);
    }

    if (!rectangleRef.current) return;

    const bounds = rectangleRef.current.getBounds();
    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();

    try {
      const response = await axios.get('http://localhost:5000/find-courts', {
        params: {
          lat_top_left: ne.lat(),
          lon_top_left: sw.lng(),
          lat_bottom_right: sw.lat(),
          lon_bottom_right: ne.lng(),
        },
      });

      const courts = response.data.tennis_courts;
      setTennisCourts(courts);
    } catch (error) {
      console.error('Error finding courts:', error);
    }
  };

  const mapOptions = center
    ? {
        disableDefaultUI: false,
        zoomControl: true,
        zoomControlOptions: {
          position: window.google.maps.ControlPosition.RIGHT_BOTTOM,
        },
        streetViewControl: false,
        fullscreenControl: false,
        mapTypeId: window.google.maps.MapTypeId.HYBRID,
        mapTypeControl: false,
        rotateControl: false,
      }
    : {};

  return (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={center}
      zoom={15}
      options={mapOptions}
      onLoad={handleMapLoad}
      onTilesLoaded={initializeRectangle}
    >
      {center && customMarkerIcon && <Marker position={center} icon={customMarkerIcon} />}

      {tennisCourts.map((court, index) => (
        <Circle
          key={index}
          center={{ lat: court.latitude, lng: court.longitude }}
          radius={50}
          options={{
            fillColor: 'green',
            fillOpacity: 0.5,
            strokeColor: 'darkgreen',
            strokeOpacity: 0.8,
            strokeWeight: 2,
          }}
        />
      ))}
    </GoogleMap>
  );
});

export default Map;
