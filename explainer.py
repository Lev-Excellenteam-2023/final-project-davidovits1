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







# async def process_uploads():
#     """
#     Processes pending uploads from the database.
#     """
#     while True:
#         with Session() as session:
#             upload_files = session.query(Upload).filter_by(status=UploadStatus.pending).all()
#             for upload_file in upload_files:
#                 try:
#                     _, file_type = os.path.splitext(upload_file.filename)
#                     process_file(f"{upload_file.uid}{file_type}")
#                     upload_file.finish_time = datetime.now()
#                     upload_file.status = UploadStatus.done
#                     session.commit()
#                 except KeyError:
#                     continue
#         await asyncio.sleep(10)
#
#
#         pending_uploads = Upload.query.filter_by(status='pending').all()
#
#         for upload in pending_uploads:
#             file_path = os.path.join(UPLOAD_FOLDER, upload.filename)
#             list_presentation = presentation_parser.extract_text(file_path)
#
#             # Process the presentation and update status in the database
#             try:
#                 slides = await async_client.async_client(list_presentation)
#                 upload.status = 'processed'
#                 upload.finish_time = datetime.now()
#             except Exception as e:
#                 upload.status = 'error'
#                 upload.finish_time = datetime.now()
#
#             # Save the JSON output and update Outputs table
#             json_file.create_json_file(upload.uid, OUTPUT_FOLDER, slides)
#             db.session.add(uid=upload.uid, filename=f"{upload.uid}.json")
#
#             db.session.commit()
#
#         await asyncio.sleep(10)
#
#
# if __name__ == '__main__':
#     asyncio.run(process_uploads())
