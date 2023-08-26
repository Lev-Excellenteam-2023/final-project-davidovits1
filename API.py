from flask import Flask, request, render_template, jsonify
import os
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from datetime import datetime
from flask_migrate import Migrate



app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pptx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'  # Using SQLite for simplicity
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    uploads = db.relationship('Upload', back_populates='user')


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='uploads')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("upload.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    email = request.form.get('email')  # Get email from POST parameter

    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        uid = str(uuid.uuid4())

        # Save the upload to the database
        upload = Upload(uid=uid)  # Create an Upload object with uid
        if email:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email)
            upload.user = user

        db.session.add(upload)  # Add the upload object to the session
        db.session.commit()  # Commit the changes to the database

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{uid}.pptx"))
        return f"File uploaded successfully. UID: {uid}"
    return "Invalid file format", 400


@app.route('/status', methods=['GET'])
def get_upload_status():
    uid = request.args.get('uid')
    filename = request.args.get('filename')
    email = request.args.get('email')

    if uid:
        upload = Upload.query.filter_by(uid=uid).first()
    elif filename and email:
        user = User.query.filter_by(email=email).first()
        if user:
            upload = Upload.query.filter_by(uid=filename, user_id=user.id).order_by(
                Upload.created_at.desc()).first()
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Invalid parameters'}), 400

    if upload:
        response = {
            'uid': upload.uid,
            'status': upload.status,  # You can fetch status from your upload object
            'finished_at': upload.finished_at,  # Similarly, fetch other data from the object
            # Add more data as needed
        }
        return jsonify(response)
    else:
        return jsonify({'error': 'Upload not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)