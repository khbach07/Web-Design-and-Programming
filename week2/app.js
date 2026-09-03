let form = document.querySelector("#forms");

form.addEventListener("submit", function (event) {

    event.preventDefault();

    let age = document.querySelector("#age").value;

    if (Number(age) <= 0) {
        let error = document.createElement("p");
        error.textContent = "Age must be a positive number.";
        error.style.backgroundColor = "blue";
        error.style.padding = "10px";
        error.style.border = "1px solid black";
        error.style.boxShadow = "0 2px 4px gray";
        form.appendChild(error);

        setTimeout(() => {
            error.remove();
        }, 3000);
    }



    let noti = document.createElement("div");

    noti.textContent = "This is a notification!";

    noti.style.backgroundColor = "yellow";
    noti.style.padding = "10px";
    noti.style.border = "1px solid black";
    noti.style.boxShadow = "0 2px 4px gray";

    form.appendChild(noti);

    setTimeout(() => {
        noti.remove();
    }, 3000);
});