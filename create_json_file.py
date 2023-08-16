import json

def create_json_file(output_path: str, data: any) -> None:
    """
    Create json file

    :param output_path: The path of the file to be created
    :param data: Data for a json file
    :return:
    """
    try:
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"An error occurred: {e}")