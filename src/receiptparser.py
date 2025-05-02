from openai import OpenAI
from PIL import Image
import base64
import io
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import os
import json
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Item(BaseModel):
    name: str
    price: Optional[float]


class ReceiptSummary(BaseModel):
    store_name: str
    items: List[Item]
    tax: Optional[float]
    tips: Optional[float]
    total: Optional[float]
    payment_total: Optional[float]


def encode_image(image_bytes, max_size=1024):
    image = Image.open(io.BytesIO(image_bytes))
    width, height = image.size
    scale = min(max_size / width, max_size / height)
    if scale < 1:
        image = image.resize(
            (int(width * scale), int(height * scale)), Image.Resampling.LANCZOS
        )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def parse_receipt(image_bytes: bytes) -> str:
    base64_image = encode_image(image_bytes)
    schema = ReceiptSummary.model_json_schema()

    user_prompt = f"""
    You are an expert at extracting information from receipts.

    Please extract the information from the receipt. Be as detailed as possible — 
    missing or misreporting information is a crime. Be sure to include Tips and Payment Total. Duplicate items 
    should be accounted for and listed separately. If one of the fields in the JSON can not be found in
    the receipt, it should be 0 for any number type values and empty string for any string values.

    Return the information in the following JSON schema:

    {schema}
    """

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                    },
                },
                {
                    "type": "text",
                    "text": user_prompt,
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000,
    )

    # Parse the string content into a Python dictionary
    content = response.choices[0].message.content
    # Extract JSON from markdown or text
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    json_str = match.group(1) if match else content.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON. Full response was:\n" + content)
