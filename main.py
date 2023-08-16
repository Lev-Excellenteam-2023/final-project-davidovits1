import httpx
import presentation_parser
import process_slide
import json
import sys
import asyncio


PATH = "End of course exercise.pptx"


def create_json_file(name_of_file: str, data: any) -> None:
    """
    Create json file

    :param name_of_file: The name of the file to be created
    :param data: Data for a json file
    :return:
    """
    try:
        with open(name_of_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"An error occurred: {e}")


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
        tasks = [process_slide.process_slide(i, text_pptx, client) for i in range(len(text_pptx))]
        slides = await asyncio.gather(*tasks)

    name_of_file = path.replace(".pptx", ".json")
    create_json_file(name_of_file, slides)

if __name__ == "__main__":
    asyncio.run(main())
