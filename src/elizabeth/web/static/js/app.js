document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");

  const renderError = (message) => {
    errorBox.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
  };

  const clearError = () => {
    errorBox.innerHTML = "";
  };

  const renderLoading = () => {
    resultBox.innerHTML = '<div class="text-muted">Загрузка...</div>';
  };

  const renderResult = (data) => {
    const table = document.createElement("table");
    table.className = "table table-striped";

    const tbody = document.createElement("tbody");
    Object.entries(data).forEach(([key, value]) => {
      const row = document.createElement("tr");
      const keyCell = document.createElement("td");
      keyCell.textContent = key;
      const valueCell = document.createElement("td");
      valueCell.textContent =
        value === null || value === undefined || value === "" ? "—" : value;
      row.appendChild(keyCell);
      row.appendChild(valueCell);
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    resultBox.innerHTML = "";
    resultBox.appendChild(table);
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) {
      renderError("Введите артикул для поиска");
      return;
    }

    clearError();
    renderLoading();

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.error) {
        renderError(data.error || "Не удалось выполнить поиск");
        resultBox.innerHTML = "";
        return;
      }

      renderResult(data);
    } catch (error) {
      renderError("Не удалось выполнить запрос. Проверьте подключение.");
      resultBox.innerHTML = "";
    }
  });
});
