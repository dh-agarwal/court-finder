import cv2
import numpy as np
import itertools

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

def is_similar(line1, line2, threshold=10):
    return (abs(line1[0] - line2[0]) < threshold and
            abs(line1[1] - line2[1]) < threshold and
            abs(line1[2] - line2[2]) < threshold and
            abs(line1[3] - line2[3]) < threshold)

def filter_similar_lines(lines):
    if lines is None:
        return []

    filtered_lines = []
    for line in lines:
        if not any(is_similar(line[0], other_line[0]) for other_line in filtered_lines):
            filtered_lines.append(line)

    return filtered_lines

def detect_and_filter_lines(image, min_length):
    lines = cv2.HoughLinesP(image, 1, np.pi / 180, threshold=50, minLineLength=min_length, maxLineGap=10)
    lines = filter_similar_lines(lines)
    line_image = np.zeros_like(image)
    line_count = len(lines)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(line_image, (x1, y1), (x2, y2), 255, 1)
    return lines, line_image, line_count

def group_lines_by_orientation(lines):
    vertical_lines = []
    horizontal_lines = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x1 - x2) < abs(y1 - y2):
            vertical_lines.append(line)
        else:
            horizontal_lines.append(line)

    return vertical_lines, horizontal_lines

def find_intersections(vertical_lines, horizontal_lines, image_shape):
    intersections = []
    for vline in vertical_lines:
        for hline in horizontal_lines:
            x1, y1, x2, y2 = vline[0]
            x3, y3, x4, y4 = hline[0]
            A1 = y2 - y1
            B1 = x1 - x2
            C1 = A1 * x1 + B1 * y1
            A2 = y4 - y3
            B2 = x3 - x4
            C2 = A2 * x3 + B2 * y3
            det = A1 * B2 - A2 * B1
            if det != 0:
                x = (B2 * C1 - B1 * C2) / det
                y = (A1 * C2 - A2 * C1) / det
                if 0 <= x < image_shape[1] and 0 <= y < image_shape[0]:
                    intersections.append((int(x), int(y)))
    return intersections

def is_quadrilateral(corners, tolerance=20):
    if len(corners) != 4:
        return False

    def distance(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    edges = [distance(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    diagonals = [distance(corners[i], corners[(i + 2) % 4]) for i in range(2)]

    return (abs(edges[0] - edges[2]) < tolerance and
            abs(edges[1] - edges[3]) < tolerance and
            abs(diagonals[0] - diagonals[1]) < tolerance)

def detect_tennis_court(image, bright_lines_x, bright_lines_y, image_shape):
    combined_lines = np.maximum(bright_lines_x, bright_lines_y)
    lines, filtered_lines_image, line_count = detect_and_filter_lines(combined_lines, min_length=35)
    vertical_lines, horizontal_lines = group_lines_by_orientation(lines)
    intersections = find_intersections(vertical_lines, horizontal_lines, image_shape)
    
    if len(intersections) >= 4:
        for comb in itertools.combinations(intersections, 4):
            if is_quadrilateral(comb):
                for point in comb:
                    cv2.circle(filtered_lines_image, point, 5, (0, 255, 0), -1)
                cv2.polylines(filtered_lines_image, [np.array(comb, dtype=np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
                print("Tennis court detected.")
                return filtered_lines_image, line_count, intersections
    print("No tennis court detected.")
    return filtered_lines_image, line_count, intersections

image_path = '2.png'
gray_image, image_shape = preprocess_image(image_path)
sobel_x, sobel_y, laplacian_x, laplacian_y = compute_derivatives(gray_image)

bright_lines_x = find_bright_lines(sobel_x, laplacian_x)
bright_lines_y = find_bright_lines(sobel_y, laplacian_y)

output_image, line_count, intersections = detect_tennis_court(gray_image, bright_lines_x, bright_lines_y, image_shape)

cv2.imshow('Tennis Court Detection', output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()