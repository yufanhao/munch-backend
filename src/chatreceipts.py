from openai import OpenAI
from PIL import Image
import base64
import time
import threading
from rich import print
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# Create OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def load_and_resize_image(image_path, max_size=1024):
    image = Image.open(image_path)
    width, height = image.size
    scale = min(max_size / width, max_size / height)

    if scale < 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        image.save(image_path)
    return image


class Item(BaseModel):
    name: str
    total_price: Optional[float]


class ReceiptSummary(BaseModel):
    store_name: str
    store_address: str
    store_number: Optional[int]
    items: List[Item]
    tax: Optional[float]
    tips: Optional[float]
    total: Optional[float]
    payment_total: Optional[float]
    date: Optional[str] = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    payment_method: Literal["cash", "credit", "debit", "check", "other"]


# Load and prepare image
image_path = "/Users/jasonguo/Desktop/backend/munch-backend/src/pho_receipt.png"
load_and_resize_image(image_path)
base64_image = encode_image_to_base64(image_path)

# Construct prompt and messages
json_schema = ReceiptSummary.model_json_schema()
user_prompt = f"""
You are an expert at extracting information from receipts.

Please extract the information from the receipt. Be as detailed as possible — 
missing or misreporting information is a crime. Be sure to include Tips and Payment Total. Duplicate items 
should be accounted for and listed separately.

Return the information in the following JSON schema:

{json_schema}
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

# Run the model
def run_model():
    global result
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = f"❌ Error: {e}"


result = None
thread = threading.Thread(target=run_model)
thread.start()

timeout = 600
start_time = time.time()
print("Generating", end="", flush=True)

while thread.is_alive():
    if time.time() - start_time > timeout:
        print("\n❌ Timeout.")
        thread.join(timeout=1)
        result = None
        break
    print(".", end="", flush=True)
    time.sleep(1)

if result:
    print("\n✅ Generation complete!")
    print(result)
