import outlines
import torch
from transformers import AutoProcessor
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from PIL import Image
import requests
from rich import print
from transformers import Qwen2VLForConditionalGeneration

model_name = "Qwen/Qwen2-VL-7B-Instruct"
model_class = Qwen2VLForConditionalGeneration

model = outlines.models.transformers_vision(
    model_name,
    model_class=model_class,
    model_kwargs={
        "device_map": "auto",
        "torch_dtype": torch.bfloat16,
    },
    # "use_fast": True,
    # processor_kwargs={
    #     "device": "cuda",
    # },
)


def load_and_resize_image(image_path, max_size=1024):
    """
    Load and resize an image while maintaining aspect ratio to lessen computational load
    """
    image = Image.open(image_path)
    width, height = image.size
    scale = min(max_size / width, max_size / height)

    if scale < 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image


# need to get image from frontend
image_path = "https://raw.githubusercontent.com/dottxt-ai/outlines/refs/heads/main/docs/cookbook/images/trader-joes-receipt.jpg"
response = requests.get(image_path)
with open("receipt.png", "wb") as f:
    f.write(response.content)
image = load_and_resize_image("receipt.png")


class Item(BaseModel):
    name: str
    quantity: Optional[int]
    price_per_unit: Optional[float]
    total_price: Optional[float]


class ReceiptSummary(BaseModel):
    store_name: str
    store_address: str
    store_number: Optional[int]
    items: List[Item]
    tax: Optional[float]
    total: Optional[float]
    date: Optional[str] = Field(
        pattern=r"\d{4}-\d{2}-\d{2}", description="Date in the format YYYY-MM-DD"
    )
    payment_method: Literal["cash", "credit", "debit", "check", "other"]

    # Set up the content you want to send to the model


messages = [
    {
        "role": "user",
        "content": [
            {
                # The image is provided as a PIL Image object
                "type": "image",
                "image": image,
            },
            {
                "type": "text",
                "text": f"""You are an expert at extracting information from receipts.
                Please extract the information from the receipt. Be as detailed as possible --
                missing or misreporting information is a crime.

                Return the information in the following JSON schema:
                {ReceiptSummary.model_json_schema()}
            """,
            },
        ],
    }
]

# Convert to the final prompt
processor = AutoProcessor.from_pretrained(model_name, use_fast=True)
prompt = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

receipt_summary_generator = outlines.generate.json(
    model,
    ReceiptSummary,
    sampler=outlines.samplers.greedy(),
)

# Generate the receipt summary
import threading
import time


# Function to run the model in a thread
def run_model():
    global result
    result = receipt_summary_generator(prompt, [image])


result = None
thread = threading.Thread(target=run_model)

# Start the thread
thread.start()

# Show a simple progress indicator
timeout = 120  # seconds
start_time = time.time()
print("Generating", end="", flush=True)

while thread.is_alive():
    if time.time() - start_time > timeout:
        print("\n❌ Timeout: generation took too long.")
        thread.join(timeout=1)  # try to end the thread
        result = None
        break
    print(".", end="", flush=True)
    time.sleep(1)

# Final result
if result:
    print("\n✅ Generation complete!")
    print(result)
