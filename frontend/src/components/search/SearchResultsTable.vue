<template>
  <div class="card table-card">
    <div class="card-body">
      <div class="section-card-title mb-3">
        <div>
          <h5 class="card-title mb-1">Результаты поиска</h5>
          <p class="text-muted mb-0">
            <span v-if="products.length">Найдено {{ products.length }} товаров. Получите характеристики, чтобы увидеть фото, размеры и аналоги.</span>
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

      <template v-else>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <span class="badge text-bg-success" v-if="summary.ready">Готово: {{ summary.ready }}</span>
          <span class="badge text-bg-info" v-if="summary.pending">В обработке: {{ summary.pending }}</span>
          <span class="badge text-bg-danger" v-if="summary.failed">Ошибка: {{ summary.failed }}</span>
          <span class="badge text-bg-secondary" v-if="summary.idle">Ожидание: {{ summary.idle }}</span>
        </div>

        <div class="table-responsive wide-table">
          <table class="table table-sm table-hover align-middle mb-0">
            <thead>
              <tr>
                <th v-for="col in columns" :key="col.key" scope="col">{{ col.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in products" :key="product.id">
                <td v-for="col in columns" :key="col.key" class="align-middle">
                  <template v-if="col.key === 'artid'">
                    <a :href="armtekUrl(product.artid)" target="_blank" rel="noopener" class="fw-semibold text-decoration-none">
                      {{ product.artid }}
                    </a>
                  </template>
                  <template v-else-if="col.key === 'details_status'">
                    <span :class="statusClass(product.details_status)" :title="statusTooltip(product)">
                      <i :class="statusIcon(product.details_status)" class="me-1"></i>
                      {{ statusLabel(product.details_status) }}
                    </span>
                  </template>
                  <template v-else-if="col.key === 'image_url'">
                    <div v-if="product.details?.image_url" class="d-inline-flex align-items-center gap-2">
                      <a :href="product.details.image_url" target="_blank" rel="noopener" class="fw-semibold">Открыть</a>
                      <button class="btn btn-ghost btn-sm" type="button" @click="copyLink(product.details.image_url)" :title="copyHint">
                        <i class="bi bi-clipboard"></i>
                      </button>
                    </div>
                    <span v-else class="text-muted">—</span>
                  </template>
                  <template v-else-if="detailKeys.includes(col.key)">
                    {{ formatDetail(product.details, col.key) }}
                  </template>
                  <template v-else>
                    {{ formatProduct(product, col.key) }}
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-help mt-2">
          <i class="bi bi-arrows-expand"></i>
          <span>Таблица тянется на всю ширину экрана и скроллится по горизонтали.</span>
        </div>
      </template>

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
import { computed } from 'vue';
import AlertMessage from '../common/AlertMessage.vue';

const props = defineProps({
  products: { type: Array, default: () => [] },
  requesting: { type: Boolean, default: false },
  refreshing: { type: Boolean, default: false },
  helperMessage: { type: String, default: '' },
});

const emit = defineEmits(['request-details', 'refresh']);

const columns = [
  { key: 'artid', label: 'Артикул' },
  { key: 'brand', label: 'Бренд' },
  { key: 'name', label: 'Наименование' },
  { key: 'price', label: 'Цена' },
  { key: 'available_quantity', label: 'Кол-во' },
  { key: 'multiplicity', label: 'Кратн.' },
  { key: 'minimum_order', label: 'Мин. партия' },
  { key: 'supply_probability', label: 'Вероятность' },
  { key: 'delivery_date', label: 'Доставка' },
  { key: 'warehouse_partner', label: 'Склад партнёра' },
  { key: 'warehouse_code', label: 'Склад Armtek' },
  { key: 'return_days', label: 'Возврат, дн.' },
  { key: 'import_flag', label: 'Импорт/ПРО' },
  { key: 'special_flag', label: '713' },
  { key: 'max_retail_price', label: 'Макс. розн.' },
  { key: 'markup', label: 'Наценка' },
  { key: 'importer_markup', label: 'Надбавка имп.' },
  { key: 'producer_price', label: 'Цена производителя' },
  { key: 'markup_rest_rub', label: 'Остаток надб., ₽' },
  { key: 'markup_rest_percent', label: 'Остаток надб., %' },
  { key: 'is_analog', label: 'Аналог' },
  { key: 'note', label: 'Примечание' },
  { key: 'details_status', label: 'Статус' },
  { key: 'image_url', label: 'Фото' },
  { key: 'weight', label: 'Вес, кг' },
  { key: 'length', label: 'Длина, см' },
  { key: 'width', label: 'Ширина, см' },
  { key: 'height', label: 'Высота, см' },
  { key: 'analog_code', label: 'Код аналога' },
];

const detailKeys = ['image_url', 'weight', 'length', 'width', 'height', 'analog_code'];

const copyHint = 'Скопировать ссылку на фото';

const summary = computed(() => {
  const acc = { ready: 0, failed: 0, pending: 0, idle: 0 };
  for (const p of props.products || []) {
    acc[p.details_status] = (acc[p.details_status] || 0) + 1;
  }
  return acc;
});

const requestDetails = () => emit('request-details');

const armtekUrl = (artid) => `https://etp.armtek.ru/artinfo/index/${encodeURIComponent(artid || '')}`;

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
    case 'pending':
      return 'ожидание';
    default:
      return '—';
  }
};

