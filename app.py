import os
import glob
import svgwrite
import math
from flask import Flask, render_template, request
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def cluster_dots(coords, distance_threshold=40):
    """Groups nearby coordinates into clusters and finds the center of each cluster."""
    clusters = []
    for (x, y) in coords:
        found_cluster = False
        for cluster in clusters:
            # Check distance to the cluster's representative point
            if math.dist((x, y), cluster[0]) < distance_threshold:
                cluster.append((x, y))
                found_cluster = True
                break
        if not found_cluster:
            clusters.append([(x, y)])
    
    # Calculate the centroid (average point) for each cluster
    final_dots = []
    for cluster in clusters:
        x_coords = [p[0] for p in cluster]
        y_coords = [p[1] for p in cluster]
        centroid_x = int(np.mean(x_coords))
        centroid_y = int(np.mean(y_coords))
        final_dots.append((centroid_x, centroid_y))
        
    return final_dots

def create_recreation_svg(processed_image, dots, output_filename):
    """Creates an animated SVG of the Kolam recreation."""
    contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    height, width = processed_image.shape
    output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    dwg = svgwrite.Drawing(output_filepath, profile='full', size=(width, height))

    for (x, y) in dots:
        dwg.add(dwg.circle(center=(x, y), r=5, fill='black'))

    path_group = dwg.g(stroke='black', stroke_width=4, fill='none')
    total_length = 0

    for contour in contours:
        if cv2.contourArea(contour) > 100:
            path_data = "M" + " L".join(f"{p[0][0]},{p[0][1]}" for p in contour) + " Z"
            path = dwg.path(d=path_data)
            path_group.add(path)
            total_length += cv2.arcLength(contour, closed=True)

    animation_style = f"""
        .path-animation {{
            stroke-dasharray: {total_length};
            stroke-dashoffset: {total_length};
            animation: draw 10s linear forwards;
        }}
        @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    """
    dwg.defs.add(dwg.style(animation_style))
    path_group['class'] = 'path-animation'
    dwg.add(path_group)
    dwg.save()
    return output_filename

def analyze_kolam(filepath):
    """Final analyzer with clustering to get accurate dot counts."""
    image = cv2.imread(filepath)
    if image is None: return {'error': 'Could not read image.'}
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((7,7), np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    erode_kernel = np.ones((3,3), np.uint8)
    erosion = cv2.erode(closing, erode_kernel, iterations=2)
    
    diag_filename = 'diag_' + os.path.basename(filepath)
    diag_filepath = os.path.join(app.config['UPLOAD_FOLDER'], diag_filename)
    cv2.imwrite(diag_filepath, erosion)

    contours, _ = cv2.findContours(erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # First, find all potential dot fragments
    raw_dot_coords = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10 < area < 10000:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                raw_dot_coords.append((cX, cY))
    
    # NEW: Cluster the fragments to find the true dots
    final_dots = cluster_dots(raw_dot_coords)

    # Generate debug image with the final, clustered dots
    output_image_with_circles = image.copy()
    for (cX, cY) in final_dots:
        cv2.circle(output_image_with_circles, (cX, cY), 20, (0, 255, 0), 3)

    debug_filename = 'debug_' + os.path.basename(filepath)
    debug_filepath = os.path.join(app.config['UPLOAD_FOLDER'], debug_filename)
    cv2.imwrite(debug_filepath, output_image_with_circles)

    recreation_filename = None
    if final_dots:
        recreation_filename = 'recreation_' + os.path.basename(filepath).replace('.png', '.svg').replace('.jpg', '.svg')
        create_recreation_svg(closing, final_dots, recreation_filename)
    
    return {
        'dot_count': len(final_dots),
        'recreation_filename': recreation_filename,
        'diag_filename': diag_filename,
        'debug_filename': debug_filename
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_and_analyze():
    if 'kolam-image' not in request.files: return "No file part"
    file = request.files['kolam-image']
    if file.filename == '': return "No selected file"
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        analysis_result = analyze_kolam(filepath)
        return render_template('index.html', result=analysis_result)

if __name__ == '__main__':
    app.run(debug=True)
