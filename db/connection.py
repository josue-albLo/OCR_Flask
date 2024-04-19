from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import gridfs
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np


uri = "add your uri here"

client = MongoClient(
    uri, server_api=ServerApi("1"), tls=True, tlsAllowInvalidCertificates=True
)


def get_connection():
    try:
        client.admin.command("ping")
        print("Connected to the database")

    except Exception as e:

        print(e)


def create_user(data: dict[str, str]):
    db = client["TigerOCR"]
    collection = db["users"]
    try:
        collection.insert_one(data)
    except Exception as e:
        print(e)


def save_image(path_img, nis: str, start_period: str, end_period: str):
    db = client["TigerOCR"]
    collection = db["images"]
    filename = nis
    try:
        with open(path_img, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        fs = gridfs.GridFS(db)
        field_id = fs.put(encoded_string, filename=filename)
        collection.insert_one(
            {
                "filename": filename,
                "field_id": field_id,
                "nis": nis,
                "start_period": start_period,
                "end_period": end_period,
            }
        )

    except Exception as e:
        print(e)


def verify_date_start_and_end_period(nis: str, start_period: str, end_period: str):
    db = client["TigerOCR"]
    collection = db["users"]
    try:
        res = collection.find_one(
            {"nis": nis, "start_period": start_period, "end_period": end_period}
        )
        if res:
            return True
        return False
    except Exception as e:
        print(e)
        return None


def getImage(filename, start_period, end_period)-> Image.Image | None:
    db = client["TigerOCR"]
    collection = db["images"]
    fs = gridfs.GridFS(db)
    try:
        image_data = collection.find_one(
            {
                "filename": filename,
                "start_period": start_period,
                "end_period": end_period,
            }
        )
        if image_data is None:
            print("Image not found in the database")
            return None

        image_file = fs.get(image_data["field_id"])
        if image_file is None:
            print("Error retrieving image file from GridFS")
            return None

        image_bytes = image_file.read()
        if image_bytes is None:
            print("Error reading image data from GridFS")
            return None

        # Verificar el tamaño de la imagen
        max_pixels = 178956970  # Límite de Pillow para evitar ataques de DOS
        if len(image_bytes) > max_pixels:
            image_bytes = image_bytes[:max_pixels]
            

        image = Image.open(BytesIO(base64.b64decode(image_bytes)))

        return image
    except gridfs.errors.NoFile:
        print("Image not found in GridFS")
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None




def getAllUsers() -> list[dict[str, str]]:
    db = client["TigerOCR"]
    collection = db["users"]
    try:
        res = collection.find({}, {"_id": 0})
        return [user for user in res]
    except Exception as e:
        print(e)
        return None


def deleteUser(nis: str, start_period: str, end_period: str):
    db = client["TigerOCR"]
    collection = db["users"]
    try:
        collection.delete_one(
            {"nis": nis, "start_period": start_period, "end_period": end_period}
        )
        return True
    except Exception as e:
        print(e)


def deleteImage(nis: str, start_period: str, end_period: str):
    db = client["TigerOCR"]
    collection = db["images"]
    try:
        image = collection.find_one({"nis": nis})
        fs = gridfs.GridFS(db)
        fs.delete(image["field_id"])
        collection.delete_one(
            {"nis": nis, "start_period": start_period, "end_period": end_period}
        )
        return True
    except Exception as e:
        print(e)


def get_image_by_nis(nis: str):
    db = client["TigerOCR"]
    collection = db["images"]
    fs = gridfs.GridFS(db)
    try:
        image = collection.find_one({"nis": nis})
        image = fs.get(image["field_id"])
        image = Image.open(BytesIO(base64.b64decode(image.read())))
        return image
    except Exception as e:
        print(e)
        return None


def get_user_by_nis(nis: str, start_period: str, end_period: str):
    db = client["TigerOCR"]
    collection = db["users"]
    try:
        user = collection.find_one(
            {"nis": nis, "start_period": start_period, "end_period": end_period}
        )
        print(user)
        return user
    except Exception as e:
        print(e)
        return None

def create_user_login():
    pass