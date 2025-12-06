// ==UserScript==
// @name         Elizabeth Armtek Helper (Django)
// @namespace    https://github.com/s-salamatov/Elizabeth
// @version      1.0
// @description  Парсит карточку товара Armtek и отправляет характеристики в новый Django API с request_id.
// @match        https://etp.armtek.ru/*
// @run-at       document-end
// @grant        none
// ==/UserScript==

(() => {
  'use strict';

  // Настроить под окружение
  const API_BASE = 'http://127.0.0.1:8000/api/v1'; // Django backend
  const INGEST_ENDPOINT = (productId, requestId) => `${API_BASE}/products/${productId}/details?request_id=${encodeURIComponent(requestId)}`;

  const MAX_WAIT_MS = 120000;
  const CHECK_INTERVAL_MS = 1000;
  const PAGE_READY_EXTRA_DELAY_MS = 250;
  const FAIL_CLOSE_DELAY_MS = 5000;

  const logPrefix = '[Elizabeth Armtek Helper]';
  const log = (...args) => console.log(logPrefix, ...args);
  const logError = (...args) => console.error(logPrefix, ...args);
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const qs = new URL(window.location.href).searchParams;
  const requestId = qs.get('request_id');
  const productId = qs.get('elizabeth_product_id');

  if (!requestId || !productId) {
    log('No request_id or product_id in URL, skipping');
    return;
  }

  const extractArtidFromPath = (pathname) => {
    const match = pathname.match(/\/artinfo\/index\/([^/?#]+)/i);
    return match ? decodeURIComponent(match[1]) : null;
  };

  const getPropsContainer = (doc) => doc.querySelector('#main_info .content-part-props');

  const isReadyForParsing = (doc) => {
    const container = doc.querySelector('#artInfo-container');
    const props = getPropsContainer(doc);
    return Boolean(container && props && props.querySelector('div'));
  };

  const extractImageUrlFromDom = (doc) => {
    const container = doc.querySelector('#artInfo-container');
    if (!container) return null;
    const link =
      container.querySelector('div.galleryInfo div.main-image a[data-imagelightbox="tecdoc"]') ||
      container.querySelector('div.main-image a[data-imagelightbox="tecdoc"]') ||
      container.querySelector('a[data-imagelightbox="tecdoc"]');
    if (!link) return null;
    const idAttr = link.getAttribute('id');
    const hrefAttr = link.getAttribute('href');
    if (idAttr && /^https?:\/\//i.test(idAttr)) return idAttr;
    if (hrefAttr && /^https?:\/\//i.test(hrefAttr)) return hrefAttr;
    return null;
  };

  const normalizeLabel = (text) => (text || '').replace(/\s+/g, ' ').replace(/:/g, '').trim().toLowerCase();

  const findPropValue = (doc, targets) => {
    const container = getPropsContainer(doc);
    if (!container) return null;
    const normalizedTargets = targets.map(normalizeLabel);
    const rows = Array.from(container.querySelectorAll('div'));
    for (const row of rows) {
      const labelNode = row.querySelector('.item-prop');
      const valueNode = row.querySelector('.item-value');
      if (!labelNode || !valueNode) continue;
      const labelText = normalizeLabel(labelNode.getAttribute('title') || labelNode.textContent || '');
      if (!labelText) continue;
      if (normalizedTargets.some((target) => labelText.includes(target))) {
        const valueText = valueNode.textContent || '';
        const cleaned = valueText.trim();
        return cleaned || null;
      }
    }
    return null;
  };

  const extractAdditionalCharacteristics = (doc) => {
    const weightRaw = findPropValue(doc, ['вес', 'вес в индивидуальной упаковке', 'вес в инд']);
    const lengthRaw = findPropValue(doc, ['длина']);
    const heightRaw = findPropValue(doc, ['высота']);
    const widthRaw = findPropValue(doc, ['ширина']);
    const analogRaw = findPropValue(doc, ['код аналога']);
    return {
      package_weight_raw: weightRaw,
      package_length_raw: lengthRaw,
      package_height_raw: heightRaw,
      package_width_raw: widthRaw,
      analog_code: analogRaw ? analogRaw.trim() : null,
    };
  };

  const scanOemNumbers = (doc) => {
    const selectors = [
      '#oems-tab-content .oemnumber-container a',
      '#oems-tab-content .all-oemsnumber-container .brands-list .oemsnumber-brand-container a',
      '#oems-tab-content a',
    ];
    const seen = new Set();
    selectors.forEach((sel) => {
      doc.querySelectorAll(sel).forEach((a) => {
        const text = (a.textContent || '').trim();
        if (text) seen.add(text);
      });
    });
    return Array.from(seen);
  };

  const waitForOems = async (maxWaitMs = 8000, interval = 400) => {
    // 1) попробуем прочитать, даже если вкладка не активна
    let numbers = scanOemNumbers(document);
    if (numbers.length) return numbers;

    // 2) если пусто — активируем вкладку и ждём появления DOM
    const oemTabToggle =
      document.querySelector('a[href="#oems-tab-content"]') ||
      document.querySelector('[data-bs-target="#oems-tab-content"]') ||
      document.querySelector('[data-target="#oems-tab-content"]');
    if (oemTabToggle) {
      oemTabToggle.click();
    }

    const start = Date.now();
    while (Date.now() - start < maxWaitMs) {
      numbers = scanOemNumbers(document);
      if (numbers.length) return numbers;
      await sleep(interval);
    }
    return [];
  };

  const waitForProductPage = async () => {
    const start = Date.now();
    while (Date.now() - start < MAX_WAIT_MS) {
      if (isReadyForParsing(document)) {
        await sleep(PAGE_READY_EXTRA_DELAY_MS);
        return 'product';
      }
      await sleep(CHECK_INTERVAL_MS);
    }
    return 'timeout';
  };

  const sendCharacteristicsToBackend = async (imageUrl, extra, oemNumbers) => {
    const artid = extractArtidFromPath(window.location.pathname);
    const payload = {};
    if (imageUrl) payload.image_url = imageUrl;
    if (extra.package_weight_raw) payload.package_weight_raw = extra.package_weight_raw;
    if (extra.package_length_raw) payload.package_length_raw = extra.package_length_raw;
    if (extra.package_height_raw) payload.package_height_raw = extra.package_height_raw;
    if (extra.package_width_raw) payload.package_width_raw = extra.package_width_raw;
    if (extra.analog_code) payload.analog_code = extra.analog_code;
    if (oemNumbers && oemNumbers.length) payload.oem_numbers = oemNumbers;

    const resp = await fetch(INGEST_ENDPOINT(productId, requestId), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Details-Token': requestId,
      },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      throw new Error(`Ingest failed: ${resp.status}`);
    }
  };

  const main = async () => {
    const state = await waitForProductPage();
    if (state !== 'product') {
      logError('Page not ready, state=', state);
      setTimeout(() => window.close(), FAIL_CLOSE_DELAY_MS);
      return;
    }

    const imageUrl = extractImageUrlFromDom(document);
    const extra = extractAdditionalCharacteristics(document);
    const oemNumbers = await waitForOems();
    try {
      await sendCharacteristicsToBackend(imageUrl, extra, oemNumbers);
      log('Sent details for product', productId, requestId);
    } catch (err) {
      logError('Send failed', err);
    }
    setTimeout(() => window.close(), 1000);
  };

  main();
})();
