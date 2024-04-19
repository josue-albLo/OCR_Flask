from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Response,
    send_from_directory,
)
from db import connection
import os
from core import ocr
from fields import regex_fields
import io
import copy
from convert import transform
from io import BytesIO

app = Flask(__name__)

# Configuraciones de desarrollo
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "super-secret-key"

# Database
connection.get_connection()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg"}
ONLY_IMAGE_EXTENSIONS = {".png", ".jpg"}
ONLY_PDF_EXTENSIONS = {".pdf"}

DONT_SAVE_WITHOUT_NIS = "NIS no encontrado"


@app.route("/")
def index():
    users = connection.getAllUsers()
    data_session = session.get("data", None)
    load_data = None
    data = {
        "title": "Hello World",
        "saludo": "Hola desde Flask!",
        "users": users,
    }
    if data_session:
        load_data = copy.copy(data_session)
        session.pop("data", None)
        return render_template("index.html", context={**data, "data": {**load_data}})
    return render_template("index.html", context={**data, "data": data})


path_name_to_extract = None


@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["myfile"]

        if uploaded_file.filename != None:
            print("File uploaded")
            name_file, extension = os.path.splitext(uploaded_file.filename)

            if extension not in ALLOWED_EXTENSIONS:
                print("File not allowed", extension)
                flash("File not allowed", "error")
                return redirect(url_for("load_file"))

            elif extension in ONLY_IMAGE_EXTENSIONS:
                path_file = "uploads/" + uploaded_file.filename
                print("File path", path_file)
                print("Extension", extension)
                uploaded_file.save(path_file)
                print("File saved")
                text = ocr.extract(path_file, extension)
                result = regex_fields.get_important_fields(text)
                add_field_file_name = {**result, "file_name": uploaded_file.filename}
                print(f"Result: {add_field_file_name}")
                print("Text extracted")
                session["data"] = add_field_file_name
                flash("text_extract", "success")
                print("File removed")

                return redirect(url_for("load_file"))
            elif extension in ONLY_PDF_EXTENSIONS:

                path_file = "uploads/" + uploaded_file.filename
                print("File path", path_file)
                print("Extension", extension)
                uploaded_file.save(path_file)
                print("File saved")
                # Proceso para convertir el PDF a imagen y guardarla en el servidor
                image = transform.toImage(path_file)
                path_image = f"uploads/{name_file}.jpg"
                with open(path_image, "wb") as f:
                    image[0].save(f, "JPEG")

                text = ocr.extract(path_file, extension)
                result = regex_fields.get_important_fields(text)
                os.remove(path_file)
                add_field_file_name = {**result, "file_name": f"{name_file}.jpg"}
                print(f"Result: {add_field_file_name}")
                print("Text extracted")
                session["data"] = add_field_file_name
                flash("text_extract", "success")
                print("File removed")
                return redirect(url_for("load_file"))

        flash("Error uploading file", "error")
        return redirect(url_for("load_file"))
    flash("Error uploading file", "error")
    return redirect(url_for("load_file"))


