document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const themeToggle = document.getElementById("theme-toggle");
  const themeLabel = themeToggle?.querySelector(".theme-label");
  const themeIcon = themeToggle?.querySelector("i");
  const hintText = document.getElementById("hint-text");
  const root = document.documentElement;
  const themes = ["auto", "light", "dark"];
  const THEME_KEY = "ui-theme";

  const initTooltips = () => {
    if (window.bootstrap?.Tooltip) {
      document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        new window.bootstrap.Tooltip(el);
      });
    }
  };

  const setHint = (text) => {
    if (hintText) {
      hintText.innerHTML = text;
    }
  };

  const formatValue = (value) => {
    if (value === null || value === undefined || value === "") return "—";
    if (typeof value === "string" && !isNaN(Date.parse(value))) {
      const date = new Date(value);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString();
      }
    }
    return value;
  };

  const showError = (message, variant = "danger") => {
    errorBox.innerHTML = `<div class="alert alert-${variant}" role="alert">${message}</div>`;
    resultBox.innerHTML = "";
  };

  const clearError = () => {
    errorBox.innerHTML = "";
  };

  const showLoading = () => {
    resultBox.innerHTML = `
      <div class="d-flex align-items-center gap-3 fade-in-up">
        <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
        <div>
          <div class="fw-semibold">Поиск...</div>
          <div class="muted-text small">Обычно это занимает пару секунд</div>
        </div>
      </div>
    `;
  };

  const renderResult = (data) => {
    const card = document.createElement("div");
    card.className = "card border-0 fade-in-up";

    const header = document.createElement("div");
    header.className = "card-header bg-transparent border-0 d-flex align-items-center justify-content-between";
    header.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-box-seam text-primary fs-5"></i>
        <div>
          <div class="fw-bold mb-0">${data.pin || "—"} ${data.brand || ""}</div>
          <div class="muted-text small">${data.name || "Без названия"}</div>
        </div>
      </div>
      <span class="badge text-bg-primary">${data.currency || ""} ${data.price ?? ""}</span>
    `;

    const body = document.createElement("div");
    body.className = "card-body pt-0";

    const table = document.createElement("table");
    table.className = "table result-table mb-0";

    const fields = [
      "artid",
      "pin",
      "brand",
      "name",
      "store_code",
      "partner_store_code",
      "price",
      "currency",
      "quantity_available",
      "delivery_date",
      "guaranteed_delivery_date",
      "is_analog",
    ];

    const tbody = document.createElement("tbody");
    fields.forEach((field) => {
      const row = document.createElement("tr");
      const keyCell = document.createElement("td");
      keyCell.textContent = field;
      const valueCell = document.createElement("td");
      valueCell.textContent = formatValue(data[field]);
      row.appendChild(keyCell);
      row.appendChild(valueCell);
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    body.appendChild(table);
    card.appendChild(header);
    card.appendChild(body);
    resultBox.innerHTML = "";
    resultBox.appendChild(card);
  };

  const getSystemTheme = () => (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

  const applyTheme = (mode) => {
    root.setAttribute("data-theme", mode);
    const effective = mode === "auto" ? getSystemTheme() : mode;
    if (themeLabel && themeIcon) {
      const iconClass =
        mode === "auto" ? "bi bi-circle-half" : mode === "dark" ? "bi bi-moon-stars" : "bi bi-sun";
      const labelText = mode === "auto" ? "Авто" : mode === "dark" ? "Тёмная" : "Светлая";
      themeLabel.textContent = labelText;
      themeIcon.className = iconClass;
    }
    localStorage.setItem(THEME_KEY, mode);
  };

  const rotateTheme = () => {
    const current = root.getAttribute("data-theme") || "auto";
    const next = themes[(themes.indexOf(current) + 1) % themes.length];
    applyTheme(next);
  };

  const initTheme = () => {
    const stored = localStorage.getItem(THEME_KEY);
    applyTheme(stored || "auto");
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) {
      showError("Введите артикул", "warning");
      setHint('Проверьте правильность артикула и бренда. Форматы: <strong>332101_KYB</strong>, <strong>332101 KYB</strong>, <strong>332101</strong>.');
      return;
    }

    clearError();
    setHint("Выполняем поиск. Если результатов нет, попробуйте указать бренд явно.");
    showLoading();
    searchButton.disabled = true;
    searchButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Поиск...';

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.error) {
        showError(data.error || "Не удалось выполнить поиск");
        setHint("Проверьте правильность артикула и бренда.");
        return;
      }
      renderResult(data);
      setHint("Готово. Вы можете изменить запрос или попробовать другой бренд.");
    } catch (error) {
      showError("Не удалось выполнить запрос. Проверьте подключение.");
      setHint("Проверьте интернет и повторите попытку.");
    } finally {
      searchButton.disabled = false;
      searchButton.innerHTML = '<i class="bi bi-arrow-right-short"></i> Найти';
    }
  };

  initTheme();
  initTooltips();
  form.addEventListener("submit", handleSearch);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      handleSearch(event);
    }
  });
  themeToggle?.addEventListener("click", rotateTheme);
});
