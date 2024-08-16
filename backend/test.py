from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the trained model
model = load_model('tennis_court_classifier.keras')

# Function to preprocess the image
def preprocess_image(img_path):
    try:
        img = image.load_img(img_path, target_size=(150, 150))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Rescale pixel values
        return img_array
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Function to predict if the image is a tennis court
def predict_tennis_court(img_path, threshold=0.6):
    img_array = preprocess_image(img_path)
    if img_array is not None:
        prediction = model.predict(img_array)
        predicted_label = "Tennis Court" if prediction[0][0] >= threshold else "Not a Tennis Court"
        return predicted_label, prediction[0][0]
    else:
        return "Error processing image", None

# Example usage
if __name__ == "__main__":
    img_paths = [
        'iterations/images/half.png',
        'iterations/images/1.png',
        'iterations/images/2.png',
        'iterations/images/house.png'
    ]

    for img_path in img_paths:
        result, score = predict_tennis_court(img_path)
        print(f"The image '{img_path}' is classified as: {result} (score: {score})")
