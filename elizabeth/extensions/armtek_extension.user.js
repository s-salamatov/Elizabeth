// ==UserScript==
// @name         Elizabeth Armtek Helper
// @namespace    http://elizabeth.local/
// @version      0.1
// @description  Читает карточку товара Armtek и отправляет характеристики в ELIZABETH по токену elizabeth_token.
// @match        https://etp.armtek.ru/*
// @run-at       document-end
// @grant        none
// ==/UserScript==

(() => {
  'use strict';

  const ELIZABETH_BACKEND_BASE_URL = 'http://127.0.0.1:5500'; // TODO: заменить на продовый при деплое
  const CHARACTERISTICS_ENDPOINT = `${ELIZABETH_BACKEND_BASE_URL}/api/armtek/characteristics`;

  const MAX_WAIT_MS = 120000;
  const CHECK_INTERVAL_MS = 1000;
  const PAGE_READY_EXTRA_DELAY_MS = 250;
  const FAIL_CLOSE_DELAY_MS = 8000;

  const logPrefix = '[Elizabeth Armtek Helper]';
  const log = (...args) => console.log(logPrefix, ...args);
  const logError = (...args) => console.error(logPrefix, ...args);

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const getTokenFromUrl = () => {
    try {
      return new URL(window.location.href).searchParams.get('elizabeth_token');
    } catch (e) {
      return null;
    }
  };

  const extractArtidFromPath = (pathname) => {
    const match = pathname.match(/\/artinfo\/index\/([^/?#]+)/i);
    return match ? decodeURIComponent(match[1]) : null;
  };

  const extractArtidFromDom = (doc) => {
    const container = doc.querySelector('#artInfo-container');
    if (!container) {
      return null;
    }

    const directData = container.getAttribute('data-artid') || container.getAttribute('data-art');
    if (directData) {
      return directData;
    }

    const nodeWithData = container.querySelector('[data-artid]') || container.querySelector('[data-art]');
    if (nodeWithData) {
      return nodeWithData.getAttribute('data-artid') || nodeWithData.getAttribute('data-art');
    }

    const artInput = container.querySelector('input[name="artid"], input[name="art"], input#artid');
    if (artInput && artInput.value) {
      return artInput.value;
    }

    return null;
  };

  const isLoginPage = (doc) => {
    const loginInput = doc.querySelector('input#login');
    const passwordInput = doc.querySelector('input#password');
    const loginForm = doc.querySelector('form[action*="login"], form[action*="auth"], .login-form, .auth-form, #login-form');
    return Boolean((loginInput && passwordInput) || loginForm);
  };

  const isCaptchaPage = (doc) => {
    if (doc.querySelector('iframe[src*="challenges.cloudflare.com"]')) {
      return true;
    }
    if (doc.querySelector('[data-sitekey]')) {
      return true;
    }
    if (doc.querySelector('.cf-challenge, .cf-challenge-form, .cf-chl-widget, .challenge-form, .turnstile')) {
      return true;
    }
    return false;
  };

  const getPropsContainer = (doc) => doc.querySelector('#main_info .content-part-props');

  const isReadyForParsing = (doc) => {
    const container = doc.querySelector('#artInfo-container');
    const props = getPropsContainer(doc);
    return Boolean(container && props && props.querySelector('div'));
  };

  const waitForProductPage = async () => {
    const start = Date.now();

    while (Date.now() - start < MAX_WAIT_MS) {
      if (isReadyForParsing(document)) {
        return 'product';
      }

      if (isLoginPage(document) || isCaptchaPage(document)) {
        // intentionally just wait
      }

      await sleep(CHECK_INTERVAL_MS);
    }

    return 'timeout';
  };

  const extractImageUrlFromDom = (doc) => {
    const container = doc.querySelector('#artInfo-container');
    if (!container) {
      return null;
    }

    const link =
      container.querySelector('div.galleryInfo div.main-image a[data-imagelightbox="tecdoc"]') ||
      container.querySelector('div.main-image a[data-imagelightbox="tecdoc"]') ||
      container.querySelector('a[data-imagelightbox="tecdoc"]');

    if (!link) {
      return null;
    }

    const idAttr = link.getAttribute('id');
    const hrefAttr = link.getAttribute('href');

    if (idAttr && /^https?:\/\//i.test(idAttr)) {
      return idAttr;
    }

    if (hrefAttr && /^https?:\/\//i.test(hrefAttr)) {
      return hrefAttr;
    }

    return null;
  };

  const normalizeLabel = (text) => {
    if (!text) return '';
    return text.replace(/\s+/g, ' ').replace(/:/g, '').trim().toLowerCase();
  };

  const findPropValue = (doc, targets) => {
    const container = getPropsContainer(doc);
    if (!container) {
      return null;
    }

    const normalizedTargets = targets.map((target) => normalizeLabel(target));
    const rows = Array.from(container.querySelectorAll('div'));

    for (const row of rows) {
      const labelNode = row.querySelector('.item-prop');
      const valueNode = row.querySelector('.item-value');
      if (!labelNode || !valueNode) {
        continue;
      }

      const labelText = normalizeLabel(labelNode.getAttribute('title') || labelNode.textContent || '');
      if (!labelText) {
        continue;
      }

      if (normalizedTargets.some((target) => labelText.includes(target))) {
        const valueText = valueNode.textContent || '';
        const cleaned = valueText.trim();
        return cleaned || null;
      }
    }

    return null;
  };

  const extractAdditionalCharacteristics = (doc) => ({
    weight: findPropValue(doc, ['Вес в индивидуальной упаковке', 'Вес в инд', 'Вес']),
    length: findPropValue(doc, ['Длина']),
    height: findPropValue(doc, ['Высота']),
    width: findPropValue(doc, ['Ширина']),
    analog_code: findPropValue(doc, ['Код аналога']),
  });

  const sendCharacteristicsToBackend = async (token, artid, imageUrl, extra) => {
    const payload = {
      token: token,
      artid: artid ?? null,
      image_url: imageUrl || null,
      weight: extra.weight ?? null,
      length: extra.length ?? null,
      height: extra.height ?? null,
      width: extra.width ?? null,
      analog_code: extra.analog_code ?? null,
    };

    const resp = await fetch(CHARACTERISTICS_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    let data = null;
    try {
      data = await resp.json();
    } catch (e) {
      // ignore JSON parse errors
    }

    return { resp, data };
  };

  const scheduleClose = () => {
    setTimeout(() => {
      try {
        window.close();
      } catch (e) {
        log('Unable to close window after failure', e);
      }
    }, FAIL_CLOSE_DELAY_MS);
  };

  const main = async () => {
    const token = getTokenFromUrl();
    if (!token) {
      return;
    }

    const artidFromPath = extractArtidFromPath(window.location.pathname);

    const pageState = await waitForProductPage();
    if (pageState !== 'product') {
      log('Timeout waiting for product page');
      return;
    }

    await sleep(PAGE_READY_EXTRA_DELAY_MS);

    const artid = artidFromPath || extractArtidFromDom(document);
    const imageUrl = extractImageUrlFromDom(document);
    const extra = extractAdditionalCharacteristics(document);

    try {
      const { resp, data } = await sendCharacteristicsToBackend(token, artid, imageUrl, extra);
      const success = resp && resp.ok && (!data || data.status === 'ok');

      if (!resp || !resp.ok) {
        log('Backend responded with non-OK status', resp ? resp.status : 'no response');
      } else {
        log('Backend response status', resp.status, data);
      }

      if (success) {
        try {
          window.close();
        } catch (e) {
          log('Unable to close window', e);
        }
      } else {
        log('Scheduling tab close after failure');
        scheduleClose();
      }
    } catch (e) {
      logError('Failed to send characteristics', e);
      scheduleClose();
    }
  };

  main();
})();
