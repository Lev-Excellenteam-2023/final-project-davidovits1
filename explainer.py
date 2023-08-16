import os
import asyncio
import async_client
import create_json
import presentation_parser

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'


async def process_files():
    while True:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.pptx'):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                list_presentation = presentation_parser.extract_text(file_path)
                if list_presentation == [""]:
                    # Error loading the presentation
                    os.remove(file_path)
                    break

                slides = await async_client.async_client(list_presentation)

                # Save the output JSON
                create_json.create_json_file(file_path, OUTPUT_FOLDER, slides)

                # Remove the processed file from uploads
                os.remove(file_path)
                print(file_path + " removed")

        # Wait for some time before checking again
        await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(process_files())
