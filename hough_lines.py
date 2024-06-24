import os
import cv2
import numpy as np
from sklearn.cluster import DBSCAN

def merge_similar_lines(lines, angle_threshold=10, distance_threshold=10):
    if lines is None:
        return []
    
    line_features = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        line_features.append([angle, midpoint[0], midpoint[1], length])
    
    line_features = np.array(line_features)
    clustering = DBSCAN(eps=distance_threshold, min_samples=1).fit(line_features[:, 1:3])
    labels = clustering.labels_
    
    merged_lines = []
    for label in np.unique(labels):
        indices = np.where(labels == label)[0]
        cluster_lines = [lines[idx][0] for idx in indices]
        avg_x1 = np.mean([line[0] for line in cluster_lines])
        avg_y1 = np.mean([line[1] for line in cluster_lines])
        avg_x2 = np.mean([line[2] for line in cluster_lines])
        avg_y2 = np.mean([line[3] for line in cluster_lines])
        merged_lines.append([int(avg_x1), int(avg_y1), int(avg_x2), int(avg_y2)])
    
    return merged_lines

def extend_line(x1, y1, x2, y2, length=50):
    line_vec = np.array([x2 - x1, y2 - y1])
    line_length = np.sqrt(line_vec[0]**2 + line_vec[1]**2)
    unit_vec = line_vec / line_length
    extend_vec = unit_vec * length
    return (x1 - extend_vec[0], y1 - extend_vec[1], x2 + extend_vec[0], y2 + extend_vec[1])

def find_intersections(lines):
    def line_intersection(line1, line2):
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2
        denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if denom == 0:
            return None
        Px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
        Py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom
        if (min(x1, x2) <= Px <= max(x1, x2) and min(y1, y2) <= Py <= max(y1, y2) and
            min(x3, x4) <= Px <= max(x3, x4) and min(y3, y4) <= Py <= max(y3, y4)):
            return (int(Px), int(Py))
        return None
    
    extended_lines = [extend_line(*line) for line in lines]
    intersections = []
    for i, line1 in enumerate(extended_lines):
        for line2 in extended_lines[i+1:]:
            intersect_point = line_intersection(line1, line2)
            if intersect_point:
                intersections.append(intersect_point)
    return intersections

def remove_short_lines(lines, min_length):
    filtered_lines = [line for line in lines if np.sqrt((line[2] - line[0])**2 + (line[3] - line[1])**2) >= min_length]
    return filtered_lines

def merge_close_intersections(intersections, distance_threshold=10):
    if not intersections:
        return []

    points = np.array(intersections)
    clustering = DBSCAN(eps=distance_threshold, min_samples=1).fit(points)
    labels = clustering.labels_

    merged_intersections = []
    for label in np.unique(labels):
        cluster_points = points[labels == label]
        avg_x = np.mean(cluster_points[:, 0])
        avg_y = np.mean(cluster_points[:, 1])
        merged_intersections.append((int(avg_x), int(avg_y)))

    return merged_intersections

def find_tennis_courts(intersections, ratio_tolerance=0.1):
    distances = {
        'doubles_ally': 4.5,
        'service_box_width': 13.5,
        'baseline_to_service_line': 18,
        'court_width': 27
    }

    def distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def is_tennis_court(points):
        points = sorted(points, key=lambda p: (p[0], p[1]))
        base_line_points = [points[0], points[1], points[2]]
        service_line_points = [points[3], points[4], points[5]]
        
        ratios = [
            (distance(base_line_points[0], base_line_points[1]) / distances['doubles_ally']),
            (distance(base_line_points[1], base_line_points[2]) / distances['court_width']),
            (distance(service_line_points[0], service_line_points[1]) / distances['doubles_ally']),
            (distance(service_line_points[1], service_line_points[2]) / distances['court_width']),
            (distance(base_line_points[0], service_line_points[0]) / distances['baseline_to_service_line']),
            (distance(base_line_points[1], service_line_points[1]) / distances['baseline_to_service_line']),
            (distance(base_line_points[2], service_line_points[2]) / distances['baseline_to_service_line']),
        ]
        
        for ratio in ratios:
            if not (1 - ratio_tolerance <= ratio <= 1 + ratio_tolerance):
                return False
        
        return True

    tennis_courts = []
    for i, point in enumerate(intersections):
        candidate_points = [point]
        for other_point in intersections:
            if point != other_point and distance(point, other_point) <= ratio_tolerance * max(distances.values()):
                candidate_points.append(other_point)
        if len(candidate_points) >= 6 and is_tennis_court(candidate_points):
            tennis_courts.append(candidate_points)
    
    return tennis_courts

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        print(f"Mouse position: ({x}, {y})")

# Load the image
image_path = '1.png'
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Apply Canny edge detection
edges = cv2.Canny(blur, 50, 150, apertureSize=3)

# Apply Hough Line Transform to detect lines
lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

# Merge similar lines
merged_lines = merge_similar_lines(lines)

# Remove lines smaller than a certain length
min_length = 75
filtered_lines = remove_short_lines(merged_lines, min_length)

# Find intersections
intersections = find_intersections(filtered_lines)

# Merge close intersections
unique_intersections = merge_close_intersections(intersections)

# Find tennis courts
tennis_courts = find_tennis_courts(unique_intersections)

if tennis_courts:
    print("Tennis court(s) found.")
else:
    print("No tennis court found.")

# Create copies of the images to draw intersections and lines
output_image_normal = image.copy()
output_image_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

# Draw the filtered lines
for line in filtered_lines:
    x1, y1, x2, y2 = line
    cv2.line(output_image_normal, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines
    cv2.line(output_image_edges, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines

# Draw dots at intersections
for point in unique_intersections:
    cv2.circle(output_image_normal, point, 5, (0, 0, 255), -1)  # Red dots
    cv2.circle(output_image_edges, point, 5, (0, 0, 255), -1)  # Red dots

# Draw rectangles around detected tennis courts
for court in tennis_courts:
    court = np.array(court)
    min_x, min_y = np.min(court, axis=0)
    max_x, max_y = np.max(court, axis=0)
    cv2.rectangle(output_image_normal, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)  # Blue rectangle

# Function to toggle between images
def toggle_image():
    global show_edges
    show_edges = not show_edges

# Set the initial state
show_edges = False

cv2.namedWindow('Image')
cv2.setMouseCallback('Image', mouse_callback)

while True:
    # Display the appropriate image based on the state
    if show_edges:
        cv2.imshow('Image', output_image_edges)
    else:
        cv2.imshow('Image', output_image_normal)
    
    # Wait for a key press
    key = cv2.waitKey(1) & 0xFF
    
    # Toggle the image if 't' is pressed
    if key == ord('t'):
        toggle_image()
    
    # Break the loop if 'q' is pressed
    if key == ord('q'):
        break

cv2.destroyAllWindows()
