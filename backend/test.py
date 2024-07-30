from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the trained model
model = load_model('tennis_court_classifier.h5')

# Function to preprocess the image
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(150, 150))  # Adjust target_size based on your model's input shape
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Rescale pixel values
    return img_array

# Function to predict if the image is a tennis court
def predict_tennis_court(img_path):
    img_array = preprocess_image(img_path)
    prediction = model.predict(img_array)
    return "Tennis Court" if prediction[0][0] >= 0.5 else "Not a Tennis Court"

# Example usage
if __name__ == "__main__":
    img_path = 'iterations/images/half.png'
    result = predict_tennis_court(img_path)
    print(f"The image is classified as: {result}")
    img_path = 'iterations/images/1.png'
    result = predict_tennis_court(img_path)
    print(f"The image is classified as: {result}")
    img_path = 'iterations/images/2.png'
    result = predict_tennis_court(img_path)
    print(f"The image is classified as: {result}")
    img_path = 'iterations/images/house.png'
    result = predict_tennis_court(img_path)
    print(f"The image is classified as: {result}")