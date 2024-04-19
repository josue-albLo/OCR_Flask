from PIL import Image
import pytesseract
from processing_img import process_img
import os
from convert import transform

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
    return text


def read_pdf(path_file):
    img_list = transform.toImage(path_file)

    text = ""
    for img in img_list:
        text += pytesseract.image_to_string(img)
    return text
