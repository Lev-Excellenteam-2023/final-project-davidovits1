import httpx

import presentation_parser
import openAI_request
import json
import sys
import asyncio


PATH = "End of course exercise.pptx"


async def process_slide(index, text_pptx, session):
    """
    Process a slide asynchronously to generate its explanation.

    Args:
        index (int): The index of the slide being processed.
        text_pptx (list): The list of slide text content.
        session: The HTTP session for asynchronous requests.

    Returns:
        dict: A dictionary containing slide information and its generated explanation.
    """
    slide_text = text_pptx[index]
    explanation = await openAI_request.generate_explanation_async(session, slide_text)

    return {
        "slide_num": index + 1,
        "slide_from_pptx": slide_text,
        "explanation_from_chat": explanation,
    }

# def make_slides_for_json(data_dict: dict, text_pptx: list) -> list:
#     """
#     Preparing slides for a json file
#     :param data_dict: a dictionary where the key is the number of the presentation
#      and the value is the explanation of the chat
#     :param text_pptx: a list that holds the content of the presentations
#     :return: slides for json file
#     """
#     slides = []
#     for key in data_dict:
#         explanation_from_chat = data_dict[key]
#         slide_from_pptx = text_pptx[key - 1]
#
#         slide = {
#             "slide_num": key,
#             "slide_from_pptx": slide_from_pptx,
#             "explanation_from_chat": explanation_from_chat,
#         }
#
#         slides.append(slide)
#
#     return slides


async def main():
    # Optionally put a presentation in argv
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = PATH
    text_pptx = presentation_parser.extract_text(path)

    if text_pptx == [""]:
        # Error loading the presentation
        return
    print(text_pptx)

    async with httpx.AsyncClient() as client:
        tasks = [process_slide(i, text_pptx, client) for i in range(len(text_pptx))]
        slides = await asyncio.gather(*tasks)

    # data_dict = {}
    # for i in range(len(text_pptx)):
    #     data_dict[i + 1] = openAI_request.generate_explanation(text_pptx[i])
    #
    # slides = make_slides_for_json(data_dict, text_pptx)

    path = path.replace(".pptx", ".json")
    try:
        with open(path, 'w') as json_file:
            json.dump(slides, json_file, indent=4)
    except Exception as e:
        print(f"An error occurred: {e}")
    # print(data_dict)


if __name__ == "__main__":
    asyncio.run(main())
