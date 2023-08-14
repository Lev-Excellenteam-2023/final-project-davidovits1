import os
import openai
from dotenv import load_dotenv

# Load API key from environment variable
load_dotenv()
API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY


def generate_explanation(prompt: str, engine="gpt-3.5-turbo", max_tokens=100) -> str:
    """
    Generate an explanation for a given prompt using the OpenAI API.

    Args:
        prompt (str): The prompt for which to generate an explanation.
        engine (str): The OpenAI engine to use.
        max_tokens (int): The maximum number of tokens in the response.

    Returns:
        str: The generated explanation text.
    """
    # full_prompt = "\"Explain the significance of \'" + prompt + "\' slide.\""

    try:
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains slide significance."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message["content"].strip()
    except openai.error.OpenAIError as e:
        return f"An error occurred: {e}"


