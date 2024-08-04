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

suburban_areas = {
    'North America': [
        {'name': 'Plano, TX', 'lat': 33.0198, 'lon': -96.6989},
        {'name': 'Naperville, IL', 'lat': 41.7508, 'lon': -88.1535},
        {'name': 'Scottsdale, AZ', 'lat': 33.4942, 'lon': -111.9261},
        {'name': 'Bellevue, WA', 'lat': 47.6101, 'lon': -122.2015},
        {'name': 'Fremont, CA', 'lat': 37.5483, 'lon': -121.9886},
        {'name': 'Irvine, CA', 'lat': 33.6846, 'lon': -117.8265},
        {'name': 'Overland Park, KS', 'lat': 38.9822, 'lon': -94.6708},
        {'name': 'Aurora, CO', 'lat': 39.7294, 'lon': -104.8319},
        {'name': 'Rockville, MD', 'lat': 39.0837, 'lon': -77.1487},
        {'name': 'Edison, NJ', 'lat': 40.5187, 'lon': -74.4121},
        {'name': 'Carlsbad, CA', 'lat': 33.1581, 'lon': -117.3506},
        {'name': 'Frisco, TX', 'lat': 33.1507, 'lon': -96.8236},
        {'name': 'Peoria, AZ', 'lat': 33.5806, 'lon': -112.2374},
        {'name': 'Henderson, NV', 'lat': 36.0395, 'lon': -114.9817},
        {'name': 'Columbia, MD', 'lat': 39.2037, 'lon': -76.8610},
        {'name': 'Santa Clarita, CA', 'lat': 34.3917, 'lon': -118.5426},
    ],
    'South America': [
        {'name': 'San Isidro, Buenos Aires', 'lat': -34.4712, 'lon': -58.5177},
        {'name': 'Vitacura, Santiago', 'lat': -33.3806, 'lon': -70.5760},
        {'name': 'Barra da Tijuca, Rio de Janeiro', 'lat': -23.0040, 'lon': -43.3659},
        {'name': 'Pocitos, Montevideo', 'lat': -34.9133, 'lon': -56.1536},
        {'name': 'Miraflores, Lima', 'lat': -12.1175, 'lon': -77.0375},
        {'name': 'La Molina, Lima', 'lat': -12.0806, 'lon': -76.9438},
        {'name': 'Recoleta, Buenos Aires', 'lat': -34.5875, 'lon': -58.3974},
        {'name': 'Las Condes, Santiago', 'lat': -33.4087, 'lon': -70.5665},
        {'name': 'Palermo, Buenos Aires', 'lat': -34.5883, 'lon': -58.4306},
        {'name': 'Nunoa, Santiago', 'lat': -33.4569, 'lon': -70.6017},
        {'name': 'San Borja, Lima', 'lat': -12.1045, 'lon': -76.9904},
        {'name': 'Cumbaya, Quito', 'lat': -0.1850, 'lon': -78.4366},
        {'name': 'El Poblado, Medellin', 'lat': 6.2070, 'lon': -75.5678},
        {'name': 'Vitacura, Santiago', 'lat': -33.3808, 'lon': -70.5825},
        {'name': 'Los Palos Grandes, Caracas', 'lat': 10.4991, 'lon': -66.8477},
        {'name': 'Santo Domingo, Bogotá', 'lat': 4.7451, 'lon': -74.0314},
    ],
    'Europe': [
        {'name': 'Surbiton, London', 'lat': 51.3927, 'lon': -0.2989},
        {'name': 'Neuilly-sur-Seine, Paris', 'lat': 48.8842, 'lon': 2.2686},
        {'name': 'Charlottenburg, Berlin', 'lat': 52.5163, 'lon': 13.3041},
        {'name': 'Chamartin, Madrid', 'lat': 40.4668, 'lon': -3.6760},
        {'name': 'Norrmalm, Stockholm', 'lat': 59.3346, 'lon': 18.0632},
        {'name': 'Eixample, Barcelona', 'lat': 41.3888, 'lon': 2.1590},
        {'name': 'Kreuzberg, Berlin', 'lat': 52.4996, 'lon': 13.4030},
        {'name': 'Prati, Rome', 'lat': 41.9063, 'lon': 12.4674},
        {'name': 'Vesterbro, Copenhagen', 'lat': 55.6699, 'lon': 12.5560},
        {'name': 'Grunerlokka, Oslo', 'lat': 59.9222, 'lon': 10.7600},
        {'name': 'De Pijp, Amsterdam', 'lat': 52.3535, 'lon': 4.8924},
        {'name': 'Islington, London', 'lat': 51.5378, 'lon': -0.1039},
        {'name': 'San Siro, Milan', 'lat': 45.4780, 'lon': 9.1406},
        {'name': 'Chamberí, Madrid', 'lat': 40.4342, 'lon': -3.7055},
        {'name': 'Mitte, Berlin', 'lat': 52.5235, 'lon': 13.4115},
        {'name': 'Saint-Gilles, Brussels', 'lat': 50.8241, 'lon': 4.3452},
    ],
    'Africa': [
        {'name': 'Sandton, Johannesburg', 'lat': -26.1076, 'lon': 28.0567},
        {'name': 'Rivonia, Johannesburg', 'lat': -26.0614, 'lon': 28.0601},
        {'name': 'Cocody, Abidjan', 'lat': 5.3494, 'lon': -3.9891},
        {'name': 'Bole, Addis Ababa', 'lat': 9.0060, 'lon': 38.7700},
        {'name': 'Lekki, Lagos', 'lat': 6.4315, 'lon': 3.5221},
        {'name': 'Ikoyi, Lagos', 'lat': 6.4543, 'lon': 3.4441},
        {'name': 'Houghton Estate, Johannesburg', 'lat': -26.1662, 'lon': 28.0494},
        {'name': 'East Legon, Accra', 'lat': 5.6292, 'lon': -0.1665},
        {'name': 'Karen, Nairobi', 'lat': -1.3191, 'lon': 36.7206},
        {'name': 'Mokattam, Cairo', 'lat': 30.0109, 'lon': 31.2760},
        {'name': 'La Marsa, Tunis', 'lat': 36.8782, 'lon': 10.3242},
        {'name': 'Asokoro, Abuja', 'lat': 9.0441, 'lon': 7.5376},
        {'name': 'Kigamboni, Dar es Salaam', 'lat': -6.8572, 'lon': 39.3470},
        {'name': 'Menlyn, Pretoria', 'lat': -25.7844, 'lon': 28.2757},
        {'name': 'Nifas Silk-Lafto, Addis Ababa', 'lat': 8.9740, 'lon': 38.7596},
        {'name': 'Fourways, Johannesburg', 'lat': -26.0109, 'lon': 28.0130},
    ],
    'Asia': [
        {'name': 'Bandra, Mumbai', 'lat': 19.0600, 'lon': 72.8300},
        {'name': 'Setagaya, Tokyo', 'lat': 35.6461, 'lon': 139.6532},
        {'name': 'Haidian, Beijing', 'lat': 39.9784, 'lon': 116.3103},
        {'name': 'Ekkamai, Bangkok', 'lat': 13.7266, 'lon': 100.5832},
        {'name': 'Jamsil, Seoul', 'lat': 37.5145, 'lon': 127.1002},
        {'name': 'Causeway Bay, Hong Kong', 'lat': 22.2783, 'lon': 114.1747},
        {'name': 'Gangnam, Seoul', 'lat': 37.5172, 'lon': 127.0473},
        {'name': 'Thonglor, Bangkok', 'lat': 13.7341, 'lon': 100.5825},
        {'name': 'Kowloon, Hong Kong', 'lat': 22.3193, 'lon': 114.1694},
        {'name': 'Pudong, Shanghai', 'lat': 31.2304, 'lon': 121.4737},
        {'name': 'Daan, Taipei', 'lat': 25.0260, 'lon': 121.5418},
        {'name': 'Roppongi, Tokyo', 'lat': 35.6626, 'lon': 139.7310},
        {'name': 'Indiranagar, Bangalore', 'lat': 12.9716, 'lon': 77.6412},
        {'name': 'Kuningan, Jakarta', 'lat': -6.2383, 'lon': 106.8309},
        {'name': 'Ortigas, Manila', 'lat': 14.5836, 'lon': 121.0613},
        {'name': 'Hinganghat, Mumbai', 'lat': 20.5487, 'lon': 78.8398},
    ],
    'Australia': [
        {'name': 'St Kilda, Melbourne', 'lat': -37.8676, 'lon': 144.9805},
        {'name': 'Manly, Sydney', 'lat': -33.7963, 'lon': 151.2867},
        {'name': 'Kangaroo Point, Brisbane', 'lat': -27.4806, 'lon': 153.0351},
        {'name': 'Cottesloe, Perth', 'lat': -31.9954, 'lon': 115.7592},
        {'name': 'Bondi, Sydney', 'lat': -33.8915, 'lon': 151.2767},
        {'name': 'South Yarra, Melbourne', 'lat': -37.8390, 'lon': 144.9932},
        {'name': 'Fortitude Valley, Brisbane', 'lat': -27.4558, 'lon': 153.0340},
        {'name': 'Subiaco, Perth', 'lat': -31.9502, 'lon': 115.8261},
        {'name': 'Paddington, Sydney', 'lat': -33.8844, 'lon': 151.2283},
        {'name': 'Toorak, Melbourne', 'lat': -37.8394, 'lon': 145.0089},
        {'name': 'New Farm, Brisbane', 'lat': -27.4679, 'lon': 153.0459},
        {'name': 'Claremont, Perth', 'lat': -31.9808, 'lon': 115.7816},
        {'name': 'Brighton, Melbourne', 'lat': -37.9186, 'lon': 144.9984},
        {'name': 'Mosman, Sydney', 'lat': -33.8266, 'lon': 151.2398},
        {'name': 'Bulimba, Brisbane', 'lat': -27.4555, 'lon': 153.0571},
        {'name': 'Dalkeith, Perth', 'lat': -31.9987, 'lon': 115.7933},
    ],
}

