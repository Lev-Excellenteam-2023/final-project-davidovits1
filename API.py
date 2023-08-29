import os
from flask import Flask, request, render_template, redirect, url_for
import db_model
import json_file

app = Flask(__name__)

OUTPUT_FOLDER = 'outputs'


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
    file_data = db_model.get_upload_from_db(uid)
    if file_data:
        if file_data.status == db_model.UploadStatus.done:
            output_path = os.path.join(OUTPUT_FOLDER, f"{uid}.json")
            data = json_file.read_from_json(output_path)
            output_data = json_file.save_to_json(uid, file_data.filename, file_data.upload_time, file_data.status,
                                                 file_data.finish_time, data)
        else:
            output_data = json_file.save_to_json(uid, file_data.filename, file_data.upload_time, file_data.status)
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
            is_exist, data = db_model.search_user_by_email_and_filename(email, filename)
            if is_exist:
                return redirect(url_for('get_status', uid=data))
            else:
                return data, 404
            # with Session() as session:
            #     user = session.query(db_model.User).filter_by(email=email).first()
            #     if user:
            #         latest_upload = session.query(db_model.Upload).filter_by(user=user, filename=filename).order_by(
            #             db_model.Upload.upload_time.desc()).first()
            #         if latest_upload:
            #             return redirect(url_for('get_status', uid=latest_upload.uid))
            #         else:
            #             return "Filename not found", 404
            #     else:
            #         return f"Email: {email} does not exist", 404
        else:
            return "Please enter a UID, or provide both email and filename", 404
    return render_template("search.html")


@app.route('/delete', methods=['POST', 'GET'])
def delete_user():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            if db_model.delete_user_by_email(email):
                return f"User with email {email} has been deleted.", 200
            else:
                return f"User with email {email} not found.", 404
        else:
            return "You need to enter an email", 404
    return render_template("delete.html")


if __name__ == '__main__':
    db_model.set_path()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db_model.create_all()

    app.run(host='0.0.0.0', port=5000)
