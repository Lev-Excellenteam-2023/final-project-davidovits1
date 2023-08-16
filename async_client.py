import httpx
import process_slide
import asyncio


async def async_client(text_pptx: list) -> tuple:
    async with httpx.AsyncClient() as client:
        tasks = [process_slide.process_slide(i, text_pptx, client) for i in range(len(text_pptx))]
        slides = await asyncio.gather(*tasks)

    return slides
