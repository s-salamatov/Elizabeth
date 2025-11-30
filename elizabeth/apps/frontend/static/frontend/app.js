(function () {
  const apiBase = window.API_BASE || '/api/v1';
  let accessToken = null;
  let refreshToken = null;

  const els = {
    username: document.getElementById('username'),
    password: document.getElementById('password'),
    loginBtn: document.getElementById('login-btn'),
    registerBtn: document.getElementById('register-btn'),
    authStatus: document.getElementById('auth-status'),
    singleQuery: document.getElementById('single-query'),
    singleSearch: document.getElementById('single-search-btn'),
    bulkInput: document.getElementById('bulk-input'),
    bulkSearch: document.getElementById('bulk-search-btn'),
    fileInput: document.getElementById('file-input'),
    tableBody: document.querySelector('#results-table tbody'),
    searchStatus: document.getElementById('search-status'),
    productCount: document.getElementById('product-count'),
    refreshDetails: null,
  };

  function renderTableHeaders() {
    const thead = document.querySelector('#results-table thead tr');
    thead.innerHTML = '<th>ArtID</th><th>PIN</th><th>Brand</th><th>Name</th><th>Source</th><th>Details</th>';
  }

  function setAuthStatus(msg, isError = false) {
    els.authStatus.textContent = msg;
    els.authStatus.classList.toggle('error', isError);
    els.authStatus.style.display = 'block';
  }

  async function auth(endpoint) {
    const payload = {
      username: els.username.value.trim(),
      password: els.password.value.trim(),
    };
    if (!payload.username || !payload.password) {
      setAuthStatus('Username and password are required', true);
      return;
    }
    try {
      const resp = await fetch(`${apiBase}/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || 'Auth failed');
      }
      accessToken = data.tokens?.access;
      refreshToken = data.tokens?.refresh;
      setAuthStatus('Token issued. You can search now.');
      els.searchStatus.textContent = 'Authenticated. Ready to search…';
    } catch (err) {
      setAuthStatus(err.message, true);
    }
  }

  async function runSearch(isBulk) {
    if (!accessToken) {
      els.searchStatus.textContent = 'Add a token first (Auth panel).';
      return;
    }
    els.searchStatus.textContent = 'Running search…';
    const url = isBulk ? `${apiBase}/search/bulk` : `${apiBase}/search`;
    const payload = isBulk
      ? { bulk_text: els.bulkInput.value }
      : { query: els.singleQuery.value };
    if (isBulk && !payload.bulk_text.trim()) {
      els.searchStatus.textContent = 'Add queries to bulk input.';
      return;
    }
    if (!isBulk && !payload.query.trim()) {
      els.searchStatus.textContent = 'Type a query first.';
      return;
    }
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || 'Search failed');
      }
      renderResults(data.products || []);
      const count = data.products ? data.products.length : 0;
      els.searchStatus.textContent = `Request #${data.request?.id || '?'} · ${data.request?.status || 'done'}`;
      els.productCount.textContent = `${count} item${count === 1 ? '' : 's'}`;
    } catch (err) {
      els.searchStatus.textContent = err.message;
    }
  }

  function renderResults(products) {
    els.tableBody.innerHTML = '';
    renderTableHeaders();
    const requestIds = [];
    products.forEach((p) => {
      const tr = document.createElement('tr');
      const status = p.details_status || 'pending';
      if (p.request_id) requestIds.push(p.request_id);
      tr.innerHTML = `
        <td>${p.artid || ''}</td>
        <td>${p.pin || ''}</td>
        <td>${p.brand || ''}</td>
        <td>${p.name || ''}</td>
        <td>${p.source || ''}</td>
        <td>${renderDetailsCell(p, status)}</td>`;
      els.tableBody.appendChild(tr);
    });
    wirePollButton(requestIds);
  }

  function renderDetailsCell(p, status) {
    if (p.details && status === 'ready') {
      const d = p.details;
      return `Ready · ${d.weight || '-'} kg · ${d.length || '-'}×${d.width || '-'}×${d.height || '-'} · ${d.image_url ? '<a href="' + d.image_url + '" target="_blank">img</a>' : ''}`;
    }
    return `${status}${p.request_id ? ' · id ' + p.request_id.slice(0, 8) + '…' : ''}`;
  }

  function wirePollButton(requestIds) {
    let btn = document.getElementById('refresh-details-btn');
    if (!btn) {
      btn = document.createElement('button');
      btn.id = 'refresh-details-btn';
      btn.textContent = 'Refresh details (extension)';
      document.querySelector('section.card').appendChild(btn);
    }
    els.refreshDetails = btn;
    btn.onclick = () => pollDetails(requestIds);
  }

  function bindFileInput() {
    els.fileInput.addEventListener('change', (event) => {
      const file = event.target.files?.[0];
      if (!file) return;
      if (file.type !== 'text/plain') {
        els.searchStatus.textContent = 'Only .txt files are supported.';
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        els.bulkInput.value = reader.result;
      };
      reader.readAsText(file);
    });
  }

  async function pollDetails(requestIds) {
    if (!requestIds.length) {
      els.searchStatus.textContent = 'No request ids to poll. Run a search first.';
      return;
    }
    try {
      const resp = await fetch(`${apiBase}/products/details/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_ids: requestIds }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || 'Status check failed');
      }
      renderResults(data);
      els.searchStatus.textContent = 'Details refreshed from extension callbacks';
    } catch (err) {
      els.searchStatus.textContent = err.message;
    }
  }

  // Event listeners
  els.loginBtn.addEventListener('click', () => auth('login'));
  els.registerBtn.addEventListener('click', () => auth('register'));
  els.singleSearch.addEventListener('click', () => runSearch(false));
  els.bulkSearch.addEventListener('click', () => runSearch(true));
  bindFileInput();
})();
