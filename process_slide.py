import httpx

import openAI_request


async def process_slide(index: int, text_pptx: list, session: httpx.AsyncClient) -> dict:
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
