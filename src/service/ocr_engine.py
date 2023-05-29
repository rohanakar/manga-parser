import pytesseract
from PIL import Image
from utility.fileutils import get_image,list_pending_image_pair

def extract_text_from_image(image_path):
    image = get_image(image_path)
    text = pytesseract.image_to_string(image)
    return text