@app.route("/database/save", methods=["POST"])
def save_user():
    if request.method == "POST":
        nis = request.form["nis"]
        start_period = request.form["start_period"]
        end_period = request.form["end_period"]

        filename = request.form["file_name"]
        verify_not_duplicate = connection.verify_date_start_and_end_period(
            nis, start_period, end_period
        )
        
        if nis == DONT_SAVE_WITHOUT_NIS:
            if os.path.exists(f"uploads/{filename}"):
                    os.remove(f"uploads/{filename}")
            flash("NIS not found", "error")
            return redirect(url_for("load_file"))

        
        if not verify_not_duplicate:
            name_file, extension = os.path.splitext(filename)
            print("Filename", filename)
            print("Extension", extension)
            print("Name file", name_file)
            user = {
                "nis": request.form["nis"],
                "date_issue": request.form["date_issue"],
                "consumption_kwh": request.form["consumption_kwh"],
                "start_period": request.form["start_period"],
                "end_period": request.form["end_period"],
                "total_pay": request.form["total_pay"],
            }

            if extension in ONLY_PDF_EXTENSIONS:
                path_image = filename
                connection.save_image(
                    path_img=path_image,
                    nis=nis,
                    start_period=start_period,
                    end_period=end_period,
                )
                connection.create_user(user)
                print("Filename", filename)

                if os.path.exists(path_image):
                    os.remove(path_image)

                print("Saving user")
                print(request.form)
                return redirect(url_for("search"))
            elif extension in ONLY_IMAGE_EXTENSIONS:
                path_image = f"uploads/{filename}"
                connection.save_image(
                    path_img=path_image,
                    nis=nis,
                    start_period=start_period,
                    end_period=end_period,
                )
                connection.create_user(user)
                print("Filename", filename)

                if os.path.exists(f"uploads/{filename}"):
                    os.remove(f"uploads/{filename}")

                print("Saving user")
                print(request.form)
                return redirect(url_for("search"))
            else:
                if os.path.exists(f"uploads/{filename}"):
                    os.remove(f"uploads/{filename}")
                flash("Error saving user", "error")
                return redirect(url_for("load_file"))
        else:
            if os.path.exists(f"uploads/{filename}"):
                    os.remove(f"uploads/{filename}")
            flash("User already exists", "error")
            return redirect(url_for("load_file"))
    return redirect(url_for("load_file"))


@app.route(
    "/user/delete/<string:id>/<string:start_period>/<string:end_period>",
    methods=["POST"],
)
def delete_user(id, start_period, end_period):
    start_period = start_period.replace("-", "/")
    end_period = end_period.replace("-", "/")
    was_deleted = connection.deleteUser(id, start_period, end_period)
    was_deleted_image = connection.deleteImage(id, start_period, end_period)
    if was_deleted and was_deleted_image:
        flash("User and image was deleted", "success")
        return redirect(url_for("search"))
    flash("Error deleting user", "error")
    return redirect(url_for("search"))


@app.route(
    "/user/info/<string:id>/<string:start_period>/<string:end_period>",
    methods=["POST", "GET"],
)
def user_info(id, start_period, end_period):
    start_period = start_period.replace("-", "/")
    end_period = end_period.replace("-", "/")
    path_image = f"uploads/temp_image.png"
    if os.path.exists(path_image):
        os.remove(path_image)

    user = connection.get_user_by_nis(id, start_period, end_period)
    image = connection.getImage(id, start_period, end_period)
    img_bytes = BytesIO()
    image.save(img_bytes, format="JPEG")
    image = img_bytes.getvalue()
    if (user is None) or (image is None):
        flash("User and image not found", "error")
        return redirect(url_for("search"))
    with open(path_image, "wb") as f:
        f.write(image)

    return render_template("user_info.html", context={**user, "image": "none"})


@app.route("/mostrar_imagen_temporal")
def mostrar_imagen_temporal():
    return send_from_directory("uploads/", "temp_image.png")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        session["password"] = request.form["password"]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/search/user", methods=["POST"])
def search_user():
    if request.method == "POST":

        if not request.form["search"]:
            flash("NIS is required", "error")
            return redirect(url_for("search"))

        nis = request.form["search"]
        nis = nis.strip()

        if not nis.isdigit() and len(nis) == 7:
            flash("NIS must be a 7 digit number", "error")
            return redirect(url_for("search"))

        return redirect(
            url_for(
                "user_info",
                id=nis,
            )
        )
    flash("Error searching user", "error")
    return redirect(url_for("search"))


@app.route("/search", methods=["GET"])
def search():
    users = connection.getAllUsers()
    if not users:
        flash("No users found", "error")
        return render_template("search.html", context={"users": []})
    return render_template("search.html", context={"users": users})


@app.route("/reports", methods=["GET"])
def reports():
    return render_template("repots.html")


@app.route("/loadfile", methods=["GET"])
def load_file():

    data = session.get("data", None)

    if data:
        flash("File loaded", "success")
        new_data = copy.copy(data)
        session.pop("data", None)
        print("Data", new_data)
        return render_template("load_file.html", context={"data": new_data})

    return render_template("load_file.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
