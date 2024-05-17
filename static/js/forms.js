
var users = data_context ? data_context.array_data : [];


var errorsApi = {
  no_data_provided: "No se proporcionaron datos",
  missing_required_fields: "Faltan campos requeridos",
  user_invalid: "Usuario no válido",
  user_already_exists: "El usuario ya existe",
  error_saving_user: "Error al guardar el usuario",
};

var responseApi = {
  user_saved: "Usuario guardado",
};

console.log(users);

function init() {
  if (users.length > 1) {
    const container = document.getElementById("user-container");
    container.className = "container-mult-data";
    users.forEach((user, index) => {
      const form = document.createElement("form");
      form.className = "form-multiple";
      form.onsubmit = function (event) {
        event.preventDefault();
        saveData(this);
      };
      form.innerHTML = `
                <div class="form-section">
                    <div class="form-group">
                        <label for="nis-${index}">NIS</label>
                        <input class="input-field" type="text" name="nis" value="${user.nis}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="date_issue-${index}">Fecha de emisión</label>
                        <input class="input-field" type="text" name="date_issue" value="${user.date_issue}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="start_period-${index}">Fecha de inicio</label>
                        <input class="input-field" type="text" name="start_period" value="${user.start_period}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="end_period-${index}">Fecha de fin</label>
                        <input class="input-field" type="text" name="end_period" value="${user.end_period}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="consumption_kwh-${index}">Consumo de KWh</label>
                        <input class="input-field" type="text" name="consumption_kwh" value="${user.consumption_kwh}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="total_pay-${index}">Total a pagar</label>
                        <input class="input-field" type="text" name="total_pay" value="${user.total_pay}" readonly>
                    </div>
                    <input type="hidden" name="file_name" value="${user.file_name}">
                </div>
                <div class="form-actions">
                    <button class="btn button-success" type="submit">Guardar</button>
                    <button class="btn button-cancel" type="button" onclick="removeElement(this, '${user.file_name}')">Eliminar</button>
                </div>
            `;
      container.appendChild(form);
    });
  }
}

function removeElement(button, file_name = null) {
  if (file_name) {
    delFileFromServer(file_name);
  }
  button.closest("form").remove();
}

function delElement(form) {
  const data = new FormData(form);
  const nis = data.get("nis");
  const file_name = data.get("file_name");
  users = users.filter((user) => user.nis !== nis);
  form.remove();
  if (file_name) {
    delFileFromServer(file_name);
  }
}

async function saveData(form) {
  const data = new FormData(form);
  const user = {
    nis: data.get("nis"),
    date_issue: data.get("date_issue"),
    start_period: data.get("start_period"),
    end_period: data.get("end_period"),
    consumption_kwh: data.get("consumption_kwh"),
    total_pay: data.get("total_pay"),
    file_name: data.get("file_name"),
  };

  console.log("Sending:", user);

  try {
    const response = await fetch("http://127.0.0.1:5000/load/one/file", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(user),
    });

    if (!response.ok) {
      const errorText = await response.json();
      const mapError =
        errorsApi[errorText.message] ||
        "Error desconocido: " + errorText.message;
      if (mapError) {
        showAlert(mapError, "error");
        delElement(form);
      }

      throw new Error(mapError);
    }

    showAlert(responseApi.user_saved, "success");
    removeElement(form);
  } catch (error) {
    console.error("Error:", error);
    // showAlert(error.toString(), "error");
  }
}

async function delFileFromServer(file_name) {
  const filename = { filename: file_name };
  try {
    const response = await fetch("http://127.0.0.1:5000/delete/image", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(filename),
    });
    if (!response.ok) {
      throw new Error("Error al eliminar el archivo");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

function showAlert(message, type) {
  const alertBox = document.createElement("div");
  alertBox.textContent = message;
  alertBox.style.padding = "10px";
  alertBox.style.margin = "5px";
  alertBox.style.borderRadius = "5px";
  alertBox.style.color = "#fff";
  alertBox.style.backgroundColor = type === "error" ? "#f44336" : "#4CAF50"; // Rojo para error, verde para éxito

  const alertContainer = document.getElementById("alert-container");
  alertContainer.appendChild(alertBox);
  alertContainer.style.display = "block";

  setTimeout(() => {
    alertContainer.removeChild(alertBox);
    if (alertContainer.children.length === 0) {
      alertContainer.style.display = "none";
    }
  }, 3000); // Mensaje se oculta después de 3 segundos
}

// Lógica para cargar y ejecutar init según los datos disponibles
document.addEventListener("DOMContentLoaded", function () {
  if (users.length > 0) {
    init(); // Ejecuta init solo si hay usuarios
  }
});
