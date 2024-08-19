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
  const initialBoundsRef = useRef<google.maps.LatLngBounds | null>(null);

  useImperativeHandle(ref, () => ({
    updateLocation,  // Expose only the function that updates location
    findCourts,
    getRectangleRef: () => rectangleRef.current,
  }));

  const initializeRectangle = useCallback(() => {
    if (mapRef.current && center && !rectangleRef.current) {
      const mileToDegreeLat = 0.014492753623188; // Convert miles to degrees latitude
      const latOffset = 1 * mileToDegreeLat / 2; // Half of the total vertical distance in degrees
  
      // Longitude correction factor based on the current latitude
      const mileToDegreeLng = mileToDegreeLat / Math.cos(center.lat * (Math.PI / 180));
      const lngOffset = 1 * mileToDegreeLng / 2; // Half of the total horizontal distance in degrees
  
      const bounds = new window.google.maps.LatLngBounds(
        new window.google.maps.LatLng(center.lat - latOffset, center.lng - lngOffset),
        new window.google.maps.LatLng(center.lat + latOffset, center.lng + lngOffset)
      );
  
      initialBoundsRef.current = bounds;
  
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

  const updateLocation = (newCenter) => {
    if (newCenter) {
      setCenter(newCenter);
      mapRef.current?.panTo(newCenter);
  
      const mileToDegreeLat = 0.014492753623188; // Convert miles to degrees latitude
      const latOffset = 1 * mileToDegreeLat / 2; // Half of the total vertical distance in degrees
  
      // Longitude correction factor based on the new latitude
      const mileToDegreeLng = mileToDegreeLat / Math.cos(newCenter.lat * (Math.PI / 180));
      const lngOffset = 1 * mileToDegreeLng / 2; // Half of the total horizontal distance in degrees
  
      const newBounds = new window.google.maps.LatLngBounds(
        new window.google.maps.LatLng(newCenter.lat - latOffset, newCenter.lng - lngOffset),
        new window.google.maps.LatLng(newCenter.lat + latOffset, newCenter.lng + lngOffset)
      );
  
      initialBoundsRef.current = newBounds;
      if (rectangleRef.current) {
        rectangleRef.current.setBounds(newBounds);
      }
    }
  };

  // The function to find courts that only gets called after modal confirmation
  const findCourts = async () => {
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
      zoom={center ? 14 : undefined}
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
