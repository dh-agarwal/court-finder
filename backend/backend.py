from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load the trained model
model = load_model('tennis_court_classifier.h5')

# Get your Google Maps API key from environment variable
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Function to get Google Maps Static API image
def get_google_maps_image(lat, lon):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=20&size=500x400&maptype=satellite&key={GOOGLE_MAPS_API_KEY}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert('RGB')
        return img
    else:
        print(f"Failed to get image for {lat}, {lon}")
        return None

# Function to preprocess the image for the model
def preprocess_image(img):
    img = img.resize((150, 150))  # Resize image to match model's input size
    img_array = np.array(img)  # Convert image to array
    img_array = img_array / 255.0  # Normalize pixel values
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Prediction endpoint
@app.route('/predict', methods=['GET'])
def predict():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Please provide latitude and longitude"}), 400

    # Fetch satellite image
    img = get_google_maps_image(lat, lon)
    if img is None:
        return jsonify({"error": "Could not fetch image for the provided coordinates"}), 500

    # Preprocess the image and make prediction
    img_array = preprocess_image(img)
    prediction = model.predict(img_array)
    result = "Tennis Court" if prediction[0][0] >= 0.5 else "Not a Tennis Court"

    return jsonify({"latitude": lat, "longitude": lon, "result": result})

if __name__ == '__main__':
    app.run(debug=True)
