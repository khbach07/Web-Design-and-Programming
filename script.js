let form = document.querySelector("#scoreForm");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  let score1 = document.querySelector("#score1").value;
  let score2 = document.querySelector("#score2").value;
  let score3 = document.querySelector("#score3").value;

  if (Number(score1) < 0 || Number(score2) < 0 || Number(score3) < 0) {
    let error = document.createElement("p");
    error.textContent = "Điểm không được là số âm.";
    error.className = "notice notice--error";
    form.appendChild(error);

    setTimeout(() => {
      error.remove();
    }, 3000);

    return;
  }

  let total = Number(score1) + Number(score2) + Number(score3);

  let result = document.querySelector("#result");
  let totalValue = document.querySelector("#totalValue");
  totalValue.textContent = total.toFixed(1);
  result.hidden = false;
});