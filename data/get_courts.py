import pandas as pd
import requests
import random
import os
import cv2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get Google Maps Static API image
def get_google_maps_image(lat, lon, api_key, filename):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=20&size=500x400&maptype=satellite&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Saved image {filename}")
        return filename
    else:
        print(f"Failed to get image for {lat}, {lon}")
        return None

# Function to crop the bottom 3% of the image
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

# Load the CSV file
csv_file = 'data/tennis_courts.csv'
df = pd.read_csv(csv_file)

# Ensure the 'indoor' column is boolean
df['indoor'] = df['indoor'].astype(bool)

# Filter rows where indoor is False
outdoor_courts = df[df['indoor'] == False]

# Get your Google Maps API key from environment variable
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

# Create a folder to save images
output_folder = 'tennis_court_images'
os.makedirs(output_folder, exist_ok=True)

# Pick 1000 random rows and save images
for i in range(1000, 2000):
    row = outdoor_courts.sample(n=1).iloc[0]
    lat = row['latitude']
    lon = row['longitude']
    filename = os.path.join(output_folder, f"court_{i+1}.png")
    downloaded_image = get_google_maps_image(lat, lon, api_key, filename)
    if downloaded_image:
        crop_image(downloaded_image)
