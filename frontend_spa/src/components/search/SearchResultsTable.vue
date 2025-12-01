<template>
  <div class="card table-card">
    <div class="card-body">
      <div class="section-card-title mb-3">
        <div>
          <h5 class="card-title mb-1">Результаты поиска</h5>
          <p class="text-muted mb-0">
            <span v-if="products.length">Найдено {{ products.length }} товаров. Получите характеристики, чтобы увидеть фото, цену и наличие.</span>
            <span v-else>Результатов пока нет. Введите артикулы и нажмите «Найти».</span>
          </p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-outline-gradient" :disabled="products.length === 0 || requesting" @click="requestDetails">
            <span v-if="requesting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <i v-else class="bi bi-collection-play me-1"></i>
            {{ requesting ? 'Идёт обработка…' : 'Получить характеристики товаров' }}
          </button>
          <button class="btn btn-ghost btn-outline-light" :disabled="refreshing" @click="$emit('refresh')">
            <i class="bi bi-arrow-repeat me-1"></i> Обновить
          </button>
        </div>
      </div>
      <div v-if="products.length === 0" class="empty-state">
        Результатов пока нет. Введите артикулы и нажмите «Найти».
      </div>
      <div v-else>
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Артикул</th>
                <th>Бренд</th>
                <th>Наименование</th>
                <th>Цена</th>
                <th>Наличие</th>
                <th>Статус характеристик</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in products" :key="product.id">
                <td class="fw-semibold">{{ product.artid }}</td>
                <td>{{ product.brand }}</td>
                <td>{{ product.name }}</td>
                <td>{{ product.price ?? '—' }}</td>
                <td><span class="badge-pill muted-chip text-uppercase">{{ product.available ?? product.source }}</span></td>
                <td>
                  <span
                    :class="statusClass(product.details_status)"
                    :title="tooltipText(product.details_status)"
                  >
                    <i :class="statusIcon(product.details_status)" class="me-1"></i>
                    {{ statusLabel(product.details_status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-help mt-2">
          <i class="bi bi-arrows-expand"></i>
          <span>На мобильных таблица скроллится по горизонтали.</span>
        </div>
      </div>
      <AlertMessage
        v-if="helperMessage"
        :message="helperMessage"
        variant="info"
        class="mt-3"
      />
    </div>
  </div>
</template>

<script setup>
import AlertMessage from '../common/AlertMessage.vue';

defineProps({
  products: { type: Array, default: () => [] },
  requesting: { type: Boolean, default: false },
  refreshing: { type: Boolean, default: false },
  helperMessage: { type: String, default: '' },
});

const emit = defineEmits(['request-details', 'refresh']);

const statusClass = (status) => {
  switch (status) {
    case 'ready':
      return 'status-pill ready';
    case 'failed':
      return 'status-pill failed';
    case 'pending':
      return 'status-pill pending';
    default:
      return 'status-pill idle';
  }
};

const statusIcon = (status) => {
  switch (status) {
    case 'ready':
      return 'bi bi-check-circle-fill';
    case 'failed':
      return 'bi bi-exclamation-octagon-fill';
    default:
      return 'bi bi-arrow-repeat';
  }
};

const statusLabel = (status) => {
  switch (status) {
    case 'ready':
      return 'получены';
    case 'failed':
      return 'ошибка';
    default:
      return 'ожидание';
  }
};

const tooltipText = (status) => {
  switch (status) {
    case 'ready':
      return 'Характеристики получены через расширение';
    case 'failed':
      return 'Ошибка при получении характеристик';
    default:
      return 'В очереди или в процессе получения';
  }
};

const requestDetails = () => emit('request-details');
</script>
