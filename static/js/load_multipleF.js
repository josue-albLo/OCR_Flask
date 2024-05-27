document.addEventListener("DOMContentLoaded", function () {
  const dropArea = document.getElementById("drop-area");
  const fileInput = document.getElementById("file");
  const btnLoad = document.getElementById("openModal");
  const dropAreaText = document.getElementById("drop-area-text");
  let preventClick = false; // Flag to prevent multiple clicks

  // Previene el comportamiento predeterminado para drag and drop
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Añade y remueve la clase de dragover
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(
      eventName,
      () => dropArea.classList.add("dragover"),
      false
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(
      eventName,
      () => dropArea.classList.remove("dragover"),
      false
    );
  });

  // Maneja los archivos soltados
  dropArea.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    // Actualiza el input con los archivos
    fileInput.files = files;

    // Muestra los nombres de los archivos seleccionados
    updateFileList(files);
  }

  // Permite hacer clic en el área para abrir el selector de archivos
  dropArea.addEventListener("click", () => {
    if (!preventClick) {
      fileInput.click();
    }
  });

  // Maneja los cambios en el input de archivos
  fileInput.addEventListener("click", () => {
    preventClick = true;
  });

  fileInput.addEventListener("change", (e) => {
    updateFileList(fileInput.files);
    preventClick = false;
  });

  function updateFileList(files) {
    dropAreaText.innerHTML = "";
    if (files.length > 0) {
      const fileList = document.createElement("ul");
      [...files].forEach((file) => {
        const listItem = document.createElement("li");
        listItem.textContent = file.name;
        fileList.appendChild(listItem);
      });
      dropAreaText.appendChild(fileList);
    } else {
      dropAreaText.textContent = "Arrastra y suelta tu archivo aquí, o haz clic para seleccionarlo";
    }
  }

  // Lógica para alternar entre cargar un archivo o un lote
  var batchMode = false; // Estado inicial: modo carga de un archivo

  window.toggleBatchMode = function() {
    batchMode = !batchMode; // Cambia el estado del modo
    fileInput.multiple = batchMode; // Establece el atributo multiple basado en el modo
    fileInput.value = ""; // Limpia los archivos seleccionados anteriormente
    updateFileList([]); // Limpia la lista de archivos mostrada
    // Cambia el texto del botón de modo
    document.getElementById("multiple").textContent = batchMode
      ? "Cargar uno"
      : "Cargar archivos";
    // Cambia el texto del botón de carga
    btnLoad.textContent = batchMode
      ? "Cargar archivos"
      : "Cargar archivo";
  };

  // Validación del número de archivos en modo lote
  document.querySelector("form").onsubmit = function (event) {
    if (batchMode && fileInput.files.length > 50) {
      alert("No puedes subir más de 15 archivos en modo lote.");
      event.preventDefault(); // Evita que se envíe el formulario
    }
  };
});
