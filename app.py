from flask import (
    Flask,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_from_directory,
    jsonify,
)
from db import connection
import os
from core import ocr
from fields import regex_fields
import copy
from convert import transform
from io import BytesIO
from functools import wraps
import pandas as pd
from flask_cors import CORS
import time
import threading


app = Flask(__name__)
CORS(app)

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


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "logged_in" not in session:
                flash("Please log in to access this page", "error")
                return redirect(url_for("login"))
            if session.get("role") != role:
                flash(
                    "You do not have the necessary permissions to access this page",
                    "error",
                )
                return redirect(url_for("load_file"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("init"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        verify_exists = connection.get_user_login(username=username, password=password)
        if not verify_exists:
            flash("User not found, please enter your correct credentials", "error")
            return redirect(url_for("init"))
        session.clear()
        session["logged_in"] = True
        session["role"] = verify_exists["role"]
        session["username"] = verify_exists["username"]
        if verify_exists["role"] == "user":
            return redirect(url_for("load_file"))

        return redirect(url_for("index"))

    return redirect(url_for("init"))


@app.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("init"))


@app.route("/index")
@login_required
@role_required("admin")
def index():
    current_year = time.localtime().tm_year
    year = request.args.get("year")
    year = year.strip() if year else current_year

    if year:
        all_users = connection.getAllUsers(year=year)
    else:
        all_users = connection.getAllUsers()
    all_years = set(connection.get_all_years())
    all_years = sorted(all_years)
    is_valid_year = year in all_years and len(all_years) <= 1

    if is_valid_year:
        all_years.remove(year)

    if not all_users:
        flash("No users found", "error")
        return render_template("index.html", context={"users": []})

    # Convert to json
    for user in all_users:
        total_pay = user["total_pay"].replace(",", "")
        consumption_kwh = user["consumption_kwh"].replace(",", "")
        user["total_pay"] = f"{float(total_pay):.2f}"
        user["consumption_kwh"] = f"{float(consumption_kwh):.2f}"

    return render_template(
        "index.html", context={"users": all_users, "years": all_years}
    )


path_name_to_extract = None


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["myfile"]

        file_size = len(request.files.getlist("myfile"))

        are_multiple_files = file_size > 1 and file_size <= 50
        if are_multiple_files:
            files = request.files.getlist("myfile")
            data_from_files, data_errors = load_data_multiple_files(files)
            if data_errors:
                for error in data_errors:
                    flash(error, "error")
            session["array_data"] = data_from_files
            return redirect(url_for("load_file"))
        else:

            if uploaded_file.filename != None:
                name_file, extension = os.path.splitext(uploaded_file.filename)

                if extension not in ALLOWED_EXTENSIONS:
                    flash("File not allowed", "error")
                    return redirect(url_for("load_file"))

                elif extension in ONLY_IMAGE_EXTENSIONS:
                    text_from_img = get_text_from_image(uploaded_file, extension)

                    if text_from_img is None:
                        flash("Error uploading file", "error")
                        return redirect(url_for("load_file"))

                    session["data"] = text_from_img
                    return redirect(url_for("load_file"))

                elif extension in ONLY_PDF_EXTENSIONS:
                    text_from_img = get_text_from_pdf(
                        uploaded_file, name_file, extension
                    )

                    if text_from_img is None:
                        flash("Error uploading file", "error")
                        return redirect(url_for("load_file"))

                    session["data"] = text_from_img
                    return redirect(url_for("load_file"))

            flash("Error, limit files allowed is 50", "error")
            return redirect(url_for("load_file"))
    flash("Error uploading file", "error")
    return redirect(url_for("load_file"))


@app.route("/database/save", methods=["POST"])
@login_required
def save_user():
    if request.method == "POST":
        nis = request.form["nis"]
        start_period = request.form["start_period"]
        end_period = request.form["end_period"]
        total_pay = request.form["total_pay"].replace(",", "")
        kwh = request.form["consumption_kwh"].replace(",", "")

        filename = request.form["file_name"]
        verify_not_duplicate = connection.verify_date_start_and_end_period(
            nis, start_period, end_period
        )

        if nis == DONT_SAVE_WITHOUT_NIS:
            cleanup_file(filename)
            flash("NIS not found", "error")
            return redirect(url_for("load_file"))

        if not verify_not_duplicate:
            _, extension = os.path.splitext(filename)
            user = {
                "nis": request.form["nis"],
                "date_issue": request.form["date_issue"],
                "consumption_kwh": kwh,
                "start_period": request.form["start_period"],
                "end_period": request.form["end_period"],
                "total_pay": total_pay,
            }

            if extension in ALLOWED_EXTENSIONS:
                is_save = save_on_database(
                    user, nis, start_period, end_period, filename
                )

                if is_save:
                    return redirect(url_for("search"))
                return redirect(url_for("load_file"))
            else:
                cleanup_file(filename)
                flash("Error saving user", "error")
                return redirect(url_for("load_file"))
        else:
            cleanup_file(filename)
            flash("User already exists", "error")
            return redirect(url_for("load_file"))
    return redirect(url_for("load_file"))


@app.route(
    "/user/delete/<string:id>/<string:start_period>/<string:end_period>",
    methods=["POST"],
)
@login_required
@role_required("admin")
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
@login_required
@role_required("admin")
def user_info(id, start_period, end_period):
    path_image = "uploads/temp_image.png"
    start_period = start_period.replace("-", "/")
    end_period = end_period.replace("-", "/")
    cleanup_file("temp_image.png")

    user = connection.get_user_by_nis(id, start_period, end_period)

    if user is None:
        flash("User not found", "error")
        return redirect(url_for("search"))

    image = connection.getImage(id, start_period, end_period)
    totay_pay = user["total_pay"].replace(",", "")
    consumption_kwh = user["consumption_kwh"].replace(",", "")
    user["total_pay"] = f"{float(totay_pay):,.2f}"
    user["consumption_kwh"] = f"{float(consumption_kwh):,.2f}"

    if image is None:
        flash("Image not found", "error")
        return redirect(url_for("search"))

    img_bytes = BytesIO()
    image.save(img_bytes, format="JPEG")
    image = img_bytes.getvalue()

    with open(path_image, "wb") as f:
        f.write(image)

    return render_template("user_info.html", context={**user, "image": "none"})


@app.route("/mostrar_imagen_temporal")
@login_required
@role_required("admin")
def mostrar_imagen_temporal():
    return send_from_directory("uploads/", "temp_image.png")


@app.route("/", methods=["GET"])
def init():
    return render_template("login.html")


@app.route("/search/user", methods=["POST"])
@login_required
@role_required("admin")
def search_user():
    if request.method == "POST":

        if not request.form["search"]:
            flash("NIS is required", "error")
            return redirect(url_for("search"))
        if not request.form["start_period"]:
            flash("Start period is required", "error")
            return redirect(url_for("search"))
        if not request.form["end_period"]:
            flash("End period is required", "error")
            return redirect(url_for("search"))

        nis = request.form["search"]
        nis = nis.strip()
        start_period = transform_correct_date(request.form["start_period"])
        end_period = transform_correct_date(request.form["end_period"])

        if not nis.isdigit() and len(nis) == 7:
            flash("NIS must be a 7 digit number", "error")
            return redirect(url_for("search"))

        return redirect(
            url_for(
                "user_info",
                id=nis,
                start_period=start_period,
                end_period=end_period,
            )
        )
    flash("Error searching user", "error")
    return redirect(url_for("search"))


@app.route("/search", methods=["GET"])
@login_required
@role_required("admin")
def search():

    year = request.args.get("year")
    current_year = time.localtime().tm_year
    year = year.strip() if year else current_year
    all_years = set(connection.get_all_years())
    all_years = sorted(all_years)
    is_valid_year = year in all_years and len(all_years) <= 1

    if is_valid_year:
        all_years.remove(year)

    users = connection.getAllUsers(year=year)
    if not users:
        flash("No users found", "error")
        return render_template("search.html", context={"users": []})

    for user in users:
        total_pay = user["total_pay"].replace(",", "")
        consumption_kwh = user["consumption_kwh"].replace(",", "")
        user["total_pay"] = f"{float(total_pay):,.2f}"
        user["consumption_kwh"] = f"{float(consumption_kwh):,.2f}"

    return render_template("search.html", context={"users": users, "years": all_years})


@app.route("/reports", methods=["GET"])
@login_required
@role_required("admin")
def reports():
    # generate excel  to download
    all_users = connection.getAllUsers()

    df = pd.DataFrame(all_users)
    df.columns = [
        "NIS Number",
        "Date of Issue",
        "KWh Consumption",
        "Start of Period",
        "End of Period",
        "Total Payment",
    ]
    df["Total Payment"] = df["Total Payment"].apply(
        lambda x: float(f"{float(str(x).replace(',', '')):.2f}")
    )
    df["KWh Consumption"] = df["KWh Consumption"].apply(
        lambda x: float(f"{float(str(x).replace(',', '')):.2f}")
    )

    df["NIS Number"] = df["NIS Number"].apply(lambda x: str(x))
    path_xlsx = f"uploads/reports.xlsx"

    if os.path.exists(path_xlsx):
        os.remove(path_xlsx)

    with pd.ExcelWriter(path_xlsx) as writer:
        df.to_excel(writer, sheet_name="Users", index=False)

    return render_template("repots.html")


@app.route("/download/reports", methods=["GET"])
@login_required
@role_required("admin")
def download_reports():
    path_xlsx = "uploads/reports.xlsx"
    if os.path.exists(path_xlsx):
        return send_from_directory("uploads", "reports.xlsx")
    flash("Error downloading file", "error")
    return redirect(url_for("reports"))


@app.route("/loadfile", methods=["GET"])
@login_required
def load_file():

    data = session.get("data", None)
    array_data = session.get("array_data", None)
    if array_data:
        new_data = copy.copy(array_data)
        session.pop("array_data", None)
        return render_template(
            "load_file.html", context={"array_data": new_data, "data": {}}
        )

    if data:

        new_data = copy.copy(data)
        session.pop("data", None)
        return render_template(
            "load_file.html", context={"data": new_data, "array_data": []}
        )

    return render_template("load_file.html", context={"data": {}, "array_data": []})


@app.route("/load/one/file", methods=["POST"])
def load_one_file():
    data = request.json
    if not data:
        return jsonify("no_data_privide"), 400

    nis = data.get("nis")
    start_period = data.get("start_period")
    end_period = data.get("end_period")
    filename = data.get("file_name")

    new_user = {
        "nis": nis,
        "date_issue": data.get("date_issue"),
        "consumption_kwh": data.get("consumption_kwh"),
        "start_period": start_period,
        "end_period": end_period,
        "total_pay": data.get("total_pay"),
    }

    if not all([nis, start_period, end_period, filename]):
        return jsonify(message="missing_required_fields"), 400

    is_valid = is_valid_user(new_user)
    if not is_valid:
        return jsonify(message="user_is_invalid"), 400

    is_duplicate = connection.verify_date_start_and_end_period(
        nis, start_period, end_period
    )
    if is_duplicate:
        return jsonify(message="user_already_exists"), 400

    was_saved = save_on_database(
        user=new_user,
        nis=nis,
        start_period=start_period,
        end_period=end_period,
        filename=filename,
    )
    if not was_saved:
        return jsonify(message="error_saving_user"), 400

    return jsonify(message="user_saved"), 200


@app.route("/delete/image", methods=["DELETE"])
def delete_image():
    data = request.json
    filename = data.get("filename")
    path = f"uploads/{filename}"
    if not filename:
        return jsonify(message="filename_not_provided"), 400
    if os.path.exists(path):
        os.remove(path)
        return jsonify(message="image_deleted"), 200


def transform_correct_date(date):
    # date format: dd-mm-yyyy
    date = date.split("-")
    return f"{date[2]}-{date[1]}-{date[0]}"


def is_valid_user(user):
    # Return true if the user is valid
    is_valid = all(
        [
            user.get("nis"),
            user.get("date_issue"),
            user.get("consumption_kwh"),
            user.get("start_period"),
            user.get("end_period"),
            user.get("total_pay"),
        ]
    )
    return is_valid


def get_text_from_image(file, extension):
    path_file = "uploads/" + file.filename
    file.save(path_file)
    text = ocr.extract(path_file, extension)
    result = regex_fields.get_important_fields(text)
    if not is_valid_user(result):
        os.remove(path_file)
        flash(
            f"User is invild some fields are wrong, this is the file: {file.filename}",
            "error",
        )
        return None
    return {**result, "file_name": file.filename}


def get_text_from_pdf(file, name_file, extension):
    path_file = "uploads/" + file.filename
    file.save(path_file)
    # Proceso para convertir el PDF a imagen y guardarla en el servidor
    image = transform.toImage(path_file)
    path_image = f"uploads/{name_file}.jpg"
    with open(path_image, "wb") as f:
        image[0].save(f, "JPEG")

    text = ocr.extract(path_file, extension)
    result = regex_fields.get_important_fields(text)
    if not is_valid_user(result):
        if os.path.exists(path_file) or os.path.exists(path_image):
            os.remove(path_file)
            os.remove(path_image)
        return None
    if os.path.exists(path_file):
        os.remove(path_file)

    return {**result, "file_name": f"{name_file}.jpg"}


def save_on_database(user, nis, start_period, end_period, filename):
    try:
        path_image = f"uploads/{filename}"
        connection.save_image(
            path_img=path_image,
            nis=nis,
            start_period=start_period,
            end_period=end_period,
        )
        connection.create_user(user)

        if os.path.exists(path_image):
            os.remove(path_image)
        return True
    except Exception as e:
        print(e)
        if os.path.exists(path_image):
            os.remove(path_image)
        return None


def process_file(file, extension, data_from_files, data_errors):
    if extension in ONLY_IMAGE_EXTENSIONS:
        text_from_img = get_text_from_image(file, extension)
        if text_from_img is None:
            data_errors.append(f"Error uploading file {file.filename}")
        else:
            data_from_files.append(text_from_img)
    elif extension in ONLY_PDF_EXTENSIONS:
        text_from_img = get_text_from_pdf(
            file, os.path.splitext(file.filename)[0], extension
        )
        if text_from_img is None:
            data_errors.append(f"Error uploading file {file.filename}")
        else:
            data_from_files.append(text_from_img)
    else:
        data_errors.append(f"Error uploading file {file.filename}")


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(
            f"La función {func.__name__} tardó {end_time - start_time} segundos en ejecutarse."
        )
        return result

    return wrapper


def load_data_multiple_files(files):
    star_time = time.time()
    data_from_files = []
    data_errors = []
    threads = []

    for file in files:
        _, extension = os.path.splitext(file.filename)

        if extension not in ALLOWED_EXTENSIONS:
            flash(f"File not allowed {file.name}", "error")
            return redirect(url_for("load_file"))

        thread = threading.Thread(
            target=process_file, args=(file, extension, data_from_files, data_errors)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - star_time
    print(f"El proceso tardó {total_time:.4f} segundos en ejecutarse.")

    return data_from_files, data_errors


def cleanup_file(filename):
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        os.remove(file_path)


if __name__ == "__main__":
    app.run()
