<template>
  <MainLayout>
    <div class="page-header">
      <h1>Поиск товаров</h1>
      <p class="text-muted">Введите артикулы и бренды, запустите поиск и нажмите «Получить характеристики», чтобы фронтенд начал отслеживать их статус.</p>
      <div class="page-meta mt-2">
        <span class="pill-group">API /api/v1/search/bulk</span>
        <span class="muted-chip">Характеристики подтягиваются по мере готовности</span>
        <span class="muted-chip">Таблица обновляется каждые 5 секунд</span>
      </div>
    </div>

    <div class="row g-3">
      <div class="col-12">
        <SearchForm
          v-model="query"
          :loading="loading"
          :error="error"
          @submit="onSearch"
        />
      </div>
      <div class="col-12">
        <SearchResultsTable
          :products="products"
          :requesting="requestingDetails"
          :refreshing="refreshing"
          :helper-message="helperMessage"
          @request-details="requestDetails"
          @refresh="refresh"
        />
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ProductApi, SearchApi } from '../api';
import MainLayout from '../components/layout/MainLayout.vue';
import SearchForm from '../components/search/SearchForm.vue';
import SearchResultsTable from '../components/search/SearchResultsTable.vue';

const query = ref('');
const loading = ref(false);
const error = ref('');
const products = ref([]);
const searchRequestId = ref(null);
const requestingDetails = ref(false);
const refreshing = ref(false);
const helperMessage = ref('');
let pollTimer = null;
const route = useRoute();

const onSearch = async ({ value }) => {
  if (!value.trim()) {
    error.value = 'Введите артикул и бренд в формате PIN_BRAND.';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const { data } = await SearchApi.bulk({ bulk_text: value });
    searchRequestId.value = data.request.id;
    products.value = data.products || [];
    helperMessage.value =
      'Кнопка «Получить характеристики товаров» запустит процесс открытия страниц Armtek и обновит данные по мере готовности.';
    startPolling();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось выполнить поиск. Попробуйте ещё раз.';
  } finally {
    loading.value = false;
  }
};

const refresh = async () => {
  if (!searchRequestId.value) return;
  refreshing.value = true;
  try {
    const { data } = await SearchApi.detail(searchRequestId.value);
    products.value = data.products || [];
    query.value = data.request?.query_string || query.value;
    helperMessage.value =
      'Поиск обновлён. Если характеристики ещё не готовы, обновите статус позже или нажмите «Получить характеристики товаров».';
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось обновить результаты поиска.';
  } finally {
    refreshing.value = false;
  }
};

const requestDetails = async () => {
  if (!products.value.length) return;
  requestingDetails.value = true;
  try {
    const ids = products.value.map((p) => p.id);
    const { data } = await ProductApi.requestDetails(ids);
    const requests = Array.isArray(data) ? data : [];
    const requestMap = new Map(requests.map((item) => [item.product_id, item]));
    products.value = products.value.map((p) => {
      const req = requestMap.get(p.id);
      return req
        ? { ...p, request_id: req.request_id, details_status: req.status ?? 'pending' }
        : { ...p, details_status: 'pending' };
    });
    helperMessage.value =
      'Мы поставили товары в очередь. Расширение откроет вкладки Armtek, считает характеристики и вернёт их в таблицу.';
    await openArmtekQueueSequential();
    startPolling();
  } catch (err) {
    error.value =
      err.response?.data?.detail || 'Не удалось создать запросы на характеристики. Проверьте доступ к Armtek.';
  } finally {
    requestingDetails.value = false;
  }
};

const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer);
  }
  pollTimer = setInterval(pollOnce, 5000);
};

const pollOnce = async () => {
  const pending = products.value.filter((p) => p.request_id && p.details_status !== 'ready');
  if (!pending.length) {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    return;
  }
  try {
    const requestIds = pending.map((p) => p.request_id);
    const { data } = await ProductApi.pollStatus(requestIds);
    const map = new Map((data || []).map((item) => [item.id, item]));
    products.value = products.value.map((p) => (map.has(p.id) ? map.get(p.id) : p));
  } catch {
    helperMessage.value = 'Не удалось обновить статусы. Попробуйте обновить страницу или повторить позже.';
  }
};

let openingQueue = false;
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const waitForDetails = async (requestId, timeoutMs = 120000) => {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    try {
      const { data } = await ProductApi.pollStatus([requestId]);
      const entry = Array.isArray(data) ? data.find((p) => p.request_id === requestId) : null;
      if (entry && entry.details_status === 'ready') {
        const map = new Map((data || []).map((item) => [item.id, item]));
        products.value = products.value.map((p) => (map.has(p.id) ? map.get(p.id) : p));
        return 'ready';
      }
    } catch (err) {
      return err.response?.data?.detail || 'error';
    }
    await delay(3000);
  }
  return 'timeout';
};

const openArmtekQueueSequential = async () => {
  if (openingQueue) return;
  openingQueue = true;
  try {
    while (true) {
      const { data } = await ProductApi.jobs(1);
      if (!Array.isArray(data) || data.length === 0) {
        helperMessage.value =
          'Очередь характеристик пуста — если товары ещё без характеристик, попробуйте нажать «Получить характеристики товаров» снова.';
        break;
      }
      const job = data[0];
      if (job.open_url) {
        window.open(job.open_url, '_blank', 'noopener,noreferrer');
      }
      const result = await waitForDetails(job.request_id);
      if (result === 'timeout') {
        helperMessage.value = 'Таймаут ожидания расширения. Остановили очередь.';
        break;
      }
      if (result === 'error') {
        helperMessage.value = 'Ошибка при опросе статуса. Остановили очередь.';
        break;
      }
    }
  } catch (err) {
    helperMessage.value =
      err.response?.data?.detail || 'Не удалось открыть страницы Armtek для чтения характеристик.';
  } finally {
    openingQueue = false;
  }
};

const loadRequestFromRoute = async () => {
  const id = route.query.request;
  if (!id) return;
  searchRequestId.value = id;
  await refresh();
};

onMounted(() => {
  loadRequestFromRoute();
});

watch(
  () => route.query.request,
  () => {
    loadRequestFromRoute();
  },
);

onBeforeUnmount(() => {
  if (pollTimer) {
    clearInterval(pollTimer);
  }
});
</script>
