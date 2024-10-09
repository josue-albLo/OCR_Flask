import pytesseract
from processing_img import process_img
from convert import transform
import gc

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg"}
custom_config = r"--oem 3 --psm 6"


def extract(path_file, extension: str):
    if extension not in ALLOWED_EXTENSIONS:
        return "File not allowed"
    if extension == ".pdf":
        return read_pdf(path_file)
    else:
        return read_image(path_file)


def read_image(path_file):
    image = process_img.process_image(path_file)
    if image is not None:
        text = pytesseract.image_to_string(image, "spa")
        image.close()
        del image
        gc.collect()
        return text
    else:
        return "Error in image processing"


def read_pdf(path_file):
    img_list = transform.toImage(path_file)
    text = ""
    for img in img_list:
        text += pytesseract.image_to_string(img, lang="spa")
        img.close()
        del img
        gc.collect()
    return text
