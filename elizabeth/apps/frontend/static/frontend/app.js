(function () {
  const apiBase = window.API_BASE || '/api/v1';
  let accessToken = null;
  let refreshToken = null;

  const els = {
    username: document.getElementById('username'),
    password: document.getElementById('password'),
    email: document.getElementById('email'),
    defaultSource: document.getElementById('default-source'),
    loginBtn: document.getElementById('login-btn'),
    registerBtn: document.getElementById('register-btn'),
    authStatus: document.getElementById('auth-status'),
    profileStatus: document.getElementById('profile-status'),
    profileSave: document.getElementById('profile-save-btn'),
    singleQuery: document.getElementById('single-query'),
    singleSearch: document.getElementById('single-search-btn'),
    bulkInput: document.getElementById('bulk-input'),
    bulkSearch: document.getElementById('bulk-search-btn'),
    fileInput: document.getElementById('file-input'),
    tableBody: document.querySelector('#results-table tbody'),
    searchStatus: document.getElementById('search-status'),
    productCount: document.getElementById('product-count'),
    refreshDetails: null,
    credsLogin: null,
    credsPassword: null,
    credsBtn: null,
    armtekStatus: null,
  };

  function ensureCredentialInputs() {
    let card = document.getElementById('auth-card');
    const loginLabel = document.createElement('label');
    loginLabel.textContent = 'Armtek login';
    const loginInput = document.createElement('input');
    loginInput.placeholder = 'ARMTEK login';
    const passwordLabel = document.createElement('label');
    passwordLabel.textContent = 'Armtek password';
    const passwordInput = document.createElement('input');
    passwordInput.type = 'password';
    passwordInput.placeholder = 'ARMTEK password';
    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save Armtek credentials';
    saveBtn.classList.add('secondary');
    const status = document.createElement('div');
    status.id = 'armtek-status';
    status.className = 'toast';
    status.style.display = 'none';
    card.appendChild(loginLabel);
    card.appendChild(loginInput);
    card.appendChild(passwordLabel);
    card.appendChild(passwordInput);
    card.appendChild(saveBtn);
    card.appendChild(status);
    els.credsLogin = loginInput;
    els.credsPassword = passwordInput;
    els.credsBtn = saveBtn;
    els.armtekStatus = status;
    saveBtn.onclick = saveCredentials;
  }

  function renderTableHeaders() {
    const thead = document.querySelector('#results-table thead tr');
    thead.innerHTML = '<th>ArtID</th><th>PIN</th><th>Brand</th><th>Name</th><th>Source</th><th>Details</th>';
  }

  function setAuthStatus(msg, isError = false) {
    els.authStatus.textContent = msg;
    els.authStatus.classList.toggle('error', isError);
    els.authStatus.style.display = 'block';
  }

  function setProfileStatus(msg, isError = false) {
    els.profileStatus.textContent = msg;
    els.profileStatus.classList.toggle('error', isError);
    els.profileStatus.style.display = 'block';
  }

  function setArmtekStatus(msg, isError = false) {
    if (!els.armtekStatus) return;
    els.armtekStatus.textContent = msg;
    els.armtekStatus.classList.toggle('error', isError);
    els.armtekStatus.style.display = 'block';
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
      fetchProfile();
      loadCredentials();
    } catch (err) {
      setAuthStatus(err.message, true);
    }
  }

  async function fetchProfile() {
    if (!accessToken) return;
    try {
      const resp = await fetch(`${apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || 'Failed to load profile');
      els.email.value = data.user?.email || '';
      els.defaultSource.value = data.settings?.default_search_source || 'armtek';
      setProfileStatus('Profile loaded');
    } catch (err) {
      setProfileStatus(err.message, true);
    }
  }

  async function saveProfile() {
    if (!accessToken) {
      setProfileStatus('Authorize first', true);
      return;
    }
    try {
      const resp = await fetch(`${apiBase}/auth/me`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          email: els.email.value,
          default_search_source: els.defaultSource.value || 'armtek',
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || 'Profile save failed');
      setProfileStatus('Profile updated');
    } catch (err) {
      setProfileStatus(err.message, true);
    }
  }

  async function saveCredentials() {
    if (!accessToken) {
      setAuthStatus('Get JWT first', true);
      return;
    }
    const payload = {
      login: els.credsLogin.value.trim(),
      password: els.credsPassword.value.trim(),
    };
    if (!payload.login || !payload.password) {
      setAuthStatus('Login/password required for Armtek', true);
      return;
    }
    try {
      const resp = await fetch(`${apiBase}/providers/armtek/credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error('Saving credentials failed');
      setArmtekStatus('Armtek credentials saved');
    } catch (err) {
      setArmtekStatus(err.message, true);
    }
  }

  async function loadCredentials() {
    if (!accessToken) return;
    try {
      const resp = await fetch(`${apiBase}/providers/armtek/credentials`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (resp.status === 204) return;
      const data = await resp.json();
      if (data.login) {
        els.credsLogin.value = data.login;
        setArmtekStatus('Loaded Armtek credentials');
      }
    } catch (err) {
      setArmtekStatus(err.message, true);
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
    payload.source = els.defaultSource.value || 'armtek';
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
    wireJobsButton(products.map((p) => p.id));
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

  function wireJobsButton(productIds) {
    let btn = document.getElementById('open-jobs-btn');
    if (!btn) {
      btn = document.createElement('button');
      btn.id = 'open-jobs-btn';
      btn.textContent = 'Получить дополнительные характеристики';
      document.querySelector('section.card').appendChild(btn);
    }
    btn.onclick = () => startDetailsFlow(productIds);
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

  async function startDetailsFlow(productIds) {
    if (!productIds || !productIds.length) {
      els.searchStatus.textContent = 'Нет товаров для запроса деталей';
      return;
    }
    try {
      await fetch(`${apiBase}/products/details/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ product_ids: productIds }),
      });
      const jobsResp = await fetch(`${apiBase}/products/details/jobs?limit=50`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const jobs = await jobsResp.json();
      jobs.forEach((job) => {
        window.open(job.open_url, '_blank', 'noopener,noreferrer');
      });
      const ids = jobs.map((j) => j.request_id);
      if (ids.length) {
        setTimeout(() => pollDetails(ids), 5000);
      }
    } catch (err) {
      els.searchStatus.textContent = err.message;
    }
  }

  // Event listeners
  els.loginBtn.addEventListener('click', () => auth('login'));
  els.registerBtn.addEventListener('click', () => auth('register'));
  els.profileSave.addEventListener('click', saveProfile);
  els.singleSearch.addEventListener('click', () => runSearch(false));
  els.bulkSearch.addEventListener('click', () => runSearch(true));
  bindFileInput();
  ensureCredentialInputs();
})();
