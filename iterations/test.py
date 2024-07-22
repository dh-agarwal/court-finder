import cv2
import numpy as np

# Load the image
image_path = '1.png'
image = cv2.imread(image_path)
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the range of white color in HSV, adjusted for shadows
lower_white = np.array([0, 0, 100])
upper_white = np.array([180, 50, 255])

# Threshold the HSV image to get only white colors
mask = cv2.inRange(hsv, lower_white, upper_white)

# Perform morphological operations to clean up the mask
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# Find contours
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Function to filter contours based on shape and size
def is_tennis_court(cnt):
    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if 0.9 < aspect_ratio < 1.1 and 5000 < w * h < 50000:  # Adjust size thresholds as needed
            return True
    return False

# Filter contours
tennis_courts = [cnt for cnt in contours if is_tennis_court(cnt)]

# Draw detected tennis courts on the original image
for cnt in tennis_courts:
    cv2.drawContours(image, [cnt], -1, (0, 255, 0), 3)

# Show the result
cv2.imshow('Detected Tennis Courts', image)
cv2.imshow('Mask of White Areas', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
