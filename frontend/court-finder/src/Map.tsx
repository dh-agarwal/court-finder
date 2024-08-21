import React, { useState, useRef, useCallback, forwardRef, useImperativeHandle } from 'react';
import { GoogleMap, InfoWindow, Marker } from '@react-google-maps/api';
import axios from 'axios';

const containerStyle = {
  width: '100%',
  height: '100%',
};

interface MapProps {
  setCourtCount: (count: number) => void;
}

const Map = forwardRef((props: MapProps, ref) => {
  const { setCourtCount } = props;

  const [center, setCenter] = useState<{ lat: number; lng: number } | null>(null);
  const [selectedCourt, setSelectedCourt] = useState<{ lat: number; lng: number } | null>(null);
  const [circles, setCircles] = useState<google.maps.Circle[]>([]);
  const [mapTypeId, setMapTypeId] = useState<google.maps.MapTypeId>(google.maps.MapTypeId.HYBRID); // Updated
  const rectangleRef = useRef<google.maps.Rectangle | null>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const initialBoundsRef = useRef<google.maps.LatLngBounds | null>(null);

  const ZOOM_THRESHOLD = 17;

  useImperativeHandle(ref, () => ({
    updateLocation,
    findCourts,
    getRectangleRef: () => rectangleRef.current,
  }));

  const initializeRectangle = useCallback(() => {
    if (mapRef.current && center && !rectangleRef.current) {
      const mileToDegreeLat = 0.014492753623188;
      const latOffset = 1 * mileToDegreeLat / 2;

      const mileToDegreeLng = mileToDegreeLat / Math.cos(center.lat * (Math.PI / 180));
      const lngOffset = 1 * mileToDegreeLng / 2;

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
        },
        () => {
          console.error('Error fetching location');
        }
      );
    }
  };

  const handleMapLoad = (map: google.maps.Map) => {
    mapRef.current = map;
    initializeMap();

    map.addListener('zoom_changed', () => {
      const currentZoom = map.getZoom();
      if (rectangleRef.current) {
        if (currentZoom && currentZoom >= ZOOM_THRESHOLD) {
          rectangleRef.current.setDraggable(false);
          rectangleRef.current.setEditable(false);
        } else {
          rectangleRef.current.setDraggable(true);
          rectangleRef.current.setEditable(true);
        }
      }
    });

    map.addListener('click', () => {
      setSelectedCourt(null);
    });
  };

  const updateLocation = (newCenter: google.maps.LatLngLiteral) => {
    if (newCenter) {
      setCenter(newCenter);
      mapRef.current?.panTo(newCenter);

      const mileToDegreeLat = 0.014492753623188;
      const latOffset = 1 * mileToDegreeLat / 2;

      const mileToDegreeLng = mileToDegreeLat / Math.cos(newCenter.lat * (Math.PI / 180));
      const lngOffset = 1 * mileToDegreeLng / 2;

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

  const clearCircles = () => {
    circles.forEach(circle => circle.setMap(null));
    setCircles([]);
  };

  const smoothZoom = (map: google.maps.Map, targetZoom: number, currentZoom: number = map.getZoom() || 0) => {
    if (currentZoom !== targetZoom) {
      google.maps.event.addListenerOnce(map, 'zoom_changed', () => {
        smoothZoom(map, targetZoom, currentZoom + (targetZoom > currentZoom ? 1 : -1));
      });
      setTimeout(() => map.setZoom(currentZoom + (targetZoom > currentZoom ? 1 : -1)), 100);
    }
  };

  const findCourts = async () => {
    clearCircles();

    if (!rectangleRef.current) return;

    const bounds = rectangleRef.current.getBounds();
    if (!bounds) return;
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

      if (courts && Array.isArray(courts)) {
        const validCourts = courts.map((court: { latitude: number; longitude: number }) => ({
          lat: court.latitude,
          lng: court.longitude,
        }));

        // Removed the unused setTennisCourts call
        setCourtCount(validCourts.length);

        validCourts.forEach((court) => {
          const circle = new window.google.maps.Circle({
            center: { lat: court.lat, lng: court.lng },
            radius: 75,
            fillColor: '#8A84E2',
            fillOpacity: 0.3,
            strokeColor: '#8A84E2',
            strokeOpacity: 1,
            strokeWeight: 2,
            map: mapRef.current,
            zIndex: 1000,
          });

          circle.addListener('mouseover', () => {
            circle.setOptions({
              fillColor: '#FF6B6B',
              strokeColor: '#FF6B6B',
            });
          });

          circle.addListener('mouseout', () => {
            circle.setOptions({
              fillColor: '#8A84E2',
              strokeColor: '#8A84E2',
            });
          });

          circle.addListener('click', () => {
            const center = circle.getCenter();
            if (center) {
              setSelectedCourt(court);
              mapRef.current?.panTo(center);
              smoothZoom(mapRef.current!, 18);
            }
          });

          setCircles(prevCircles => [...prevCircles, circle]);
        });
      } else {
        console.error('Invalid courts data:', courts);
        setCourtCount(0);
      }
    } catch (error) {
      console.error('Error finding courts:', error);
      setCourtCount(0);
    }
  };

  const handleMapTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setMapTypeId(event.target.value as google.maps.MapTypeId);
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
      mapTypeId: mapTypeId,
      mapTypeControl: false,
      rotateControl: false,
      tilt: 0,
    }
    : {};

  return (
    <>
      <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 1000 }}>
        <select
          onChange={handleMapTypeChange}
          value={mapTypeId}
          style={{
            padding: '8px',
            borderRadius: '5px',
            border: '1px solid #ccc',
            backgroundColor: '#293241',
            color: '#ffffff',
            fontSize: '14px',
            outline: 'none',
          }}
        >
          <option value="roadmap">Map</option>
          <option value="hybrid">Satellite</option>
        </select>
      </div>

      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center || undefined}
        zoom={center ? 14 : undefined}
        options={mapOptions}
        onLoad={handleMapLoad}
        onTilesLoaded={initializeRectangle}
      >
        {center && (
          <Marker
            position={center}
            icon={{
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: 10,
              fillColor: 'dodgerblue',
              fillOpacity: 0.8,
              strokeColor: 'white',
              strokeWeight: 2,
            }}
          />
        )}

        {selectedCourt && (
          <InfoWindow
            position={{ lat: selectedCourt.lat, lng: selectedCourt.lng }}
            onCloseClick={() => setSelectedCourt(null)}
            options={{
              pixelOffset: new window.google.maps.Size(0, -30),
            }}
          >
            <div style={{
              padding: '5px',
              paddingLeft: '25px',
              color: 'dodgerblue',
              fontSize: '12px',
              textAlign: 'center',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}>
              <u>
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${selectedCourt.lat},${selectedCourt.lng}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: 'dodgerblue',
                    textDecoration: 'none',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  Get Directions
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    width="16px"
                    height="16px"
                    style={{ marginLeft: '4px', marginBottom: '4.5px' }}
                  >
                    <path d="M14,3 L14,5 L19.59,5 L7,17.59 L8.41,19 L21,6.41 L21,12 L23,12 L23,3 L14,3 Z M19,13 L19,21 L5,21 L5,7 L13,7 L13,5 L5,5 C3.9,5 3,5.9 3,7 L3,21 C3,22.1 3.9,23 5,23 L19,23 C20.1,23 21,22.1 21,21 L21,13 L19,13 Z" />
                  </svg>
                </a>
              </u>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </>
  );
});

export default Map;
