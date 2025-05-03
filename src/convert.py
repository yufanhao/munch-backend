import openai
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Create OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def get_closest_match(target_string, options_list, context=""):
    """
    Uses OpenAI to return the most similar string in options_list to target_string.
    """
    options_string = "\n".join(options_list)
    prompt = f"""
You are helping identify the best match for a given name from a list. 
Given the input: "{target_string}", choose the closest matching string from the following list:
{options_string}

Context (if any): {context}

Return only the best matching string. Do not include any explanation or extra text.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant for fuzzy matching.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )

        best_match = response.choices[0].message.content.strip()
        return best_match if best_match in options_list else None

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return None
