<template>
  <MainLayout>
    <div class="row g-3">
      <div class="col-12">
        <div class="hero-intro">
          <h2 class="mb-1">Мои запросы</h2>
          <p class="text-muted mb-0">История поисков. Откройте любой запрос, чтобы повторно посмотреть результаты или обновить характеристики.</p>
        </div>
      </div>
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
              <div>
                <h5 class="card-title mb-1">Последние запросы</h5>
                <p class="text-muted mb-0">Показываем свежие запросы первого экрана. Нужный не найден? Нажмите «Обновить».</p>
              </div>
              <button class="btn btn-outline-light" @click="loadRequests" :disabled="loading">
                <i class="bi bi-arrow-repeat me-1"></i> Обновить
              </button>
            </div>
            <LoadingSpinner v-if="loading" />
            <div v-else>
              <div v-if="!requests.length" class="empty-state">
                Вы ещё не выполняли поиска. Перейдите на вкладку «Поиск товаров» и запустите первый запрос.
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>Дата/время</th>
                      <th>Строка запроса</th>
                      <th>Найдено товаров</th>
                      <th>Статус</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="request in requests" :key="request.id">
                      <td>{{ formatDate(request.created_at) }}</td>
                      <td>
                        <span :title="request.query_string">{{ truncate(request.query_string) }}</span>
                      </td>
                      <td><span class="badge bg-secondary">{{ request.total_items }}</span></td>
                      <td>
                        <span :class="statusClass(request.status)">{{ statusLabel(request.status) }}</span>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-outline-gradient btn-sm" @click="openRequest(request.id)">
                          Открыть
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { SearchApi } from '../api';
import MainLayout from '../components/layout/MainLayout.vue';
import LoadingSpinner from '../components/common/LoadingSpinner.vue';

const requests = ref([]);
const loading = ref(false);
const router = useRouter();

const loadRequests = async () => {
  loading.value = true;
  try {
    const { data } = await SearchApi.list();
    requests.value = data || [];
  } catch {
    requests.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadRequests();
});

const openRequest = (id) => {
  router.push({ name: 'search', query: { request: id } });
};

const statusLabel = (status) => {
  switch (status) {
    case 'done':
      return 'выполнен';
    case 'in_progress':
      return 'в процессе';
    case 'failed':
      return 'ошибка';
    default:
      return 'ожидание';
  }
};

const statusClass = (status) => {
  switch (status) {
    case 'done':
      return 'badge text-bg-success';
    case 'failed':
      return 'badge text-bg-danger';
    case 'in_progress':
      return 'badge text-bg-info';
    default:
      return 'badge text-bg-warning text-dark';
  }
};

const truncate = (text) => {
  if (!text) return '';
  return text.length > 60 ? `${text.slice(0, 60)}…` : text;
};

const formatDate = (value) => {
  if (!value) return '';
  const date = new Date(value);
  return date.toLocaleString();
};
</script>
