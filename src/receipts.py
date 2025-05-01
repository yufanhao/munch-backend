import re
from PIL import Image
import pytesseract

# Optional: set path to tesseract if not in PATH (Windows users)
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\fanha\AppData\Local\Programs\Tesseract-OCR"
)


def extract_items_from_receipt(image_path):
    image = Image.open(image_path)

    # Use OCR to extract raw text from image
    text = pytesseract.image_to_string(image)

    print("=== Raw OCR Text ===")
    print(text)

    # Regex to find lines with an item and a price (e.g., "Milk 3.49")
    item_pattern = re.compile(r"(?P<item>[A-Za-z0-9\s\-]+?)\s+(?P<price>\d+\.\d{2})")

    items = []
    for line in text.splitlines():
        match = item_pattern.search(line)
        if match:
            item = match.group("item").strip()
            price = float(match.group("price"))
            items.append((item, price))

    return items


if __name__ == "__main__":
    receipt_path = "receipt.png"  # Replace with your image file path
    items = extract_items_from_receipt(receipt_path)

    print("\n=== Extracted Items ===")
    for name, price in items:
        print(f"{name} - ${price:.2f}")
