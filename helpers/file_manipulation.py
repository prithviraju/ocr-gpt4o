file_manipulimport io
import os
import base64
import fitz
from PIL import Image
BASE_DIR = os.getcwd()

def extract_images_base64_from_file(file_name):
    document = fitz.open(os.path.join(BASE_DIR,"tmp"+f"/{file_name}"))
    images = []
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            images.append(base64.b64encode(buffered.getvalue()).decode("utf-8"))
    return images

def del_file_from_disk(file_name: str):
    try:
        os.remove(os.path.join(BASE_DIR,"tmp"+f"/{file_name}"))
        return True
    except Exception as e:
        print(f"error: {e}")
        return False

def write_file_to_disk(file):
    try:
        file.save(os.path.join(BASE_DIR,"tmp"+f"/{file.filename}"))
        return True
    except Exception as e:
        print(f"error: {e}")
        return False
