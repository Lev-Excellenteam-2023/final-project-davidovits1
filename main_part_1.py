import presentation_parser
import sys
import asyncio
import async_client
import json_file


PATH = "End of course exercise.pptx"
OUTPUTS_PART_1 = "outputs_part_1"


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

    slides = await async_client.async_client(text_pptx)
    json_file.create_json_file(path, OUTPUTS_PART_1, slides)

if __name__ == "__main__":
    asyncio.run(main())
