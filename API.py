from flask import Flask, request, render_template, jsonify
import os
import uuid
import json_file
from datetime import datetime


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pptx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("upload.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        uid = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        original_filename = os.path.splitext(file.filename)[0]
        new_filename = f"{original_filename}_{timestamp}_{uid}.pptx"

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        return f"File uploaded successfully. New filename: {file.filename}, UID: {uid}"
    return "Invalid file format", 400


@app.route('/status/<uid>', methods=['GET'])
def check_status(uid):
    # Check if the UID exists in uploads or outputs folder
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uid}.pptx")
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{uid}.json")

    if os.path.exists(output_path):
        # If output JSON exists, return its contents
        output_data = json_file.read_from_json(output_path)
        response = json_file.sort_json_to_send(output_data)
        return response
    elif os.path.exists(upload_path):
        # If UID exists in uploads but not yet processed, return processing status
        return jsonify({"status": "processing"})
    else:
        # If UID doesn't exist, return appropriate response
        return jsonify({"status": "not_found"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
