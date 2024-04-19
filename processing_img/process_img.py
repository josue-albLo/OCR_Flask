import cv2
from PIL import Image


def preprocess_image(image_path):
    try:
        # Cargar la imagen con OpenCV
        image = cv2.imread(image_path)

        # Convertir la imagen a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Aplicar filtrado para eliminar ruido
        filtered_image = cv2.GaussianBlur(gray, (5, 5), 0)

        # Aplicar umbralización adaptativa para binarizar la imagen
        binary_image = cv2.adaptiveThreshold(filtered_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        return binary_image
    except Exception as e:
        print(f"Error en el preprocesamiento de la imagen: {e}")
        return None


def process_image(image_path):
    try:
        # Procesar la imagen con OpenCV
        processed_image = preprocess_image(image_path)

        if processed_image is not None:
            # Convertir la imagen de OpenCV a un objeto Image de Pillow
            pil_image = Image.fromarray(processed_image)
            return pil_image
        else:
            return None
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None
