import os
import asyncio
from datetime import datetime

import async_client
import json_file
import presentation_parser
from API import db, Upload

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'


async def process_uploads():
    """
    Processes pending uploads from the database.
    """
    while True:
        pending_uploads = Upload.query.filter_by(status='pending').all()

        for upload in pending_uploads:
            file_path = os.path.join(UPLOAD_FOLDER, upload.filename)
            list_presentation = presentation_parser.extract_text(file_path)

            # Process the presentation and update status in the database
            try:
                slides = await async_client.async_client(list_presentation)
                upload.status = 'processed'
                upload.finish_time = datetime.now()
            except Exception as e:
                upload.status = 'error'
                upload.finish_time = datetime.now()

            # Save the JSON output and update Outputs table
            json_file.create_json_file(upload.uid, OUTPUT_FOLDER, slides)
            db.session.add(uid=upload.uid, filename=f"{upload.uid}.json")

            db.session.commit()

        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(process_uploads())
