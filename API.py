from flask import Flask, request, render_template, jsonify, flash, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import db_model

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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/status/<uid>/<filename>/<email>', methods=['GET'])
def get_upload_status(uid, filename, email):
    #uid = request.args.get('uid')
    # filename = request.args.get('filename')
    # email = request.args.get('email')

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
            'status': upload.status,
            'finished_at': upload.finished_at,
        }
        return jsonify(response)
    else:
        return jsonify({'error': 'Upload not found'}), 404


if __name__ == '__main__':
    db_model.set_path()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db_model.create_all()
    app.run(host='0.0.0.0', port=5000)