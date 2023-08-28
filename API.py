import os

from flask import Flask, request, render_template, flash, redirect
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


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("upload.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files.get('file')
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        email = request.form.get('email')
        if email:
            uid = db_model.save_upload_with_user(file, email)
        else:
            uid = db_model.save_upload(file)
        return f"File uploaded successfully. UID: {uid}", 200
    return "Invalid file format", 400


@app.route('/status/<uid>', methods=['GET'])
def get_upload_status(uid):
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


if __name__ == '__main__':
    db_model.set_path()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db_model.create_all()
    app.run(host='0.0.0.0', port=5000)