const statusTooltip = (product) => {
  if (product.details_status === 'failed' && product.details_error) return product.details_error;
  if (product.details_status === 'ready') return 'Характеристики получены через расширение';
  return 'В очереди или в процессе получения';
};

const formatMoney = (value, currency = '') => {
  if (value === null || value === undefined) return '—';
  return `${value} ${currency || ''}`.trim();
};

const formatPercent = (value) => {
  if (value === null || value === undefined) return '—';
  return `${value}%`;
};

const formatProduct = (product, key) => {
  switch (key) {
    case 'price':
      return formatMoney(product.price, product.currency);
    case 'available_quantity':
      return product.available_quantity ?? '—';
    case 'supply_probability':
      return formatPercent(product.supply_probability);
    case 'delivery_date':
      return product.delivery_date || '—';
    case 'max_retail_price':
      return formatMoney(product.max_retail_price, product.currency);
    case 'markup':
      return formatMoney(product.markup, product.currency);
    case 'importer_markup':
      return formatMoney(product.importer_markup, product.currency);
    case 'producer_price':
      return formatMoney(product.producer_price, product.currency);
    case 'markup_rest_rub':
      return formatMoney(product.markup_rest_rub, product.currency);
    case 'markup_rest_percent':
      return formatPercent(product.markup_rest_percent);
    case 'is_analog':
      if (product.is_analog === null || product.is_analog === undefined) return '—';
      return product.is_analog ? 'Да' : 'Нет';
    default:
      return product[key] ?? '—';
  }
};

const formatDetail = (details = {}, key) => {
  if (!details) return '—';
  switch (key) {
    case 'weight':
      return details.weight ?? '—';
    case 'length':
      return details.length ?? '—';
    case 'width':
      return details.width ?? '—';
    case 'height':
      return details.height ?? '—';
    case 'analog_code':
      return details.analog_code || '—';
    default:
      return '—';
  }
};

const copyLink = async (url) => {
  try {
    await navigator.clipboard.writeText(url);
  } catch {
    // fail silently; UI is light-weight
  }
};
</script>

<style scoped>
.wide-table {
  width: 100%;
  overflow-x: auto;
}

.wide-table table {
  min-width: 1400px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 12px;
  color: #0f172a;
}

.status-pill.ready {
  background: #d1fae5;
  color: #065f46;
}

.status-pill.pending {
  background: #e0f2fe;
  color: #0ea5e9;
}

.status-pill.failed {
  background: #fee2e2;
  color: #b91c1c;
}

.status-pill.idle {
  background: #e5e7eb;
  color: #374151;
}

.table-card {
  border: 1px solid #e5e7eb;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.04);
}

.table-responsive::-webkit-scrollbar {
  height: 8px;
}

.table-responsive::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-help {
  color: #6b7280;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
