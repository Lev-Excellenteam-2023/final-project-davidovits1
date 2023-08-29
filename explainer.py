import os
import asyncio
from datetime import datetime
from db_model import Session, Upload, UploadStatus
import async_client
import json_file
import presentation_parser

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'


async def process_files():
    while True:
        with Session() as session:
            upload_files = session.query(Upload).filter_by(status=UploadStatus.pending).all()
            for upload_file in upload_files:
                try:
                    _, file_type = os.path.splitext(upload_file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, f"{upload_file.uid}{file_type}")
                    list_presentation = presentation_parser.extract_text(file_path)
                    if list_presentation == [""]:
                        # Error loading the presentation
                        os.remove(file_path)
                        continue

                    slides = await async_client.async_client(list_presentation)

                    # Save the output JSON
                    json_file.create_json_file(file_path, OUTPUT_FOLDER, slides)

                    # Remove the processed file from uploads
                    os.remove(file_path)
                    print(file_path + " removed")

                    upload_file.finish_time = datetime.now()
                    upload_file.status = UploadStatus.done
                    session.commit()
                except KeyError:
                    continue

        await asyncio.sleep(10)


# Run the asyncio event loop
async def main():
    await asyncio.gather(process_files())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
