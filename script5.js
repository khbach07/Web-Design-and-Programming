async function fetchUsers() {
  try {
    const response = await fetch("https://jsonplaceholder.typicode.com/users");
    const users = await response.json();
    console.log("Fetched users:", users);
    return users;
  } catch (err) {
    console.error(err);
    return [];
  }
}

async function renderUsers() {
  const userData = await fetchUsers();
  const tableBody = document.querySelector("#user-table tbody");

  tableBody.innerHTML = "";

  userData.forEach((user) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${user.id}</td>
      <td>${user.name.toUpperCase()}</td>
      <td>${user.address.street}, ${user.address.city}</td>
      <td>${user.email.toLowerCase()}</td>
      <td>${user.phone}</td>
    `;

    tableBody.appendChild(row);
  });
}

const fetchBtn = document.getElementById("fetchBtn");
if (fetchBtn) {
  fetchBtn.addEventListener("click", renderUsers);
}