from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg'}

def handle_upload(file):
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    previous_file = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    if os.path.exists(previous_file):
        os.remove(previous_file)
    
    file.save(previous_file)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            handle_upload(file)
            return redirect(url_for('upload_file'))
        
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    image_exists = os.path.exists(full_filename)
    return render_template('upload.html', user_image='uploads/uploaded_image.jpg' if image_exists else None)

@app.route('/image', methods=['POST'])
def analyze_image():
    # Simulate image analysis result
    result = {
        "created": datetime.now().isoformat(),
        "id": "",
        "iteration": "",
        "predictions": [
            {"boundingBox": None, "probability": 0.99487996, "tagId": "", "tagName": "Benign"},
            {"boundingBox": None, "probability": 0.00025697, "tagId": "", "tagName": "InSitu"},
            {"boundingBox": None, "probability": 0.0009369, "tagId": "", "tagName": "Invasive"},
            {"boundingBox": None, "probability": 0.00392611, "tagId": "", "tagName": "Normal"}
        ],
        "project": ""
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
