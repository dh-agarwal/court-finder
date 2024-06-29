import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import itertools

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

def find_tennis_courts(intersections, ratio_tolerance=0.2):
    expected_distances = {
        'doubles_alley_width': 25.50,
        'service_box_width': 74.22,
        'baseline_to_service_line': 101.39,
        'court_width': 150.15,
        'service_outer_alley_width': 25.50,
        'service_line_to_middle': 76.66
    }

    def distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def is_within_tolerance(actual, expected, tolerance):
        return expected * (1 - tolerance) <= actual <= expected * (1 + tolerance)

    def is_tennis_court(points):
        if len(points) != 9:
            return False
        
        # Check all permutations of the points to avoid missing correct pairs
        for perm in itertools.permutations(points):
            points = np.array(perm)
            
            d1 = distance(points[0], points[1])
            d2 = distance(points[1], points[2])
            d3 = distance(points[3], points[4])
            d4 = distance(points[4], points[5])
            d5 = distance(points[0], points[3])
            d6 = distance(points[1], points[4])
            d7 = distance(points[2], points[5])
            d8 = distance(points[0], points[6])
            d9 = distance(points[1], points[7])
            d10 = distance(points[2], points[8])

            if (is_within_tolerance(d1, expected_distances['doubles_alley_width'], ratio_tolerance) and
                is_within_tolerance(d2, expected_distances['court_width'], ratio_tolerance) and
                is_within_tolerance(d3, expected_distances['doubles_alley_width'], ratio_tolerance) and
                is_within_tolerance(d4, expected_distances['court_width'], ratio_tolerance) and
                is_within_tolerance(d5, expected_distances['baseline_to_service_line'], ratio_tolerance) and
                is_within_tolerance(d6, expected_distances['baseline_to_service_line'], ratio_tolerance) and
                is_within_tolerance(d7, expected_distances['baseline_to_service_line'], ratio_tolerance) and
                is_within_tolerance(d8, expected_distances['baseline_to_service_line'], ratio_tolerance) and
                is_within_tolerance(d9, expected_distances['baseline_to_service_line'], ratio_tolerance) and
                is_within_tolerance(d10, expected_distances['baseline_to_service_line'], ratio_tolerance)):
                return True

        return False

    tennis_courts = []
    for subset in itertools.combinations(intersections, 9):
        if is_tennis_court(subset):
            tennis_courts.append(subset)
    
    return tennis_courts

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        print(f"Mouse position: ({x}, {y})")

# Load the image
image_path = 'half.png'
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
print(unique_intersections)

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
