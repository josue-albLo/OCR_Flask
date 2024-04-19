const modal = document.getElementById("mymodal");
const btn = document.getElementById("openModal");

btn.onclick = function () {
  modal.style.display = "block";
  
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

