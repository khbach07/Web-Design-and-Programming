async function fetchItems() {
  try {
    const response = await fetch("/items");

    if (!response.ok) {
      throw new Error("Failed to fetch items");
    }

    const items = await response.json();

    console.log("Fetched items:", items);

    return items;
  } catch (err) {
    console.error(err);
    return [];
  }
}


async function renderItems() {
  const data = await fetchItems();

  const itemData = data.items;

  const tableBody = document.querySelector("#user-table tbody");

  tableBody.innerHTML = "";

  itemData.forEach((item) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${item.id}</td>
      <td>${item.name}</td>
      <td>${item.price}</td>
    `;

    tableBody.appendChild(row);
  });
}


const fetchBtn = document.getElementById("fetchBtn");

if (fetchBtn) {
  fetchBtn.addEventListener("click", renderItems);
}