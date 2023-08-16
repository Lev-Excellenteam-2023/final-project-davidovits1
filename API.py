from flask import Flask, request, render_template
import os
import uuid


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pptx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
        filename = uid + '.pptx'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return f"File uploaded successfully. UID: {uid}"

    return "Invalid file format", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
