from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import pandas as pd
import uuid
import requests
import json

api_key = "EvFviXpe7Pz7XkS3laruCpqNIIv0Vhfo"
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variables to store current filenames
current_excel_filename = None
current_image_filename = None

def delete_file(filename):
    if filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    global current_excel_filename, current_image_filename
    excel_data = None

    if request.method == 'POST':
        if 'excel_file' in request.files:
            excel_file = request.files['excel_file']
            if excel_file.filename != '':
                delete_file(current_excel_filename)
                current_excel_filename = str(uuid.uuid4()) + os.path.splitext(excel_file.filename)[1]
                excel_path = os.path.join(app.config['UPLOAD_FOLDER'], current_excel_filename)
                excel_file.save(excel_path)
                df = pd.read_excel(excel_path)
                excel_data = df.to_html(classes='table table-striped', index=False)

        if 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file.filename != '':
                delete_file(current_image_filename)
                current_image_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], current_image_filename)
                image_file.save(image_path)

    if excel_data is None and current_excel_filename:
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], current_excel_filename)
        df = pd.read_excel(excel_path)
        excel_data = df.to_html(classes='table table-striped', index=False)

    return render_template('upload.html', excel_data=excel_data, image_filename=current_image_filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(app.config['UPLOAD_FOLDER'], filename)
    root_dir = os.path.dirname(os.getcwd())
    print(os.path.join(root_dir, 'Microsoft-Azure-Project', app.config['UPLOAD_FOLDER']))
    return send_from_directory(os.path.join(root_dir, 'Microsoft-Azure-Project', app.config['UPLOAD_FOLDER']), filename)

@app.route('/predict_image', methods=['POST'])
def predict_image():
    if current_image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], current_image_filename)
        url = 'http://127.0.0.1/image'
        files = {'imageData': open(image_path, 'rb')}
        response = requests.post(url, files=files)
        return jsonify(response.json())
    return jsonify({'error': 'No image uploaded'})

@app.route('/predict_excel', methods=['POST'])
def predict_excel():
    data = request.json
    url = "http://38a0394d-1866-41df-89a4-f7c5313bd973.westeurope.azurecontainer.io/score"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Template for the input data
    input_template = {
        "radius_mean": None, "texture_mean": None, "perimeter_mean": None,
        "area_mean": None, "smoothness_mean": None, "compactness_mean": None,
        "concavity_mean": None, "concave points_mean": None, "symmetry_mean": None,
        "fractal_dimension_mean": None, "radius_se": None, "texture_se": None,
        "perimeter_se": None, "area_se": None, "smoothness_se": None,
        "compactness_se": None, "concavity_se": None, "concave points_se": None,
        "symmetry_se": None, "fractal_dimension_se": None, "radius_worst": None,
        "texture_worst": None, "perimeter_worst": None, "area_worst": None,
        "smoothness_worst": None, "compactness_worst": None, "concavity_worst": None,
        "concave points_worst": None, "symmetry_worst": None, "fractal_dimension_worst": None
    }
    
    # Fill the template with data from the request
    for key, value in data.items():
        if key in input_template:
            try:
                input_template[key] = float(value) if value not in (None, '') else None
            except ValueError:
                return jsonify({'error': f'Invalid value for {key}: {value}'}), 400
    
    # Check if all required fields are filled
    if any(value is None for value in input_template.values()):
        return jsonify({'error': 'Missing required fields'}), 400
    
    payload = {
        "Inputs": {
            "input1": [input_template]
        },
        "GlobalParameters": {}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)