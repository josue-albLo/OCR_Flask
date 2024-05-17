var modal = document.getElementById("mymodal") || null;
var btn = document.getElementById("openModal") || null;
var btnOneFile = document.getElementById("multiple").textContent || null;
var context = data_context.data || null;

btn.onclick = function () {
  modal.style.display = "block";
  
};

window.onload = function() {
  if (context != 1) {
      modal.style.display = "none";
  }
};

window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
    const element = document.getElementById("send-form");
    const input_element = document.getElementById("file");
    element.innerHTML = "";
    input_element.value = "";
  }
};

function clearInfo() {
  const form = document.getElementById("data-to-save");
  const inputFile = document.getElementById("file");
  form.innerHTML = "";
  inputFile.value = "";
  modal.style.display = "none";
}