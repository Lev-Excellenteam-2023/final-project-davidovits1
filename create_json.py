import json
import os


def create_json_file(path: str, output_folder: str,  data: any) -> None:
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
