import fitz
from PIL import Image
import tempfile


def toImage(
    pdf_path,
    resolution=400,
    initial_scale_factor=1.0,
    max_scale_factor=2.0,
    max_pixels=178956970,
):
    images = []
    pdf_doc = fitz.open(pdf_path)
    for page_number in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_number)
        scale_factor = max_scale_factor
        while True:
            matrix = fitz.Matrix(scale_factor, scale_factor)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image = Image.frombytes(
                "RGB", [pixmap.width, pixmap.height], pixmap.samples
            )
            if image.width * image.height <= max_pixels or scale_factor <= 1.0:
                break
            scale_factor /= 2
        image = image.convert("L")

        image = image.resize(
            (int(image.width * resolution / 72), int(image.height * resolution / 72)),
            resample=Image.BICUBIC,
        )
        images.append(image)
    return images


def to_image_to_save_temp(pdf_path, resolution=600, scale_factor=3.0):
    images = []
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_doc = fitz.open(pdf_path)
        for page_number in range(pdf_doc.page_count):
            page = pdf_doc.load_page(page_number)

            # Get transformation matrix and image pixmap
            matrix = fitz.Matrix(scale_factor, scale_factor)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)

            # Create temporary file path for the image
            temp_image_path = f"{temp_dir}/{page_number}.png"

            try:
                # Convert pixmap to PIL Image and save temporarily
                image = Image.frombytes(
                    "RGB", [pixmap.width, pixmap.height], pixmap.samples
                )
                image = image.resize(
                    (
                        int(image.width * resolution / 72),
                        int(image.height * resolution / 72),
                    ),
                    resample=Image.BICUBIC,
                )
                image = image.convert("L")
                image.save(temp_image_path)

                # Add temporary image to the list
                images.append(image)
            except Exception as e:
                raise Exception(f"Error saving temporary image: {e}")

    return images
