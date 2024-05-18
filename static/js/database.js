var modal = document.getElementById("mymodal") || null;
var btn = document.getElementById("openModal") || null;
var btnOneFile = document.getElementById("multiple").textContent || null;

btn.onclick = function () {
  modal.style.display = "block";
  
};

window.onload = function() {
  if (data_context.data) {
      document.getElementById("mymodal").style.display = "block";
  }
};

window.onclick = function (event) {
  if (event.target == modal) {
    const filename = document.getElementById("file_name").value;
    delFileFromServer(filename);
    modal.style.display = "none";
    const element = document.getElementById("send-form");
    const input_element = document.getElementById("file");
    element.innerHTML = "";
    input_element.value = "";
  }
};

function clearInfo(filename) {
  const form = document.getElementById("data-to-save");
  const inputFile = document.getElementById("file");
  form.innerHTML = "";
  inputFile.value = "";
  modal.style.display = "none";
  delFileFromServer(filename);
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
