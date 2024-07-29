import pandas as pd
import requests
import random
import os
import cv2
from dotenv import load_dotenv
import hashlib
import numpy as np

# Load environment variables from .env file
load_dotenv()

# List of major cities with approximate coordinates
cities = {
    'North America': [
        {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
        {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
        {'name': 'Mexico City', 'lat': 19.4326, 'lon': -99.1332},
        {'name': 'Toronto', 'lat': 43.651070, 'lon': -79.347015},
    ],
    'South America': [
        {'name': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333},
        {'name': 'Buenos Aires', 'lat': -34.6037, 'lon': -58.3816},
        {'name': 'Santiago', 'lat': -33.4489, 'lon': -70.6693},
        {'name': 'Lima', 'lat': -12.0464, 'lon': -77.0428},
    ],
    'Europe': [
        {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
        {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050},
        {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038},
    ],
    'Africa': [
        {'name': 'Lagos', 'lat': 6.5244, 'lon': 3.3792},
        {'name': 'Cairo', 'lat': 30.0444, 'lon': 31.2357},
        {'name': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473},
        {'name': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219},
    ],
    'Asia': [
        {'name': 'Tokyo', 'lat': 35.6895, 'lon': 139.6917},
        {'name': 'Beijing', 'lat': 39.9042, 'lon': 116.4074},
        {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Bangkok', 'lat': 13.7563, 'lon': 100.5018},
    ],
    'Australia': [
        {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
        {'name': 'Melbourne', 'lat': -37.8136, 'lon': 144.9631},
        {'name': 'Brisbane', 'lat': -27.4698, 'lon': 153.0251},
        {'name': 'Perth', 'lat': -31.9505, 'lon': 115.8605},
    ],
}

def get_random_coordinates(city, range_km=5):
    range_degrees = range_km / 111  # 1 degree is approximately 111 km
    lat = city['lat'] + random.uniform(-range_degrees, range_degrees)
    lon = city['lon'] + random.uniform(-range_degrees, range_degrees)
    return lat, lon

def is_majority_white(image_path, threshold=0.95):
    image = cv2.imread(image_path)
    if image is not None:
        # Convert image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Calculate the number of white pixels
        white_pixels = np.sum(gray_image > 245)  # Consider near white as white
        total_pixels = gray_image.size
        white_ratio = white_pixels / total_pixels
        return white_ratio > threshold
    return False

def get_google_maps_image(lat, lon, api_key, filename):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=18&size=500x400&maptype=satellite&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        if is_majority_white(filename):
            print(f"No imagery for coordinates {lat}, {lon}. Skipping.")
            os.remove(filename)
            return None
        else:
            print(f"Saved image {filename}")
            return filename
    else:
        print(f"Failed to get image for {lat}, {lon}")
        return None

def crop_image(image_path):
    image = cv2.imread(image_path)
    if image is not None:
        height = image.shape[0]
        crop_height = int(height * 0.97)
        cropped_image = image[:crop_height, :]
        cv2.imwrite(image_path, cropped_image)
        print(f"Cropped and saved image {image_path}")
    else:
        print(f"Failed to read image {image_path}")

api_key = os.getenv('GOOGLE_MAPS_API_KEY')

output_folder = 'non_tennis_court_images'
os.makedirs(output_folder, exist_ok=True)

total_images = 1500
urban_ratio = 0.6
urban_images = int(total_images * urban_ratio)
suburban_images = total_images - urban_images

used_coordinates = set()

def generate_unique_filename(lat, lon):
    coords_str = f"{lat:.5f}_{lon:.5f}"
    filename_hash = hashlib.md5(coords_str.encode()).hexdigest()
    return filename_hash

def find_unique_coordinates(city, range_km):
    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        lat, lon = get_random_coordinates(city, range_km)
        coord_tuple = (lat, lon)
        if coord_tuple not in used_coordinates:
            used_coordinates.add(coord_tuple)
            return coord_tuple
        attempts += 1
    return None

# Collect urban images
for _ in range(urban_images):
    city = random.choice(random.choice(list(cities.values())))
    coordinates = find_unique_coordinates(city, range_km=5)
    if coordinates:
        lat, lon = coordinates
        filename = os.path.join(output_folder, f"urban_non_court_{generate_unique_filename(lat, lon)}.png")
        downloaded_image = get_google_maps_image(lat, lon, api_key, filename)
        if downloaded_image:
            crop_image(downloaded_image)
    else:
        print("Failed to find unique coordinates for an urban area.")

# Collect suburban images
for _ in range(suburban_images):
    city = random.choice(random.choice(list(cities.values())))
    coordinates = find_unique_coordinates(city, range_km=20)
    if coordinates:
        lat, lon = coordinates
        filename = os.path.join(output_folder, f"suburban_non_court_{generate_unique_filename(lat, lon)}.png")
        downloaded_image = get_google_maps_image(lat, lon, api_key, filename)
        if downloaded_image:
            crop_image(downloaded_image)
    else:
        print("Failed to find unique coordinates for a suburban area.")
