import cv2
import numpy as np
import os

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray, image.shape

def compute_derivatives(gray_image):
    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
    laplacian_x = cv2.Sobel(sobel_x, cv2.CV_64F, 1, 0, ksize=3)
    laplacian_y = cv2.Sobel(sobel_y, cv2.CV_64F, 0, 1, ksize=3)
    return sobel_x, sobel_y, laplacian_x, laplacian_y

def find_bright_lines(sobel, laplacian):
    bright_lines = (sobel > 50) & (laplacian < -50)
    return bright_lines.astype(np.uint8) * 255

def detect_and_draw_lines(image, min_length):
    lines = cv2.HoughLinesP(image, 1, np.pi / 180, threshold=50, minLineLength=min_length, maxLineGap=10)
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), 255, 1)
    return line_image

input_folder = 'tennis_court_images'
output_folder = 'filtered_tennis_court_images'
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith('.png') or filename.endswith('.jpg'):
        image_path = os.path.join(input_folder, filename)
        gray_image, image_shape = preprocess_image(image_path)
        sobel_x, sobel_y, laplacian_x, laplacian_y = compute_derivatives(gray_image)
        
        bright_lines_x = find_bright_lines(sobel_x, laplacian_x)
        bright_lines_y = find_bright_lines(sobel_y, laplacian_y)
        
        combined_lines = np.maximum(bright_lines_x, bright_lines_y)
        filtered_lines_image = detect_and_draw_lines(combined_lines, min_length=35)
        
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, filtered_lines_image)
        print(f"Processed and saved: {output_path}")
