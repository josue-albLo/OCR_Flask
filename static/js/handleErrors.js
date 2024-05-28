// script.js
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("errorModal");

  // Si se encuentra el div, muestra los errores en el modal
  if (modal) {

    // Muestra el modal
    modal.style.display = "block";

    // Oculta el modal después de 5 segundos
    setTimeout(() => {
      modal.style.display = "none";
    }, 5000);
  }

  // Cierra el modal cuando el usuario hace clic fuera del modal
  window.addEventListener("click", function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
});
