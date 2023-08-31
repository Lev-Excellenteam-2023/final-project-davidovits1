import json
import os
from datetime import datetime
from flask import Response
from typing_extensions import Union


def create_json_file(path: str, output_folder: str, data: any) -> None:
    """
    Create json file

    :param output_folder: The folder for file
    :param path: The path of the file to be created
    :param data: Data for a json file
    :return:
    """
    output_path = crate_path_to_json(path, output_folder)
    try:
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"An error occurred: {e}")


def crate_path_to_json(path: str, output_folder: str) -> str:
    """
    Creates a folder (if it doesn't exist) and changes the file name to json
    :param output_folder: The folder for file
    :param path: The path of the file to be created
    :return: output_path
    """
    filename = os.path.basename(path)
    filename_json = filename.replace(".pptx", ".json")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, filename_json)

    return output_path


def read_from_json(output_path: str) -> list:
    """
    This function reads data from a JSON file located at the given
     output_path and returns the parsed data as a Python list.

    Parameters:

    output_path (str): The path to the JSON file to be read.
    Returns:

    output_data (list): The parsed data from the JSON file.

    """
    with open(output_path, 'r') as json_file:
        output_data = json.load(json_file)
    return output_data


def sort_json_to_send(output_data: Union[list, dict]) -> Response:
    """
    This function takes a list of data, sorts it, and creates a Flask Response object containing the sorted JSON data.

    Parameters:

    output_data (list or dict): The JSON data to be sorted and formatted.
    Returns:

    response (Response): A Flask Response object containing sorted JSON data.
    """
    response = Response(
        json.dumps(output_data, indent=4, sort_keys=False),
        content_type='application/json'
    )
    return response


def save_to_json(uid: str, name: str, start_time: datetime, upload_status: str,
                 finish_time: datetime = None, explanation: any = None) -> dict:
    """
    Creates a dictionary representing the data to be saved as JSON.

    Args:
        uid (str): The unique identifier for the data.
        name (str): The filename associated with the data.
        start_time (datatime) The time when the file was uploaded
        upload_status (str): The status of the upload process.
        finish_time (datetime, optional): The time when the upload process finished.
        explanation (optional): Additional explanation or notes about the data.

    Returns:
        dict: A dictionary containing the data to be saved as JSON.

    Example:
        data = save_to_json('12345', 'success', 'example.txt', datetime.now(), 'Upload completed without errors.')
    """
    temp_dict = {
        'uid': uid,
        'filename': name,
        'start_time': str(start_time),
        'status': upload_status,
    }
    if finish_time:
        temp_dict['finish time'] = str(finish_time)
    if explanation:
        temp_dict['explanation'] = explanation
    return temp_dict
