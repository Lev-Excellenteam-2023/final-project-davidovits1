import os
import httpx
import openai
from dotenv import load_dotenv

# Load API key from environment variable
load_dotenv()
API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY


async def generate_explanation_async(session: httpx.AsyncClient, prompt: str, max_tokens: int = 100,
                                     timeout: int = 30) -> str:
    """
    Generate an explanation asynchronously for a given prompt using the OpenAI API.

    Args:
        session: The HTTP session for asynchronous requests.
        prompt (str): The prompt for which to generate an explanation.
        max_tokens (int, optional): The maximum number of tokens in the response.
        timeout (int, optional): Timeout duration in seconds.

    Returns:
        str: The generated explanation text.
    """
    response = await session.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that explains slide significance."},
                {"role": "user", "content": prompt},
            ],
            "model": "gpt-3.5-turbo",
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    response_data = response.json()
    return response_data["choices"][0]["message"]["content"].strip()
