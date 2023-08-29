import os

from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import db_model
import json_file

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pptx'}


# Create the engine
engine = create_engine('sqlite:///db/db.sqlite3')

# Create a scoped session to manage sessions for each request
Session = scoped_session(sessionmaker(bind=engine))

# Base class for the models
Base = declarative_base()


@app.route('/')
def index():
    return render_template("upload.html")


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if file.filename == '':
            return "No selected file", 404
        if not file.filename.endswith("pptx"):
            return "Invalid file type", 404
        email = request.form.get('email')
        if email:
            uid = db_model.save_upload_with_user(file, email)
        else:
            uid = db_model.save_upload(file)
        return f"File uploaded successfully. UID: {uid}", 200
    return render_template("upload.html")


@app.route('/status/<uid>', methods=['GET'])
def get_status(uid):
    with Session() as session:
        file_data = session.query(db_model.Upload).filter_by(uid=uid).first()
        if file_data:
            if file_data.status == db_model.UploadStatus.done:
                output_path = os.path.join(OUTPUT_FOLDER, f"{uid}.json")
                data = json_file.read_from_json(output_path)
                output_data = json_file.save_to_json(uid, file_data.status, file_data.filename,
                                                     file_data.finish_time, data)
            else:
                output_data = json_file.save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time)
            response = json_file.sort_json_to_send(output_data)
            return response
    return "status: not_found", 404


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        uid = request.form.get('uid')
        email = request.form.get('email')
        filename = request.form.get('filename')
        if uid:
            return redirect(url_for('get_status', uid=uid))
        elif email and filename:  # Only search if both email and filename are provided
            with Session() as session:
                user = session.query(db_model.User).filter_by(email=email).first()
                if user:
                    latest_upload = session.query(db_model.Upload).filter_by(user=user, filename=filename).order_by(
                        db_model.Upload.upload_time.desc()).first()
                    if latest_upload:
                        return redirect(url_for('get_status', uid=latest_upload.uid))
                    else:
                        return "Filename not found", 404
                else:
                    return f"Email: {email} does not exist", 404
        else:
            return "Please enter a UID, or provide both email and filename", 404
    return render_template("search.html")


if __name__ == '__main__':
    db_model.set_path()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db_model.create_all()
    app.run(host='0.0.0.0', port=5000)