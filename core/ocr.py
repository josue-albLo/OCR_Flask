import pytesseract
from processing_img import process_img
from convert import transform
import gc

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg"}

def extract(path_file, extension: str):
    if extension not in ALLOWED_EXTENSIONS:
        return "File not allowed"
    if extension == ".pdf":
        return read_pdf(path_file)
    else:
        return read_image(path_file)

def read_image(path_file):
    image = process_img.process_image(path_file)
    text = pytesseract.image_to_string(image)
    image.close()
    del image
    gc.collect()
    return text

def read_pdf(path_file):
    img_list = transform.toImage(path_file)
    text = ""
    for img in img_list:
        text += pytesseract.image_to_string(img)
        img.close()
        del img
        gc.collect()
    return text
