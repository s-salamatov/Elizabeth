export async function mockBackend(page) {
  const user = { id: 1, email: 'demo@example.com', name: 'Demo User' };
  const settings = { theme: 'light', locale: 'ru' };
  const products = [
    { id: 10, artid: 'A001', brand: 'Bosch', name: 'Filter', source: 'Armtek', details_status: 'pending' },
    { id: 11, artid: 'B222', brand: 'NGK', name: 'Spark Plug', source: 'Armtek', details_status: 'ready' }
  ];

  await page.route('**/api/v1/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ user, settings }) })
  );

  await page.route('**/api/v1/auth/login', async (route) => {
    const body = await route.request().postDataJSON();
    const success = body.password === 'password';
    if (!success) {
      return route.fulfill({ status: 400, body: JSON.stringify({ detail: 'invalid credentials' }) });
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ user, tokens: { access: 'token', refresh: 'refresh' } })
    });
  });

  await page.route('**/api/v1/search/bulk', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ request: { id: 'req-1', query_string: 'A001' }, products })
    })
  );

  await page.route('**/api/v1/search/req-1', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ request: { id: 'req-1', query_string: 'A001' }, products })
    })
  );

  await page.route('**/api/v1/products/details/request', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 10, product_id: 10, request_id: 'job-1', status: 'pending' },
        { id: 11, product_id: 11, request_id: 'job-2', status: 'ready' }
      ])
    })
  );

  await page.route('**/api/v1/products/details/status', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 10, artid: 'A001', brand: 'Bosch', name: 'Filter', source: 'Armtek', details_status: 'pending', request_id: 'job-1' },
        { id: 11, artid: 'B222', brand: 'NGK', name: 'Spark Plug', source: 'Armtek', details_status: 'ready', request_id: 'job-2' }
      ])
    })
  );

  await page.route('**/api/v1/providers/armtek/credentials', (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({ status: 200, body: JSON.stringify({ username: 'armtek-user' }) });
    }
    return route.fulfill({ status: 200, body: JSON.stringify({ username: 'armtek-user' }) });
  });

  await page.route('**/api/v1/providers/armtek/credentials', (route) => {
    if (route.request().method() === 'DELETE') {
      return route.fulfill({ status: 204, body: '' });
    }
    route.fallback();
  });
}

export async function primeLocalAuth(page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('elizabeth_tokens', JSON.stringify({ access: 'token', refresh: 'refresh' }));
  });
}
