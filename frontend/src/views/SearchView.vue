<template>
  <MainLayout>
    <SearchForm
      v-model="query"
      :loading="loading"
      :error="error"
      :collapsed="isCollapsed"
      :can-collapse="hasSearched"
      @toggle-collapse="toggleCollapse"
      @submit="onSearch"
    />

    <transition name="fade-up">
      <SearchResultsTable
        v-if="hasSearched"
        ref="resultsCard"
        class="mt-3"
        :products="products"
        :requesting="requestingDetails"
        :refreshing="refreshing"
        @request-details="requestDetails"
        @refresh="refresh"
      />
    </transition>
  </MainLayout>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
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
const hasSearched = ref(false);
const isCollapsed = ref(false);
const resultsCard = ref(null);
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
    startPolling();
    hasSearched.value = true;
    isCollapsed.value = true;
    await focusResults();
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
    hasSearched.value = true;
    isCollapsed.value = true;
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
    // silent polling failure
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
  const processed = new Set();
  try {
    while (true) {
      const { data } = await ProductApi.jobs(50, searchRequestId.value);
      const queue = Array.isArray(data)
        ? data.filter((job) => job && !processed.has(job.request_id))
        : [];

      if (!queue.length) {
        break;
      }

      for (const job of queue) {
        if (!job?.request_id) {
          continue;
        }
        processed.add(job.request_id);
        if (job.open_url) {
          window.open(job.open_url, '_blank', 'noopener,noreferrer');
        }
        const result = await waitForDetails(job.request_id);
        if (result === 'timeout' || result === 'error') {
          return;
        }
      }
    }
  } catch {
    // ignore errors, user can retry
  } finally {
    openingQueue = false;
  }
};

const loadRequestFromRoute = async () => {
  const id = route.query.request;
  if (!id) return;
  searchRequestId.value = id;
  hasSearched.value = true;
  await refresh();
};

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const focusResults = async () => {
  await nextTick();
  if (resultsCard.value?.$el) {
    resultsCard.value.$el.focus({ preventScroll: false });
  }
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
