import presentation_parser
import openAI_request
import json
import sys
import os
from dotenv import load_dotenv

PATH = "End of course exercise.pptx"


def main(argv=None):
    load_dotenv()
    # Optionally put a presentation in argv
    print(sys.argv)
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = PATH

    text_pptx = presentation_parser.extract_text(path)
    if text_pptx == [""]:
        # Error loading the presentation
        return
    print(text_pptx)

    data_dict = {}
    for i in range(len(text_pptx)):
        data_dict[i + 1] = openAI_request.generate_explanation(text_pptx[i])

    slides = make_slides_for_json(data_dict, text_pptx)

    path = path.replace(".pptx", ".json")
    try:
        with open(path, 'w') as json_file:
            json.dump(slides, json_file, indent=4)
    except Exception as e:
        print(f"An error occurred: {e}")
    print(data_dict)


if __name__ == "__main__":
    main()


def make_slides_for_json(data_dict: dict, text_pptx: list) -> list:
    """
    Preparing slides for a json file
    :param data_dict: a dictionary where the key is the number of the presentation
     and the value is the explanation of the chat
    :param text_pptx: a list that holds the content of the presentations
    :return: slides for json file
    """
    slides = []
    for key in data_dict:
        explanation_from_chat = data_dict[key]
        slide_from_pptx = text_pptx[key - 1]

        slide = {
            "slide_num": key,
            "slide_from_pptx": slide_from_pptx,
            "explanation_from_chat": explanation_from_chat,
        }

        slides.append(slide)

    return slides
