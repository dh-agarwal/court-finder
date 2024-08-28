from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from flask_cors import CORS
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import aiohttp
import asyncio
from io import BytesIO
import os
from dotenv import load_dotenv
import math
from flask_socketio import SocketIO, emit
from geopy.distance import geodesic
import boto3

load_dotenv()
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable SocketIO

# S3 configuration
BUCKET_NAME = 'courtfind-model'
MODEL_FILENAME = 'tennis_court_classifier.keras'
LOCAL_MODEL_PATH = '/tmp/tennis_court_classifier.keras'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def download_model_from_s3(bucket_name, model_filename, local_model_path):
    print("Downloading model from S3...")
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, model_filename, local_model_path)
    print("Model downloaded successfully")
    return load_model(local_model_path)

# model = download_model_from_s3(BUCKET_NAME, MODEL_FILENAME, LOCAL_MODEL_PATH)
model = load_model(LOCAL_MODEL_PATH)

async def fetch_image(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            img_data = await response.read()
            img = Image.open(BytesIO(img_data)).convert('RGB')
            return img
        else:
            return None

async def get_google_maps_images_async(coords):
    images = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for lat, lon in coords:
            url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=19&size=1000x1000&maptype=satellite&key={GOOGLE_MAPS_API_KEY}"
            tasks.append(fetch_image(session, url))
        images = await asyncio.gather(*tasks)
    return images

def combine_close_courts(tennis_courts, new_court, proximity=200):
    for court in tennis_courts:
        distance = geodesic((court["latitude"], court["longitude"]), (new_court["latitude"], new_court["longitude"])).meters
        if distance < proximity:
            # Average the locations
            court["latitude"] = (court["latitude"] + new_court["latitude"]) / 2
            court["longitude"] = (court["longitude"] + new_court["longitude"]) / 2
            return tennis_courts
    tennis_courts.append(new_court)
    return tennis_courts

def preprocess_image(img):
    try:
        if isinstance(img, Image.Image):  # If img is a PIL Image object
            img = np.array(img)
        
        if img is None:
            print(f"Error: Failed to read image.")
            return None

        # Calculate the cropping based on the 140-meter height
        height, width = img.shape[:2]
        meters_per_pixel = 140 / height  # Assuming 140 meters is the height of the image
        crop_meters = 0.03 * 140  # 3% of 140 meters
        crop_pixels = int(crop_meters / meters_per_pixel)

        # Crop the bottom 3% of the image
        cropped_img = img[:height - crop_pixels, :]

        # Convert to PIL Image for further processing
        img_pil = Image.fromarray(cropped_img)
        img_pil = img_pil.resize((150, 150))

        img_array = image.img_to_array(img_pil)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Rescale pixel values

        return img_array
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def is_tennis_court(prediction):
    return prediction[0][0] >= 0.5

def get_grid_coordinates(top_left, bottom_right, box_size=140):
    R = 6371e3  # Earth's radius in meters
    lat_start, lon_start = top_left
    lat_end, lon_end = bottom_right
    coords = []

    lat_start_rad = math.radians(lat_start)
    lon_start_rad = math.radians(lon_start)
    lat_end_rad = math.radians(lat_end)
    lon_end_rad = math.radians(lon_end)

    # Calculate latitude and longitude step based on box size
    d_lat = box_size / R
    d_lon = box_size / (R * math.cos((lat_start_rad + lat_end_rad) / 2))

    lat = lat_start_rad
    while lat > lat_end_rad:
        lon = lon_start_rad
        while lon < lon_end_rad:
            # Get the center of the box
            center_lat = lat - d_lat / 2
            center_lon = lon + d_lon / 2

            coords.append((math.degrees(center_lat), math.degrees(center_lon)))

            lon += d_lon
        lat -= d_lat

    return coords
    
def divide_image_into_quadrants(img):
    width, height = img.size
    mid_width = width // 2
    mid_height = height // 2
    
    quadrant1 = img.crop((0, 0, mid_width, mid_height))
    quadrant2 = img.crop((mid_width, 0, width, mid_height))
    quadrant3 = img.crop((0, mid_height, mid_width, height))
    quadrant4 = img.crop((mid_width, mid_height, width, height))
    
    return [quadrant1, quadrant2, quadrant3, quadrant4]

def get_quadrant_coordinates(center_coords, quadrant_index, box_size=140):
    lat, lon = center_coords
    delta_lat = box_size / 4 / 111111  # 111111 meters per degree latitude
    delta_lon = box_size / 4 / (111111 * math.cos(math.radians(lat)))
    
    if quadrant_index == 0:  # top-left quadrant
        return (lat + delta_lat, lon - delta_lon)
    elif quadrant_index == 1:  # top-right quadrant
        return (lat + delta_lat, lon + delta_lon)
    elif quadrant_index == 2:  # bottom-left quadrant
        return (lat - delta_lat, lon - delta_lon)
    elif quadrant_index == 3:  # bottom-right quadrant
        return (lat - delta_lat, lon + delta_lon)

@app.route('/find-courts', methods=['GET'])
def find_courts():
    lat_top_left = float(request.args.get('lat_top_left'))
    lon_top_left = float(request.args.get('lon_top_left'))
    lat_bottom_right = float(request.args.get('lat_bottom_right'))
    lon_bottom_right = float(request.args.get('lon_bottom_right'))
    
    if not (lat_top_left and lon_top_left and lat_bottom_right and lon_bottom_right):
        return jsonify({"error": "Please provide top-left and bottom-right coordinates"}), 400

    try:
        coords = get_grid_coordinates((lat_top_left, lon_top_left), (lat_bottom_right, lon_bottom_right))
        print(len(coords))
        
        socketio.emit('status', {'message': 'Fetching images'})
        
        images = asyncio.run(get_google_maps_images_async(coords))
        
        socketio.emit('status', {'message': 'Scanning region'})
        
        tennis_courts = []

        for i, img in enumerate(images):
            if img:
                img_array = preprocess_image(img)
                prediction = model.predict(img_array)
                if is_tennis_court(prediction):
                    new_court = {
                        "latitude": coords[i][0],
                        "longitude": coords[i][1]
                    }
                    tennis_courts = combine_close_courts(tennis_courts, new_court, proximity=200)
                    
                    quadrants = divide_image_into_quadrants(img)
                    
                    for j, quadrant in enumerate(quadrants):
                        quadrant_array = preprocess_image(quadrant)
                        quadrant_prediction = model.predict(quadrant_array)
                        if is_tennis_court(quadrant_prediction):
                            quadrant_coords = get_quadrant_coordinates(coords[i], j)
                            quadrant_court = {
                                "latitude": quadrant_coords[0],
                                "longitude": quadrant_coords[1]
                            }
                            tennis_courts = combine_close_courts(tennis_courts, quadrant_court, proximity=200)

        socketio.emit('complete', {'courtCount': len(tennis_courts)})
        print(tennis_courts)
        return jsonify({"tennis_courts": [1,2,3]})

    except Exception as e:
        print(f"An error occurred: {e}")
        socketio.emit('error', {'message': 'Something went wrong during court detection.'})
        return jsonify({"error": "An error occurred during processing"}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

