import io
import os
import shutil
import base64
import fitz
from PIL import Image
BASE_DIR = os.getcwd()
from pdf2image import convert_from_path

def extract_images_base64_from_file(file_name):
    images = []
    images_absolute_paths = save_file_as_images(file_name)

    for image_raw in images_absolute_paths:
            image = Image.open(image_raw)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            images.append(base64.b64encode(buffered.getvalue()).decode("utf-8"))
    return images

def save_file_as_images(file_name):
    images=convert_from_path(os.path.join(BASE_DIR,"tmp"+f"/{file_name}"),poppler_path="")

    images_absolute_paths = []

    for i in range(len(images)):
            image_path = os.path.join(BASE_DIR,"tmp"+f"/{file_name}_") + str(i) + '.jpg'
            images_absolute_paths.append(image_path)
            images[i].save(image_path, 'JPEG')
    return images_absolute_paths

def convert_page_to_image(pdf_path, page_num):
    images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
    return images[0]

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

def clear_tmp_directory():
    with os.scandir(os.path.join(BASE_DIR,'tmp/')) as entries:
        for entry in entries:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)