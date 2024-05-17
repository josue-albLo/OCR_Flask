var batchMode = false; // Estado inicial: modo carga de un archivo

function toggleBatchMode() {
  batchMode = !batchMode; // Cambia el estado del modo
  const fileInput = document.getElementById("file");
  const btnLoad = document.getElementById("openModal");
  fileInput.multiple = batchMode; // Establece el atributo multiple basado en el modo
  fileInput.value = ""; // Limpia los archivos seleccionados anteriormente
  // Cambia el texto del botón de modo
  document.querySelector(".btn").textContent = batchMode
    ? "Cargar uno"
    : "Cargar archivos";
    // Cambia el texto del botón de carga
    btnLoad.textContent = batchMode
    ? "Cargar archivos"
    : "Cargar archivo";
}

document.querySelector("form").onsubmit = function (event) {
  const fileInput = document.getElementById("file");
  if (batchMode && fileInput.files.length > 15) {
    alert("No puedes subir más de 15 archivos en modo lote.");
    event.preventDefault(); // Evita que se envíe el formulario
  }
};
