import os
from flask import Flask, request, render_template, redirect, url_for
import db_model
import json_file

app = Flask(__name__)

OUTPUT_FOLDER = 'outputs'


@app.route('/')
def default():
    """
    Render the default page.

    Returns:
        str: The rendered HTML content for the default page.

    This route renders the default page, which provides a user interface for file upload and other actions.
    """
    return render_template("upload.html")


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    """
    Handle file upload and save it to the database.

    Returns:
        str: A message indicating the result of the upload.

    This route handles both GET and POST requests. For GET requests, it renders the upload page.
    For POST requests, it processes the uploaded file, associates it with a user (if provided),
    saves the upload to the database, and returns a message indicating the success or failure of the upload.
    """

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
    """
    Get the status and data of an uploaded file by UID.

    Args:
        uid (str): The unique identifier of the uploaded file.

    Returns:
        Response: A Flask Response containing the status and data of the uploaded file.

    This route retrieves the status and data of an uploaded file based on its unique identifier (UID).
    If the file's status is "done," it fetches additional data from a JSON file and returns a formatted JSON response.
    Otherwise, it returns a simplified JSON response with basic information about the upload.
    """
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
    """
    Search for an uploaded file by UID, email, and filename.

    Returns:
        str or Response: A message or redirect based on the search result.

    This route handles both GET and POST requests. For GET requests, it renders the search page.
    For POST requests, it processes the search parameters (UID, email, filename), performs the search,
    and either redirects to the status page or returns an error message.
    """
    if request.method == 'POST':
        uid = request.form.get('uid')
        email = request.form.get('email')
        filename = request.form.get('filename')
        if uid:
            return redirect(url_for('get_status', uid=uid))
        elif filename:
            if email:
                is_exist, data = db_model.search_user_by_email_and_filename(email, filename)
                if is_exist:
                    return redirect(url_for('get_status', uid=data))
                else:
                    return data, 404
            else:
                return "Please enter email also", 404

        elif email:
            return db_model.get_uploads_by_email(email), 200
        else:
            return "No UID or email or file name and email was entered", 404
    return render_template("search.html")


@app.route('/delete', methods=['POST', 'GET'])
def delete_user():
    """
    Delete a user by email (and deletes all uploads that the user has uploaded).

    Returns:
        str: A message indicating the result of the user deletion.

    This route handles both GET and POST requests. For GET requests, it renders the delete page.
    For POST requests, it processes the provided email, deletes the user if found in the database,
    and returns a message indicating the success or failure of the deletion.
    """
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