urban_areas = {
    'North America': [
        {'name': 'New York, NY', 'lat': 40.7128, 'lon': -74.0060},
        {'name': 'Los Angeles, CA', 'lat': 34.0522, 'lon': -118.2437},
        {'name': 'Chicago, IL', 'lat': 41.8781, 'lon': -87.6298},
        {'name': 'Houston, TX', 'lat': 29.7604, 'lon': -95.3698},
        {'name': 'San Francisco, CA', 'lat': 37.7749, 'lon': -122.4194},
        {'name': 'Miami, FL', 'lat': 25.7617, 'lon': -80.1918},
        {'name': 'Boston, MA', 'lat': 42.3601, 'lon': -71.0589},
        {'name': 'Atlanta, GA', 'lat': 33.7490, 'lon': -84.3880},
    ],
    'South America': [
        {'name': 'São Paulo, Brazil', 'lat': -23.5505, 'lon': -46.6333},
        {'name': 'Buenos Aires, Argentina', 'lat': -34.6037, 'lon': -58.3816},
        {'name': 'Santiago, Chile', 'lat': -33.4489, 'lon': -70.6693},
        {'name': 'Lima, Peru', 'lat': -12.0464, 'lon': -77.0428},
        {'name': 'Bogotá, Colombia', 'lat': 4.7110, 'lon': -74.0721},
        {'name': 'Caracas, Venezuela', 'lat': 10.4806, 'lon': -66.9036},
        {'name': 'Quito, Ecuador', 'lat': -0.1807, 'lon': -78.4678},
        {'name': 'Montevideo, Uruguay', 'lat': -34.9011, 'lon': -56.1645},
    ],
    'Europe': [
        {'name': 'London, UK', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'Paris, France', 'lat': 48.8566, 'lon': 2.3522},
        {'name': 'Berlin, Germany', 'lat': 52.5200, 'lon': 13.4050},
        {'name': 'Madrid, Spain', 'lat': 40.4168, 'lon': -3.7038},
        {'name': 'Rome, Italy', 'lat': 41.9028, 'lon': 12.4964},
        {'name': 'Vienna, Austria', 'lat': 48.2082, 'lon': 16.3738},
        {'name': 'Amsterdam, Netherlands', 'lat': 52.3676, 'lon': 4.9041},
        {'name': 'Copenhagen, Denmark', 'lat': 55.6761, 'lon': 12.5683},
    ],
    'Africa': [
        {'name': 'Lagos, Nigeria', 'lat': 6.5244, 'lon': 3.3792},
        {'name': 'Cairo, Egypt', 'lat': 30.0444, 'lon': 31.2357},
        {'name': 'Johannesburg, South Africa', 'lat': -26.2041, 'lon': 28.0473},
        {'name': 'Nairobi, Kenya', 'lat': -1.2921, 'lon': 36.8219},
        {'name': 'Cape Town, South Africa', 'lat': -33.9249, 'lon': 18.4241},
        {'name': 'Addis Ababa, Ethiopia', 'lat': 9.0250, 'lon': 38.7469},
        {'name': 'Casablanca, Morocco', 'lat': 33.5731, 'lon': -7.5898},
        {'name': 'Accra, Ghana', 'lat': 5.6037, 'lon': -0.1870},
    ],
    'Asia': [
        {'name': 'Tokyo, Japan', 'lat': 35.6895, 'lon': 139.6917},
        {'name': 'Beijing, China', 'lat': 39.9042, 'lon': 116.4074},
        {'name': 'Mumbai, India', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Bangkok, Thailand', 'lat': 13.7563, 'lon': 100.5018},
        {'name': 'Seoul, South Korea', 'lat': 37.5665, 'lon': 126.9780},
        {'name': 'Shanghai, China', 'lat': 31.2304, 'lon': 121.4737},
        {'name': 'Singapore, Singapore', 'lat': 1.3521, 'lon': 103.8198},
        {'name': 'Hong Kong', 'lat': 22.3193, 'lon': 114.1694},
    ],
    'Australia': [
        {'name': 'Sydney, Australia', 'lat': -33.8688, 'lon': 151.2093},
        {'name': 'Melbourne, Australia', 'lat': -37.8136, 'lon': 144.9631},
        {'name': 'Brisbane, Australia', 'lat': -27.4698, 'lon': 153.0251},
        {'name': 'Perth, Australia', 'lat': -31.9505, 'lon': 115.8605},
        {'name': 'Adelaide, Australia', 'lat': -34.9285, 'lon': 138.6007},
        {'name': 'Gold Coast, Australia', 'lat': -28.0167, 'lon': 153.4000},
        {'name': 'Canberra, Australia', 'lat': -35.2809, 'lon': 149.1300},
        {'name': 'Hobart, Australia', 'lat': -42.8821, 'lon': 147.3272},
    ],
}

def get_random_coordinates(city, range_km=20):
    range_degrees = range_km / 111  # 1 degree is approximately 111 km
    lat = city['lat'] + random.uniform(-range_degrees, range_degrees)
    lon = city['lon'] + random.uniform(-range_degrees, range_degrees)
    return lat, lon

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def is_majority_color(image_path, color, threshold=0.95):
    image = cv2.imread(image_path)
    if image is not None:
        color_rgb = hex_to_rgb(color)
        color_diff = np.sum(np.abs(image - color_rgb), axis=-1)
        match_pixels = np.sum(color_diff < 50)  # Allow some tolerance
        total_pixels = image.shape[0] * image.shape[1]
        match_ratio = match_pixels / total_pixels
        return match_ratio > threshold
    return False

def get_google_maps_image(lat, lon, api_key, filename):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=19&size=1000x1000&maptype=satellite&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
        with open(filename, 'wb') as file:
            file.write(response.content)
        if is_majority_color(filename, '#e3e2de'):
            os.remove(filename)
            return None
        return filename
    return None

def crop_image(image_path):
    image = cv2.imread(image_path)
    if image is not None:
        height = image.shape[0]
        crop_height = int(height * 0.97)
        cropped_image = image[:crop_height, :]
        cv2.imwrite(image_path, cropped_image)
    else:
        print(f"Failed to read image {image_path}")

api_key = os.getenv('GOOGLE_MAPS_API_KEY')

output_folder = 'non_tennis_court_images'
os.makedirs(output_folder, exist_ok=True)

total_images = 1000
suburban_ratio = .67
urban_ratio = 1

suburban_images = int(total_images * suburban_ratio)
urban_images = int(total_images * urban_ratio)

def generate_unique_filename(index):
    return f"non_tennis_court_{index}.png"

def find_unique_coordinates(city, range_km):
    lat, lon = get_random_coordinates(city, range_km)
    return lat, lon

def download_images(num_images, city_range_km, areas, start_index):
    index = start_index
    downloaded_count = 0
    while downloaded_count < num_images:
        if index % 100 == 0:
            print(index)
        city = random.choice(random.choice(list(areas.values())))
        coordinates = find_unique_coordinates(city, range_km=city_range_km)
        if coordinates:
            lat, lon = coordinates
            filename = os.path.join(output_folder, generate_unique_filename(index))
            downloaded_image = get_google_maps_image(lat, lon, api_key, filename)
            if downloaded_image:
                crop_image(downloaded_image)
                downloaded_count += 1
                index += 1

# Collect suburban images
# download_images(suburban_images, city_range_km=20, areas=suburban_areas, start_index=4709)

# Collect urban images
download_images(urban_images, city_range_km=5, areas=urban_areas, start_index=7000)