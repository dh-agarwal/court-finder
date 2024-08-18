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
import cv2

load_dotenv()
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable SocketIO
model = load_model('tennis_court_classifier.keras')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

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

@app.route('/find-courts', methods=['GET'])
def find_courts():
    lat_top_left = float(request.args.get('lat_top_left'))
    lon_top_left = float(request.args.get('lon_top_left'))
    lat_bottom_right = float(request.args.get('lat_bottom_right'))
    lon_bottom_right = float(request.args.get('lon_bottom_right'))
    
    if not (lat_top_left and lon_top_left and lat_bottom_right and lon_bottom_right):
        return jsonify({"error": "Please provide top-left and bottom-right coordinates"}), 400

    coords = get_grid_coordinates((lat_top_left, lon_top_left), (lat_bottom_right, lon_bottom_right))
    
    
    # Notify client that image fetching is starting
    socketio.emit('status', {'message': 'Fetching images'})
    
    images = asyncio.run(get_google_maps_images_async(coords))
    print(len(images))
    # Notify client that image fetching is complete and scanning is starting
    socketio.emit('status', {'message': 'Scanning region'})
    
    tennis_courts = []

    for i, img in enumerate(images):
        if img:
            img_array = preprocess_image(img)
            prediction = model.predict(img_array)
            if is_tennis_court(prediction):
                tennis_courts.append({
                    "latitude": coords[i][0],
                    "longitude": coords[i][1]
                })
    
    return jsonify({"tennis_courts": tennis_courts})

if __name__ == '__main__':
    socketio.run(app, debug=True)
