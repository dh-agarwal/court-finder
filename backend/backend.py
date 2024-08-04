from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import aiohttp
import asyncio
from io import BytesIO
import os
from dotenv import load_dotenv
import math

load_dotenv()
app = Flask(__name__)
model = load_model('tennis_court_classifier.h5')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

async def fetch_image(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            img_data = await response.read()
            return Image.open(BytesIO(img_data)).convert('RGB')
        else:
            return None

async def get_google_maps_images_async(coords):
    images = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for lat, lon in coords:
            url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=20&size=500x400&maptype=satellite&key={GOOGLE_MAPS_API_KEY}"
            tasks.append(fetch_image(session, url))
        images = await asyncio.gather(*tasks)
    return images

def preprocess_image(img):
    img = img.resize((150, 150))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def is_tennis_court(prediction):
    return prediction[0][0] >= 0.5

def get_grid_coordinates(top_left, bottom_right, spacing):
    R = 6371e3  # Earth radius in meters
    lat_start, lon_start = top_left
    lat_end, lon_end = bottom_right
    coords = []
    
    lat_start_rad = math.radians(lat_start)
    lon_start_rad = math.radians(lon_start)
    lat_end_rad = math.radians(lat_end)
    lon_end_rad = math.radians(lon_end)

    d_lat = spacing / R
    d_lon = spacing / (R * math.cos((lat_start_rad + lat_end_rad) / 2))

    lat = lat_start_rad
    while lat >= lat_end_rad:
        lon = lon_start_rad
        while lon <= lon_end_rad:
            coords.append((math.degrees(lat), math.degrees(lon)))
            lon += d_lon
        lat -= d_lat
    
    return coords

@app.route('/find-courts', methods=['GET'])
def find_courts():
    lat_top_left = float(request.args.get('lat_top_left'))
    lon_top_left = float(request.args.get('lon_top_left'))
    lat_bottom_right = float(request.args.get('lat_bottom_right'))
    lon_bottom_right = float(request.args.get('lon_bottom_right'))
    spacing = 75  # Spacing in meters

    if not (lat_top_left and lon_top_left and lat_bottom_right and lon_bottom_right):
        return jsonify({"error": "Please provide top-left and bottom-right coordinates"}), 400

    coords = get_grid_coordinates((lat_top_left, lon_top_left), (lat_bottom_right, lon_bottom_right), spacing)
    print(len(coords))
    
    images = asyncio.run(get_google_maps_images_async(coords))
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

# Prediction endpoint
@app.route('/predict', methods=['GET'])
def predict():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Please provide latitude and longitude"}), 400

    img = get_google_maps_images_async(lat, lon)
    if img is None:
        return jsonify({"error": "Could not fetch image for the provided coordinates"}), 500

    img_array = preprocess_image(img)
    prediction = model.predict(img_array)
    result = "Tennis Court" if is_tennis_court(prediction) else "Not a Tennis Court"

    return jsonify({"latitude": lat, "longitude": lon, "result": result})

if __name__ == '__main__':
    app.run(debug=True)
