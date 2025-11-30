document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");
  const importButton = document.getElementById("import-button");
  const fileInput = document.getElementById("file-input");
  const fetchCharacteristicsBtn = document.getElementById("fetch-characteristics-btn");
  const retryFailedBtn = document.getElementById("retry-failed-btn");
  const characteristicsActions = document.getElementById("characteristics-actions");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const themeToggle = document.getElementById("theme-toggle");
  const themeLabel = themeToggle?.querySelector(".theme-label");
  const themeIcon = themeToggle?.querySelector("i");
  const hintText = document.getElementById("hint-text");
  const root = document.documentElement;
  const themes = ["auto", "light", "dark"];
  const THEME_KEY = "ui-theme";
  const BACKEND_BASE_URL = (window.BACKEND_BASE_URL || "").replace(/\/$/, "");
  const polls = new Map();
  let rows = [];
  let hasCompletedParsingCycle = false;
  let highlightToken = null;

  const HUMAN_LABELS = {
    artid: "ID товара (ARTID)",
    pin: "Артикул",
    brand: "Бренд",
    name: "Название",
    store_code: "Код склада",
    partner_store_code: "Код партнёра",
    price: "Цена",
    currency: "Валюта",
    quantity_available: "Количество",
    delivery_date: "Дата отгрузки",
    guaranteed_delivery_date: "Гарантированная дата",
    is_analog: "Аналог",
    return_days: "Дней на возврат",
    multiplicity: "Кратность",
    min_quantity: "Мин. количество",
    supply_probability: "Вероятность поставки",
    image_url: "Ссылка на изображение",
    weight: "Вес в индивидуальной упаковке",
    length: "Длина",
    height: "Высота",
    width: "Ширина",
    analog_code: "Код аналога",
    status: "",
  };

  const API_FIELDS = [
    "artid",
    "pin",
    "brand",
    "name",
    "price",
    "currency",
    "quantity_available",
    "delivery_date",
    "guaranteed_delivery_date",
    "store_code",
    "partner_store_code",
    "return_days",
    "multiplicity",
    "min_quantity",
    "supply_probability",
    "is_analog",
  ];
  const CHARACTERISTIC_FIELDS = ["image_url", "weight", "length", "height", "width", "analog_code"];
  const DISPLAY_FIELDS = ["status", ...API_FIELDS, ...CHARACTERISTIC_FIELDS];
  const STATUS_META = {
    idle: { label: "Не запрошено", icon: "bi-dash-circle" },
    processing: { label: "В обработке", icon: "bi-hourglass-split" },
    success: { label: "Успешно", icon: "bi-check-circle" },
    failed: { label: "Не удалось", icon: "bi-x-circle" },
  };
  const CHARACTERISTICS_CONFIRM_TEXT =
    "Будут по очереди открываться страницы товаров на Armtek. Расширение прочитает характеристики и отправит их в систему, вкладки закроются автоматически. Не закрывайте их вручную до завершения.";
  const backendUrl = (path) => `${BACKEND_BASE_URL}${path}`;

  const confirmModalEl = document.getElementById("confirm-modal");
  const confirmModalText = document.getElementById("confirm-modal-text");
  const confirmModalConfirm = document.getElementById("confirm-modal-confirm");
  const confirmModalCancel = document.getElementById("confirm-modal-cancel");
  const confirmModal =
    confirmModalEl && window.bootstrap?.Modal ? new window.bootstrap.Modal(confirmModalEl, { backdrop: "static" }) : null;

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

  const shouldTreatAsDate = (field) => ["delivery_date", "guaranteed_delivery_date"].includes(field);

  const formatValue = (value, field) => {
    if (value === null || value === undefined || value === "") return "—";
    if (field === "is_analog") {
      if (value === true) return "Да";
      if (value === false) return "Нет";
    }
    if (shouldTreatAsDate(field) && typeof value === "string" && !isNaN(Date.parse(value))) {
      const date = new Date(value);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString();
      }
    }
    if (typeof value === "number" && Number.isFinite(value)) {
      return value % 1 === 0 ? value : value.toFixed(2);
    }
    return value;
  };

  const showError = (message, variant = "danger") => {
    errorBox.innerHTML = `<div class="alert alert-${variant}" role="alert">${message}</div>`;
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
          <div class="muted-text small">Обрабатываем список артикулов по очереди</div>
        </div>
      </div>
    `;
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
    return effective;
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

  const clearAllPolls = () => {
    polls.forEach((timer) => clearTimeout(timer));
    polls.clear();
  };

  const stopPolling = (token) => {
    const timer = polls.get(token);
    if (timer) {
      clearTimeout(timer);
      polls.delete(token);
    }
  };

  const renderStatusBadge = (status) => {
    const meta = STATUS_META[status] || STATUS_META.idle;
    return `<span class="status-icon" data-status="${status}" data-bs-toggle="tooltip" title="${meta.label}">
      <i class="bi ${meta.icon}"></i>
    </span>`;
  };

  const renderCellValue = (row, field) => {
    if (field === "status") {
      return renderStatusBadge(row.status);
    }

    if (CHARACTERISTIC_FIELDS.includes(field)) {
      const value = row.characteristics[field];
      if (field === "image_url" && value) {
        return `<div class="d-inline-flex align-items-center gap-1">
          <a href="${value}" target="_blank" rel="noopener" class="fw-semibold">Открыть</a>
          <button class="copy-link-btn" type="button" data-url="${value}" data-bs-toggle="tooltip" title="Скопировать ссылку">
            <i class="bi bi-clipboard"></i>
          </button>
        </div>`;
      }
      return formatValue(value, field);
    }

    const value = row.data[field];
    if (field === "artid" && value) {
      const url = `https://etp.armtek.ru/artinfo/index/${encodeURIComponent(value)}`;
      return `<a href="${url}" target="_blank" rel="noopener" class="fw-semibold">${value}</a>`;
    }
    return formatValue(value, field);
  };

  const defaultCharacteristics = () => ({
    image_url: null,
    weight: null,
    length: null,
    height: null,
    width: null,
    analog_code: null,
  });

  const upsertRow = (item) => {
    const idx = rows.findIndex((row) => row.data.elizabeth_token === item.elizabeth_token);
    const base = {
      data: item,
      status: "idle",
      characteristics: defaultCharacteristics(),
    };
    if (idx === -1) {
      rows.push(base);
    } else {
      const prev = rows[idx];
      rows[idx] = {
        ...base,
        status: "idle",
        characteristics: prev.characteristics ?? defaultCharacteristics(),
      };
    }
  };

  const renderPlaceholder = () => {
    resultBox.innerHTML = `<div class="muted-text">Результаты появятся здесь после поиска.</div>`;
    fetchCharacteristicsBtn.disabled = true;
    retryFailedBtn.disabled = true;
    if (characteristicsActions) {
      characteristicsActions.classList.add("d-none");
    }
  };

  const statusSummary = () => {
    const counters = rows.reduce(
      (acc, row) => {
        acc[row.status] = (acc[row.status] || 0) + 1;
        return acc;
      },
      { idle: 0, processing: 0, success: 0, failed: 0 }
    );
    return `Готово: ${counters.success}, в обработке: ${counters.processing}, ожидание: ${counters.idle}, неудачно: ${counters.failed}`;
  };

  const renderResults = () => {
    if (!rows.length) {
      renderPlaceholder();
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "d-flex flex-column gap-3 fade-in";

    const counters = rows.reduce(
      (acc, row) => {
        acc[row.status] = (acc[row.status] || 0) + 1;
        return acc;
      },
      { idle: 0, processing: 0, success: 0, failed: 0 }
    );

    const summary = document.createElement("div");
    summary.className = "d-flex justify-content-between align-items-center flex-wrap gap-2";
    const summaryBadges = [];
    if (counters.success) {
      summaryBadges.push(`<span class="badge text-bg-success">Готово: ${counters.success}</span>`);
    }
    if (counters.processing) {
      summaryBadges.push(`<span class="badge text-bg-info">В обработке: ${counters.processing}</span>`);
    }
    if (counters.idle) {
      summaryBadges.push(`<span class="badge text-bg-secondary">Ожидание: ${counters.idle}</span>`);
    }
    if (counters.failed) {
      summaryBadges.push(`<span class="badge text-bg-danger">Неудачно: ${counters.failed}</span>`);
    }

    summary.innerHTML = `
      <div class="muted-text small d-flex align-items-center flex-wrap gap-2">
        <span>Найдено ${rows.length} товаров.</span>
        ${summaryBadges.join("") || ""}
      </div>
      <div class="d-flex align-items-center gap-2">
        <span class="badge text-bg-light text-uppercase">Bulk</span>
        <span class="badge text-bg-secondary text-uppercase">Armtek</span>
      </div>
    `;

    const tableWrapper = document.createElement("div");
    tableWrapper.className = "table-responsive result-table-wrapper";

    const table = document.createElement("table");
    table.className = "table table-hover align-middle result-table mb-0";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    DISPLAY_FIELDS.forEach((field, idx) => {
      const th = document.createElement("th");
      th.textContent = idx === 0 ? "" : HUMAN_LABELS[field] || field;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    const tbody = document.createElement("tbody");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      if (highlightToken && row.data.elizabeth_token === highlightToken) {
        tr.classList.add("row-highlight");
      }
      DISPLAY_FIELDS.forEach((field) => {
        const td = document.createElement("td");
        td.innerHTML = renderCellValue(row, field);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    tableWrapper.appendChild(table);

    wrapper.appendChild(summary);
    wrapper.appendChild(tableWrapper);

    resultBox.innerHTML = "";
    resultBox.appendChild(wrapper);
    updateActionButtons();
    initTooltips();
  };

  const setStatus = (token, status) => {
    const row = rows.find((item) => item.data.elizabeth_token === token);
    if (!row) return;
    row.status = status;
    renderResults();
  };

  const applyCharacteristics = (token, payload) => {
    const row = rows.find((item) => item.data.elizabeth_token === token);
    if (!row) return;
    row.characteristics = {
      image_url: payload.image_url ?? null,
      weight: payload.weight ?? null,
      length: payload.length ?? null,
      height: payload.height ?? null,
      width: payload.width ?? null,
      analog_code: payload.analog_code ?? null,
    };
    row.data.artid = payload.artid ?? row.data.artid;
    row.status = "success";
    highlightToken = token;
    renderResults();
    highlightToken = null;
  };

  const markFailed = (token) => {
    const row = rows.find((item) => item.data.elizabeth_token === token);
    if (!row) return;
    row.status = "failed";
    renderResults();
  };

  const waitForCharacteristics = (token) =>
    new Promise((resolve) => {
      const timeoutMs = 60000;
      const delayMs = 1500;
      const startedAt = Date.now();

      const attempt = async () => {
        try {
          const response = await fetch(
            backendUrl(`/api/armtek/characteristics?token=${encodeURIComponent(token)}`),
            { method: "GET" }
          );
          const data = await response.json().catch(() => ({}));

          if (data.status === "ok") {
            stopPolling(token);
            resolve({ status: "ok", data });
            return;
          }

          if (data.status === "pending") {
            if (Date.now() - startedAt > timeoutMs) {
              stopPolling(token);
              resolve({ status: "timeout" });
              return;
            }
            const timer = setTimeout(attempt, delayMs);
            polls.set(token, timer);
            return;
          }

          stopPolling(token);
          resolve({ status: data.status || "not_found" });
        } catch (error) {
          stopPolling(token);
          resolve({ status: "error" });
        }
      };

      attempt();
    });

  const showConfirmModal = (message) =>
    new Promise((resolve) => {
      if (!confirmModal || !confirmModalEl || !confirmModalText || !confirmModalConfirm || !confirmModalCancel) {
        resolve(window.confirm(message));
        return;
      }

      confirmModalText.textContent = message;
      let settled = false;

      const cleanup = () => {
        confirmModalConfirm.removeEventListener("click", onConfirm);
        confirmModalCancel.removeEventListener("click", onCancel);
        confirmModalEl.removeEventListener("hidden.bs.modal", onHide);
      };

      const onConfirm = () => {
        settled = true;
        cleanup();
        confirmModal.hide();
        resolve(true);
      };

      const onCancel = () => {
        settled = true;
        cleanup();
        confirmModal.hide();
        resolve(false);
      };

      const onHide = () => {
        cleanup();
        if (!settled) {
          settled = true;
          resolve(false);
        }
      };

      confirmModalConfirm.addEventListener("click", onConfirm);
      confirmModalCancel.addEventListener("click", onCancel);
      confirmModalEl.addEventListener("hidden.bs.modal", onHide);

      confirmModal.show();
    });

  const processCharacteristics = async (targetRows) => {
    if (!targetRows.length) {
      showError("Нет строк для обработки. Выполните поиск или выберите другие статусы.", "warning");
      return;
    }

    const confirmed = await showConfirmModal(CHARACTERISTICS_CONFIRM_TEXT);
    if (!confirmed) return;

    clearError();
    hasCompletedParsingCycle = false;
    updateActionButtons();
    for (const row of targetRows) {
      setStatus(row.data.elizabeth_token, "processing");
      const url = `https://etp.armtek.ru/artinfo/index/${encodeURIComponent(
        row.data.artid
      )}?elizabeth_token=${row.data.elizabeth_token}`;
      window.open(url, "_blank");
      try {
        const result = await waitForCharacteristics(row.data.elizabeth_token);
        if (result.status === "ok") {
          applyCharacteristics(row.data.elizabeth_token, result.data);
        } else {
          markFailed(row.data.elizabeth_token);
        }
      } catch (err) {
        markFailed(row.data.elizabeth_token);
      }
    }
    hasCompletedParsingCycle = true;
    updateActionButtons();
  };

  const updateActionButtons = () => {
    const hasProcessable = rows.some(
      (row) => ["idle", "failed"].includes(row.status) && row.data.artid && row.data.elizabeth_token
    );
    const hasFailed = rows.some((row) => row.status === "failed");
    if (characteristicsActions) {
      characteristicsActions.classList.toggle("d-none", rows.length === 0);
    }
    fetchCharacteristicsBtn.disabled = !hasProcessable;
    retryFailedBtn.disabled = !(hasCompletedParsingCycle && hasFailed);
    retryFailedBtn.classList.toggle("d-none", !(hasCompletedParsingCycle && hasFailed));
  };

  const parseOmniInput = (text) => {
    const normalized = text.replace(/\r/g, "\n");
    const parts = normalized.split(/[,\n;/.]+/);
    const queries = [];
    const invalid = [];

    parts.forEach((raw) => {
      const chunk = raw.trim();
      if (!chunk) return;

      const registerInvalid = (reason) =>
        invalid.push({ value: chunk, reason });

      if (chunk.includes("_")) {
        const segments = chunk.split("_");
        if (segments.length !== 2) {
          registerInvalid("Используйте один разделитель '_' между артикулом и брендом");
          return;
        }
        const [pin, brandPart] = segments;
        if (!pin.trim() || !brandPart.trim()) {
          registerInvalid("Артикул и бренд не должны быть пустыми");
          return;
        }
        queries.push({ pin: pin.trim(), brand: brandPart.trim().toUpperCase() });
        return;
      }

      if (chunk.includes(" ")) {
        registerInvalid("Используйте '_' вместо пробела между артикулом и брендом");
        return;
      }

      registerInvalid("Добавьте бренд через подчёркивание");
    });

    return { queries, invalid };
  };

  const searchArmtek = async ({ pin, brand }) => {
    if (!brand) {
      throw new Error("Бренд обязателен");
    }
    const query = `${pin}_${brand}`;
    const response = await fetch(backendUrl("/api/armtek/search"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.error || !data.items?.length) {
      throw new Error(data.error || "Товар не найден");
    }

    return data.items[0];
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    const { queries, invalid } = parseOmniInput(input.value || "");
    if (!queries.length) {
      const msg =
        invalid.length > 0
          ? `Исправьте формат: ${invalid
              .slice(0, 3)
              .map((it) => `${it.value} (${it.reason})`)
              .join("; ")}`
          : "Введите хотя бы один артикул в omni-box";
      showError(msg, "warning");
      setHint(
        'Формат: <strong>PIN_BRAND</strong>, например <strong>332101_KYB</strong>. Разделители между позициями: запятая, точка, точка с запятой, слеш, новая строка. Бренд обязателен.'
      );
      return;
    }

    clearError();
    if (invalid.length) {
      showError(
        `Некоторые строки пропущены: ${invalid
          .slice(0, 3)
          .map((it) => `${it.value} (${it.reason})`)
          .join("; ")}`,
        "warning"
      );
    }
    setHint("Ищем позиции по списку. Убедитесь, что у каждой строки указан бренд.");
    clearAllPolls();
    rows = [];
    hasCompletedParsingCycle = false;
    renderPlaceholder();
    showLoading();
    document.body.classList.add("layout-expanded", "fade-in");
    searchButton.disabled = true;
    importButton.disabled = true;
    searchButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    const errors = [];
    for (const query of queries) {
      try {
        const item = await searchArmtek(query);
        upsertRow(item);
      } catch (error) {
        errors.push(`${query.pin}${query.brand ? " " + query.brand : ""}: ${error.message}`);
      }
    }

    renderResults();
    updateActionButtons();
    if (errors.length) {
      showError(`Не удалось найти: ${errors.join("; ")}`, "warning");
      setHint("Часть артикулов не найдена. Проверьте формат или укажите бренд точнее.");
    } else {
      clearError();
      setHint("Готово. Теперь можно запросить дополнительные характеристики для найденных товаров.");
    }

    searchButton.disabled = false;
    importButton.disabled = false;
    searchButton.innerHTML = '<i class="bi bi-search"></i>';
  };

  const handleFileImport = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const current = input.value ? `${input.value}\n` : "";
      input.value = `${current}${reader.result || ""}`.trim();
      input.dispatchEvent(new Event("input"));
    };
    reader.readAsText(file);
  };

  const autoResizeInput = () => {
    if (!input) return;
    input.style.height = "auto";
    input.style.height = `${input.scrollHeight}px`;
  };

  initTheme();
  initTooltips();
  renderPlaceholder();
  form.addEventListener("submit", handleSearch);
  input.addEventListener("input", autoResizeInput);
  themeToggle?.addEventListener("click", rotateTheme);
  importButton?.addEventListener("click", () => fileInput?.click());
  fileInput?.addEventListener("change", handleFileImport);
  fetchCharacteristicsBtn?.addEventListener("click", () => {
    const targets = rows.filter(
      (row) => ["idle", "failed"].includes(row.status) && row.data.artid && row.data.elizabeth_token
    );
    processCharacteristics(targets);
  });
  retryFailedBtn?.addEventListener("click", () => {
    const targets = rows.filter((row) => row.status === "failed" && row.data.artid && row.data.elizabeth_token);
    processCharacteristics(targets);
  });

  resultBox.addEventListener("click", async (event) => {
    const btn = event.target.closest(".copy-link-btn");
    if (!btn) return;
    const url = btn.getAttribute("data-url");
    if (!url) return;
    try {
      await navigator.clipboard.writeText(url);
      btn.setAttribute("title", "Скопировано");
      btn.setAttribute("data-bs-original-title", "Скопировано");
      if (window.bootstrap?.Tooltip) {
        const instance = window.bootstrap.Tooltip.getInstance(btn) || new window.bootstrap.Tooltip(btn);
        instance.show();
        setTimeout(() => instance.hide(), 800);
      }
    } catch (err) {
      showError("Не удалось скопировать ссылку. Проверьте доступ к буферу обмена.", "warning");
    }
  });
});
