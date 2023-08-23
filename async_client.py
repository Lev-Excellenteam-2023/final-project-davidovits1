import asyncio
import httpx
import process_slide


async def async_client(text_pptx: list) -> tuple:
    """
    Asynchronously process text data for PowerPoint slides.

    :param text_pptx: A list containing text data for PowerPoint slides.
    :return: A tuple containing processed slides.
    """
    # Create an asynchronous HTTP client using httpx.
    async with httpx.AsyncClient() as client:
        tasks = [process_slide.process_slide(i, text_pptx, client) for i in range(len(text_pptx))]
        slides = await asyncio.gather(*tasks)

    return slides
